from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    from colorama import Fore, Style, init as colorama_init
except ImportError:  # pragma: no cover - exercised in dependency-light test envs
    class _NoColor:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        RESET = RESET_ALL = BRIGHT = DIM = NORMAL = ""

    Fore = Style = _NoColor()

    def colorama_init(*args, **kwargs) -> None:
        return None

from chat_providers import detect_provider, RoleMessage


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def provider_readiness_summary() -> str:
    """Return a human-readable provider readiness summary based on env vars."""
    azure_key = bool(os.getenv("AZURE_OPENAI_API_KEY"))
    azure_endpoint = bool(os.getenv("AZURE_OPENAI_ENDPOINT"))
    azure_deployment = bool(os.getenv("AZURE_OPENAI_DEPLOYMENT"))
    azure_version = bool(os.getenv("AZURE_OPENAI_API_VERSION"))
    azure_ready = azure_key and azure_endpoint and azure_deployment and azure_version

    openai_ready = bool(os.getenv("OPENAI_API_KEY"))
    lmstudio_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

    lines = [
        "Provider readiness:",
        f"  Azure OpenAI : {'ready' if azure_ready else 'not ready'} "
        f"(key={'set' if azure_key else 'missing'}, endpoint={'set' if azure_endpoint else 'missing'}, "
        f"deployment={'set' if azure_deployment else 'missing'}, api_version={'set' if azure_version else 'missing'})",
        f"  OpenAI       : {'ready' if openai_ready else 'not ready'} (OPENAI_API_KEY {'set' if openai_ready else 'missing'})",
        f"  LM Studio    : configured via LMSTUDIO_BASE_URL={lmstudio_url}",
        f"  Ollama       : configured via OLLAMA_BASE_URL={ollama_url}",
        "  Local Echo   : always available",
    ]
    return "\n".join(lines)


def save_conversation(messages: List[RoleMessage], logs_dir: Path) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"chat_{now_ts()}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    return path


def print_system(msg: str) -> None:
    print(Fore.MAGENTA + msg + Style.RESET_ALL)


def print_user(msg: str) -> None:
    print(Fore.CYAN + msg + Style.RESET_ALL)


def print_assistant_chunk(chunk: str) -> None:
    # Avoid styles on every print for speed
    sys.stdout.write(chunk)
    sys.stdout.flush()


def print_assistant_done() -> None:
    print(Style.RESET_ALL)


def interactive_chat(args: argparse.Namespace) -> int:
    colorama_init()

    system_prompt = args.system or os.getenv(
        "SYSTEM_PROMPT",
        "You are a concise, friendly assistant. Be helpful and brief by default.",
    )
    logs_dir = Path(__file__).resolve().parent.parent / "logs"

    provider, info = detect_provider(
        explicit=args.provider, model_override=args.model)

    messages: List[RoleMessage] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    print_system(f"Provider: {info.name} | Model: {info.model}")
    print_system(
        "Type your message. Commands: /help, /new, /save, /history, /model, /providers, /reasoning, /exit")

    while True:
        try:
            user = input(Fore.CYAN + "you> " + Style.RESET_ALL)
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        cmd = user.strip().lower()
        if cmd == "/exit":
            return 0

        if cmd == "/help":
            print_system(
                "Available commands:\n"
                "  /new        — start a fresh conversation (clears history)\n"
                "  /save       — save conversation to a JSONL file\n"
                "  /history    — show conversation history summary\n"
                "  /model      — show current provider and model info\n"
                "  /providers  — show provider readiness from current env vars\n"
                "  /reasoning  — show AGI reasoning summary (AGI provider only)\n"
                "  /exit       — quit the chat\n"
                "  /help       — show this message"
            )
            continue

        if cmd == "/new":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            print_system("Started a new conversation.")
            continue

        if cmd == "/save":
            path = save_conversation(messages, logs_dir)
            print_system(f"Saved to {path}")
            continue

        if cmd == "/history":
            user_msgs = [m for m in messages if m.get("role") == "user"]
            asst_msgs = [m for m in messages if m.get("role") == "assistant"]
            print_system(
                f"Conversation: {len(user_msgs)} user message(s), "
                f"{len(asst_msgs)} assistant reply(ies)."
            )
            if user_msgs:
                last = user_msgs[-1]["content"]
                preview = last[:120] + "..." if len(last) > 120 else last
                print_system(f"Last user message: {preview}")
            continue

        if cmd == "/model":
            print_system(f"Provider : {info.name}")
            print_system(f"Model    : {info.model}")
            continue

        if cmd == "/providers":
            print_system(provider_readiness_summary())
            continue

        if cmd == "/reasoning":
            # Only AGIProvider exposes get_reasoning_summary()
            if hasattr(provider, "get_reasoning_summary"):
                # type: ignore[union-attr]
                summary = provider.get_reasoning_summary()
                print_system(
                    f"AGI Reasoning Summary:\n"
                    f"  Reasoning chains stored : {summary.get('total_reasoning_chains', 0)}\n"
                    f"  Conversation turns      : {summary.get('conversation_length', 0)}\n"
                    f"  Active goals            : {', '.join(summary.get('active_goals', [])) or 'none'}\n"
                    f"  Learned patterns        : {summary.get('learned_patterns_count', 0)}"
                )
            else:
                print_system(
                    "Reasoning summary is only available with the AGI provider (--provider agi).")
            continue

        if not user.strip():
            continue

        messages.append({"role": "user", "content": user})

        # Stream assistant reply
        print(Fore.GREEN + "assistant> " + Style.RESET_ALL, end="")
        reply_accum = ""
        result = provider.complete(messages, stream=True)
        if isinstance(result, str):
            reply_accum = result
            print_assistant_chunk(result)
        else:
            for chunk in result:
                reply_accum += chunk
                print_assistant_chunk(chunk)
        print_assistant_done()

        messages.append({"role": "assistant", "content": reply_accum})


def one_shot(args: argparse.Namespace) -> int:
    colorama_init()
    if not args.once:
        print("--once requires a message string.")
        return 2

    system_prompt = args.system or os.getenv(
        "SYSTEM_PROMPT",
        "You are a concise, friendly assistant.",
    )

    provider, info = detect_provider(
        explicit=args.provider, model_override=args.model)

    messages: List[RoleMessage] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": args.once})

    print_system(f"Provider: {info.name} | Model: {info.model}")
    print(Fore.GREEN + "assistant> " + Style.RESET_ALL, end="")

    reply_accum = ""
    result = provider.complete(messages, stream=True)
    if isinstance(result, str):
        reply_accum = result
        print_assistant_chunk(result)
    else:
        for chunk in result:
            reply_accum += chunk
            print_assistant_chunk(chunk)
    print_assistant_done()

    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Simple terminal chat app with local/OpenAI/Azure providers")
    p.add_argument("--provider", choices=["auto", "openai", "azure", "local", "lora", "agi", "quantum",
                   "lmstudio", "ollama"], default="auto", help="Which provider to use (default: auto)")
    p.add_argument("--system", type=str, help="Custom system prompt")
    p.add_argument("--model", type=str, help="Model/deployment name override")
    p.add_argument("--once", type=str, help="Send a single message then exit")
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.once:
        return one_shot(args)
    return interactive_chat(args)


if __name__ == "__main__":
    raise SystemExit(main())
