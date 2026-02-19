#!/bin/bash
# Health check and monitoring script
# Monitors API, logs metrics, and alerts on issues

set -e

API_URL="${API_URL:-http://localhost:8000}"
LOGS_DIR="./logs"
METRICS_FILE="$LOGS_DIR/metrics.json"
ALERT_FILE="$LOGS_DIR/alerts.json"

# Create logs directory
mkdir -p "$LOGS_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGS_DIR/health_check.log"
}

log_error() {
    echo -e "${RED}[ERROR $(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOGS_DIR/health_check.log"
}

log_alert() {
    echo -e "${YELLOW}[ALERT $(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOGS_DIR/alerts.log"
}

# Check API health
check_api_health() {
    if curl -s "$API_URL/health" > /dev/null; then
        log_info "✓ API is healthy"
        return 0
    else
        log_error "✗ API is unreachable"
        return 1
    fi
}

# Get current metrics
get_metrics() {
    response=$(curl -s "$API_URL/metrics")
    echo "$response" > "$METRICS_FILE"
    
    # Parse metrics
    drift_score=$(echo "$response" | jq '.model_drift_score // 0')
    failed_preds=$(echo "$response" | jq '.failed_predictions // 0')
    total_preds=$(echo "$response" | jq '.total_predictions // 0')
    
    log_info "Metrics - Total: $total_preds, Failed: $failed_preds, Drift Score: $drift_score"
    
    # Check thresholds
    check_thresholds "$drift_score" "$failed_preds" "$total_preds"
}

# Check alert thresholds
check_thresholds() {
    local drift_score=$1
    local failed_preds=$2
    local total_preds=$3
    
    # Drift alert threshold
    if (( $(echo "$drift_score > 0.3" | bc -l) )); then
        log_alert "Model drift detected! Score: $drift_score"
    fi
    
    # Failure rate alert
    if [ "$total_preds" -gt 0 ]; then
        failure_rate=$(echo "scale=2; $failed_preds / $total_preds" | bc -l)
        if (( $(echo "$failure_rate > 0.05" | bc -l) )); then
            log_alert "High failure rate detected: $failure_rate"
        fi
    fi
}

# Get model info
get_model_info() {
    curl -s "$API_URL/model-info" | jq . > "$LOGS_DIR/model_info.json"
    log_info "Model info retrieved"
}

# Run continuous monitoring
continuous_monitoring() {
    log_info "Starting continuous health monitoring..."
    
    while true; do
        log_info "=== Health Check Cycle ==="
        
        if check_api_health; then
            get_metrics
            get_model_info
        else
            log_error "Health check failed - API may be down"
        fi
        
        log_info "Next check in 60 seconds..."
        sleep 60
    done
}

# Display current status
show_status() {
    log_info "=== Current Status ==="
    
    if [ -f "$METRICS_FILE" ]; then
        cat "$METRICS_FILE" | jq .
    else
        log_info "No metrics available yet"
    fi
}

# Main
case "${1:-monitor}" in
    health)
        check_api_health
        ;;
    metrics)
        get_metrics
        ;;
    status)
        show_status
        ;;
    monitor)
        continuous_monitoring
        ;;
    *)
        echo "Usage: $0 {health|metrics|status|monitor}"
        exit 1
        ;;
esac
