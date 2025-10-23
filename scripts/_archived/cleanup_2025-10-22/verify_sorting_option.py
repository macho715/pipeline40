#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVDC Pipeline 정렬 옵션 검증 스크립트
Verify Sorting Option Script for HVDC Pipeline

두 가지 실행 옵션(정렬/비정렬)의 결과를 검증하고 비교 보고서를 생성합니다.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime

# 프로젝트 루트 경로 추가
PIPELINE_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PIPELINE_ROOT))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SortingVerifier:
    """정렬 옵션 검증 클래스"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or PIPELINE_ROOT
        self.data_dir = self.project_root / "data"
        self.synced_dir = self.data_dir / "processed" / "synced"

    def find_output_files(self) -> Tuple[Path, Path]:
        """정렬/비정렬 버전 출력 파일 찾기"""
        synced_files = list(self.synced_dir.glob("*.synced*.xlsx"))

        sorted_file = None
        no_sorted_file = None

        for file in synced_files:
            if "_no_sorting" in file.name:
                no_sorted_file = file
            elif "synced_v2.9.4" in file.name and "_no_sorting" not in file.name:
                sorted_file = file

        if not sorted_file:
            raise FileNotFoundError("정렬 버전 출력 파일을 찾을 수 없습니다.")
        if not no_sorted_file:
            raise FileNotFoundError("비정렬 버전 출력 파일을 찾을 수 없습니다.")

        logger.info(f"정렬 버전 파일: {sorted_file}")
        logger.info(f"비정렬 버전 파일: {no_sorted_file}")

        return sorted_file, no_sorted_file

    def load_data(self, file_path: Path) -> pd.DataFrame:
        """Excel 파일 로드"""
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"파일 로드 완료: {file_path.name} ({len(df)}행)")
            return df
        except Exception as e:
            logger.error(f"파일 로드 실패: {file_path} - {e}")
            raise

    def find_case_column(self, df: pd.DataFrame) -> str:
        """Case NO 컬럼 찾기"""
        patterns = [r"^case(\s*no\.?)?$", r"^case_no$", r"^sku$", r"^case$"]
        for col in df.columns:
            col_lower = str(col).strip().lower()
            for pattern in patterns:
                if pd.Series([col_lower]).str.match(pattern).any():
                    return col
        raise ValueError("Case NO 컬럼을 찾을 수 없습니다.")

    def find_master_no_column(self, df: pd.DataFrame) -> str:
        """Master NO 컬럼 찾기"""
        patterns = [r"^no\.?$", r"^number$", r"^index$", r"^id$"]
        for col in df.columns:
            col_lower = str(col).strip().lower()
            for pattern in patterns:
                if pd.Series([col_lower]).str.match(pattern).any():
                    return col
        return None

    def verify_sorting_order(
        self, sorted_df: pd.DataFrame, no_sorted_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """정렬 순서 검증"""
        logger.info("정렬 순서 검증 시작...")

        # Case NO 컬럼 찾기
        sorted_case_col = self.find_case_column(sorted_df)
        no_sorted_case_col = self.find_case_column(no_sorted_df)

        # Master NO 컬럼 찾기 (정렬 버전에서만)
        master_no_col = self.find_master_no_column(sorted_df)

        results = {
            "sorted_case_col": sorted_case_col,
            "no_sorted_case_col": no_sorted_case_col,
            "master_no_col": master_no_col,
            "sorting_verification": {},
            "order_comparison": {},
        }

        # 1. 정렬 버전에서 Master NO 순서 확인
        if master_no_col:
            sorted_master_nos = sorted_df[master_no_col].dropna().tolist()
            sorted_case_nos = sorted_df[sorted_case_col].dropna().tolist()

            # Master NO가 숫자형인지 확인
            try:
                master_nos_numeric = pd.to_numeric(sorted_master_nos, errors="coerce")
                is_sorted_by_master = master_nos_numeric.is_monotonic_increasing

                results["sorting_verification"] = {
                    "master_no_column_found": True,
                    "master_no_column": master_no_col,
                    "is_sorted_by_master_no": bool(is_sorted_by_master),
                    "total_rows": len(sorted_df),
                    "master_no_range": [
                        min(master_nos_numeric),
                        max(master_nos_numeric),
                    ],
                }

                logger.info(
                    f"정렬 버전 Master NO 순서: {'정렬됨' if is_sorted_by_master else '정렬 안됨'}"
                )

            except Exception as e:
                logger.warning(f"Master NO 정렬 검증 실패: {e}")
                results["sorting_verification"] = {
                    "master_no_column_found": True,
                    "master_no_column": master_no_col,
                    "is_sorted_by_master_no": False,
                    "error": str(e),
                }
        else:
            logger.warning("Master NO 컬럼을 찾을 수 없습니다.")
            results["sorting_verification"] = {
                "master_no_column_found": False,
                "is_sorted_by_master_no": False,
            }

        # 2. 두 버전의 첫 10개 Case NO 순서 비교
        sorted_first_10 = sorted_df[sorted_case_col].head(10).tolist()
        no_sorted_first_10 = no_sorted_df[no_sorted_case_col].head(10).tolist()

        results["order_comparison"] = {
            "sorted_first_10": sorted_first_10,
            "no_sorted_first_10": no_sorted_first_10,
            "first_10_match": sorted_first_10 == no_sorted_first_10,
            "order_different": True,  # 정렬 버전과 비정렬 버전은 순서가 달라야 함
        }

        logger.info(
            f"첫 10개 Case NO 순서 일치: {sorted_first_10 == no_sorted_first_10}"
        )

        return results

    def verify_data_consistency(
        self, sorted_df: pd.DataFrame, no_sorted_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """데이터 일관성 검증"""
        logger.info("데이터 일관성 검증 시작...")

        # Case NO 컬럼 찾기
        sorted_case_col = self.find_case_column(sorted_df)
        no_sorted_case_col = self.find_case_column(no_sorted_df)

        # Case NO를 기준으로 정렬하여 비교 가능하게 만들기
        sorted_df_sorted = sorted_df.sort_values(sorted_case_col).reset_index(drop=True)
        no_sorted_df_sorted = no_sorted_df.sort_values(no_sorted_case_col).reset_index(
            drop=True
        )

        results = {
            "row_count_comparison": {},
            "case_no_comparison": {},
            "data_content_comparison": {},
        }

        # 1. 행 수 비교
        sorted_rows = len(sorted_df)
        no_sorted_rows = len(no_sorted_df)

        results["row_count_comparison"] = {
            "sorted_rows": sorted_rows,
            "no_sorted_rows": no_sorted_rows,
            "row_count_match": sorted_rows == no_sorted_rows,
        }

        logger.info(
            f"행 수 비교: 정렬={sorted_rows}, 비정렬={no_sorted_rows}, 일치={sorted_rows == no_sorted_rows}"
        )

        # 2. Case NO 목록 비교
        sorted_case_nos = set(sorted_df[sorted_case_col].dropna().astype(str))
        no_sorted_case_nos = set(no_sorted_df[no_sorted_case_col].dropna().astype(str))

        common_cases = sorted_case_nos & no_sorted_case_nos
        sorted_only = sorted_case_nos - no_sorted_case_nos
        no_sorted_only = no_sorted_case_nos - sorted_case_nos

        results["case_no_comparison"] = {
            "sorted_case_count": len(sorted_case_nos),
            "no_sorted_case_count": len(no_sorted_case_nos),
            "common_cases": len(common_cases),
            "sorted_only": len(sorted_only),
            "no_sorted_only": len(no_sorted_only),
            "case_sets_match": len(sorted_only) == 0 and len(no_sorted_only) == 0,
        }

        logger.info(
            f"Case NO 비교: 공통={len(common_cases)}, 정렬전용={len(sorted_only)}, 비정렬전용={len(no_sorted_only)}"
        )

        # 3. 데이터 내용 비교 (공통 Case들만)
        if len(common_cases) > 0:
            # 공통 컬럼 찾기
            common_cols = set(sorted_df.columns) & set(no_sorted_df.columns)
            non_case_cols = [
                col
                for col in common_cols
                if col not in [sorted_case_col, no_sorted_case_col]
            ]

            content_differences = 0
            total_comparisons = 0

            for case_no in list(common_cases)[:100]:  # 처음 100개만 비교 (성능상)
                sorted_row = sorted_df_sorted[
                    sorted_df_sorted[sorted_case_col].astype(str) == case_no
                ]
                no_sorted_row = no_sorted_df_sorted[
                    no_sorted_df_sorted[no_sorted_case_col].astype(str) == case_no
                ]

                if len(sorted_row) > 0 and len(no_sorted_row) > 0:
                    for col in non_case_cols:
                        if col in sorted_row.columns and col in no_sorted_row.columns:
                            sorted_val = sorted_row.iloc[0][col]
                            no_sorted_val = no_sorted_row.iloc[0][col]

                            # NaN 처리
                            if pd.isna(sorted_val) and pd.isna(no_sorted_val):
                                continue
                            elif pd.isna(sorted_val) or pd.isna(no_sorted_val):
                                content_differences += 1
                            elif str(sorted_val) != str(no_sorted_val):
                                content_differences += 1

                            total_comparisons += 1

            results["data_content_comparison"] = {
                "common_columns": len(non_case_cols),
                "total_comparisons": total_comparisons,
                "content_differences": content_differences,
                "data_content_match": content_differences == 0,
            }

            logger.info(
                f"데이터 내용 비교: 차이={content_differences}/{total_comparisons}"
            )

        return results

    def generate_report(self, verification_results: Dict[str, Any]) -> str:
        """검증 보고서 생성"""
        report = []
        report.append("# HVDC Pipeline 정렬 옵션 검증 보고서")
        report.append(f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 1. 정렬 순서 검증 결과
        report.append("## 1. 정렬 순서 검증")
        sorting_verification = verification_results.get("sorting_verification", {})
        order_comparison = verification_results.get("order_comparison", {})

        if sorting_verification.get("master_no_column_found"):
            report.append(
                f"- **Master NO 컬럼**: {sorting_verification['master_no_column']}"
            )
            report.append(
                f"- **Master NO 정렬 상태**: {'✅ 정렬됨' if sorting_verification.get('is_sorted_by_master_no') else '❌ 정렬 안됨'}"
            )
            report.append(
                f"- **총 행 수**: {sorting_verification.get('total_rows', 'N/A')}"
            )
        else:
            report.append("- **Master NO 컬럼**: ❌ 찾을 수 없음")

        report.append(
            f"- **첫 10개 Case NO 순서**: {'✅ 일치' if order_comparison.get('first_10_match') else '❌ 불일치'}"
        )
        report.append("")

        # 2. 데이터 일관성 검증 결과
        report.append("## 2. 데이터 일관성 검증")
        row_count = verification_results.get("row_count_comparison", {})
        case_comparison = verification_results.get("case_no_comparison", {})
        content_comparison = verification_results.get("data_content_comparison", {})

        report.append(
            f"- **행 수 일치**: {'✅ 일치' if row_count.get('row_count_match') else '❌ 불일치'}"
        )
        report.append(f"  - 정렬 버전: {row_count.get('sorted_rows', 'N/A')}행")
        report.append(f"  - 비정렬 버전: {row_count.get('no_sorted_rows', 'N/A')}행")

        report.append(
            f"- **Case NO 일치**: {'✅ 일치' if case_comparison.get('case_sets_match') else '❌ 불일치'}"
        )
        report.append(f"  - 공통 Case: {case_comparison.get('common_cases', 'N/A')}개")
        report.append(f"  - 정렬 전용: {case_comparison.get('sorted_only', 'N/A')}개")
        report.append(
            f"  - 비정렬 전용: {case_comparison.get('no_sorted_only', 'N/A')}개"
        )

        if content_comparison:
            report.append(
                f"- **데이터 내용 일치**: {'✅ 일치' if content_comparison.get('data_content_match') else '❌ 불일치'}"
            )
            report.append(
                f"  - 비교 컬럼: {content_comparison.get('common_columns', 'N/A')}개"
            )
            report.append(
                f"  - 내용 차이: {content_comparison.get('content_differences', 'N/A')}건"
            )
        report.append("")

        # 3. 결론
        report.append("## 3. 검증 결론")

        all_good = (
            sorting_verification.get("is_sorted_by_master_no", False)
            and not order_comparison.get("first_10_match", True)  # 순서가 달라야 함
            and row_count.get("row_count_match", False)
            and case_comparison.get("case_sets_match", False)
            and content_comparison.get("data_content_match", True)
        )

        if all_good:
            report.append("✅ **검증 통과**: 정렬 옵션이 올바르게 구현되었습니다.")
            report.append("- 정렬 버전은 Master NO 순서로 정렬됨")
            report.append("- 비정렬 버전은 원본 순서 유지")
            report.append("- 두 버전의 데이터 내용은 동일함")
        else:
            report.append("❌ **검증 실패**: 일부 문제가 발견되었습니다.")
            if not sorting_verification.get("is_sorted_by_master_no", False):
                report.append("- 정렬 버전이 Master NO 순서로 정렬되지 않음")
            if order_comparison.get("first_10_match", True):
                report.append("- 정렬 버전과 비정렬 버전의 순서가 동일함 (예상과 다름)")
            if not row_count.get("row_count_match", False):
                report.append("- 두 버전의 행 수가 다름")
            if not case_comparison.get("case_sets_match", False):
                report.append("- 두 버전의 Case NO가 다름")
            if not content_comparison.get("data_content_match", True):
                report.append("- 두 버전의 데이터 내용이 다름")

        return "\n".join(report)

    def run_verification(self) -> Dict[str, Any]:
        """전체 검증 실행"""
        logger.info("HVDC Pipeline 정렬 옵션 검증 시작...")

        try:
            # 1. 출력 파일 찾기
            sorted_file, no_sorted_file = self.find_output_files()

            # 2. 데이터 로드
            sorted_df = self.load_data(sorted_file)
            no_sorted_df = self.load_data(no_sorted_file)

            # 3. 정렬 순서 검증
            sorting_results = self.verify_sorting_order(sorted_df, no_sorted_df)

            # 4. 데이터 일관성 검증
            consistency_results = self.verify_data_consistency(sorted_df, no_sorted_df)

            # 5. 결과 통합
            verification_results = {
                "files": {
                    "sorted_file": str(sorted_file),
                    "no_sorted_file": str(no_sorted_file),
                },
                **sorting_results,
                **consistency_results,
            }

            # 6. 보고서 생성
            report = self.generate_report(verification_results)

            # 7. 보고서 저장
            report_file = self.project_root / "SORTING_VERIFICATION_REPORT.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"검증 완료. 보고서 저장: {report_file}")
            print(report)  # 콘솔에도 출력

            return verification_results

        except Exception as e:
            logger.error(f"검증 실행 실패: {e}")
            raise


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="HVDC Pipeline 정렬 옵션 검증",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python verify_sorting_option.py                    # 기본 검증
  python verify_sorting_option.py --project-root .  # 프로젝트 루트 지정
        """,
    )

    parser.add_argument(
        "--project-root", type=str, help="프로젝트 루트 디렉토리 경로 (기본: 자동 감지)"
    )

    args = parser.parse_args()

    try:
        # 프로젝트 루트 설정
        project_root = Path(args.project_root) if args.project_root else PIPELINE_ROOT

        # 검증 실행
        verifier = SortingVerifier(project_root)
        results = verifier.run_verification()

        print("\n" + "=" * 60)
        print("검증 완료! 자세한 결과는 SORTING_VERIFICATION_REPORT.md를 확인하세요.")
        print("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"검증 실패: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
