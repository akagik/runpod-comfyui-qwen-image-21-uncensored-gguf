#!/usr/bin/env python3
"""Install the exact recommended files from abenzerps' Qwen 2.1 GGUF repo."""

from __future__ import annotations

import argparse
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import hf_hub_download


REPO = "abenzerps/Qwen-Image-2.1-Uncensored-GGUF"
REVISION = "1206d38bb47ef93961bfb77bc2c700d43a25860e"


@dataclass(frozen=True)
class ModelFile:
    path: str
    size: int
    sha256: str


FILES = (
    ModelFile(
        "qwen-image-2.1-UC-Q4_K_M.gguf",
        4_604_558_112,
        "e79c8a009f2ecbdb6c70fd663d9aea9ee304a0d91f347e4169a756b8ad141b41",
    ),
    ModelFile(
        "text_encoders/qwen3vl_8b_int8_convrot.safetensors",
        9_350_798_360,
        "8bfd0f6e12abf2d2d697ecc888e5e90b0d6741d6708f05799f53afa560452e8f",
    ),
    ModelFile(
        "vae/qwen_image_2.1_vae_bf16.safetensors",
        675_509_688,
        "bb21f7473051e1ac368515dd3f2e15cd44d7a11748ee8823e1ddca3e4876b7c9",
    ),
)


def destination_relative(source_path: str) -> Path:
    source = Path(source_path)
    if source.suffix == ".gguf":
        return Path("diffusion_models") / source.name
    return source


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path: Path, model: ModelFile, marker_dir: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing model file: {path}")
    if path.stat().st_size != model.size:
        raise RuntimeError(
            f"Unexpected size for {path}: {path.stat().st_size} != {model.size}"
        )

    marker = marker_dir / f"{model.sha256}.verified"
    if marker.is_file() and marker.read_text().strip() == str(path.resolve()):
        return
    actual = sha256(path)
    if actual != model.sha256:
        raise RuntimeError(f"SHA-256 mismatch for {path}: {actual} != {model.sha256}")
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(f"{path.resolve()}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    root = (
        Path(os.environ.get("RUNPOD_VOLUME_ROOT", "/workspace"))
        / "qwen-image-2.1-uncensored-gguf"
    )
    cache = root / "hf-cache" / "hub"
    model_dir = root / "comfy-models"
    marker_dir = root / ".verified-models"

    for model in FILES:
        dest = model_dir / destination_relative(model.path)
        if args.verify_only:
            verify(dest, model, marker_dir)
            print(f"OK {dest} ({model.size} bytes, sha256={model.sha256})", flush=True)
            continue

        source = Path(
            hf_hub_download(
                repo_id=REPO,
                filename=model.path,
                revision=REVISION,
                cache_dir=cache,
            )
        )
        verify(source, model, marker_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            if dest.resolve() != source.resolve():
                raise RuntimeError(f"Different existing symlink: {dest}")
        elif dest.exists():
            verify(dest, model, marker_dir)
        else:
            dest.symlink_to(source)
        verify(dest, model, marker_dir)
        print(
            f"Ready {dest} -> {source} ({model.size} bytes, sha256={model.sha256})",
            flush=True,
        )


if __name__ == "__main__":
    main()
