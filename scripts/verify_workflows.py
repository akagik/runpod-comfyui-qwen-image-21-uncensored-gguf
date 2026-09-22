#!/usr/bin/env python3
"""Verify bundled GUI workflows use only the selected GGUF stack."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "workflows" / "gui"
FILES = sorted(ROOT.glob("*.json"))
assert FILES, "No GUI workflows"

EXPECTED = {
    "qwen-image-2.1-UC-Q4_K_M.gguf",
    "qwen3vl_8b_int8_convrot.safetensors",
    "qwen_image_2.1_vae_bf16.safetensors",
}

for path in FILES:
    data = json.loads(path.read_text())
    text = json.dumps(data)
    assert EXPECTED.issubset(set(value for value in EXPECTED if value in text)), path
    assert "qwen_image_2.1_bf16.safetensors" not in text, path

    gguf_nodes = []

    def walk(value):
        if isinstance(value, dict):
            if value.get("type") == "UnetLoaderGGUF":
                gguf_nodes.append(value)
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    assert len(gguf_nodes) == 1, (path, len(gguf_nodes))
    assert gguf_nodes[0]["widgets_values"] == ["qwen-image-2.1-UC-Q4_K_M.gguf"]
    print("OK", path.name)
