#!/bin/bash
# Quick Dataset Collection Status Check

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DATASET COLLECTION - QUICK STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count datasets
CSV_COUNT=$(find datasets -name '*.csv' 2>/dev/null | wc -l)
JSONL_COUNT=$(find datasets -name '*.jsonl' 2>/dev/null | wc -l)
TOTAL=$((CSV_COUNT + JSONL_COUNT))

echo ""
echo "📦 Current Inventory:"
echo "   CSV files:    $CSV_COUNT"
echo "   JSONL files:  $JSONL_COUNT"
echo "   Total:        $TOTAL"

# Check active processes
echo ""
echo "🔄 Active Collectors:"
COLLECTORS=$(ps aux | grep -E '(aggressive|huggingface|dataset_automation)' | grep python | grep -v grep | wc -l)
if [ "$COLLECTORS" -gt 0 ]; then
    echo "   ✅ $COLLECTORS collector(s) running"
    ps aux | grep -E '(aggressive|huggingface|dataset_automation)' | grep python | grep -v grep | awk '{print "      - "$11" "$12" "$13}'
else
    echo "   ⏸️  No collectors running (may have completed)"
fi

# Check logs
echo ""
echo "📝 Recent Activity:"
if [ -f "data_out/logs/huggingface.log" ]; then
    echo "   HuggingFace (last 3 lines):"
    tail -3 data_out/logs/huggingface.log | sed 's/^/      /'
fi

if [ -f "data_out/logs/aggressive.log" ]; then
    echo "   Aggressive (last 2 lines):"
    tail -2 data_out/logs/aggressive.log | grep -E '(✅|INFO)' | sed 's/^/      /'
fi

# Check reports
echo ""
echo "📄 Reports:"
if [ -f "data_out/data_collection/huggingface_bulk_report.json" ]; then
    SUCCESS=$(jq -r '.succeeded // 0' data_out/data_collection/huggingface_bulk_report.json 2>/dev/null)
    ATTEMPTED=$(jq -r '.attempted // 0' data_out/data_collection/huggingface_bulk_report.json 2>/dev/null)
    echo "   HuggingFace: $SUCCESS/$ATTEMPTED succeeded"
fi

if [ -f "data_out/data_collection/collection_report.json" ]; then
    DOWNLOADED=$(jq -r '.stats.downloaded // 0' data_out/data_collection/collection_report.json 2>/dev/null)
    echo "   Aggressive: $DOWNLOADED datasets"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 Growth Rate: +$((TOTAL - 1210)) datasets since start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
