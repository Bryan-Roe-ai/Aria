import os
import sys
import types
from pathlib import Path


def _make_openai_module_raising():
    """Create a fake `openai` module with OpenAI that raises a quota error for images.generate."""
    mod = types.ModuleType('openai')

    class OpenAI:
        def __init__(self, *args, **kwargs):
            # images API is exposed on the instance
            def _raise(**kwargs):
                raise Exception('Exceeded your premium request allowance for images API')

            self.images = types.SimpleNamespace(generate=_raise)

    mod.OpenAI = OpenAI
    return mod


def test_image_generate_azure_quota_fallback(monkeypatch):
    # Ensure top-level module import works
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

    # Prepare environment to force Azure path
    monkeypatch.setenv('OPENAI_API_KEY', '')
    monkeypatch.setenv('AZURE_OPENAI_API_KEY', 'fake')
    monkeypatch.setenv('AZURE_OPENAI_ENDPOINT', 'https://example.openai.azure.com')

    # Inject fake openai module that raises quota error
    fake = _make_openai_module_raising()
    sys.modules['openai'] = fake

    import function_app as fa

    class DummyReq:
        def __init__(self, body):
            self.method = 'POST'
            self._body = body

        def get_json(self):
            return self._body

    req = DummyReq({'prompt': 'a cat', 'size': '512x512', 'style': ''})
    resp = fa.image_generate(req)
    # HttpResponse body is JSON bytes / str depending on runtime
    body = resp.get_body().decode() if hasattr(resp, 'get_body') else str(resp.get_body())
    assert 'quota' in body.lower() or 'premium' in body.lower() or 'images api' in body.lower()
