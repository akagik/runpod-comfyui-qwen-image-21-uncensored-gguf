# Qwen-Image-2.1 Uncensored GGUF on RunPod

RunPod Pod image for the exact recommended stack from
[`abenzerps/Qwen-Image-2.1-Uncensored-GGUF`](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF):

| Component | File | Precision | Size |
| --- | --- | --- | ---: |
| Diffusion transformer | `qwen-image-2.1-UC-Q4_K_M.gguf` | GGUF Q4_K_M | 4.60 GB |
| Qwen3-VL text encoder | `qwen3vl_8b_int8_convrot.safetensors` | INT8 ConvRot | 9.35 GB |
| VAE | `qwen_image_2.1_vae_bf16.safetensors` | BF16 | 0.68 GB |

The image contains no model weights. The first Pod start downloads the three
pinned files into persistent `/workspace` storage, verifies their byte sizes
and SHA-256 hashes, and starts ComfyUI with the loader cache enabled.

```text
RunPod template: d4detb1p14
Immutable image: ghcr.io/akagik/runpod-comfyui-qwen-image-21-uncensored-gguf:0.1.0@sha256:975e514e05af250bcab6caa1c3ec161c808a5f039729ca1d01bf889edc2eeba7
```

## Fixed sources

```text
Model repo: abenzerps/Qwen-Image-2.1-Uncensored-GGUF
Model revision: 1206d38bb47ef93961bfb77bc2c700d43a25860e
ComfyUI-GGUF fork: leejet/ComfyUI-GGUF
ComfyUI-GGUF commit: edd981b10e107d3b8f58e16c498f2d08f631bc47
Parent image: ghcr.io/akagik/runpod-comfyui-qwen-image-21-bf16:0.1.3@sha256:ec46236609a7e7ecea33904df0a043a1b529d77ad52eb8c7f0b1d1250cdc5e9b
```

`Q4_K_M` and the INT8 ConvRot encoder are the model author's recommended
quality and memory balance. This is a GGUF stack, not NVFP4.

## Included workflows

ComfyUI manual workflows:

- `qwen21_uncensored_gguf_t2i_1024_25step.json`
- `qwen21_uncensored_gguf_t2i_2048_40step.json`
- `qwen21_uncensored_gguf_novel_game_16x9_25step.json`
- `qwen21_uncensored_gguf_image_edit_25step.json`

RunPod Comfy Manager workflows:

- `qwen-image-2.1-uncensored-gguf-t2i` v1
- `qwen-image-2.1-uncensored-gguf-edit` v1

Both Manager workflows use model profile
`qwen-image-2.1-uncensored-gguf-q4km`. Switching between T2I and Edit inside
one running Pod reuses the same ComfyUI loader signature.

Ready-to-validate Manager requests are in [`examples/t2i.md`](examples/t2i.md)
and [`examples/edit.md`](examples/edit.md). The edit example supplies two local
reference images for character and clothing guidance.

## Persistence

The persistent tree is:

```text
/workspace/qwen-image-2.1-uncensored-gguf/
  comfy-models/
  hf-cache/
  input/
  logs/
  outputs/
  user/
```

The container refuses to start ComfyUI when `/workspace` is not a persistent
mount. The 40 GB container disk is disposable.

## License

The diffusion model is distributed under the Qwen Research License. The model
card describes research and evaluation use and requires a separate licence for
commercial use. The container source does not change or expand the model
licence.

See [REPRODUCE.md](REPRODUCE.md) for deployment and verification and
[RUNPOD_COMFY_MANAGER.md](RUNPOD_COMFY_MANAGER.md) for Manager usage. The
verified A40 run, timings, VRAM measurements and outputs are recorded in
[VALIDATION_2026-09-23.md](VALIDATION_2026-09-23.md).

For another AI agent preparing Markdown requests and submitting them through
the Manager, use the Japanese end-to-end runbook
[AI_GENERATION_GUIDE.md](AI_GENERATION_GUIDE.md).
