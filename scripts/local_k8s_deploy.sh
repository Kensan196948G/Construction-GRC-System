#!/bin/bash
# Local K8s deploy script for Construction-GRC-System
# Supports minikube and kind
# Usage: ./scripts/local_k8s_deploy.sh [namespace]

set -euo pipefail

NAMESPACE="${1:-construction-grc}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"
K8S_DIR="${REPO_ROOT}/k8s"

BACKEND_IMAGE="construction-grc-backend:local"
FRONTEND_IMAGE="construction-grc-frontend:local"

HEALTH_TIMEOUT=120   # seconds to wait for each rollout
HEALTH_INTERVAL=5    # polling interval

log_info()  { echo "[INFO]  $*"; }
log_warn()  { echo "[WARN]  $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

# --- Prerequisites ---
detect_local_k8s() {
    if command -v minikube &>/dev/null && minikube status &>/dev/null 2>&1; then
        LOCAL_K8S="minikube"
    elif command -v kind &>/dev/null && kind get clusters 2>/dev/null | grep -q .; then
        LOCAL_K8S="kind"
    else
        log_warn "Neither minikube nor kind detected. Assuming kubeconfig is already set."
        LOCAL_K8S="generic"
    fi
    log_info "Local K8s provider: ${LOCAL_K8S}"
}

check_prerequisites() {
    for cmd in kubectl docker; do
        if ! command -v "${cmd}" &>/dev/null; then
            log_error "Required command not found: ${cmd}"
            exit 1
        fi
    done
    detect_local_k8s
}

# --- Image build & load ---
build_images() {
    log_info "Building Docker images..."

    if [[ -f "${REPO_ROOT}/backend/Dockerfile" ]]; then
        log_info "Building backend image: ${BACKEND_IMAGE}"
        docker build -t "${BACKEND_IMAGE}" "${REPO_ROOT}/backend/"
    else
        log_warn "backend/Dockerfile not found — skipping backend image build."
    fi

    if [[ -f "${REPO_ROOT}/frontend/Dockerfile" ]]; then
        log_info "Building frontend image: ${FRONTEND_IMAGE}"
        docker build -t "${FRONTEND_IMAGE}" "${REPO_ROOT}/frontend/"
    else
        log_warn "frontend/Dockerfile not found — skipping frontend image build."
    fi
}

load_images() {
    log_info "Loading images into local K8s runtime..."

    case "${LOCAL_K8S}" in
        minikube)
            for img in "${BACKEND_IMAGE}" "${FRONTEND_IMAGE}"; do
                if docker image inspect "${img}" &>/dev/null; then
                    log_info "Loading ${img} into minikube..."
                    minikube image load "${img}"
                fi
            done
            ;;
        kind)
            local cluster_name
            cluster_name=$(kind get clusters | head -1)
            for img in "${BACKEND_IMAGE}" "${FRONTEND_IMAGE}"; do
                if docker image inspect "${img}" &>/dev/null; then
                    log_info "Loading ${img} into kind cluster '${cluster_name}'..."
                    kind load docker-image "${img}" --name "${cluster_name}"
                fi
            done
            ;;
        generic)
            log_info "Generic provider: assuming images are already accessible."
            ;;
    esac
}

# --- Manifest application (ordered) ---
apply_manifests() {
    log_info "Applying K8s manifests in order..."

    local manifest_order=(
        "namespace.yaml"
        "secrets.yaml"
        "configmap.yaml"
        "postgres-statefulset.yaml"
        "redis-deployment.yaml"
        "backend-deployment.yaml"
        "backend-service.yaml"
        "celery-deployment.yaml"
        "frontend-deployment.yaml"
        "frontend-service.yaml"
        "ingress.yaml"
        "hpa.yaml"
        "pdb.yaml"
    )

    for manifest in "${manifest_order[@]}"; do
        local path="${K8S_DIR}/${manifest}"
        if [[ -f "${path}" ]]; then
            log_info "Applying ${manifest}..."
            # Override namespace in manifests so local deploy targets the correct namespace
            sed "s/namespace: grc-system/namespace: ${NAMESPACE}/g" "${path}" \
                | kubectl apply -f -
        else
            log_warn "Manifest not found, skipping: ${path}"
        fi
    done

    # Apply kustomization last if present and not already covered above
    if [[ -f "${K8S_DIR}/kustomization.yaml" ]]; then
        log_info "Detected kustomization.yaml — you can also deploy via:"
        log_info "  kubectl apply -k ${K8S_DIR}/ -n ${NAMESPACE}"
    fi
}

