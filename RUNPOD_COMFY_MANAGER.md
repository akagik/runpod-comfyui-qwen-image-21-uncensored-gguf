# RunPod Comfy Manager integration

## Profiles

```text
Model profile: qwen-image-2.1-uncensored-gguf-q4km
T2I: qwen-image-2.1-uncensored-gguf-t2i v1
Edit: qwen-image-2.1-uncensored-gguf-edit v1
```

The workflows share the same three loader files and therefore the same model
signature. Image `0.1.0` runs ComfyUI with `--cache-classic`, so the first job
after a cold Pod start loads the stack and later T2I/Edit jobs reuse it.

## T2I Markdown

````markdown
---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-t2i
workflowVersion: 1
outputRoot: ./outputs
values:
  width: 1536
  height: 864
  seed: 42
  steps: 25
  cfg: 1
---
# Scene

## プロンプト

```text
Photorealistic visual novel character portrait of an adult Japanese woman.
No text, logo, watermark, or game UI.
```
````

## Multi-image Edit Markdown

`referenceImages` accepts 1 to 10 local paths. Their order maps to `<image1>`
through `<image10>`.

````markdown
---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-edit
workflowVersion: 1
outputRoot: ./outputs
values:
  referenceImages:
    - ./character.png
    - ./pose.png
  resolution: 1024
  seed: 42
  steps: 25
  cfg: 1
---
# Character pose edit

## プロンプト

```text
Keep the adult character identity, face, hairstyle and outfit from <image1>.
Use the body pose and camera framing from <image2>.
Preserve a realistic photographic style. No text, logo, watermark, or UI.
```
````

Validate and preview before submission:

```bash
rcmctl validate /absolute/path/request.md --json
rcmctl markdown-preview --source-path /absolute/path/request.md \
  --output-root /absolute/path/outputs --preferred-pod-id POD_ID --json
rcmctl markdown-submit --source-path /absolute/path/request.md \
  --output-root /absolute/path/outputs --preferred-pod-id POD_ID --json
```

Manager auto rental is intentionally not configured for this profile. Start a
Pod from template `d4detb1p14` first, then submit to that live Pod. The template
does not contain a Network Volume ID, so select the persistent Volume during
manual Pod creation.
