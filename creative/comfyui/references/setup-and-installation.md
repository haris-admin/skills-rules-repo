# Setup & Onboarding — Full Installation Paths

Full detail behind the condensed "Setup & Onboarding" section in `SKILL.md`:
hardware verification, the full installation-path decision table, all five
installation paths (Cloud, Desktop, Portable, comfy-cli, Manual), and the
post-install steps (model downloads, custom nodes, verification).

## Contents

- [Step 1: Verify Hardware](#step-1-verify-hardware-only-if-user-chose-local)
- [Choosing an Installation Path](#choosing-an-installation-path)
- [Path A: Comfy Cloud](#path-a-comfy-cloud-no-local-install)
- [Path B: ComfyUI Desktop](#path-b-comfyui-desktop-windows--macos)
- [Path C: ComfyUI Portable](#path-c-comfyui-portable-windows-only)
- [Path D: comfy-cli](#path-d-comfy-cli-all-platforms--recommended-for-agents)
- [Path E: Manual Install](#path-e-manual-install-advanced--unsupported-hardware)
- [Post-Install: Download Models](#post-install-download-models)
- [Post-Install: Install Custom Nodes](#post-install-install-custom-nodes)
- [Post-Install: Verify](#post-install-verify)

Official docs: https://docs.comfy.org/installation | CLI: https://docs.comfy.org/comfy-cli/getting-started | Cloud: https://docs.comfy.org/get_started/cloud | Cloud API: https://docs.comfy.org/development/cloud/overview

## Step 1: Verify Hardware (ONLY if user chose local)

```bash
python scripts/hardware_check.py --json
# Optional: also probe `torch` for actual CUDA/MPS:
python scripts/hardware_check.py --json --check-pytorch
```

| Verdict    | Meaning                                                       | Action |
|------------|-----------------------------------------------------------------|--------|
| `ok`       | ≥8 GB VRAM (discrete) OR ≥32 GB unified (Apple Silicon)       | Local install — use `comfy_cli_flag` from report |
| `marginal` | SD1.5 works; SDXL tight; Flux/video unlikely                  | Local OK for light workflows, else **Path A (Cloud)** |
| `cloud`    | No usable GPU, <6 GB VRAM, <16 GB Apple unified, Intel Mac, Rosetta Python | **Switch to Cloud** unless user explicitly forces local |

The script also surfaces `wsl: true` (WSL2 with NVIDIA passthrough) and
`rosetta: true` (x86_64 Python on Apple Silicon — must reinstall as ARM64).

If verdict is `cloud` but the user wants local, do not proceed silently.
Show the `notes` array verbatim and ask whether they want to (a) switch to
Cloud or (b) force a local install (will OOM or be unusably slow on modern models).

## Choosing an Installation Path

Use the hardware check first. The table below is the fallback for when the
user has already told you their hardware:

| Situation | Recommended Path |
|-----------|------------------|
| `verdict: cloud` from hardware check | **Path A: Comfy Cloud** |
| No GPU / want to try without commitment | **Path A: Comfy Cloud** |
| Windows + NVIDIA + non-technical | **Path B: ComfyUI Desktop** |
| Windows + NVIDIA + technical | **Path C: Portable** or **Path D: comfy-cli** |
| Linux + any GPU | **Path D: comfy-cli** (easiest) |
| macOS + Apple Silicon | **Path B: Desktop** or **Path D: comfy-cli** |
| Headless / server / CI / agents | **Path D: comfy-cli** |

For the fully automated path (hardware check → install → launch → verify):

```bash
bash scripts/comfyui_setup.sh
# Or with overrides:
bash scripts/comfyui_setup.sh --m-series --port=8190 --workspace=/data/comfy
```

It runs `hardware_check.py` internally, refuses to install locally when the
verdict is `cloud` (unless `--force-cloud-override`), picks the right
`comfy-cli` flag, and prefers `pipx`/`uvx` over global `pip` to avoid polluting
system Python.

## Path A: Comfy Cloud (No Local Install)

For users without a capable GPU or who want zero setup. Hosted on RTX 6000 Pro.

**Docs:** https://docs.comfy.org/get_started/cloud

1. Sign up at https://comfy.org/cloud
2. Generate an API key at https://platform.comfy.org/login
3. Set the key:
   ```bash
   export COMFY_CLOUD_API_KEY="your-comfyui-key"
   ```
4. Run workflows:
   ```bash
   python scripts/run_workflow.py \
     --workflow workflows/flux_dev_txt2img.json \
     --args '{"prompt": "..."}' \
     --host https://cloud.comfy.org \
     --output-dir ./outputs
   ```

**Pricing:** https://www.comfy.org/cloud/pricing
**Concurrent jobs:** Free/Standard 1, Creator 3, Pro 5. Free tier
**cannot run workflows via API** — only browse models. Paid subscription
required for `/api/prompt`, `/api/upload/*`, `/api/view`, etc.

## Path B: ComfyUI Desktop (Windows / macOS)

One-click installer for non-technical users. Currently Beta.

**Docs:** https://docs.comfy.org/installation/desktop
- **Windows (NVIDIA):** https://download.comfy.org/windows/nsis/x64
- **macOS (Apple Silicon):** https://comfy.org

Linux is **not supported** for Desktop — use Path D.

## Path C: ComfyUI Portable (Windows Only)

**Docs:** https://docs.comfy.org/installation/comfyui_portable_windows

Download from https://github.com/comfyanonymous/ComfyUI/releases, extract,
run `run_nvidia_gpu.bat`. Update via `update/update_comfyui_stable.bat`.

## Path D: comfy-cli (All Platforms — Recommended for Agents)

The official CLI is the best path for headless/automated setups. Full flag
reference (install options, workspace resolution, model/node management):
see [comfy-cli Command Reference](official-cli.md).

**Docs:** https://docs.comfy.org/comfy-cli/getting-started

```bash
# Install (in order of preference)
pipx install comfy-cli
uvx --from comfy-cli comfy --help
pip install --user comfy-cli

# Disable analytics non-interactively
comfy --skip-prompt tracking disable

# Install ComfyUI (pick your GPU)
comfy --skip-prompt install --nvidia
comfy --skip-prompt install --amd                 # ROCm (Linux)
comfy --skip-prompt install --m-series             # Apple Silicon (MPS)
comfy --skip-prompt install --cpu                  # CPU only (slow)
comfy --skip-prompt install --nvidia --fast-deps   # uv-based dep resolution

# Launch / verify
comfy launch --background                       # background daemon on :8188
comfy launch -- --listen 0.0.0.0 --port 8190    # LAN-accessible custom port
curl -s http://127.0.0.1:8188/system_stats      # health check
```

Default location: `~/comfy/ComfyUI` (Linux), `~/Documents/comfy/ComfyUI`
(macOS/Win). Override with `comfy --workspace /custom/path install`.

## Path E: Manual Install (Advanced / Unsupported Hardware)

For Ascend NPU, Cambricon MLU, Intel Arc, or other unsupported hardware.

**Docs:** https://docs.comfy.org/installation/manual_install

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
pip install -r requirements.txt
python main.py
```

## Post-Install: Download Models

Full `comfy model` flag reference: [comfy-cli Command Reference](official-cli.md).

```bash
# SDXL (general purpose, ~6.5 GB)
comfy model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --relative-path models/checkpoints

# SD 1.5 (lighter, ~4 GB, good for 6 GB cards)
comfy model download \
  --url "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  --relative-path models/checkpoints

# Flux Dev fp8 (smaller variant, ~12 GB)
comfy model download \
  --url "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" \
  --relative-path models/checkpoints

# CivitAI (set token first):
comfy model download \
  --url "https://civitai.com/api/download/models/128713" \
  --relative-path models/checkpoints \
  --set-civitai-api-token "YOUR_TOKEN"
```

List installed: `comfy model list`.

## Post-Install: Install Custom Nodes

```bash
comfy node install comfyui-impact-pack             # popular utility pack
comfy node install comfyui-animatediff-evolved     # video generation
comfy node install comfyui-controlnet-aux          # ControlNet preprocessors
comfy node install comfyui-essentials              # common helpers
comfy node update all
comfy node install-deps --workflow=workflow.json   # install everything a workflow needs
```

## Post-Install: Verify

```bash
python scripts/health_check.py
# → comfy_cli on PATH? server reachable? checkpoints? smoke test?

python scripts/check_deps.py my_workflow.json
# → are this workflow's nodes/models/embeddings installed?

python scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```
