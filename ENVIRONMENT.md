# Environment setup for this repo

The scripts in `src/` require OpenMMLab detection + OCR stacks.

## Why

- `src/test.py` imports `mmcv` and `mmdet` and uses `mmdet.apis.init_detector` / `inference_detector`.
- `src/batches_to_coco.py` imports `mmcv`.
- `src/pipeline2.sh` runs both:
  - `mmdetection/tools/dist_test.sh`
  - `mmocr/tools/dist_test.sh`

So you need both `mmdetection` and `mmocr` with a version combination that matches your model configs.

## Do you need to install from source?

Short answer: **for your current `pipeline2.sh`, yes**.

`pipeline2.sh` calls repo scripts directly via absolute paths:

- `/ceph/.../mmdetection/tools/dist_test.sh`
- `/ceph/.../mmocr/tools/dist_test.sh`

That assumes local source checkouts exist at those locations.

If you do not want source checkouts, you can still use pip/mim installs, but then you must update `pipeline2.sh` to call the package entrypoints instead of those hardcoded source paths.

## Important version note (your SATRN config)

Based on your SATRN config (e.g. `from mmocr.datasets.pipelines.ocr_transforms import OnlineCropOCR`, `Collect`, and `data=dict(...)` style), this looks like the **legacy MMOCR 0.x stack** rather than MMOCR 1.x/MMEngine style.

That means the safer target is:

- `mmocr` **0.x** (commonly `0.6.x`)
- `mmdetection` **2.x**
- `mmcv-full` **1.x**
- no `mmengine` requirement for that legacy pipeline

## Recommended install for legacy config (likely what you need)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Core dependency used by repo scripts
python -m pip install pandas

# Install PyTorch first (pick wheel index for your CUDA)
# Example below is CUDA 11.3 for many older OpenMMLab builds:
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu113

# Use OpenMIM to resolve compatible OpenMMLab wheels
python -m pip install -U openmim

# Legacy stack
mim install "mmcv-full<2.0.0"
mim install "mmdet>=2,<3"
mim install "mmocr>=0.6,<1.0"
```


## CUDA 13 on your server: will this work?

Short answer: **not directly with CUDA 13-specific wheels for this legacy stack**.

For `mmocr 0.x` + `mmdet 2.x` + `mmcv-full 1.x`, prebuilt wheels are generally tied to older PyTorch/CUDA combos (often CUDA 11.x).

Practical options:

1. **Recommended**: keep your CUDA 13 **driver**, but install a compatible PyTorch+CUDA runtime wheel (for example cu113/cu116 depending on wheel availability). Newer NVIDIA drivers are usually backward-compatible with older CUDA runtime builds.
2. Use a container/conda env pinned to an older CUDA runtime known to work with this legacy OpenMMLab stack.
3. Build from source against CUDA 13 (possible, but typically fragile for these old versions and not recommended unless you must).

If `mim install mmcv-full<2` cannot find a wheel for your exact Python/PyTorch/CUDA combo, that is a compatibility mismatch—switch to a supported PyTorch/CUDA combo instead of forcing CUDA 13 builds first.


## If `pip` says "No matching distribution found for torch"

This usually means one of these is true:

- your Python version is too new for the selected wheel channel (common with legacy OpenMMLab stacks),
- your OS/architecture has no wheel on that index URL,
- the selected CUDA channel does not provide wheels for your exact Python version.

Check first:

```bash
python -V
python -m pip debug --verbose | sed -n '/Compatible tags/,$p' | head -n 40
```

For this legacy stack (`mmcv-full<2`, `mmdet 2.x`, `mmocr 0.x`), the most reliable setup is usually:

- Python **3.8 or 3.9**
- PyTorch **1.10.x / 1.12.x**
- CUDA runtime channel that has matching wheels (often cu113/cu116)

Example (Python 3.9 env):

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Try cu116 first (often better wheel availability than cu113)
python -m pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
```

If that still fails, create a dedicated conda env (recommended fallback for older MM stacks):

```bash
conda create -n fastighet-mm python=3.9 -y
conda activate fastighet-mm
pip install -U pip openmim pandas
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
mim install "mmcv-full<2.0.0"
mim install "mmdet>=2,<3"
mim install "mmocr>=0.6,<1.0"
```

