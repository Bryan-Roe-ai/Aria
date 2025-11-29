#!/usr/bin/env python3
"""Manual integration test for Cosmos world persistence and retrieval."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'aria_web'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import server
from shared import cosmos_client

def test_cosmos_functions():
    """Test that all cosmos functions are accessible."""
    print("✓ Testing Cosmos client functions...")
    
    # Health check
    health = cosmos_client.health()
    print(f"  Cosmos enabled: {health['enabled']}")
    print(f"  Settings present: {health['settings_present']}")
    
    # Check worlds container function exists
    assert hasattr(cosmos_client, 'worlds_container'), "worlds_container function missing"
    assert hasattr(cosmos_client, 'record_world'), "record_world function missing"
    assert hasattr(cosmos_client, 'get_world'), "get_world function missing"
    assert hasattr(cosmos_client, 'list_worlds'), "list_worlds function missing"
    print("✓ All Cosmos functions accessible")

def test_world_generation_and_persistence():
    """Test world generation with filesystem persistence."""
    print("\n✓ Testing world generation...")
    
    theme = 'test_theme'
    seed = 98765
    world = server.generate_world_fallback(theme, 5, seed=seed, spacing=10, algorithm='poisson')
    
    assert world is not None
    assert world['environment']['theme'] == theme
    assert world['environment']['seed'] == seed
    assert len(world['objects']) == 5
    print(f"  Generated {len(world['objects'])} objects for theme '{theme}'")
    
    # Test filesystem persistence
    path = server.persist_world(world, theme, seed=seed)
    assert path, "Filesystem persistence failed"
    print(f"  Persisted to: {path}")
    
    # Test Cosmos persistence (will gracefully fail if disabled)
    cosmos_ok = server.persist_world_cosmos(world, theme)
    print(f"  Cosmos persistence: {'✓ success' if cosmos_ok else '✗ disabled or failed (expected)'}")

def test_retrieval_functions():
    """Test world retrieval from filesystem and Cosmos."""
    print("\n✓ Testing retrieval functions...")
    
    theme = 'retrieval_test'
    seed = 11111
    
    # Generate and persist
    world = server.generate_world_fallback(theme, 3, seed=seed)
    server.persist_world(world, theme, seed=seed)
    
    # Fetch from filesystem
    fs_world = server.fetch_world_filesystem(theme, seed)
    assert fs_world is not None, "Filesystem retrieval failed"
    assert fs_world['environment']['seed'] == seed
    print(f"  ✓ Filesystem retrieval successful")
    
    # Fetch from Cosmos (will return None if disabled)
    cosmos_world = server.fetch_world_cosmos(theme, seed)
    if cosmos_world:
        print(f"  ✓ Cosmos retrieval successful")
    else:
        print(f"  ✗ Cosmos retrieval returned None (expected if disabled)")

def main():
    print("=" * 70)
    print("Aria World Cosmos Integration Test")
    print("=" * 70)
    
    try:
        test_cosmos_functions()
        test_world_generation_and_persistence()
        test_retrieval_functions()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
