"""
QAI Integration Service - FastAPI Application
Unified API for quantum AI, chat, and training operations
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from .chat_integration import ChatIntegration
    from .path_resolver import load_qai_config
    from .quantum_integration import QuantumIntegration
    from .training_integration import TrainingIntegration
except ImportError:
    # Support direct script execution (python mount/app.py).
    from chat_integration import ChatIntegration
    from path_resolver import load_qai_config
    from quantum_integration import QuantumIntegration
    from training_integration import TrainingIntegration


logger = logging.getLogger("qai.fastapi")
startup_time_utc = datetime.now(timezone.utc)
DEFAULT_CHECK_TIMEOUT_SECONDS = 3.0


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    provider: str | None = None
    stream: bool = False
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    success: bool
    provider: str | None = None
    message: str | None = None
    response: str | None = None
    conversation_id: str | None = None
    timestamp: str | None = None
    error: str | None = None


class TrainQuantumRequest(BaseModel):
    dataset: str
    n_qubits: int = Field(default=4, ge=2, le=20)
    n_layers: int = Field(default=2, ge=1, le=10)
    epochs: int = Field(default=10, ge=1, le=1000)
    backend: str = "qiskit_aer"


class TrainLoRARequest(BaseModel):
    dataset: str
    max_train_samples: int = Field(default=64, ge=1)
    max_eval_samples: int = Field(default=16, ge=1)
    epochs: int = Field(default=1, ge=1)


class OrchestratorRequest(BaseModel):
    job_name: str | None = None
    dry_run: bool = False


# Load configuration
config_path = Path(__file__).parent / "config.yaml"
config = load_qai_config(config_path)


# Initialize integration modules
quantum_integration = QuantumIntegration(config)
chat_integration = ChatIntegration(config)
training_integration = TrainingIntegration(config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("🚀 QAI Integration Service starting...")
    print(f"📊 Quantum enabled: {config['quantum']['enabled']}")
    print(f"💬 Chat enabled: {config['chat']['enabled']}")
    print(f"🎓 Training enabled: {config['training']['enabled']}")
    yield
    # Shutdown
    print("🛑 QAI Integration Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="QAI Integration Service",
    description="Unified API for Quantum AI, Chat, and Training operations",
    version=config["service"]["version"],
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Attach request id + latency headers and emit concise request logs."""
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            "request_failed request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_with_request_id(request: Request, exc: HTTPException):
    """Preserve default FastAPI HTTP errors while including request id."""
    response = await http_exception_handler(request, exc)
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return stable error shape for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.exception(
        "unhandled_exception request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


# CORS configuration
if config["api"]["cors_enabled"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["api"]["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================================
# Root & Health Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Serve the web UI"""
    static_index = Path(__file__).parent / "static" / "index.html"
    if static_index.exists():
        return FileResponse(str(static_index))

    # Fallback to API info if no UI
    return {
        "service": config["service"]["name"],
        "version": config["service"]["version"],
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "quantum": "/quantum/*",
            "chat": "/chat/*",
            "training": "/training/*",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    now = datetime.now(timezone.utc)
    return {
        "status": "healthy",
        "service": config["service"]["name"],
        "version": config["service"]["version"],
        "timestamp": now.isoformat(),
        "startup_time": startup_time_utc.isoformat(),
        "uptime_seconds": int((now - startup_time_utc).total_seconds()),
    }


@app.get("/health/live")
async def liveness_check():
    """Liveness probe indicating process is running."""
    return {
        "status": "alive",
        "service": config["service"]["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _run_component_check(
    name: str,
    getter,
    *,
    timeout_seconds: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
) -> tuple[str, str, dict | None]:
    """Run a component status getter with timeout and normalized result."""
    try:
        data = await asyncio.wait_for(getter(), timeout=timeout_seconds)
        return name, "ok", data
    except asyncio.TimeoutError:
        logger.warning("component_check_timeout component=%s", name)
        return name, f"error: timeout>{timeout_seconds:.1f}s", None
    except Exception as exc:  # noqa: BLE001
        logger.warning("component_check_failed component=%s error=%s", name, type(exc).__name__)
        return name, f"error: {type(exc).__name__}", None


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe that validates integration modules are responsive."""
    checks: dict[str, str] = {}
    status_code = 200

    results = await asyncio.gather(
        _run_component_check("quantum", quantum_integration.get_status),
        _run_component_check("chat", chat_integration.get_status),
        _run_component_check("training", training_integration.get_status),
    )
    for name, state, _ in results:
        checks[name] = state
        if state != "ok":
            status_code = 503

    body = {
        "status": "ready" if status_code == 200 else "degraded",
        "service": config["service"]["name"],
        "version": config["service"]["version"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }

    if status_code == 200:
        return body
    return JSONResponse(status_code=status_code, content=body)


@app.get("/status")
async def get_full_status():
    """Get comprehensive system status"""
    now = datetime.now(timezone.utc)
    results = await asyncio.gather(
        _run_component_check("quantum", quantum_integration.get_status),
        _run_component_check("chat", chat_integration.get_status),
        _run_component_check("training", training_integration.get_status),
    )

    checks: dict[str, str] = {}
    details: dict[str, dict | None] = {}
    degraded = False
    for name, state, payload in results:
        checks[name] = state
        details[name] = payload
        if state != "ok":
            degraded = True

    return {
        "service": config["service"]["name"],
        "version": config["service"]["version"],
        "status": "degraded" if degraded else "healthy",
        "timestamp": now.isoformat(),
        "startup_time": startup_time_utc.isoformat(),
        "uptime_seconds": int((now - startup_time_utc).total_seconds()),
        "checks": checks,
        "quantum": details["quantum"],
        "chat": details["chat"],
        "training": details["training"],
    }


# ============================================================================
# Quantum Endpoints
# ============================================================================


@app.get("/quantum/status")
async def get_quantum_status():
    """Get quantum system status"""
    return await quantum_integration.get_status()


@app.get("/quantum/datasets")
async def list_quantum_datasets():
    """List available quantum datasets"""
    return await quantum_integration.list_datasets()


@app.get("/quantum/backends")
async def list_quantum_backends():
    """List available quantum backends"""
    status = await quantum_integration.get_status()
    return {
        "backends": status["available_backends"],
        "azure_connected": status["azure_connected"],
    }


@app.post("/quantum/train")
async def train_quantum_classifier(request: TrainQuantumRequest, background_tasks: BackgroundTasks):
    """Train a quantum classifier"""
    result = await quantum_integration.train_classifier(
        dataset=request.dataset,
        n_qubits=request.n_qubits,
        n_layers=request.n_layers,
        epochs=request.epochs,
        backend=request.backend,
    )
    return result


@app.post("/quantum/autorun")
async def run_quantum_autorun(request: OrchestratorRequest):
    """Run a quantum autorun job"""
    normalized_job_name = (request.job_name or "").strip()
    if not normalized_job_name:
        raise HTTPException(status_code=400, detail="job_name is required")

    result = await quantum_integration.run_autorun_job(job_name=normalized_job_name, dry_run=request.dry_run)
    return result


@app.get("/quantum/circuit-info")
async def get_circuit_info(circuit_type: str = "variational"):
    """Get quantum circuit information"""
    return await quantum_integration.get_circuit_info(circuit_type)


# ============================================================================
# Chat Endpoints
# ============================================================================


@app.get("/chat/status")
async def get_chat_status():
    """Get chat system status"""
    return await chat_integration.get_status()


@app.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a chat message and get response"""
    result = await chat_integration.chat(
        message=request.message,
        provider=request.provider,
        stream=request.stream,
        conversation_id=request.conversation_id,
    )
    return ChatResponse(**result)


@app.get("/chat/providers")
async def get_chat_providers():
    """Get available chat providers"""
    status = await chat_integration.get_status()
    return status["providers"]


@app.get("/chat/detect-provider")
async def detect_best_provider():
    """Auto-detect best available chat provider"""
    provider = await chat_integration.detect_provider()
    return {"provider": provider}


@app.get("/chat/conversations")
async def list_conversations():
    """List all saved conversations"""
    return await chat_integration.list_conversations()


@app.get("/chat/conversations/{filename}")
async def get_conversation(filename: str):
    """Get a specific conversation"""
    messages = await chat_integration.get_conversation(filename)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"filename": filename, "messages": messages}


# ============================================================================
# Training Endpoints
# ============================================================================


@app.get("/training/status")
async def get_training_status():
    """Get training system status"""
    return await training_integration.get_status()


@app.get("/training/datasets")
async def list_training_datasets():
    """List available training datasets"""
    return await training_integration.list_datasets()


@app.post("/training/lora")
async def train_lora(request: TrainLoRARequest, background_tasks: BackgroundTasks):
    """Train a LoRA adapter"""
    result = await training_integration.train_lora(
        dataset=request.dataset,
        max_train_samples=request.max_train_samples,
        max_eval_samples=request.max_eval_samples,
        epochs=request.epochs,
    )
    return result


@app.post("/training/autotrain")
async def run_autotrain(request: OrchestratorRequest):
    """Run AutoTrain orchestrator"""
    result = await training_integration.run_autotrain(job_name=request.job_name, dry_run=request.dry_run)
    return result


@app.get("/training/autotrain/jobs")
async def list_autotrain_jobs():
    """List all configured AutoTrain jobs"""
    jobs = await training_integration.list_autotrain_jobs()
    return {"jobs": jobs}


@app.get("/training/lora-adapter")
async def get_lora_adapter_info():
    """Get LoRA adapter information"""
    status = await training_integration.get_status()
    return status["lora_adapter"]


@app.get("/training/runs")
async def list_training_runs():
    """List recent training runs"""
    status = await training_integration.get_status()
    return status["recent_trainings"]


@app.get("/training/runs/{run_name}")
async def get_training_metrics(run_name: str):
    """Get metrics for a specific training run"""
    metrics = await training_integration.get_training_metrics(run_name)
    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])
    return metrics


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    app_import = "mount.app:app" if __package__ else "app:app"

    uvicorn.run(
        app_import,
        host=config["service"]["host"],
        port=config["service"]["port"],
        reload=config["service"]["debug"],
    )
