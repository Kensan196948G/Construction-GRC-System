#!/bin/bash
# K8s secrets setup script for Construction-GRC-System
# Usage: ./scripts/k8s_setup.sh [namespace]
#
# Required environment variables:
#   DB_PASSWORD   - PostgreSQL database password
#   SECRET_KEY    - Django secret key
#   REDIS_URL     - Redis connection URL (default: redis://redis:6379/0)
#   DATABASE_URL  - Full PostgreSQL URL (optional, built from DB_PASSWORD if not set)

set -euo pipefail

NAMESPACE="${1:-construction-grc}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "${SCRIPT_DIR}")/k8s"

log_info()  { echo "[INFO]  $*"; }
log_warn()  { echo "[WARN]  $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

# --- Validation ---
check_prerequisites() {
    for cmd in kubectl base64; do
        if ! command -v "${cmd}" &>/dev/null; then
            log_error "Required command not found: ${cmd}"
            exit 1
        fi
    done

    if ! kubectl cluster-info &>/dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check kubeconfig."
        exit 1
    fi
}

check_env_vars() {
    local missing=0
    for var in DB_PASSWORD SECRET_KEY; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Environment variable not set: ${var}"
            missing=1
        fi
    done
    [[ "${missing}" -eq 0 ]] || exit 1
}

# --- Namespace ---
create_namespace() {
    log_info "Creating namespace: ${NAMESPACE}"
    if kubectl get namespace "${NAMESPACE}" &>/dev/null; then
        log_info "Namespace '${NAMESPACE}' already exists. Skipping."
    else
        kubectl create namespace "${NAMESPACE}"
        kubectl label namespace "${NAMESPACE}" \
            app.kubernetes.io/name=construction-grc \
            app.kubernetes.io/part-of=grc-system \
            --overwrite
        log_info "Namespace '${NAMESPACE}' created."
    fi
}

# --- Secrets ---
apply_secrets() {
    log_info "Generating Kubernetes Secret from environment variables..."

    local redis_url="${REDIS_URL:-redis://redis:6379/0}"
    local database_url="${DATABASE_URL:-postgresql://grc_admin:${DB_PASSWORD}@postgres:5432/grc_db}"

    local secret_key_b64 db_password_b64 redis_url_b64 database_url_b64
    secret_key_b64=$(printf '%s' "${SECRET_KEY}"    | base64 -w 0)
    db_password_b64=$(printf '%s' "${DB_PASSWORD}"   | base64 -w 0)
    redis_url_b64=$(printf '%s'   "${redis_url}"     | base64 -w 0)
    database_url_b64=$(printf '%s' "${database_url}" | base64 -w 0)

    kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: grc-secrets
  namespace: ${NAMESPACE}
  labels:
    app.kubernetes.io/name: construction-grc
    app.kubernetes.io/managed-by: k8s_setup.sh
type: Opaque
data:
  SECRET_KEY: ${secret_key_b64}
  DB_PASSWORD: ${db_password_b64}
  DATABASE_URL: ${database_url_b64}
  REDIS_URL: ${redis_url_b64}
EOF
    log_info "Secret 'grc-secrets' applied to namespace '${NAMESPACE}'."
}

# --- ConfigMap ---
apply_configmap() {
    log_info "Applying ConfigMap..."
    if [[ -f "${K8S_DIR}/configmap.yaml" ]]; then
        # Patch namespace if manifest uses a different one
        sed "s/namespace: .*/namespace: ${NAMESPACE}/" "${K8S_DIR}/configmap.yaml" \
            | kubectl apply -f -
        log_info "ConfigMap applied."
    else
        log_warn "ConfigMap file not found: ${K8S_DIR}/configmap.yaml — skipping."
    fi
}

# --- Deployment status ---
check_deployment_status() {
    log_info "Checking deployment status in namespace '${NAMESPACE}'..."
    if kubectl get deployments -n "${NAMESPACE}" &>/dev/null; then
        kubectl get deployments -n "${NAMESPACE}" \
            -o custom-columns='NAME:.metadata.name,READY:.status.readyReplicas,DESIRED:.spec.replicas,AVAILABLE:.status.availableReplicas' \
            2>/dev/null || true
    else
        log_info "No deployments found yet in namespace '${NAMESPACE}'."
    fi

    log_info "Pods:"
    kubectl get pods -n "${NAMESPACE}" 2>/dev/null || log_info "No pods found."
}

# --- Main ---
main() {
    log_info "=== Construction-GRC K8s Setup ==="
    log_info "Target namespace: ${NAMESPACE}"
    log_info "K8s manifests directory: ${K8S_DIR}"

    check_prerequisites
    check_env_vars
    create_namespace
    apply_secrets
    apply_configmap
    check_deployment_status

    log_info "=== Setup complete ==="
    log_info "Next step: run './scripts/local_k8s_deploy.sh ${NAMESPACE}' to deploy all workloads."
}

main "$@"
