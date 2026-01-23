#!/bin/bash
# Aria Complete System Startup Script
# Starts all components: Aria web, Functions, Training, Quantum, Monitoring

set -e

REPO_ROOT="/workspaces/AI"
LOG_DIR="$REPO_ROOT/data_out"
mkdir -p "$LOG_DIR"

echo "═══════════════════════════════════════════════════════════════"
echo "ARIA Complete System Startup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

start_service() {
    local name=$1
    local cmd=$2
    local log=$3
    local isBackground=$4
    
    echo -e "${BLUE}▶ Starting ${GREEN}${name}${BLUE}...${NC}"
    
    if [ "$isBackground" = true ]; then
        nohup bash -c "$cmd" > "$log" 2>&1 &
        local pid=$!
        echo -e "  ${GREEN}✓${NC} Started in background (PID: $pid)"
        echo "  Log: $log"
    else
        echo "  Run in separate terminal:"
        echo "  ${YELLOW}${cmd}${NC}"
    fi
    echo ""
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
python --version
echo -e "  ${GREEN}✓${NC} Python ready"
echo ""

# 1. Aria Web Interface
start_service \
    "Aria Web Interface" \
    "cd $REPO_ROOT/aria_web && python server.py" \
    "$LOG_DIR/aria_web.log" \
    false

# 2. Azure Functions
start_service \
    "Azure Functions" \
    "cd $REPO_ROOT && func host start" \
    "$LOG_DIR/functions.log" \
    false

# 3. Autonomous Training
start_service \
    "Autonomous Training" \
    "cd $REPO_ROOT && python scripts/training/autonomous_training_orchestrator.py" \
    "$LOG_DIR/autonomous_training.log" \
    true

# 4. Quantum MCP Server
start_service \
    "Quantum MCP Server" \
    "cd $REPO_ROOT && python quantum-ai/quantum_mcp_server.py" \
    "$LOG_DIR/quantum_mcp_server.log" \
    true

# 5. Master Orchestrator
start_service \
    "Master Orchestrator" \
    "cd $REPO_ROOT && python scripts/automation/master_orchestrator.py" \
    "$LOG_DIR/master_orchestrator.log" \
    true

# 6. Monitoring Dashboard
start_service \
    "Monitoring Dashboard" \
    "cd $REPO_ROOT && python scripts/monitoring/auto_ops_dashboard.py --watch" \
    "$LOG_DIR/monitoring_dashboard.log" \
    true

# Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}ARIA STARTUP COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🚀 Component Status:"
echo ""
echo -e "  ${GREEN}Web UI${NC}               http://localhost:8080"
echo -e "  ${GREEN}Auto-Execute UI${NC}      http://localhost:8080/auto-execute.html"
echo -e "  ${GREEN}Quantum World${NC}        http://localhost:8080/quantum-world.html"
echo ""
echo -e "  ${GREEN}Azure Functions${NC}      http://localhost:7071"
echo -e "  ${GREEN}Health Check${NC}         curl http://localhost:7071/api/ai/status | jq ."
echo ""
echo -e "  ${GREEN}Training${NC}             Continuous 30-min cycles"
echo -e "  ${GREEN}Quantum Jobs${NC}         Via MCP server"
echo -e "  ${GREEN}Monitoring${NC}           Live dashboard active"
echo ""
echo "📋 Useful Commands:"
echo ""
echo "  # View training logs"
echo "  tail -f $LOG_DIR/autonomous_training.log"
echo ""
echo "  # Check orchestrator status"
echo "  python scripts/monitoring/auto_ops_dashboard.py --problems"
echo ""
echo "  # Test chat"
echo "  python talk-to-ai/src/chat_cli.py --provider local --once 'Hello Aria'"
echo ""
echo "  # Trigger immediate training cycle"
echo "  pkill -USR1 -f autonomous_training"
echo ""
echo "  # Stop all services"
echo "  pkill -f 'aria_web|func host|autonomous_training|quantum_mcp|master_orchestrator|auto_ops'"
echo ""
