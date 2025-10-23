# -*- coding: utf-8 -*-
"""
최종 보고서 생성 (단순화 버전)
- 입고 리포트 복사
- 통합_원본데이터_Fixed 시트에 색상만 적용
- 별도 시트 추가 없음
"""
import openpyxl
import shutil
import json
import argparse
from pathlib import Path
from anomaly_visualizer import AnomalyVisualizer
from anomaly_detector import AnomalyRecord, AnomalyType, AnomalySeverity
from datetime import datetime


def create_final_report_with_anomaly(
    report_file: str, anomaly_json: str, output_file: str = None
):
    """
    최종 보고서 생성

    작업:
    1. 입고 리포트 전체 복사
    2. '통합_원본데이터_Fixed' 시트에 색상만 적용
    3. 저장

    별도 시트 추가 없음!
    """
    print(f"🔧 최종 보고서 생성 시작...")

    # 1. 파일 복사
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = report_file.replace(
            ".xlsx", f"_최종_WITH_ANOMALY_{timestamp}.xlsx"
        )

    print(f"📋 입고 리포트 복사: {report_file}")
    shutil.copy2(report_file, output_file)
    print(f"✅ 복사 완료: {output_file}")

    # 2. JSON에서 이상치 로드
    print(f"📊 이상치 데이터 로드: {anomaly_json}")
    with open(anomaly_json, "r", encoding="utf-8") as f:
        anomaly_data = json.load(f)

    print(f"✅ 로드된 이상치: {len(anomaly_data)}건")

    # 3. AnomalyRecord 객체 생성
    anomalies = []
    for item in anomaly_data:
        anomaly = AnomalyRecord(
            case_id=item["Case_ID"],
            anomaly_type=AnomalyType(item["Anomaly_Type"]),
            severity=AnomalySeverity(item["Severity"]),
            description=item["Description"],
            detected_value=item["Detected_Value"],
            expected_range=(
                tuple(item["Expected_Range"]) if item["Expected_Range"] else None
            ),
            location=item["Location"],
            timestamp=datetime.fromisoformat(item["Timestamp"]),
            risk_score=item["Risk_Score"],
        )
        anomalies.append(anomaly)

    # 4. '통합_원본데이터_Fixed' 시트에 색상 적용
    print(f"🎨 색상 적용 시작: 통합_원본데이터_Fixed 시트")
    visualizer = AnomalyVisualizer(anomalies)

    viz_result = visualizer.apply_anomaly_colors(
        excel_file=output_file,
        sheet_name="통합_원본데이터_Fixed",
        case_col="Case No.",
        create_backup=False,  # 이미 복사본이므로 백업 불필요
    )

    if viz_result["success"]:
        print(f"✅ 색상 적용 완료!")
        print(f"  - 시간 역전: {viz_result['time_reversal_count']}건 (빨강)")
        print(f"  - ML 이상치: {viz_result['ml_outlier_count']}건 (주황/노랑)")
        print(f"  - 데이터 품질: {viz_result['data_quality_count']}건 (보라)")
    else:
        print(f"❌ 색상 적용 실패: {viz_result['message']}")
        return None

    print(f"\n🎉 최종 보고서 생성 완료!")
    print(f"📁 파일 위치: {Path(output_file).absolute()}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="HVDC 최종 보고서 생성 (이상치 색상 적용)"
    )
    parser.add_argument("--report", required=True, help="입고 리포트 파일 경로")
    parser.add_argument("--anomaly", required=True, help="이상치 JSON 파일 경로")
    parser.add_argument("--output", help="출력 파일 경로 (선택, 기본값: 자동 생성)")

    args = parser.parse_args()

    result = create_final_report_with_anomaly(
        report_file=args.report, anomaly_json=args.anomaly, output_file=args.output
    )

    if result:
        print(f"\n✅ 성공!")
    else:
        print(f"\n❌ 실패!")


