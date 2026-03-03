#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="fastighet-legacy-mm:cu116"
CONTAINER_NAME="fastighet-legacy-mm"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Optional data mount on host; override if needed
DATA_DIR="${DATA_DIR:-/ceph}"

cd "$REPO_ROOT"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Cannot access Docker daemon (permission denied or daemon not running)." >&2
  echo "Try one of:" >&2
  echo "  1) sudo usermod -aG docker $USER && newgrp docker" >&2
  echo "  2) sudo systemctl start docker" >&2
  echo "  3) run with sudo: sudo bash docker/run_legacy_container.sh" >&2
  exit 1
fi

HOST_ARCH="$(uname -m)"
if [ "$HOST_ARCH" = "x86_64" ]; then
  TARGETARCH="amd64"
elif [ "$HOST_ARCH" = "aarch64" ] || [ "$HOST_ARCH" = "arm64" ]; then
  TARGETARCH="arm64"
else
  echo "[ERROR] Unsupported host architecture: $HOST_ARCH" >&2
  exit 1
fi


# Guard against stale/broken Dockerfile versions from earlier revisions
# Validate Dockerfile shape to catch bad conflict resolutions
if [ "$(grep -c '^RUN .*miniconda\.sh' docker/Dockerfile.legacy || true)" -gt 1 ]; then
  echo "[ERROR] docker/Dockerfile.legacy contains multiple Miniconda RUN blocks (likely bad merge resolution)." >&2
  echo "Open docker/Dockerfile.legacy and keep only the architecture-aware block." >&2
  exit 1
fi

if grep -q 'RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh' docker/Dockerfile.legacy; then
  echo "[ERROR] Detected old hardcoded x86_64 Miniconda RUN line in docker/Dockerfile.legacy." >&2
  echo "This usually means conflict resolution kept stale lines." >&2
  echo "Re-check merge or reset this file from latest branch." >&2
  exit 1
fi

if grep -q "Install Miniconda (x86_64 image)" docker/Dockerfile.legacy; then
  echo "[ERROR] Detected stale docker/Dockerfile.legacy content (old x86_64-only block)." >&2
  echo "Please update your repo and retry:" >&2
  echo "  git pull" >&2
  echo "  bash docker/run_legacy_container.sh" >&2
  exit 1
fi

echo "[INFO] Using script: docker/run_legacy_container.sh"
echo "[INFO] Building image for TARGETARCH=$TARGETARCH"
BUILD_FLAGS=()
if [ "${NO_CACHE:-0}" = "1" ]; then
  BUILD_FLAGS+=(--no-cache)
fi
docker build "${BUILD_FLAGS[@]}" --build-arg TARGETARCH="$TARGETARCH" -f docker/Dockerfile.legacy -t "$IMAGE_NAME" .

docker run --rm -it \
  --gpus all \
  --name "$CONTAINER_NAME" \
  -v "$REPO_ROOT":/workspace/fastighet_vega \
  -v "$DATA_DIR":"$DATA_DIR" \
  -w /workspace/fastighet_vega \
  "$IMAGE_NAME"
