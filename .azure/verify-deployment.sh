#!/bin/bash
# ============================================================================
# Aria Platform - Deployment Verification Script
# ============================================================================
# This script verifies that a deployed Aria instance is healthy and ready
# for production traffic.
#
# Usage: ./verify-deployment.sh <function-app-url> [--verbose]

set -euo pipefail

FUNCTION_APP_URL="${1:-}"
VERBOSE="${2:-}"

if [ -z "$FUNCTION_APP_URL" ]; then
    echo "Usage: $0 <function-app-url> [--verbose]"
    echo "Example: $0 https://aria-prod.azurewebsites.net"
    exit 1
fi

# Normalize URL (remove trailing slash)
FUNCTION_APP_URL="${FUNCTION_APP_URL%/}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
TOTAL=0

# ============================================================================
# Test Functions
# ============================================================================

test_endpoint() {
    local name="$1"
    local method="${2:-GET}"
    local endpoint="$3"
    local expected_code="${4:-200}"
    
    TOTAL=$((TOTAL + 1))
    
    echo -n "Testing $name... "
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
        "$FUNCTION_APP_URL$endpoint" \
        -H "Content-Type: application/json" \
        2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $response)"
        FAILED=$((FAILED + 1))
    fi
}

test_json_response() {
    local name="$1"
    local endpoint="$2"
    local required_field="$3"
    
    TOTAL=$((TOTAL + 1))
    
    echo -n "Testing $name... "
    
    local response=$(curl -s "$FUNCTION_APP_URL$endpoint" 2>/dev/null)
    
    if echo "$response" | jq -e "$required_field" &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
        if [ -n "${VERBOSE:-}" ]; then
            echo "Response: $response"
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Missing field: $required_field)"
        FAILED=$((FAILED + 1))
    fi
}

# ============================================================================
# Health Checks
# ============================================================================

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Aria Platform Deployment Tests${NC}"
echo -e "${BLUE}================================${NC}"
echo "Target: $FUNCTION_APP_URL"
echo ""

# Test 1: Basic connectivity
echo -e "${YELLOW}[Core Endpoints]${NC}"
test_endpoint "Root endpoint" "GET" "/" "200"

# Test 2: Health endpoint
test_json_response "Health endpoint" "/api/ai/status" ".status"

# Test 3: Routes endpoint
test_json_response "Routes endpoint" "/api/ai/routes" ".routes | length > 0"

# Test 4: Chat provider probe
echo ""
echo -e "${YELLOW}[Chat System]${NC}"
test_endpoint "Provider probe" "POST" "/api/ai/provider-probe" "200"

# Test 5: Chat endpoint
test_endpoint "Chat streaming" "POST" "/api/chat/stream" "400"

# Test 6: Quantum endpoints (if available)
echo ""
echo -e "${YELLOW}[Quantum System]${NC}"
test_endpoint "Quantum status" "GET" "/api/quantum/status" "200"

# Test 7: Vision endpoints (if available)
echo ""
echo -e "${YELLOW}[Vision System]${NC}"
test_endpoint "Vision endpoints" "GET" "/api/vision/info" "200"

# Test 8: Aria web server (optional)
echo ""
echo -e "${YELLOW}[Optional: Aria Web]${NC}"
test_endpoint "Aria HTTP API" "GET" "/api/aria/state" "200"

# Test 9: Static content
echo ""
echo -e "${YELLOW}[Static Content]${NC}"
test_endpoint "Chat UI" "GET" "/chat" "200"

# ============================================================================
# Performance Tests
# ============================================================================

echo ""
echo -e "${YELLOW}[Performance]${NC}"

echo -n "Testing response time for health endpoint... "
START_TIME=$(date +%s%N)
curl -s "$FUNCTION_APP_URL/api/ai/status" > /dev/null 2>&1
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
echo -e "${GREEN}${RESPONSE_TIME}ms${NC}"

if [ $RESPONSE_TIME -lt 2000 ]; then
    echo -e "${GREEN}✓ Response time acceptable${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ Response time high${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}================================${NC}"
echo "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "Deployment is healthy and ready for production traffic."
    exit 0
else
    echo -e "${RED}✗ Some tests failed.${NC}"
    echo "Review the failures above and take corrective action."
    exit 1
fi
