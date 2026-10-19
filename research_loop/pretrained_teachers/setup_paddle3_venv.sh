#!/usr/bin/env bash
set -euo pipefail

CAMPAIGN=/workspace/media/gmo/linhnx/workspace/workdir_Research/results/lightocr_loopocr_v1_screen_20261019
ENV="$CAMPAIGN/envs/paddleocr3_cu118"
python -m venv --system-site-packages "$ENV"
"$ENV/bin/python" -m pip install --disable-pip-version-check \
  --extra-index-url https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
  paddlepaddle-gpu==3.3.0
"$ENV/bin/python" -c 'import paddle, paddleocr, paddlex; print("paddle", paddle.__version__, "cuda", paddle.is_compiled_with_cuda()); print("paddleocr", paddleocr.__version__); print("paddlex", paddlex.__version__)'
