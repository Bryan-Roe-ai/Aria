"""Tests for deterministic local summarization fallback helpers."""

import unittest

from shared.local_summary import is_summary_request, normalize_text, summarize_text


class LocalSummaryTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_text("  hello\n\nworld\t "), "hello world")
        self.assertEqual(normalize_text(""), "")

    def test_is_summary_request_detects_hints_case_insensitive(self) -> None:
        self.assertTrue(is_summary_request("TL;DR this thread"))
        self.assertTrue(is_summary_request("Could you summarize this?"))
        self.assertFalse(is_summary_request("Explain this in depth"))

    def test_summarize_text_strips_inline_prefix(self) -> None:
        text = "Please summarize this: Alpha introduces the topic. Beta explains the impact."
        summary = summarize_text(text)
        self.assertNotIn("Please summarize this", summary)
        self.assertIn("Alpha introduces the topic.", summary)

    def test_summarize_text_drops_leading_instruction_sentence(self) -> None:
        text = (
            "Can you summarize this quickly. "
            "First content sentence has project context. "
            "Second content sentence adds extra details."
        )
        summary = summarize_text(text)
        self.assertNotIn("Can you summarize this quickly", summary)
        self.assertIn("First content sentence", summary)

    def test_single_sentence_is_truncated_to_max_chars(self) -> None:
        text = "A" * 40
        self.assertEqual(summarize_text(text, max_chars=15), "A" * 15)

    def test_blank_input_returns_empty_summary(self) -> None:
        self.assertEqual(summarize_text("   "), "")

    def test_symbol_only_content_uses_cleaned_fallback(self) -> None:
        self.assertEqual(summarize_text("-"), "")

    def test_stopword_only_sentences_use_fallback_ordering(self) -> None:
        text = "The and or. It is as. We are in."
        summary = summarize_text(text)
        self.assertEqual(summary, "The and or. It is as.")

    def test_sentence_without_tokens_gets_low_default_score(self) -> None:
        text = "Engineering update includes roadmap priorities. The and or."
        summary = summarize_text(text)
        self.assertIn("Engineering update includes roadmap priorities.", summary)
        self.assertIn("The and or.", summary)

    def test_multi_sentence_output_respects_character_budget(self) -> None:
        text = (
            "Alpha project update includes milestone 1 and milestone 2. "
            "Beta includes implementation details and test coverage updates. "
            "Gamma contains extra context for later planning."
        )
        summary = summarize_text(text, max_chars=90)
        self.assertLessEqual(len(summary), 90)

    def test_first_selected_sentence_over_budget_uses_ellipsis(self) -> None:
        text = "Key details include launch readiness " + ("X" * 120) + ". Short follow up sentence."
        summary = summarize_text(text, max_chars=30)
        self.assertTrue(summary.endswith("..."))
        self.assertLessEqual(len(summary), 30)


if __name__ == "__main__":
    unittest.main()
