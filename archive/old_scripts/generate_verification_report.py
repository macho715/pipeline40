#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 검증 보고서 생성 스크립트
모든 검증 결과를 하나의 마크다운 보고서로 통합
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_verification_script(script_name):
    """검증 스크립트를 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


def generate_verification_report():
    """통합 검증 보고서를 생성합니다."""

    print("=== 통합 검증 보고서 생성 ===")

    # 현재 시간
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # 검증 스크립트 목록
    verification_scripts = [
        "verify_master_no_sorting.py",
        "verify_colors_applied.py",
        "verify_derived_columns.py",
    ]

    # 각 검증 실행
    results = {}
    for script in verification_scripts:
        print(f"검증 중: {script}")
        results[script] = run_verification_script(script)

    # 파일 존재 확인
    file_checks = {}
    files_to_check = [
        "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx",
        "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_colored.xlsx",
        "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_for_stage2.xlsx",
        "data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).derived_v2.9.4.xlsx",
        "data/processed/reports/HVDC_입고로직_종합리포트_20251019_221002_v3.0-corrected.xlsx",
        "data/anomaly/HVDC_anomaly_report.xlsx",
    ]

    for file_path in files_to_check:
        file_checks[file_path] = Path(file_path).exists()

    # 마크다운 보고서 생성
    report_content = f"""# 파이프라인 실행 결과 검증 보고서

**생성 시간**: {timestamp}
**검증 대상**: HVDC Invoice Audit Pipeline v2.9.4

## 📋 요약

이 보고서는 HVDC Invoice Audit Pipeline의 전체 실행 결과를 검증한 내용을 담고 있습니다.

## 📁 파일 존재 확인

| 파일 경로 | 상태 |
|-----------|------|
"""

    for file_path, exists in file_checks.items():
        status = "✅ 존재" if exists else "❌ 없음"
        report_content += f"| `{file_path}` | {status} |\n"

    # 각 검증 결과 추가
    report_content += "\n## 🔍 상세 검증 결과\n\n"

    for script, result in results.items():
        script_name = script.replace(".py", "").replace("_", " ").title()
        report_content += f"### {script_name}\n\n"

        if result["success"]:
            report_content += "✅ **검증 성공**\n\n"
        else:
            report_content += "❌ **검증 실패**\n\n"

        if result["stdout"]:
            report_content += "**출력 결과:**\n```\n" + result["stdout"] + "\n```\n\n"

        if result["stderr"]:
            report_content += "**오류 메시지:**\n```\n" + result["stderr"] + "\n```\n\n"

    # 전체 평가
    all_verifications_passed = all(result["success"] for result in results.values())
    all_files_exist = all(file_checks.values())

    report_content += "## 📊 전체 평가\n\n"

    if all_verifications_passed and all_files_exist:
        report_content += "🎉 **전체 검증 성공**\n\n"
        report_content += "- 모든 검증 스크립트가 성공적으로 실행되었습니다\n"
        report_content += "- 모든 예상 출력 파일이 생성되었습니다\n"
        report_content += "- 파이프라인이 정상적으로 완료되었습니다\n"
    else:
        report_content += "⚠️ **일부 검증 실패**\n\n"
        if not all_verifications_passed:
            report_content += "- 일부 검증 스크립트에서 문제가 발견되었습니다\n"
        if not all_files_exist:
            report_content += "- 일부 예상 출력 파일이 생성되지 않았습니다\n"

    # 권장사항
    report_content += "\n## 💡 권장사항\n\n"

    if all_verifications_passed and all_files_exist:
        report_content += "1. **Git 커밋**: 모든 변경사항을 Git에 커밋하여 버전 관리\n"
        report_content += "2. **백업**: 성공적인 실행 결과를 안전한 위치에 백업\n"
        report_content += "3. **문서화**: 실행 가이드 및 CHANGELOG 업데이트\n"
    else:
        report_content += "1. **문제 해결**: 실패한 검증 항목의 원인 분석 및 수정\n"
        report_content += "2. **재실행**: 수정 후 파이프라인 재실행\n"
        report_content += "3. **검증**: 재실행 후 다시 검증 수행\n"

    # 보고서 저장
    report_file = "VERIFICATION_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"SUCCESS: 검증 보고서가 생성되었습니다: {report_file}")

    # 간단한 요약 출력
    print(f"\n검증 요약:")
    print(
        f"  - 검증 스크립트: {sum(1 for r in results.values() if r['success'])}/{len(results)} 성공"
    )
    print(
        f"  - 출력 파일: {sum(1 for exists in file_checks.values() if exists)}/{len(file_checks)} 존재"
    )
    print(
        f"  - 전체 상태: {'성공' if all_verifications_passed and all_files_exist else '실패'}"
    )

    return all_verifications_passed and all_files_exist


if __name__ == "__main__":
    success = generate_verification_report()
    sys.exit(0 if success else 1)
