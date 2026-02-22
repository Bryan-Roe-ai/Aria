import json, threading, time, urllib.request
from pathlib import Path
import sys
import pytest

# Ensure aria_web is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'web' / 'aria' / 'aria_web'))
import server  # noqa: E402


def test_world_retrieval_filesystem(tmp_path):
    # Generate + persist world to temporary dir then copy into canonical location
    theme = 'forest'
    seed = 456
    world = server.generate_world_fallback(theme, 5, seed=seed, spacing=10)
    persisted = server.persist_world(world, theme, seed=seed, base_dir=tmp_path)
    assert persisted
    fp = Path(persisted)
    assert fp.exists()
    target_dir = Path(server.REPO_ROOT) / 'data_out' / 'aria_worlds'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / fp.name
    target_file.write_text(fp.read_text())

    # Start ephemeral server
    from http.server import HTTPServer
    httpd = HTTPServer(('127.0.0.1', 0), server.AriaRequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)

    try:
        url = f'http://127.0.0.1:{port}/api/aria/world/get?theme={theme}&seed={seed}'
        with urllib.request.urlopen(url) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        assert payload['status'] == 'success'
        assert payload['theme'] == theme
        assert int(payload['environment']['seed']) == seed
        assert payload['source'] in ('filesystem', 'cosmos')
    finally:
        httpd.shutdown()
        thread.join(timeout=2)


def test_world_retrieval_not_found(tmp_path):
    # Make sure seed does not exist
    theme = 'garden'
    missing_seed = 999999
    # Ensure aria_worlds dir exists but empty
    target_dir = Path(server.REPO_ROOT) / 'data_out' / 'aria_worlds'
    target_dir.mkdir(parents=True, exist_ok=True)

    from http.server import HTTPServer
    httpd = HTTPServer(('127.0.0.1', 0), server.AriaRequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)
    try:
        url = f'http://127.0.0.1:{port}/api/aria/world/get?theme={theme}&seed={missing_seed}'
        with pytest.raises(Exception):  # urllib will raise for 404
            urllib.request.urlopen(url)
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
