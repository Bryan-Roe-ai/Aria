#!/usr/bin/env bash
# Test Aria Auto-Execute System
# Comprehensive test suite for LLM-powered action generation and execution

echo "===== Aria Auto-Execute Test Suite ====="
echo ""
echo "Prerequisites: Start Aria server with 'cd apps/aria && python server.py'"
echo ""

# Run the full test suite
python -m pytest tests/test_aria_auto_execute.py -v \
    --tb=short \
    --disable-warnings \
    -ra

# Show test summary
echo ""
echo "Test Summary:"
python -m pytest tests/test_aria_auto_execute.py --co -q | wc -l
echo "test cases discovered"
