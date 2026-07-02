#!/bin/bash
# LM Studio Helper Script
# Quick access to LM Studio for code analysis, documentation, and more

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_BIN="${REPO_ROOT}/.venv/bin"
PYTHON="${VENV_BIN}/python"
CHAT_CLI="${REPO_ROOT}/ai-projects/chat-cli/src/chat_cli.py"

# Auto-source .env for persistent defaults (won't override already-exported vars)
if [ -f "${REPO_ROOT}/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${REPO_ROOT}/.env"
    set +a
fi

# Export LM Studio endpoint (container-friendly default via host bridge)
export LMSTUDIO_BASE_URL="${LMSTUDIO_BASE_URL:-http://host.docker.internal:1234/v1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check LM Studio availability
check_lmstudio() {
    print_header "Checking LM Studio Connection"
    
    timeout 2 curl -s "${LMSTUDIO_BASE_URL}/models" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "LM Studio is running at ${LMSTUDIO_BASE_URL}"
        return 0
    else
        print_error "Cannot connect to LM Studio at ${LMSTUDIO_BASE_URL}"
        print_info "Make sure LM Studio is running on your host machine"
        return 1
    fi
}

# Query LM Studio
query() {
    local prompt="$1"
    local max_turns="${2:-1}"
    
    if ! check_lmstudio; then
        return 1
    fi
    
    print_header "Query: $prompt"
    $PYTHON "$CHAT_CLI" \
        --provider lmstudio \
        --no-stream \
        --once "$prompt" \
        2>&1
}

# Code analysis
analyze_code() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi
    
    local code_content=$(cat "$file")
    local prompt="Analyze this code for bugs, performance issues, and improvements. Be concise. Code:\n\n$code_content"
    
    query "$prompt"
}

# Generate documentation
generate_docs() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi
    
    local code_content=$(cat "$file")
    local prompt="Generate comprehensive documentation (docstrings, comments, and a summary) for this code:\n\n$code_content"
    
    query "$prompt"
}

# Generate unit tests
generate_tests() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi
    
    local code_content=$(cat "$file")
    local prompt="Write comprehensive pytest unit tests for this code. Include edge cases and error handling:\n\n$code_content"
    
    query "$prompt"
}

# Code review
review_code() {
    local file="$1"

    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi

    print_header "Code Review: $file"
    local code_content
    code_content=$(cat "$file")
    local prompt="Review this code as a senior engineer. Cover: correctness, security, readability, performance. End with a one-sentence verdict.\n\n$code_content"
    query "$prompt"
}

# Summarise a file
summarise_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi

    print_header "Summary: $file"
    local code_content
    code_content=$(cat "$file")
    local prompt="Summarise this file in 3-5 sentences: what it does, main entry points, notable dependencies.\n\n$code_content"
    query "$prompt"
}

# Refactor code
refactor_code() {
    local file="$1"

    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        return 1
    fi

    local code_content
    code_content=$(cat "$file")
    local prompt="Refactor this code to be more readable, performant and idiomatic. Explain changes:\n\n$code_content"

    query "$prompt"
}

# Debug error
debug_error() {
    local error_msg="$1"
    local prompt="Why does this error occur? How do I fix it?\n\nError: $error_msg"
    
    query "$prompt"
}

# Explain concept
explain() {
    local concept="$1"
    local prompt="Explain '$concept' in simple terms. Include a practical example for the Aria project."
    
    query "$prompt"
}

# Interactive multi-turn conversation
chat() {
    if ! check_lmstudio; then
        return 1
    fi
    
    print_header "Starting Interactive Chat"
    print_info "Type 'exit' or 'quit' to end the conversation"
    
    $PYTHON "$CHAT_CLI" \
        --provider lmstudio \
        2>&1
}

# Show usage
usage() {
    cat << EOF
${BLUE}LM Studio Helper Script${NC}

Usage: $(basename "$0") [command] [args]

Commands:
    check              Check LM Studio connection
    query TEXT         Send a single query
    analyze FILE       Analyze code for bugs and improvements
    docs FILE          Generate documentation
    tests FILE         Generate unit tests
    review FILE        Senior-engineer code review
    summary FILE       Concise file summary
    refactor FILE      Suggest refactoring improvements
    debug ERROR        Debug an error message
    explain CONCEPT    Explain a concept
    chat               Start interactive multi-turn conversation
    help               Show this help message

Examples:
    $(basename "$0") check
    $(basename "$0") query "How does Aria's auto-execute system work?"
    $(basename "$0") analyze ai-projects/chat-cli/src/chat_cli.py
    $(basename "$0") docs apps/aria/server.py
    $(basename "$0") tests shared/chat_memory.py
    $(basename "$0") debug "ModuleNotFoundError: No module named 'xyz'"
    $(basename "$0") explain "semantic memory"
    $(basename "$0") chat

Environment:
    LMSTUDIO_BASE_URL  Set custom LM Studio endpoint (default: http://host.docker.internal:1234/v1)
    LMSTUDIO_MODEL     Optional model id to force (e.g. openai/gpt-oss-20b)

EOF
}

# Main entry point
main() {
    local cmd="${1:-help}"
    
    case "$cmd" in
        check)
            check_lmstudio
            ;;
        query)
            shift
            query "$@"
            ;;
        analyze)
            analyze_code "$2"
            ;;
        docs)
            generate_docs "$2"
            ;;
        tests)
            generate_tests "$2"
            ;;
        review)
            review_code "$2"
            ;;
        summary)
            summarise_file "$2"
            ;;
        refactor)
            refactor_code "$2"
            ;;
        debug)
            debug_error "$2"
            ;;
        explain)
            explain "$2"
            ;;
        chat)
            chat
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"
