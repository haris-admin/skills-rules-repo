# HeartMuLa — Open-Source Music Generation

[HeartMuLa](https://github.com/HeartMuLa/heartlib) is an Apache-2.0 family of music foundation models that generates music conditioned on lyrics and tags, with multilingual support. Comparable to Suno for open-source.

## Components

- **HeartMuLa** — Music language model (3B/7B) for generation from lyrics + tags
- **HeartCodec** — 12.5Hz music codec for high-fidelity audio reconstruction
- **HeartTranscriptor** — Whisper-based lyrics transcription
- **HeartCLAP** — Audio-text alignment model

## Hardware Requirements

- **Minimum**: 8GB VRAM with `--lazy_load true` (loads/unloads models sequentially)
- **Recommended**: 16GB+ VRAM for comfortable single-GPU usage
- **Multi-GPU**: Use `--mula_device cuda:0 --codec_device cuda:1` to split across GPUs
- 3B model with lazy_load peaks at ~6.2GB VRAM
- **No GPU?** CPU mode works but is extremely slow (30-60 min per song)

## Installation

```bash
cd ~/
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib

uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .

# Fix dependency conflicts
uv pip install --upgrade datasets
uv pip install --upgrade transformers
```

## Critical Source Patches

### Patch 1 — RoPE cache fix
In `src/heartlib/heartmula/modeling_heartmula.py`, in the `setup_caches` method, add RoPE reinitialization after the `reset_caches` try/except block:

```python
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**Why:** `from_pretrained` creates model on meta device first; RoPE cache building is skipped on meta tensors, then never rebuilt after weights load.

### Patch 2 — HeartCodec loading fix
In `src/heartlib/pipelines/music_generation.py`, add `ignore_mismatched_sizes=True` to ALL `HeartCodec.from_pretrained()` calls (two locations: the eager load in `__init__` and the lazy load in the `codec` property).

**Why:** VQ codebook `initted` buffers have shape `[1]` in checkpoint vs `[]` in model. Safe to ignore.

## Model Download

```bash
cd heartlib
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

## Usage

```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length in ms (240s = 4 min) |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temperature |
| `--cfg_scale` | 1.5 | Classifier-free guidance scale |
| `--lazy_load` | false | Load/unload models on demand (saves VRAM) |
| `--mula_dtype` | bfloat16 | Dtype for HeartMuLa (bf16 recommended) |
| `--codec_dtype` | float32 | Dtype for HeartCodec (fp32 recommended for quality) |

### Performance
- RTF (Real-Time Factor) ≈ 1.0 — a 4-minute song takes ~4 minutes to generate
- Output: MP3, 48kHz stereo, 128kbps

## Pitfalls

1. Do NOT use bf16 for HeartCodec — degrades audio quality. Use fp32 (default).
2. Tags may be ignored — lyrics tend to dominate; experiment with tag ordering.
3. Triton not available on macOS — Linux/CUDA only for GPU acceleration.
4. RTX 5080 incompatibility reported in upstream issues.
5. Dependency pin conflicts require manual upgrades and the patches above.

## Links

- Repo: https://github.com/HeartMuLa/heartlib
- Models: https://huggingface.co/HeartMuLa
- Paper: https://arxiv.org/abs/2601.10547
