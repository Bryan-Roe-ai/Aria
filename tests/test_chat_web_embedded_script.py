"""Validate chat-web embedded controller script parses cleanly."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = REPO_ROOT / "apps" / "chat" / "index.html"
MARKER = "// Anime Character Controller with AI Chat"


def _extract_embedded_script(html: str) -> str:
    start = html.index(MARKER)
    end = html.index("</script>", start)
    return html[start:end]


def test_embedded_controller_script_has_balanced_structure():
    script = _extract_embedded_script(INDEX_HTML.read_text(encoding="utf-8"))
    assert script.count("{") == script.count("}")
    assert "Send + AGI routing delegated to chat.js" in script
    assert "aria-chat-assistant" in script
    assert "moveAriaToPercent" in script
    assert "function ariaSpin" in script
    assert "sendBubbleMessage" in script
    assert "__ariaChatTransport" in script


def test_embedded_controller_parses_canonical_aria_tags():
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert "[aria:position:" in html or "moveAriaToNamedPosition" in html
    assert "function parseAriaCommands" in html
    script = _extract_embedded_script(html)
    assert "moveAriaToNamedPosition" in script
    assert "ariaSpin" in script


def test_embedded_controller_stage_bridge_and_tag_handlers():
    html = INDEX_HTML.read_text(encoding="utf-8")
    script = _extract_embedded_script(html)
    assert "function parseCanonicalAriaTags" in script
    assert "function bridgeAssistantTextToStage" in script
    assert "function setAriaExpression" in script
    assert "function ariaPickup" in script
    assert "function ariaLook" in script
    assert "ARIA_STAGE_API_BASE" in script
    assert "ARIA_STAGE_BRIDGE_ENABLED" in script
    assert "window.location.origin" in script
    assert "characterHeldProp" in html
    assert "expression-smile" in html
    assert "[aria:expression:" in script or "setAriaExpression" in script
    assert "[aria:pickup:" in script or "ariaPickup" in script
    assert "[aria:look" in script or "ariaLook" in script


def test_chat_js_declares_embedded_transport():
    chat_js = (REPO_ROOT / "apps" / "chat" / "chat.js").read_text(encoding="utf-8")
    assert "function initEmbeddedTransport()" in chat_js
    assert "window.__ariaChatTransport" in chat_js
    assert "emitEmbeddedChatEvent" in chat_js
