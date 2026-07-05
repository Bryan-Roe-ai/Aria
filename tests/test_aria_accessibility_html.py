"""Focused accessibility structure checks for the user-facing Aria pages."""

from pathlib import Path

BASE = Path(__file__).parent.parent / "apps" / "aria"
INDEX_HTML: str = (BASE / "index.html").read_text(encoding="utf-8")
AUTO_EXECUTE_HTML: str = (BASE / "auto-execute.html").read_text(encoding="utf-8")
AGI_HTML: str = (BASE / "agi.html").read_text(encoding="utf-8")
ARIA_CONTROLLER_JS: str = (BASE / "aria_controller.js").read_text(encoding="utf-8")
TEST_HTML: str = (BASE / "test.html").read_text(encoding="utf-8")


def assert_contains(haystack: str, needle: str) -> None:
    assert needle in haystack


def test_index_has_landmarks_and_text_alternatives() -> None:
    assert 'class="skip-link"' in INDEX_HTML
    assert 'id="main-content"' in INDEX_HTML
    assert 'aria-label="Aria stage quick links"' in INDEX_HTML
    assert 'aria-current="page"' in INDEX_HTML
    assert 'id="stage-help-text"' in INDEX_HTML
    assert 'role="img"' in INDEX_HTML and 'id="aria"' in INDEX_HTML
    assert 'role="log"' in INDEX_HTML and 'id="logContainer"' in INDEX_HTML
    assert 'id="chatMessages"' in INDEX_HTML
    assert 'aria-relevant="additions text"' in INDEX_HTML


def test_index_stage_objects_are_keyboard_accessible() -> None:
    for object_id in ("apple", "book", "cup", "ball", "flower"):
        assert_contains(INDEX_HTML, f'id="{object_id}"')
        assert_contains(INDEX_HTML, 'role="button"')
        assert_contains(INDEX_HTML, 'tabindex="0"')
        assert_contains(INDEX_HTML, "Press Enter or Space to pick up or drop it.")


def test_auto_execute_has_semantic_examples_and_live_regions() -> None:
    assert 'class="skip-link"' in AUTO_EXECUTE_HTML
    assert 'id="main-content"' in AUTO_EXECUTE_HTML
    assert 'aria-label="Aria page navigation"' in AUTO_EXECUTE_HTML
    assert 'href="./auto-execute.html" aria-current="page"' in AUTO_EXECUTE_HTML
    assert 'id="page-status"' in AUTO_EXECUTE_HTML
    assert 'id="results"' in AUTO_EXECUTE_HTML
    assert 'aria-busy="false"' in AUTO_EXECUTE_HTML
    assert 'role="status"' in AUTO_EXECUTE_HTML
    assert 'id="loading"' in AUTO_EXECUTE_HTML
    assert '<button type="button" onclick="setCommand(' in AUTO_EXECUTE_HTML


def test_auto_execute_reports_busy_focus_and_theme_state() -> None:
    assert "function announceStatus(message)" in AUTO_EXECUTE_HTML
    assert "function setResultsBusy(isBusy)" in AUTO_EXECUTE_HTML
    assert "function focusResults()" in AUTO_EXECUTE_HTML
    assert 'btn.setAttribute("aria-pressed", "true")' in AUTO_EXECUTE_HTML
    assert 'btn.setAttribute("aria-pressed", "false")' in AUTO_EXECUTE_HTML


def test_agi_has_landmarks_live_regions_and_keyboard_submit() -> None:
    assert 'class="skip-link"' in AGI_HTML
    assert 'id="agi-main"' in AGI_HTML
    assert 'aria-label="Aria page navigation"' in AGI_HTML
    assert 'href="./agi.html" aria-current="page"' in AGI_HTML
    assert 'id="statusPill"' in AGI_HTML and 'role="status"' in AGI_HTML
    assert 'id="output"' in AGI_HTML and 'role="log"' in AGI_HTML
    assert "focusOutput()" in AGI_HTML
    assert "ctrlKey || event.metaKey" in AGI_HTML


def test_controller_preserves_keyboard_accessible_stage_objects() -> None:
    assert "function describeStageObject(objectId)" in ARIA_CONTROLLER_JS
    assert "Press Enter or Space to pick up or drop it." in ARIA_CONTROLLER_JS
    assert 'obj.setAttribute("role", "button")' in ARIA_CONTROLLER_JS
    assert 'obj.setAttribute("tabindex", hidden ? "-1" : "0")' in ARIA_CONTROLLER_JS
    assert 'obj.setAttribute("aria-pressed", held ? "true" : "false")' in ARIA_CONTROLLER_JS
    assert 'btn.setAttribute("aria-pressed", hidden ? "false" : "true")' in ARIA_CONTROLLER_JS


def test_controller_supports_keyboard_activation_for_stage_objects() -> None:
    assert 'obj.addEventListener("keydown", e => {' in ARIA_CONTROLLER_JS
    assert 'if (e.key === "Enter" || e.key === " ") {' in ARIA_CONTROLLER_JS
    assert "e.preventDefault()" in ARIA_CONTROLLER_JS
    assert "obj.click()" in ARIA_CONTROLLER_JS


def test_test_page_has_basic_accessibility_landmarks() -> None:
    assert 'lang="en"' in TEST_HTML
    assert 'class="skip-link"' in TEST_HTML
    assert 'aria-label="Aria page navigation"' in TEST_HTML
    assert 'id="main-content"' in TEST_HTML
    assert 'aria-current="page"' in TEST_HTML
