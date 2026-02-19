#!/bin/bash
# Deployment script for waste classification model
# Handles versioning, health checks, and rollback preparation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_DIR="$PROJECT_ROOT/docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE="waste-classifier:latest"
CONTAINER_NAME="waste-classifier-api"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if API is healthy
check_health() {
    log_info "Checking API health..."
    
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null; then
            log_info "API is healthy ✓"
            return 0
        fi
        log_warn "Health check attempt $i/30..."
        sleep 2
    done
    
    log_error "API health check failed"
    return 1
}

# Get current version
get_current_version() {
    docker exec "$CONTAINER_NAME" python -c "from api.config import API_VERSION; print(API_VERSION)" 2>/dev/null || echo "unknown"
}

# Get previous version
get_previous_version() {
    git describe --tags --abbrev=0 2>/dev/null || echo "v0.9.9"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: $DOCKER_IMAGE"
    cd "$PROJECT_ROOT"
    docker build -f docker/Dockerfile -t "$DOCKER_IMAGE" .
    log_info "Image built successfully ✓"
}

# Start deployment
start_deployment() {
    log_info "Starting deployment..."
    
    cd "$DOCKER_COMPOSE_DIR"
    
    # Stop existing containers (graceful)
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_info "Stopping existing container..."
        docker-compose down
    fi
    
    # Start new containers
    log_info "Starting new containers..."
    docker-compose up -d
    
    # Wait for service to be ready
    sleep 5
    
    # Health check
    if check_health; then
        log_info "Deployment successful! ✓"
        log_info "API Version: $(get_current_version)"
        return 0
    else
        log_error "Deployment failed health check"
        return 1
    fi
}

# Rollback to previous version
rollback() {
    log_warn "Initiating rollback..."
    
    prev_version=$(get_previous_version)
    log_warn "Rolling back to version: $prev_version"
    
    cd "$DOCKER_COMPOSE_DIR"
    
    # Stop current
    log_info "Stopping current deployment..."
    docker-compose down
    
    # Checkout previous version
    git checkout "$prev_version" -- api/ model/ monitoring/ docker/
    
    # Rebuild and restart
    build_image
    if start_deployment; then
        log_info "Rollback successful ✓"
        return 0
    else
        log_error "Rollback failed"
        return 1
    fi
}

# Save version snapshot
save_version_snapshot() {
    local version="$1"
    local snapshot_dir="$PROJECT_ROOT/.versions/$version"
    
    mkdir -p "$snapshot_dir"
    
    log_info "Saving version snapshot for $version..."
    cp -r "$PROJECT_ROOT/api" "$snapshot_dir/"
    cp -r "$PROJECT_ROOT/model" "$snapshot_dir/"
    cp -r "$PROJECT_ROOT/monitoring" "$snapshot_dir/"
    
    log_info "Version snapshot saved ✓"
}

# Main deployment flow
main() {
    log_info "=== Waste Classification Model Deployment ==="
    log_info "Environment: $ENVIRONMENT"
    
    # Build
    build_image
    
    # Deploy
    if start_deployment; then
        # Save snapshot
        current_version=$(get_current_version)
        save_version_snapshot "$current_version"
        
        log_info "=== Deployment Complete ==="
        log_info "Service available at: http://localhost:8000"
        log_info "Health check: http://localhost:8000/health"
        log_info "Metrics: http://localhost:8000/metrics"
        log_info "Prometheus: http://localhost:9090"
        log_info "Grafana: http://localhost:3000"
        
        exit 0
    else
        log_error "Deployment failed, attempting rollback..."
        if rollback; then
            log_warn "Rolled back to previous version"
            exit 0
        else
            log_error "Rollback also failed. Manual intervention required."
            exit 1
        fi
    fi
}

# Check arguments
if [ "$1" = "rollback" ]; then
    rollback
    exit $?
elif [ "$1" = "health" ]; then
    check_health
    exit $?
else
    main
fi
