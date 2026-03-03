#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="fastighet-legacy-mm:cu116"
CONTAINER_NAME="fastighet-legacy-mm"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Optional data mount on host; override if needed
DATA_DIR="${DATA_DIR:-/ceph}"

cd "$REPO_ROOT"

docker build -f docker/Dockerfile.legacy -t "$IMAGE_NAME" .

docker run --rm -it \
  --gpus all \
  --name "$CONTAINER_NAME" \
  -v "$REPO_ROOT":/workspace/fastighet_vega \
  -v "$DATA_DIR":"$DATA_DIR" \
  -w /workspace/fastighet_vega \
  "$IMAGE_NAME"
