# Reproduce the Qwen-Image-2.1 Uncensored GGUF Pod

## Fixed stack

```text
Image: ghcr.io/akagik/runpod-comfyui-qwen-image-21-uncensored-gguf:0.1.0@sha256:975e514e05af250bcab6caa1c3ec161c808a5f039729ca1d01bf889edc2eeba7
Template: d4detb1p14
Network Volume: selected when creating a Pod; never embedded in the template
Container disk: 40GB
Ports: 8188/http, 22/tcp
Mount: /workspace
```

The model source, revision, filenames, sizes and SHA-256 hashes are fixed in
`scripts/bootstrap_models.py`.

The template was read back from the RunPod API after creation. It contains no
Network Volume ID and does not enable Manager auto rental. Attach the desired
persistent Volume manually when creating a Pod.

## Before creating a Pod

Run live read-only checks for GPU stock, hourly price, data center and Volume
capacity. Present the complete cost and obtain explicit approval before Pod
creation. Do not reuse the historical price in this document.

The stack was validated on a Secure A40 with a 30GB Pod Volume. At the time of
validation it cost $0.49/hour for the GPU and used 19.11 GiB peak GPU memory in
a two-reference Edit. Current stock and price must still be checked before
every new Pod.

The 30GB Pod Volume survives Stop/Start on that Pod and keeps the downloaded
models, but it is deleted when the Pod is terminated. Use a Network Volume when
the cache must survive Pod replacement. The template accepts either at
`/workspace`.

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
