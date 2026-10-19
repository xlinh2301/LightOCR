#!/usr/bin/env bash
set -euo pipefail

CAMPAIGN=/workspace/media/gmo/linhnx/workspace/workdir_Research/results/lightocr_loopocr_v1_screen_20261019
ENV="$CAMPAIGN/envs/paddleocr3_cu118"
LOG_DIR="$CAMPAIGN/pretrained_runtime_setup"
PID_FILE="$LOG_DIR/pip_install.pid"
mkdir -p "$LOG_DIR"
python -m venv --system-site-packages "$ENV"
if "$ENV/bin/python" -c 'import paddle; raise SystemExit(0 if paddle.__version__.startswith("3.") else 1)' 2>/dev/null; then
  echo "Paddle 3 already available: $ENV/bin/python"
  exit 0
fi
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Paddle 3 installation is already active: pid $(cat "$PID_FILE")"
  exit 0
fi
nohup "$ENV/bin/python" -m pip install --disable-pip-version-check --no-cache-dir --timeout 30 --retries 1 \
  --extra-index-url https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
  paddlepaddle-gpu==3.3.0 > "$LOG_DIR/pip_install.log" 2>&1 < /dev/null &
echo $! > "$PID_FILE"
echo "Started isolated Paddle 3.3.0 GPU install: pid=$(cat "$PID_FILE"); log=$LOG_DIR/pip_install.log"
