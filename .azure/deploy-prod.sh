#!/bin/bash
# ============================================================================
# Aria Platform - Production Deployment Script
# ============================================================================
# This script orchestrates the complete deployment to Azure:
# 1. Validate prerequisites
# 2. Build and push container images
# 3. Deploy infrastructure (Bicep)
# 4. Configure application settings
# 5. Verify deployment
#
# Usage: ./deploy-prod.sh [--dry-run] [--resource-group <rg>] [--subscription <sub-id>]

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DRY_RUN=false
RESOURCE_GROUP="${RESOURCE_GROUP:-aria-prod}"
LOCATION="${LOCATION:-eastus}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-}"
REGISTRY_NAME="${REGISTRY_NAME:-ariaprod}"
REGISTRY_RESOURCE_GROUP="${REGISTRY_RESOURCE_GROUP:-aria-prod}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Argument Parsing
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            log_warn "Running in DRY-RUN mode (no changes will be made)"
            shift
            ;;
        --resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --subscription)
            SUBSCRIPTION_ID="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dry-run              Run without making changes"
            echo "  --resource-group RG    Resource group name (default: aria-prod)"
            echo "  --subscription SUB_ID  Azure subscription ID"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Step 1: Validate Prerequisites
# ============================================================================

log_info "Step 1: Validating prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    log_error "Azure CLI not found. Install from https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check git
if ! command -v git &> /dev/null; then
    log_error "Git not found"
    exit 1
fi

# Check for clean git status
if ! git -C "$REPO_ROOT" diff-index --quiet HEAD -- 2>/dev/null; then
    log_warn "Git working directory has uncommitted changes. Consider committing before deployment."
fi

# Login to Azure if needed
if ! az account show &> /dev/null; then
    log_info "Logging in to Azure..."
    az login
fi

# Set subscription
if [ -n "$SUBSCRIPTION_ID" ]; then
    az account set --subscription "$SUBSCRIPTION_ID"
    log_info "Switched to subscription: $SUBSCRIPTION_ID"
fi

# Verify resource group exists
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    log_info "Creating resource group: $RESOURCE_GROUP..."
    if [ "$DRY_RUN" = false ]; then
        az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    fi
fi

log_info "✓ Prerequisites validated"

# ============================================================================
# Step 2: Run Tests
# ============================================================================

log_info "Step 2: Running tests..."

cd "$REPO_ROOT"

if [ "$DRY_RUN" = false ]; then
    if ! python scripts/test_runner.py --unit --continue-on-fail; then
        log_warn "Some unit tests failed. Review before deploying."
    fi
    
    if ! python scripts/pre_commit_check.py; then
        log_error "Pre-commit checks failed. Please fix before deploying."
        exit 1
    fi
else
    log_warn "Skipping tests in DRY-RUN mode"
fi

log_info "✓ Tests completed"

# ============================================================================
# Step 3: Build Container Images
# ============================================================================

log_info "Step 3: Building and pushing container images..."

# Get ACR credentials
if ! az acr show --resource-group "$REGISTRY_RESOURCE_GROUP" --name "$REGISTRY_NAME" &> /dev/null; then
    log_error "Container registry not found: $REGISTRY_NAME"
    exit 1
fi

if [ "$DRY_RUN" = false ]; then
    log_info "Building Functions image..."
    az acr build \
        --registry "$REGISTRY_NAME" \
        --image functions:latest \
        --image functions:$(git -C "$REPO_ROOT" rev-parse --short HEAD) \
        --file function_app.Dockerfile \
        "$REPO_ROOT"
    
    log_info "Building Aria image..."
    az acr build \
        --registry "$REGISTRY_NAME" \
        --image aria:latest \
        --image aria:$(git -C "$REPO_ROOT" rev-parse --short HEAD) \
        --file apps/aria/Dockerfile \
        "$REPO_ROOT"
else
    log_warn "Skipping container builds in DRY-RUN mode"
fi

log_info "✓ Container images built and pushed"

# ============================================================================
# Step 4: Deploy Infrastructure (Bicep)
# ============================================================================

log_info "Step 4: Deploying infrastructure..."

# Get SQL admin password from user or environment
if [ -z "${SQL_ADMIN_PASSWORD:-}" ]; then
    read -s -p "Enter SQL Server admin password: " SQL_ADMIN_PASSWORD
    echo
fi

DEPLOY_PARAMS="
  location=$LOCATION
  functionAppName=aria-prod
  storageAccountName=ariaprodstorage$(date +%s)
  sqlServerName=aria-prod-sql-$(date +%s)
  sqlAdminPassword='$SQL_ADMIN_PASSWORD'
  containerRegistryName=$REGISTRY_NAME
  functionImageUri=$REGISTRY_NAME.azurecr.io/functions:latest
"

if [ "$DRY_RUN" = false ]; then
    az deployment group what-if \
        --name aria-prod-deploy \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$SCRIPT_DIR/main.bicep" \
        --parameters $DEPLOY_PARAMS
    
    read -p "Review the above changes. Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        az deployment group create \
            --name aria-prod-deploy \
            --resource-group "$RESOURCE_GROUP" \
            --template-file "$SCRIPT_DIR/main.bicep" \
            --parameters $DEPLOY_PARAMS
        log_info "✓ Infrastructure deployed"
    else
        log_warn "Deployment cancelled"
        exit 1
    fi
else
    log_warn "Skipping infrastructure deployment in DRY-RUN mode"
fi

# ============================================================================
# Step 5: Verify Deployment
# ============================================================================

log_info "Step 5: Verifying deployment..."

if [ "$DRY_RUN" = false ]; then
    # Get deployment outputs
    OUTPUTS=$(az deployment group show \
        --name aria-prod-deploy \
        --resource-group "$RESOURCE_GROUP" \
        --query properties.outputs -o json)
    
    FUNCTION_APP_URL=$(echo "$OUTPUTS" | jq -r '.functionAppUrl.value')
    log_info "Function App URL: $FUNCTION_APP_URL"
    
    # Wait for function app to be ready
    log_info "Waiting for Function App to be ready..."
    for i in {1..30}; do
        if curl -fsS "${FUNCTION_APP_URL}/api/ai/status" &> /dev/null; then
            log_info "✓ Function App is ready"
            break
        fi
        log_warn "Waiting... ($i/30)"
        sleep 10
    done
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -fsS "${FUNCTION_APP_URL}/api/ai/status" | jq '.')
    log_info "Health check response: $HEALTH_RESPONSE"
    
    if echo "$HEALTH_RESPONSE" | jq -e '.status' &> /dev/null; then
        log_info "✓ Health endpoint is responding"
    else
        log_warn "Health endpoint returned unexpected response"
    fi
else
    log_warn "Skipping verification in DRY-RUN mode"
fi

# ============================================================================
# Summary
# ============================================================================

log_info ""
log_info "=========================================="
log_info "Deployment Complete!"
log_info "=========================================="
log_info "Resource Group: $RESOURCE_GROUP"
log_info "Location: $LOCATION"
log_info ""
log_info "Next Steps:"
log_info "1. Monitor the deployment at: https://portal.azure.com"
log_info "2. Configure Application Settings in Key Vault"
log_info "3. Test API endpoints with ./test-deployment.sh"
log_info "4. Set up monitoring and alerts"
log_info "5. Enable auto-scaling for Functions"
log_info ""
