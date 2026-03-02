#!/usr/bin/env python3
"""
Project structure cleanup script for Aria repository.

This script:
1. Removes empty and duplicate project folders (symengine, services)
2. Fixes all path references from AI/microsoft_phi-silica-3.6_v1 to lora
3. Updates all imports from quantum-ai to quantum (already done in code)
4. Reports cleanup results

Run from repo root: python cleanup_project.py
"""
import shutil
import os
import sys
from pathlib import Path

def cleanup():
    repo_root = Path.cwd()
    print("🧹 Cleaning up Aria project structure...")
    print(f"   Working in: {repo_root}\n")
    
    changes = {
        'deleted': [],
        'fixed':  [],
        'skipped': [],
    }
    
    # 1. Remove empty symengine folder
    symengine_path = repo_root / "symengine"
    if symengine_path.exists():
        try:
            shutil.rmtree(symengine_path)
            print("✓ Deleted: symengine/ (empty folder)")
            changes['deleted'].append('symengine')
        except Exception as e:
            print(f"✗ Failed to delete symengine: {e}")
            changes['skipped'].append(f'symengine ({e})')
    else:
        print("⊘ symengine/ not found (might be already deleted)")
    
    # 2. Remove duplicate services folder (canonical is root function_app.py)
    services_path = repo_root / "services"
    if services_path.exists():
        try:
            shutil.rmtree(services_path)
            print("✓ Deleted: services/ (duplicate HTTP function apps)")
            changes['deleted'].append('services')
        except Exception as e:
            print(f"✗ Failed to delete services: {e}")
            changes['skipped'].append(f'services ({e})')
    else:
        print("⊘ services/ not found (might be already deleted)")
    
    print("\n🔄 Fixing path references in YAML files...")
    print("   Replacing: AI/microsoft_phi-silica-3.6_v1 → lora\n")
    
    # 3. Fix YAML files with wrong paths
    yaml_files_fixed = 0
    for yaml_file in repo_root.rglob("*.yaml"):
        # Skip .git directory
        if '.git' in yaml_file.parts:
            continue
        
        try:
            content = yaml_file.read_text(encoding='utf-8')
            if 'AI/microsoft_phi-silica-3.6_v1' in content:
                new_content = content.replace(
                    'AI/microsoft_phi-silica-3.6_v1',
                    'lora'
                )
                yaml_file.write_text(new_content, encoding='utf-8')
                print(f"  ✓ Fixed: {yaml_file.relative_to(repo_root)}")
                changes['fixed'].append(str(yaml_file.relative_to(repo_root)))
                yaml_files_fixed += 1
        except Exception as e:
            print(f"  ✗ Error processing {yaml_file}: {e}")
            changes['skipped'].append(str(yaml_file))
    
    print("\n" + "="*70)
    print("📋 CLEANUP SUMMARY")
    print("="*70)
    print(f"✓ Folders deleted: {len(changes['deleted'])}")
    for item in changes['deleted']:
        print(f"   - {item}")
    
    print(f"\n✓ YAML files fixed: {yaml_files_fixed}")
    if changes['fixed']:
        for item in changes['fixed'][:5]:  # Show first 5
            print(f"   - {item}")
        if len(changes['fixed']) > 5:
            print(f"   ... and {len(changes['fixed']) - 5} more")
    
    if changes['skipped']:
        print(f"\n⚠ Skipped/Failed: {len(changes['skipped'])}")
        for item in changes['skipped'][:3]:
            print(f"   - {item}")
    
    print("\n" + "="*70)
    print("✅ Cleanup Complete!")
    print("="*70)
    print("\n📝 Next Steps:")
    print("   1. Review changes: git status")
    print("   2. Run tests: python -m pytest tests/ -x --tb=short")
    print("   3. Check health: python scripts/system_health_check.py")
    print("   4. Commit: git add -A && git commit -m 'fix: cleanup project structure'")

if __name__ == "__main__":
    try:
        cleanup()
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}", file=sys.stderr)
        sys.exit(1)
