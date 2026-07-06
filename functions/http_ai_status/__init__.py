import importlib.util as _iu
import json
import os
import sys
import threading
import time
from pathlib import Path

import azure.functions as func
import yaml

# Reuse shared chat providers (already copied for performance)
shared_path = Path(__file__).resolve().parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

try:
    from runtime_env import build_venv_info  # type: ignore[no-redef]  # noqa: E402
except ModuleNotFoundError:
    # Test and local import fallback when shared/ isn't injected as top-level.
    from shared.runtime_env import build_venv_info  # type: ignore[no-redef]  # noqa: E402

from chat_providers import detect_provider  # noqa: E402

_STATUS_CACHE: dict[str, object] = {
    "key": None,
    "cached_at": 0.0,
    "payload_json": None,
}
_STATUS_CACHE_LOCK = threading.RLock()
_STATUS_CACHE_DEFAULT_TTL_SECONDS = 3.0


def _get_status_cache_ttl_seconds() -> float:
    raw = os.getenv("QAI_STATUS_CACHE_TTL", str(_STATUS_CACHE_DEFAULT_TTL_SECONDS))
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = _STATUS_CACHE_DEFAULT_TTL_SECONDS
    if value < 0:
        return 0.0
    if value > 300:
        return 300.0
    return value


def _request_wants_refresh(req: func.HttpRequest) -> bool:
    try:
        refresh = (req.params or {}).get("refresh")
    except Exception:
        refresh = None
    if refresh is None:
        return False
    return str(refresh).strip().lower() in {"1", "true", "yes", "y", "on"}


def _build_status_cache_key(repo_root: Path) -> tuple[object, ...]:
    """Build a cache key that invalidates on relevant config or status changes."""

    def _mtime_or_none(path: Path) -> int | None:
        try:
            return path.stat().st_mtime_ns
        except Exception:
            return None

    adapter_cfg = repo_root / "data_out" / "lora_training" / "lora_adapter" / "adapter_config.json"
    autotrain_status = repo_root / "data_out" / "autotrain" / "status.json"
    qautorun_status = repo_root / "data_out" / "quantum_autorun" / "status.json"
    qconfig = repo_root / "ai-projects" / "quantum-ml" / "config" / "quantum_config.yaml"

    return (
        bool(os.getenv("AZURE_OPENAI_API_KEY")),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        bool(os.getenv("OPENAI_API_KEY")),
        os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
        os.getenv("LMSTUDIO_MODEL", "local-model"),
        os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"),
        os.getenv("OLLAMA_MODEL", "llama3.2"),
        os.getenv("CHAT_TEMPERATURE", "0.7"),
        _mtime_or_none(adapter_cfg),
        _mtime_or_none(autotrain_status),
        _mtime_or_none(qautorun_status),
        _mtime_or_none(qconfig),
    )


def _get_cached_payload_json(cache_key: tuple[object, ...], ttl_seconds: float) -> str | None:
    if ttl_seconds <= 0:
        return None
    with _STATUS_CACHE_LOCK:
        if _STATUS_CACHE.get("key") != cache_key:
            return None
        if (time.time() - float(_STATUS_CACHE.get("cached_at", 0.0))) >= ttl_seconds:
            return None
        payload_json = _STATUS_CACHE.get("payload_json")
        if isinstance(payload_json, str):
            return payload_json
        return None


def _set_cached_payload_json(cache_key: tuple[object, ...], payload_json: str) -> None:
    with _STATUS_CACHE_LOCK:
        _STATUS_CACHE["key"] = cache_key
        _STATUS_CACHE["cached_at"] = time.time()
        _STATUS_CACHE["payload_json"] = payload_json


