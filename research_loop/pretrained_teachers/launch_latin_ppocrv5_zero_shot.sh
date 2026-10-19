#!/usr/bin/env bash
set -euo pipefail

CAMPAIGN=/workspace/media/gmo/linhnx/workspace/workdir_Research/results/lightocr_loopocr_v1_screen_20261019
REPO=/workspace/media/gmo/linhnx/workspace/workdir_Research/source/LightOCR-1M-architecture-loop
PYTHON=/workspace/media/gmo/linhnx/workspace/workdir_Research/results/lightocr_loopocr_v1_screen_20261019/envs/paddleocr3_cu118/bin/python
RUN_ID=teacher_latin_ppocrv5_mobile_rec_zero_shot
OUT="$CAMPAIGN/$RUN_ID"
LOG_DIR="$CAMPAIGN/${RUN_ID}_logs"
PID_FILE="$LOG_DIR/eval.pid"
mkdir -p "$LOG_DIR"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Refusing duplicate teacher inference; pid $(cat "$PID_FILE") is active" >&2
  exit 2
fi
if [[ -e "$OUT" ]]; then
  echo "Refusing to overwrite existing teacher output: $OUT" >&2
  exit 2
fi

if [[ ! -x "$PYTHON" ]]; then
  echo "Missing isolated Paddle 3 interpreter: $PYTHON" >&2
  exit 2
fi

nohup env PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True "$PYTHON" -u \
  "$REPO/research_loop/pretrained_teachers/evaluate_paddlex_recognition.py" \
  --model-name latin_PP-OCRv5_mobile_rec \
  --split "$CAMPAIGN/local_split2201_source/EditCTC/experiments/PAE_CTC/pilot_007/cache/model_dev.jsonl" \
  --image-root /workspace/media/gmo/linhnx/workspace/workdir_Research/data/Indomain_curated/crops/train \
  --image-root /workspace/media/gmo/linhnx/workspace/workdir_Research/data/Indomain_curated/crops/valid \
  --output-dir "$OUT" --batch-size 8 --device gpu:0 \
  --source-url https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/latin_PP-OCRv5_mobile_rec_pretrained.pdparams \
  > "$LOG_DIR/eval.log" 2>&1 < /dev/null &
echo $! > "$PID_FILE"
echo "Started $RUN_ID pid=$(cat "$PID_FILE"); log=$LOG_DIR/eval.log"
