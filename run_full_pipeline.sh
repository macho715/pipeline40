#!/usr/bin/env bash
# HVDC 파이프라인 v4.0.17 - Stage 3 벡터화 최적화
# Samsung C&T Logistics | ADNOC·DSV Partnership
set -euo pipefail

echo "========================================"
echo "HVDC 파이프라인 v4.0.17 - Stage 3 벡터화 최적화"
echo "Samsung C&T Logistics | ADNOC·DSV"
echo "========================================"

python tools/session_guard.py --mode=run --summary docs/SESSION_SUMMARY.md --pointer temp/LAST_OUTPUT.pointer
python run_pipeline.py --all --stage4-visualize || true