if __name__ == "__main__":
    main()
"""
최종 보고서 생성 (단순화 버전)
- 입고 리포트 복사
- 통합_원본데이터_Fixed 시트에 색상만 적용
- 별도 시트 추가 없음
"""
import openpyxl
import shutil
import json
import argparse
from pathlib import Path
from anomaly_visualizer import AnomalyVisualizer
from anomaly_detector import AnomalyRecord, AnomalyType, AnomalySeverity
from datetime import datetime


def create_final_report_with_anomaly(
    report_file: str, anomaly_json: str, output_file: str = None
):
    """
    최종 보고서 생성

    작업:
    1. 입고 리포트 전체 복사
    2. '통합_원본데이터_Fixed' 시트에 색상만 적용
    3. 저장

    별도 시트 추가 없음!
    """
    print(f"🔧 최종 보고서 생성 시작...")

    # 1. 파일 복사
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = report_file.replace(
            ".xlsx", f"_최종_WITH_ANOMALY_{timestamp}.xlsx"
        )

    print(f"📋 입고 리포트 복사: {report_file}")
    shutil.copy2(report_file, output_file)
    print(f"✅ 복사 완료: {output_file}")

    # 2. JSON에서 이상치 로드
    print(f"📊 이상치 데이터 로드: {anomaly_json}")
    with open(anomaly_json, "r", encoding="utf-8") as f:
        anomaly_data = json.load(f)

    print(f"✅ 로드된 이상치: {len(anomaly_data)}건")

    # 3. AnomalyRecord 객체 생성
    anomalies = []
    for item in anomaly_data:
        anomaly = AnomalyRecord(
            case_id=item["Case_ID"],
            anomaly_type=AnomalyType(item["Anomaly_Type"]),
            severity=AnomalySeverity(item["Severity"]),
            description=item["Description"],
            detected_value=item["Detected_Value"],
            expected_range=(
                tuple(item["Expected_Range"]) if item["Expected_Range"] else None
            ),
            location=item["Location"],
            timestamp=datetime.fromisoformat(item["Timestamp"]),
            risk_score=item["Risk_Score"],
        )
        anomalies.append(anomaly)

    # 4. '통합_원본데이터_Fixed' 시트에 색상 적용
    print(f"🎨 색상 적용 시작: 통합_원본데이터_Fixed 시트")
    visualizer = AnomalyVisualizer(anomalies)

    viz_result = visualizer.apply_anomaly_colors(
        excel_file=output_file,
        sheet_name="통합_원본데이터_Fixed",
        case_col="Case No.",
        create_backup=False,  # 이미 복사본이므로 백업 불필요
    )

    if viz_result["success"]:
        print(f"✅ 색상 적용 완료!")
        print(f"  - 시간 역전: {viz_result['time_reversal_count']}건 (빨강)")
        print(f"  - ML 이상치: {viz_result['ml_outlier_count']}건 (주황/노랑)")
        print(f"  - 데이터 품질: {viz_result['data_quality_count']}건 (보라)")
    else:
        print(f"❌ 색상 적용 실패: {viz_result['message']}")
        return None

    print(f"\n🎉 최종 보고서 생성 완료!")
    print(f"📁 파일 위치: {Path(output_file).absolute()}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="HVDC 최종 보고서 생성 (이상치 색상 적용)"
    )
    parser.add_argument("--report", required=True, help="입고 리포트 파일 경로")
    parser.add_argument("--anomaly", required=True, help="이상치 JSON 파일 경로")
    parser.add_argument("--output", help="출력 파일 경로 (선택, 기본값: 자동 생성)")

    args = parser.parse_args()

    result = create_final_report_with_anomaly(
        report_file=args.report, anomaly_json=args.anomaly, output_file=args.output
    )

    if result:
        print(f"\n✅ 성공!")
    else:
        print(f"\n❌ 실패!")


if __name__ == "__main__":
    main()