def _build_status_payload(
    repo_root: Path, azure_env: dict[str, bool], openai_env: dict[str, bool]
) -> dict[str, object]:
    """Compute the full status payload (expensive path)."""
    # In-process ML deps availability
    inproc_ml = {
        "torch": _iu.find_spec("torch") is not None,
        "transformers": _iu.find_spec("transformers") is not None,
        "peft": _iu.find_spec("peft") is not None,
    }

    # Repo root and venv python
    venv_info = build_venv_info(repo_root, timeout_seconds=10)

    # LoRA default adapter location and readiness
    lora_default = repo_root / "data_out" / "lora_training" / "lora_adapter"
    adapter_cfg = lora_default / "adapter_config.json"
    tokenizer_dir = lora_default.parent / "tokenizer"
    lora_info = {
        "default_adapter_path": str(lora_default),
        "exists": lora_default.exists(),
        "adapter_config_exists": adapter_cfg.exists(),
        "tokenizer_dir_exists": tokenizer_dir.exists(),
        "base_model": None,
        "inproc_ready": all(inproc_ml.values()),
        "subprocess_ready": venv_info["exists"]
        and bool(venv_info.get("packages", {}).get("available", {}).get("torch"))
        and bool(venv_info.get("packages", {}).get("available", {}).get("transformers"))
        and bool(venv_info.get("packages", {}).get("available", {}).get("peft")),
    }
    if lora_info["adapter_config_exists"]:
        try:
            with open(adapter_cfg, encoding="utf-8") as f:
                cfg = json.load(f)
            lora_info["base_model"] = cfg.get("base_model_name_or_path")
        except Exception:
            pass

    provider, info = detect_provider(explicit="auto")
    local_resolution = {
        "requested_provider": "local",
        "resolved_provider": None,
        "resolved_model": None,
        "provider_class": None,
        "runtime_backed": False,
        "error": None,
    }
    try:
        local_provider, local_info = detect_provider(explicit="local")
        local_resolution.update(
            {
                "resolved_provider": local_info.name,
                "resolved_model": local_info.model,
                "provider_class": local_provider.__class__.__name__,
                "runtime_backed": local_info.name in ("lmstudio", "ollama"),
            }
        )
    except Exception as local_err:  # noqa: BLE001
        local_resolution["error"] = str(local_err)

    temperature = os.getenv("CHAT_TEMPERATURE", "0.7")
    chat_web_html = (repo_root / "chat-web" / "index.html").exists()
    chat_web_js = (repo_root / "chat-web" / "chat.js").exists()

    autotrain_dir = repo_root / "data_out" / "autotrain"
    autotrain_status_path = autotrain_dir / "status.json"
    autotrain_last: dict | None = None
    if autotrain_status_path.exists():
        try:
            with autotrain_status_path.open("r", encoding="utf-8") as f:
                autotrain_last = json.load(f)
        except Exception:
            autotrain_last = {"error": "failed to parse status.json"}

    qautorun_dir = repo_root / "data_out" / "quantum_autorun"
    qautorun_status_path = qautorun_dir / "status.json"
    qautorun_last: dict | None = None
    quantum_azure: dict | None = None
    if qautorun_status_path.exists():
        try:
            with qautorun_status_path.open("r", encoding="utf-8") as f:
                qautorun_last = json.load(f)
        except Exception:
            qautorun_last = {"error": "failed to parse status.json"}

        try:
            cfg_path = repo_root / "ai-projects" / "quantum-ml" / "config" / "quantum_config.yaml"
            azure_ctx = None
            workspace_url = None
            if cfg_path.exists():
                with cfg_path.open("r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                az = cfg.get("azure", {})
                sub = az.get("subscription_id")
                rg = az.get("resource_group")
                ws = az.get("workspace_name")
                loc = az.get("location")
                azure_ctx = {
                    "subscription_id": sub,
                    "resource_group": rg,
                    "workspace_name": ws,
                    "location": loc,
                }
                if sub and rg and ws:
                    workspace_url = (
                        f"https://portal.azure.com/#resource/subscriptions/{sub}/resourceGroups/{rg}"
                        f"/providers/Microsoft.Quantum/Workspaces/{ws}/overview"
                    )

            azure_jobs = []
            jobs = (qautorun_last or {}).get("jobs", [])
            for j in jobs:
                meta = j.get("meta", {}) if isinstance(j, dict) else {}
                job_id = meta.get("azure_job_id")
                if job_id:
                    azure_jobs.append(
                        {
                            "name": j.get("name"),
                            "mode": j.get("mode"),
                            "job_id": job_id,
                            "backend": meta.get("azure_backend") or meta.get("backend") or j.get("mode"),
                            "success": meta.get("azure_success"),
                            "counts": meta.get("azure_counts"),
                            "results_file": meta.get("azure_results_file"),
                        }
                    )
            if azure_ctx or azure_jobs:
                quantum_azure = {
                    "workspace": azure_ctx,
                    "workspace_portal_url": workspace_url,
                    "jobs": azure_jobs,
                    "portal_job_url_template": (
                        "https://portal.azure.com/#view/Microsoft_Azure_Quantum/JobDetailsBlade?"
                        "jobId={job_id}&subscriptionId={subscription_id}&resourceGroup={resource_group}"
                        "&workspaceName={workspace_name}&location={location}"
                    ),
                }
        except Exception:
            pass

    return {
        "active_provider": info.name,
        "model": info.model,
        "local_resolution": local_resolution,
        "env": {
            "azure_openai": azure_env,
            "openai": openai_env,
            "local_fallback": True,
        },
        "ml_inprocess": inproc_ml,
        "lora": lora_info,
        "venv": venv_info,
        "temperature": temperature,
        "server": {
            "executable": sys.executable,
            "python_version": sys.version,
            "cwd": os.getcwd(),
        },
        "assets": {
            "chat_web_html": chat_web_html,
            "chat_web_js": chat_web_js,
        },
        "autotrain": autotrain_last,
        "quantum_autorun": qautorun_last,
        "quantum_azure": quantum_azure,
        "endpoints": [
            "/api/chat-web",
            "/api/chat-web/chat.js",
            "/api/chat-web/static/agi_stream_utils.js",
            "/api/chat",
            "/api/ai/status",
            "/api/agi/analyze",
            "/api/agi/reason",
            "/api/agi/stream",
            "/api/agi/status",
            "/api/agi/persistence",
        ],
        "status": "ok",
    }


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Health / status endpoint for AI provider readiness.

    Returns JSON describing:
      - active_provider: which provider auto-detect selects (azure|openai|local)
      - model: resolved model/deployment name
      - env: boolean flags indicating if required env vars are present for each cloud provider
      - temperature: current CHAT_TEMPERATURE setting

    This helps verify cloud configuration after deploying to Azure.
    """
    # Collect environment info
    azure_env = {
        "AZURE_OPENAI_API_KEY": bool(os.getenv("AZURE_OPENAI_API_KEY")),
        "AZURE_OPENAI_ENDPOINT": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
        "AZURE_OPENAI_DEPLOYMENT": bool(os.getenv("AZURE_OPENAI_DEPLOYMENT")),
        "AZURE_OPENAI_API_VERSION": bool(os.getenv("AZURE_OPENAI_API_VERSION")),
    }
    openai_env = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_MODEL": bool(os.getenv("OPENAI_MODEL")),
    }

    repo_root = Path(__file__).resolve().parents[1]
    try:
        ttl_seconds = _get_status_cache_ttl_seconds()
        cache_key = _build_status_cache_key(repo_root)
        use_cache = not _request_wants_refresh(req)
        if use_cache:
            cached_payload_json = _get_cached_payload_json(cache_key, ttl_seconds)
            if cached_payload_json is not None:
                return func.HttpResponse(cached_payload_json, status_code=200, mimetype="application/json")

        payload = _build_status_payload(repo_root, azure_env=azure_env, openai_env=openai_env)
        payload_json = json.dumps(payload)

        if use_cache and ttl_seconds > 0:
            _set_cached_payload_json(cache_key, payload_json)

        return func.HttpResponse(payload_json, status_code=200, mimetype="application/json")
    except Exception as e:  # noqa: BLE001
        payload = {
            "status": "error",
            "error": str(e),
            "env": {
                "azure_openai": azure_env,
                "openai": openai_env,
            },
        }
        return func.HttpResponse(json.dumps(payload), status_code=500, mimetype="application/json")
