---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-edit
workflowVersion: 1
outputRoot: ./outputs
values:
  referenceImages:
    - ../workflows/assets/portrait_model_denim.png
    - ../workflows/assets/clothing_light_blue_denim_shirt.png
  resolution: 1024
  seed: 42
  steps: 25
  cfg: 1
---
# Character and clothing reference edit

## プロンプト

```text
Keep the adult woman's identity, face, hairstyle, and realistic photographic style from <image1>.
Use the light blue denim shirt from <image2> while preserving the framing and natural body proportions from <image1>.
No text, logo, watermark, subtitles, or game UI.
```
