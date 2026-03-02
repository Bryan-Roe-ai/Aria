#!/bin/bash
# Project folder and path cleanup script
# Fixes all remaining path references and removes duplicate folders

echo "🧹 Cleaning up Aria project structure..."
echo ""

# 1. Remove empty symengine folder
if [ -d "symengine" ]; then
    echo "Removing empty symengine folder..."
    rm -rf symengine
    echo "✓ symengine deleted"
else
    echo "⊘ symengine not found (already deleted)"
fi

# 2. Remove duplicate services folder (functions are in root function_app.py)
if [ -d "services" ]; then
    echo "Removing duplicate services folder..."
    rm -rf services
    echo "✓ services deleted"
else
    echo "⊘ services not found (already deleted)"
fi

echo ""
echo "🔄 Fixing remaining path references in YAML files..."
echo ""

# 3. Fix all YAML references from AI/microsoft_phi-silica-3.6_v1 to lora
find . -name "*.yaml" -type f ! -path "./.git/*" | while read file; do
    if grep -q "AI/microsoft_phi-silica-3.6_v1" "$file"; then
        echo "Fixing: $file"
        sed -i 's|AI/microsoft_phi-silica-3.6_v1|lora|g' "$file"
    fi
done

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Verify changed files: git status"
echo "2. Run tests: python -m pytest tests/ -x"
echo "3. Check structure: python scripts/system_health_check.py"
echo ""
