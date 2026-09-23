# A40 Manager validation — 2026-09-23

## Pod

```text
Pod: x1x47m24k6it8d
Template: d4detb1p14
GPU: NVIDIA A40
VRAM: 46,068 MiB reported by nvidia-smi (44.42 GiB Torch total)
Cloud / DC: Secure / EU-SE-1
GPU price: $0.49/hour
Container disk: 40GB
Pod Volume: 30GB mounted at /workspace
Driver: 580.173.02
CUDA: 13.0
PyTorch: 2.13.0+cu130
Python: 3.12.3
ComfyUI: 0.37.0
```

All three pinned model files passed their byte-size and SHA-256 checks. The
`UnetLoaderGGUF` object schema exposed exactly
`qwen-image-2.1-UC-Q4_K_M.gguf`; `CLIPLoader` exposed exactly
`qwen3vl_8b_int8_convrot.safetensors`.

## Manager T2I

```text
Workflow: qwen-image-2.1-uncensored-gguf-t2i v1
Job: 01a0cbb9-d498-74a3-8dd0-c1e248037a10
Resolution: 1536x864
Steps / CFG / seed: 25 / 1 / 42
Started: 2026-09-23T00:46:04.165927Z
Finished: 2026-09-23T00:46:56.223090Z
Manager execution time: 52.06 sec
Peak GPU memory sampled by nvidia-smi: 13,091 MiB (12.78 GiB)
```

Output: [`results/x1x47m24k6it8d/t2i/t2i.png`](results/x1x47m24k6it8d/t2i/t2i.png)

SHA-256:
`f3abf2956d281aa04dac8813d48cac8cc055532a556283b9c007f25ea5e68d1d`

## Manager multi-image Edit

The generated T2I image was `<image1>` and the bundled denim-shirt reference
was `<image2>`. The prompt kept identity and cafe style, transferred the shirt,
and changed the pose to standing beside the window.

```text
Workflow: qwen-image-2.1-uncensored-gguf-edit v1
Job: 01a0cbbc-3687-7272-8d4a-e5581be756c5
References: 2
Input resolution parameter: 1024
Output: 1376x768
Steps / CFG / seed: 25 / 1 / 42
Started: 2026-09-23T00:48:41.913817Z
Finished: 2026-09-23T00:49:35.926603Z
Manager execution time: 54.01 sec
```

Output: [`results/x1x47m24k6it8d/edit/edit-t2i-and-clothing.png`](results/x1x47m24k6it8d/edit/edit-t2i-and-clothing.png)

SHA-256:
`ca6f1e64042d15f8f88401a66c61acb44f4005f89ae58af4e1404aeb3d7ba389`

A second warm Edit at seed 43 completed in 54.66 seconds. Its sampled peak was
19,565 MiB (19.11 GiB), and the post-job resident allocation was 13,829 MiB
(13.50 GiB). ComfyUI stayed in the same process, demonstrating that T2I and
Edit reused the loaded stack instead of restarting or unloading it.

Warm output:
[`results/x1x47m24k6it8d/edit-warm/edit-t2i-and-clothing.png`](results/x1x47m24k6it8d/edit-warm/edit-t2i-and-clothing.png)

## Result

The exact recommended Q4_K_M stack works on a 48GB-class A40 through RunPod
Comfy Manager for both T2I and two-image instruction editing. Manager uploaded
the references, submitted the workflow, tracked it, downloaded the PNG, and
placed it at the Markdown-selected local path.

