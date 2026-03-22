from __future__ import annotations
from pathlib import Path
import unittest
import tempfile
import sys
import os
import json
import chat_providers
import pytest

pytest.importorskip("colorama")


# Ensure this src folder is importable when tests run from repo root
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from chat_cli import save_conversation  # noqa: E402


class ChatProviderTests(unittest.TestCase):
    def test_detect_provider_explicit_local_with_model_override(self) -> None:
        """Explicit local provider should always resolve to LocalEchoProvider."""
        # Remove keys so auto-detection cannot drift to cloud providers
        original = {
            "AZURE_OPENAI_API_KEY": os.environ.pop("AZURE_OPENAI_API_KEY", None),
            "AZURE_OPENAI_ENDPOINT": os.environ.pop("AZURE_OPENAI_ENDPOINT", None),
            "AZURE_OPENAI_DEPLOYMENT": os.environ.pop("AZURE_OPENAI_DEPLOYMENT", None),
            "OPENAI_API_KEY": os.environ.pop("OPENAI_API_KEY", None),
        }
        try:
            provider, info = chat_providers.detect_provider(
                explicit="local", model_override="offline-test-model")
            self.assertIsInstance(provider, chat_providers.LocalEchoProvider)
            self.assertEqual(info.name, "local")
            self.assertEqual(info.model, "offline-test-model")
        finally:
            for key, value in original.items():
                if value is not None:
                    os.environ[key] = value

    def test_local_echo_includes_aria_movement_tags(self) -> None:
        """Offline mode should still emit actionable Aria movement tags."""
        provider = chat_providers.LocalEchoProvider(seed=1)
        messages = [
            {"role": "user", "content": "Please move right and then wave"}]

        reply = provider.complete(messages, stream=False)

        self.assertIsInstance(reply, str)
        self.assertIn("[aria:", reply)
        self.assertTrue(any(tag in reply for tag in [
                        "[aria:walk:right]", "[aria:wave]"]))

    def test_local_echo_question_mentions_live_provider(self) -> None:
        """Generic question in local mode should direct user to real providers."""
        provider = chat_providers.LocalEchoProvider(seed=2)
        messages = [
            {"role": "user", "content": "What is quantum entanglement?"}]

        reply = provider.complete(messages, stream=False)

        self.assertIsInstance(reply, str)
        lowered = reply.lower()
        self.assertTrue("provider" in lowered or "offline" in lowered)
        self.assertTrue(any(name in lowered for name in [
                        "openai", "azure", "agi", "lm studio", "ollama"]))

    def test_local_echo_autonomous_prompt_returns_actionable_plan(self) -> None:
        """Autonomous prompts should stay useful offline instead of repeating fallback warnings."""
        provider = chat_providers.LocalEchoProvider(seed=3)
        messages = [
            {
                "role": "user",
                "content": "Start working autonomously on the most useful next step and keep driving the conversation without waiting for user input.",
            }
        ]

        reply = provider.complete(messages, stream=False)

        self.assertIsInstance(reply, str)
        lowered = reply.lower()
        self.assertIn("autonomous", lowered)
        self.assertTrue(any(token in lowered for token in ["plan", "next step", "review", "objective"]))
        self.assertNotIn("canned responses", lowered)

    def test_save_conversation_writes_jsonl(self) -> None:
        """save_conversation should persist one JSON object per line in order."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = save_conversation(messages, Path(tmp_dir))

            self.assertTrue(out_path.exists())
            lines = out_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 3)

            parsed = [json.loads(line) for line in lines]
            self.assertEqual(parsed, messages)

    def test_save_conversation_retries_when_timestamp_collides(self) -> None:
        """Saving twice with the same timestamp should not overwrite the first file."""
        messages = [{"role": "user", "content": "Hello"}]

        with tempfile.TemporaryDirectory() as tmp_dir:
            with unittest.mock.patch("chat_cli.now_ts", return_value="20250101_010203_000000"):
                first_path = save_conversation(messages, Path(tmp_dir))
                second_path = save_conversation(messages, Path(tmp_dir))

            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())
            self.assertNotEqual(first_path, second_path)
            self.assertEqual(first_path.name, "chat_20250101_010203_000000.jsonl")
            self.assertEqual(second_path.name, "chat_20250101_010203_000000_1.jsonl")
            self.assertEqual(
                first_path.read_text(encoding="utf-8"),
                second_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