Tip: prefer `--extra-index-url` (not only `--index-url`) so PyPI remains available for dependencies.


## If you get `conda: command not found`

Yes — you can absolutely just install conda.

Quick install (Linux, Miniconda):

```bash
# start clean if a previous failed install left partial files
rm -rf "$HOME/miniconda3"
```

```bash
mkdir -p "$HOME/miniconda3"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O "$HOME/miniconda3/miniconda.sh"
bash "$HOME/miniconda3/miniconda.sh" -b -u -p "$HOME/miniconda3"
if [ -x "$HOME/miniconda3/bin/conda" ]; then
  "$HOME/miniconda3/bin/conda" init bash
else
  echo "Expected $HOME/miniconda3/bin/conda not found"
  echo "Try the Miniforge fallback below"
fi
exec "$SHELL"
```



If you get `Exec format error` (for `_conda`), you likely downloaded the wrong installer architecture (for example `Linux-x86_64` on an ARM/aarch64 machine).

Check architecture first:

```bash
uname -m
```

Then use the matching installer:

```bash
# x86_64
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O "$HOME/miniconda3/miniconda.sh"

# aarch64 / arm64
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O "$HOME/miniconda3/miniconda.sh"
```

If Miniconda still fails, use Miniforge with matching arch:

```bash
# x86_64
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O "$HOME/miniforge3.sh"

# aarch64 / arm64
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O "$HOME/miniforge3.sh"
```

If you instead see only `_conda` (and no `bin/conda`) after install, the install is incomplete/failed.
Use the Miniforge fallback (usually more robust on servers):

```bash
rm -rf "$HOME/miniforge3"
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
  URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
  URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh"
else
  echo "Unsupported arch: $ARCH"; exit 1
fi
wget "$URL" -O "$HOME/miniforge3.sh"
bash "$HOME/miniforge3.sh" -b -p "$HOME/miniforge3"
"$HOME/miniforge3/bin/conda" init bash
exec "$SHELL"
```

Then run the same environment creation commands with `conda` as shown below.

Then create and use the env:

```bash
conda create -n fastighet-mm python=3.9 -y
conda activate fastighet-mm
pip install -U pip openmim pandas
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
mim install "mmcv-full<2.0.0"
mim install "mmdet>=2,<3"
mim install "mmocr>=0.6,<1.0"
```


If this command fails with `No matching distribution found for torch==...+cu116`:

```bash
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
```

it usually means your platform/channel does not publish `+cu116`-tagged wheels (common on some ARM/aarch64 setups).

Try this fallback in the same env:

```bash
# 1) install without the +cu local-version suffix
pip install torch==1.12.1 torchvision==0.13.1

# 2) verify CUDA availability from torch
python -c "import torch; print(torch.__version__, 'cuda?', torch.cuda.is_available())"
```

If CUDA is `False`, use one of these options:

- run in an x86_64 container/host where legacy CUDA wheels exist, or
- keep this env CPU-only (often too slow for production inference), or
- build the legacy stack from source for your exact platform/CUDA (advanced).

For conda users on x86_64, you can also try installing PyTorch via conda channels first, then install MM packages:

```bash
conda install pytorch==1.12.1 torchvision==0.13.1 cudatoolkit=11.6 -c pytorch -y
```

(If that package set is unavailable on your arch, conda will tell you; then use the platform-specific options above.)

If you do not want to install conda, use one of these paths instead:

1. **Plain `venv` + pip (no conda required)**

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -U openmim pandas
python -m pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
mim install "mmcv-full<2.0.0"
mim install "mmdet>=2,<3"
mim install "mmocr>=0.6,<1.0"
```

2. **Use micromamba** (lightweight replacement):

```bash
micromamba create -n fastighet-mm python=3.9 -y
micromamba activate fastighet-mm
pip install -U pip openmim pandas
pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 \
  --extra-index-url https://download.pytorch.org/whl/cu116
