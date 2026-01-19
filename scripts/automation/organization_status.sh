#!/bin/bash
# Quick File Organization Status

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FILE ORGANIZATION STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if organization is running
if ps aux | grep -q "[a]uto_organize.py"; then
    echo "✅ Organization: RUNNING"
else
    echo "⏸️  Organization: Not running"
fi

# Check latest report
LATEST_REPORT=$(ls -t data_out/reports/organization_report_*.json 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo ""
    echo "📄 Latest Organization Report:"
    echo "   File: $(basename $LATEST_REPORT)"
    
    if command -v jq &> /dev/null; then
        echo "   Files moved: $(jq -r '.files_moved // 0' "$LATEST_REPORT")"
        echo "   Files archived: $(jq -r '.files_archived // 0' "$LATEST_REPORT")"
        echo "   Files deleted: $(jq -r '.files_deleted // 0' "$LATEST_REPORT")"
        echo "   Space freed: $(jq -r '.space_freed_mb // 0' "$LATEST_REPORT") MB"
    fi
fi

# Check directory structure
echo ""
echo "📁 Directory Statistics:"
echo "   Datasets:"
echo "      Quantum: $(find datasets/quantum -name '*.csv' 2>/dev/null | wc -l) files"
echo "      Chat: $(find datasets/chat -name '*.jsonl' 2>/dev/null | wc -l) files"
echo ""
echo "   Logs:"
echo "      Training: $(find data_out/logs/training -name '*.log' 2>/dev/null | wc -l) files"
echo "      Collection: $(find data_out/logs/collection -name '*.log' 2>/dev/null | wc -l) files"
echo ""
echo "   Reports: $(find data_out/reports -name '*.json' 2>/dev/null | wc -l) files"

# Check temp files
TEMP_COUNT=$(find . -name '*.tmp' -o -name '*.temp' -o -name '*~' 2>/dev/null | wc -l)
if [ "$TEMP_COUNT" -gt 0 ]; then
    echo ""
    echo "⚠️  Found $TEMP_COUNT temp files (run organization to clean)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Commands:"
echo "   Organize now: python scripts/automation/auto_organize.py"
echo "   Start scheduler: nohup python scripts/automation/schedule_organization.py &"
echo "   View guide: cat docs/AUTO_ORGANIZATION_GUIDE.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