# --- Health check ---
wait_for_deployment() {
    local name="$1"
    local ns="$2"
    local timeout="$3"

    log_info "Waiting for deployment '${name}' in namespace '${ns}' (timeout: ${timeout}s)..."
    if kubectl rollout status deployment/"${name}" -n "${ns}" --timeout="${timeout}s" 2>/dev/null; then
        log_info "Deployment '${name}' is ready."
    else
        log_warn "Deployment '${name}' did not become ready within ${timeout}s."
    fi
}

wait_for_statefulset() {
    local name="$1"
    local ns="$2"
    local timeout="$3"

    log_info "Waiting for statefulset '${name}' in namespace '${ns}' (timeout: ${timeout}s)..."
    if kubectl rollout status statefulset/"${name}" -n "${ns}" --timeout="${timeout}s" 2>/dev/null; then
        log_info "StatefulSet '${name}' is ready."
    else
        log_warn "StatefulSet '${name}' did not become ready within ${timeout}s."
    fi
}

health_checks() {
    log_info "Running health checks..."

    # StatefulSets
    wait_for_statefulset "postgres" "${NAMESPACE}" "${HEALTH_TIMEOUT}"

    # Deployments
    local deployments=("redis" "grc-backend" "celery-worker" "grc-frontend")
    for dep in "${deployments[@]}"; do
        # Try the name as-is; manifest names may differ slightly
        if kubectl get deployment "${dep}" -n "${NAMESPACE}" &>/dev/null; then
            wait_for_deployment "${dep}" "${NAMESPACE}" "${HEALTH_TIMEOUT}"
        else
            log_warn "Deployment '${dep}' not found in namespace '${NAMESPACE}' — skipping wait."
        fi
    done

    log_info "--- Final pod status ---"
    kubectl get pods -n "${NAMESPACE}" -o wide 2>/dev/null || true

    log_info "--- Services ---"
    kubectl get services -n "${NAMESPACE}" 2>/dev/null || true

    log_info "--- Ingress ---"
    kubectl get ingress -n "${NAMESPACE}" 2>/dev/null || true
}

# --- Access info ---
print_access_info() {
    log_info "=== Access Information ==="

    case "${LOCAL_K8S}" in
        minikube)
            log_info "minikube IP: $(minikube ip 2>/dev/null || echo 'unknown')"
            log_info "To open the frontend service:"
            log_info "  minikube service grc-frontend -n ${NAMESPACE}"
            log_info "To tunnel ingress:"
            log_info "  minikube tunnel"
            ;;
        kind)
            log_info "For kind, forward the backend port with:"
            log_info "  kubectl port-forward -n ${NAMESPACE} svc/grc-backend 8000:8000"
            log_info "  kubectl port-forward -n ${NAMESPACE} svc/grc-frontend 3000:80"
            ;;
        generic)
            log_info "Use 'kubectl port-forward' or your cluster's ingress IP to access services."
            ;;
    esac
}

# --- Main ---
main() {
    log_info "=== Construction-GRC Local K8s Deploy ==="
    log_info "Namespace: ${NAMESPACE}"
    log_info "K8s dir:   ${K8S_DIR}"

    check_prerequisites
    build_images
    load_images

    # Run secrets setup if environment variables are available
    if [[ -n "${DB_PASSWORD:-}" && -n "${SECRET_KEY:-}" ]]; then
        log_info "DB_PASSWORD and SECRET_KEY detected — running k8s_setup.sh..."
        "${SCRIPT_DIR}/k8s_setup.sh" "${NAMESPACE}"
    else
        log_warn "DB_PASSWORD / SECRET_KEY not set. Skipping secrets setup."
        log_warn "Set these env vars and run './scripts/k8s_setup.sh ${NAMESPACE}' before deploying."
    fi

    apply_manifests
    health_checks
    print_access_info

    log_info "=== Deploy complete ==="
}

main "$@"
