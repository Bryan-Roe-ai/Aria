import sys, json, math, os, threading, time, urllib.request
from pathlib import Path
import pytest

# Ensure aria_web is importable
sys.path.append(str(Path(__file__).resolve().parents[1] / 'aria_web'))
import server  # noqa: E402


def _pairwise_distances(positions):
    dists = []
    for i, a in enumerate(positions):
        for j, b in enumerate(positions):
            if i < j:
                dists.append(math.hypot(a['x'] - b['x'], a['y'] - b['y']))
    return dists


def test_generate_world_fallback_bounds_and_spacing():
    world = server.generate_world_fallback('forest', 8, seed=1234, spacing=12)
    assert world['environment']['theme'] == 'forest'
    objs = list(world['objects'].values())
    assert len(objs) == 8
    # Bounds
    for o in objs:
        assert 0 <= o['position']['x'] <= 100
        assert 0 <= o['position']['y'] <= 100
    # Spacing (allow slight relax but should meet >= 8 when spacing=12 due to relax logic)
    positions = [o['position'] for o in objs]
    dists = _pairwise_distances(positions)
    assert min(dists) >= 8, f"Minimum distance too small: {min(dists)}"


def test_generate_world_fallback_deterministic_seed():
    world1 = server.generate_world_fallback('space', 5, seed=555, spacing=10)
    world2 = server.generate_world_fallback('space', 5, seed=555, spacing=10)
    assert json.dumps(world1['objects'], sort_keys=True) == json.dumps(world2['objects'], sort_keys=True)
    assert world1['environment']['seed'] == world2['environment']['seed']


def test_generate_world_fallback_poisson_algorithm():
    world = server.generate_world_fallback('garden', 12, seed=2024, spacing=10, algorithm='poisson')
    assert world['environment']['generation_method'] == 'fallback_poisson_disc'
    positions = [o['position'] for o in world['objects'].values()]
    dists = _pairwise_distances(positions)
    # Poisson-disc should maintain stronger average spacing
    assert sum(dists)/len(dists) > 20  # heuristic check


class FakeProviderSuccess:
    def complete(self, messages, stream=False):
        return {
            'content': json.dumps({
                'objects': {
                    'orb': {'id': 'orb', 'emoji': '🧿', 'position': {'x': 12, 'y': 34}, 'state': 'on_stage'}
                },
                'environment': {'extra': 'value'}
            })
        }


class FakeProviderFail:
    def complete(self, messages, stream=False):
        return {'content': 'this is not valid json !!'}


def test_generate_world_with_llm_success():
    provider = FakeProviderSuccess()
    world = server.generate_world_with_llm('lab', 3, provider, seed=999, spacing=10, algorithm='poisson')
    assert world['llm'] is True
    assert 'orb' in world['objects']
    assert world['environment']['theme'] == 'lab'


def test_generate_world_with_llm_fallback_on_bad_json():
    provider = FakeProviderFail()
    world = server.generate_world_with_llm('garden', 4, provider, seed=42, spacing=10, algorithm='poisson')
    assert world['llm'] is False
    assert world['environment']['theme'] == 'garden'
    assert len(world['objects']) == 4


def test_world_persistence(tmp_path):
    world = server.generate_world_fallback('arcade', 3, seed=77)
    path = server.persist_world(world, 'arcade', seed=77, base_dir=tmp_path)
    assert path
    fp = Path(path)
    assert fp.exists()
    data = json.loads(fp.read_text())
    assert data['environment']['theme'] == 'arcade'
    assert data['environment']['seed'] == 77


@pytest.mark.parametrize('theme', ['forest', 'space', 'ocean'])
def test_theme_catalog_cycle(theme):
    # Request more than catalog length to trigger cycling
    world = server.generate_world_fallback(theme, 10, seed=321)
    assert len(world['objects']) == 10
    # Ensure suffixed ids present when count > catalog size
    catalog_len = len(server.THEME_OBJECT_LIBRARY.get(theme))
    if 10 > catalog_len:
        # At least one object id should contain suffix underscore
        assert any('_' in o['id'] for o in world['objects'].values())


def test_endpoint_world_generation(monkeypatch, tmp_path):
    # Simulate persistence env flag
    monkeypatch.setenv('ARIA_WORLD_PERSIST', 'true')
    world = server.generate_world_fallback('medieval', 5, seed=101)
    path = server.persist_world(world, 'medieval', seed=101, base_dir=tmp_path)
    assert Path(path).exists()


def test_world_list_endpoint(tmp_path):
    # Persist a couple of worlds to temp dir and manually copy into expected location
    world_a = server.generate_world_fallback('forest', 2, seed=11)
    world_b = server.generate_world_fallback('space', 3, seed=22)
    # Use custom base dir then move files into real aria_worlds dir for listing
    dir_tmp = tmp_path / 'worlds'
    dir_tmp.mkdir()
    pa = Path(server.persist_world(world_a, 'forest', seed=11, base_dir=dir_tmp))
    pb = Path(server.persist_world(world_b, 'space', seed=22, base_dir=dir_tmp))
    target_dir = Path(server.REPO_ROOT) / 'data_out' / 'aria_worlds'
    target_dir.mkdir(parents=True, exist_ok=True)
    for p in [pa, pb]:
        target = target_dir / p.name
        target.write_text(p.read_text())

    # Start ephemeral server
    from http.server import HTTPServer
    httpd = HTTPServer(('127.0.0.1', 0), server.AriaRequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)

    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/aria/world/list') as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        assert payload['status'] == 'success'
        assert len(payload['worlds']) >= 2
    finally:
        httpd.shutdown()
        thread.join(timeout=2)