mim install "mmcv-full<2.0.0"
mim install "mmdet>=2,<3"
mim install "mmocr>=0.6,<1.0"
```

If you want the fastest path right now: use option 1 (`venv`), since it requires no extra system install.


## AArch64 + no Python 3.9: practical PyTorch command

Given your reported resolver output (where `torch==1.12.1+cu116` is missing but plain `1.12.1`/`1.13.1` are listed), start with:

```bash
pip install torch==1.13.1
```

Then verify:

```bash
python -c "import torch; print(torch.__version__, 'cuda?', torch.cuda.is_available())"
```

Important for legacy OpenMMLab (`mmcv-full<2`, `mmdet 2.x`, `mmocr 0.x`): on aarch64, prebuilt `mmcv-full` wheels are often unavailable. If `mim install "mmcv-full<2.0.0"` fails, you will likely need one of:

- an x86_64 environment/container for prebuilt legacy wheels, or
- source builds of `mmcv`/`mmdet`/`mmocr` on your aarch64 machine.


If `torch==1.13.1` installs but `torch.cuda.is_available()` is `False` on aarch64, that usually means you got a CPU wheel (exactly like your output).

Confirm with:

```bash
python -c "import torch; print('torch', torch.__version__, 'built_cuda', torch.version.cuda, 'cuda_available', torch.cuda.is_available())"
```

For **legacy** OpenMMLab (`mmcv-full<2`, `mmdet 2.x`, `mmocr 0.x`) on aarch64, practical GPU options are limited:

1. **Recommended for fastest success:** run this legacy stack in an **x86_64 CUDA environment** (host or container) where legacy prebuilt wheels exist.
2. **Advanced:** build PyTorch + MMCV/MMDet/MMOCR from source for your exact aarch64 + CUDA toolchain.
3. Stay CPU-only (usually not practical for full inference workloads).

So yes: your result confirms the pip command worked, but it did not deliver a CUDA-enabled wheel for that platform/version combo.

If you need to probe what pip can install on your exact machine before committing, use:

```bash
python -m pip install --dry-run torch==1.13.1
python -m pip install --dry-run torch==1.12.1
python -m pip install --dry-run torchvision==0.14.1
```

## Quick verification

```bash
python -c "import mmcv, mmdet, mmocr; print('mmcv', mmcv.__version__, 'mmdet', mmdet.__version__, 'mmocr', mmocr.__version__)"
python -c "from mmocr.datasets.pipelines.ocr_transforms import OnlineCropOCR; print('OnlineCropOCR import OK')"
```

## If you intentionally migrate to modern OpenMMLab (optional)

If you later move configs to MMOCR 1.x / MMEngine style, use modern packages (`mmcv>=2`, `mmdet>=3`, `mmocr>=1`, `mmengine`). That is a separate migration and may require config rewrites.

## Notes

- This repo's `pipeline2.sh` expects local source checkouts at fixed absolute paths for both `mmdetection` and `mmocr` (under `/ceph/...`).
- If you run outside that HPC layout, either:
  - clone those repos (source install) and adjust paths in `src/pipeline2.sh`, or
  - keep pip/mim installs and rewrite `src/pipeline2.sh` to use installed entrypoints.

## Run the legacy stack in a container (recommended on servers)

If host setup is painful, use the included container files:

- `docker/Dockerfile.legacy`
- `docker/run_legacy_container.sh`

They build a CUDA 11.6 + Python 3.9 environment with:

- `torch==1.12.1+cu116`
- `mmcv-full<2.0.0`
- `mmdet>=2,<3`
- `mmocr>=0.6,<1.0`

### Requirements

- Docker installed
- NVIDIA Container Toolkit installed on host (`--gpus all` support)

### Build and run

```bash
cd /path/to/fastighet_vega
bash docker/run_legacy_container.sh
```

By default, the script mounts:

- repo root -> `/workspace/fastighet_vega`
- `/ceph` -> `/ceph` (set `DATA_DIR=/your/path` to override)

### Inside the container

The `fastighet-mm` conda env is auto-activated. You can run your pipeline from `src/` directly, for example:

```bash
cd src
bash pipeline2.sh 1 /ceph/.../load_path /ceph/.../output_path
```

If your server is **aarch64**, this Dockerfile (x86_64 Miniconda installer) is not suitable; use an x86_64 host/container for easiest legacy-wheel compatibility, or prepare aarch64 source builds.
