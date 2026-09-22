# Reproduce the Qwen-Image-2.1 Uncensored GGUF Pod

## Fixed stack

```text
Image: ghcr.io/akagik/runpod-comfyui-qwen-image-21-uncensored-gguf:0.1.0
Template: pending until the first immutable image build completes
Network Volume: selected when creating a Pod; never embedded in the template
Container disk: 40GB
Ports: 8188/http, 22/tcp
Mount: /workspace
```

The model source, revision, filenames, sizes and SHA-256 hashes are fixed in
`scripts/bootstrap_models.py`.

## Before creating a Pod

Run live read-only checks for GPU stock, hourly price, data center and Volume
capacity. Present the complete cost and obtain explicit approval before Pod
creation. Do not reuse the historical price in this document.

The initial target is a 24 GB or larger NVIDIA GPU. An RTX PRO 4500 Blackwell
32 GB in the same data center as an existing Volume is a practical first test,
but the actual choice must follow current stock and price.

## Readiness

The entrypoint performs the following work:

1. verifies CUDA, Torch and the GGUF Python package;
2. downloads exactly the selected transformer, text encoder and VAE;
3. verifies size and SHA-256 for each file;
4. installs the four manual workflows;
5. starts ComfyUI with `--cache-classic --disable-pinned-memory`.

The Pod is ready only when `/system_stats` returns HTTP 200 and the newest
`/workspace/qwen-image-2.1-uncensored-gguf/logs/bootstrap-*.txt` contains three
`Ready` lines.

## Manual ComfyUI

Open `https://POD_ID-8188.proxy.runpod.net` and select one of the workflows
listed in the README. The image-edit workflow supports the same Qwen-Image-2.1
reference path as the official workflow.

## Manager

RunPod Comfy Manager submits jobs to an already running compatible Pod. Auto
rental remains disabled for this stack. See `RUNPOD_COMFY_MANAGER.md`.
