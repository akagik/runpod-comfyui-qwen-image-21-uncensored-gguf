# syntax=docker/dockerfile:1.7
# Model-free image. The selected GGUF transformer, INT8 text encoder and BF16
# VAE are downloaded into persistent storage on the first Pod start.
FROM ghcr.io/akagik/runpod-comfyui-qwen-image-21-bf16:0.1.3@sha256:ec46236609a7e7ecea33904df0a043a1b529d77ad52eb8c7f0b1d1250cdc5e9b

ARG COMFYUI_GGUF_COMMIT=edd981b10e107d3b8f58e16c498f2d08f631bc47
ARG GGUF_PYTHON_VERSION=0.19.0
ARG IMAGE_VERSION=0.1.0

LABEL org.opencontainers.image.title="Qwen Image 2.1 Uncensored GGUF on RunPod" \
      org.opencontainers.image.source="https://github.com/akagik/runpod-comfyui-qwen-image-21-uncensored-gguf" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      io.runpod.qwen.model="abenzerps/Qwen-Image-2.1-Uncensored-GGUF" \
      io.runpod.qwen.transformer="qwen-image-2.1-UC-Q4_K_M.gguf" \
      io.runpod.qwen.text_encoder="qwen3vl_8b_int8_convrot.safetensors" \
      io.runpod.qwen.quantization="GGUF Q4_K_M + INT8 ConvRot" \
      io.runpod.comfyui_gguf.commit="${COMFYUI_GGUF_COMMIT}"

ENV MODE_TO_RUN=pod \
    RUNPOD_VOLUME_ROOT=/workspace \
    QWEN_GGUF_MODEL_AUTO_DOWNLOAD=1 \
    COMFYUI_DIR=/opt/ComfyUI-qwen21 \
    QWEN_GGUF_APP_DIR=/opt/qwen-image-21-uncensored-gguf \
    HF_HOME=/workspace/qwen-image-2.1-uncensored-gguf/hf-cache \
    HUGGINGFACE_HUB_CACHE=/workspace/qwen-image-2.1-uncensored-gguf/hf-cache/hub \
    PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN custom_node_dir="${COMFYUI_DIR}/custom_nodes/ComfyUI-GGUF" \
    && git init "$custom_node_dir" \
    && git -C "$custom_node_dir" remote add origin https://github.com/leejet/ComfyUI-GGUF.git \
    && git -C "$custom_node_dir" fetch --depth 1 origin "${COMFYUI_GGUF_COMMIT}" \
    && git -C "$custom_node_dir" checkout --detach FETCH_HEAD \
    && test "$(git -C "$custom_node_dir" rev-parse HEAD)" = "${COMFYUI_GGUF_COMMIT}" \
    && /opt/comfyui-venv/bin/python -m pip install --no-cache-dir "gguf==${GGUF_PYTHON_VERSION}" \
    && /opt/comfyui-venv/bin/python -m pip install --no-cache-dir -r "$custom_node_dir/requirements.txt" \
    && /opt/comfyui-venv/bin/python -m pip check \
    && rm -rf "$custom_node_dir/.git"

COPY config/ "${QWEN_GGUF_APP_DIR}/config/"
COPY scripts/ "${QWEN_GGUF_APP_DIR}/scripts/"
COPY workflows/ "${QWEN_GGUF_APP_DIR}/workflows/"
COPY README.md "${QWEN_GGUF_APP_DIR}/README.md"

RUN chmod +x "${QWEN_GGUF_APP_DIR}/scripts/"*.sh \
    && /opt/comfyui-venv/bin/python -m compileall -q "${QWEN_GGUF_APP_DIR}/scripts" \
    && bash -n "${QWEN_GGUF_APP_DIR}/scripts/"*.sh \
    && /opt/comfyui-venv/bin/python "${QWEN_GGUF_APP_DIR}/scripts/verify_workflows.py" \
    && cd "${COMFYUI_DIR}" \
    && timeout 300 /opt/comfyui-venv/bin/python main.py --quick-test-for-ci --cpu \
      --extra-model-paths-config "${QWEN_GGUF_APP_DIR}/config/extra_model_paths.yaml"

EXPOSE 8188 22
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8188/system_stats >/dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/opt/qwen-image-21-uncensored-gguf/scripts/start.sh"]
CMD []
