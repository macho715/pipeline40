"""
표준 헤더 순서 정의 (Standard Header Order)

실제 "통합_원본데이터_Fixed" 시트의 헤더 순서를 기준으로
Stage 2 및 Stage 3 출력 파일의 컬럼 순서를 통일합니다.

기준: Stage 3 보고서의 "통합_원본데이터_Fixed" 시트 (64개 컬럼)

중요: 기존 core/ 디렉토리의 HeaderNormalizer, HeaderRegistry, SemanticMatcher를
      활용하여 유연한 헤더 매칭 및 정규화를 수행합니다.
"""

import pandas as pd
from typing import Optional, List, Dict, Tuple, Set
import logging
import re
from difflib import SequenceMatcher

# 기존 core 로직 import
from .header_normalizer import HeaderNormalizer
from .header_registry import HeaderRegistry
from .semantic_matcher import SemanticMatcher

logger = logging.getLogger(__name__)

# 실제 "통합_원본데이터_Fixed" 시트 기준 표준 헤더 순서 (64개)
STANDARD_HEADER_ORDER = [
    # 기본 식별 정보
    "no.",
    "Shipment Invoice No.",
    "HVDC CODE",  # Stage 3에서 추가
    "Site",
    "EQ No",
    "Case No.",
    "Pkg",
    "Storage",
    "Description",
    # 치수 정보 (SQM 계산의 입력)
    "L(CM)",
    "W(CM)",
    "H(CM)",
    "CBM",
    "N.W(kgs)",
    "G.W(kgs)",
    # Stack 관련
    "Stack",
    "HS Code",
    "Currency",
    "Price",
    "Vessel",
    "COE",
    "POL",
    "POD",
    "ETD/ATD",
    "ETA/ATA",
    # 창고 정보 (HeaderRegistry에 정의된 순서)
    "DHL WH",
    "DSV Indoor",
    "DSV Al Markaz",
    "Hauler Indoor",
    "DSV Outdoor",
    "DSV MZP",
    "HAULER",
    "JDN MZD",
    "MOSB",
    "AAA Storage",
    # 추가 창고/작업
    "Shifting",
    # 현장 정보 (실제 사용 중인 컬럼명)
    "MIR",
    "SHU",
    "AGI",
    "DAS",
    # 메타데이터
    "Source_Sheet",
    # 상태 정보 (Status_로 시작하는 파생 컬럼)
    "Status_WAREHOUSE",
    "Status_SITE",
    "Status_Current",
    "Status_Location",
    "Status_Location_Date",
    "Status_Storage",
    # Handling 정보 (파생 컬럼)
    "wh_handling_legacy",  # Stage 3에서 "wh handling"을 이 이름으로 변경
    "site handling",  # 공백 1개
    "total handling",
    "minus",
    "final handling",
    # SQM 및 Stack_Status (Stage 2에서 계산)
    "SQM",
    "Stack_Status",
    "Total sqm",  # Stage 3: PKG × SQM × Stack_Status
    # Stage 3에서 추가되는 메타 컬럼
    "Vendor",
    "Source_File",
    "Status_Location_YearMonth",
    "site_handling_original",
    "total_handling_original",
    "wh_handling_original",
    "FLOW_CODE",
    "FLOW_DESCRIPTION",
    "Final_Location",
    # 입고일자
    "입고일자",
]

# Stage 2 전용 헤더 순서 (Stage 3에서만 추가되는 컬럼 제외)
STAGE2_HEADER_ORDER = [
    "no.",
    "Shipment Invoice No.",
    "SCT Ref.No",  # Stage 2에만 있음
    "Site",
    "EQ No",
    "Case No.",
    "Pkg",
    "Storage",
    "Description",
    "L(CM)",
    "W(CM)",
    "H(CM)",
    "CBM",
    "N.W(kgs)",
    "G.W(kgs)",
    "Stack",
    "HS Code",
    "Currency",
    "Price",
    "Vessel",
    "COE",
    "POL",
    "POD",
    "ETD/ATD",
    "ETA/ATA",
    # "no" 제거됨 - 26번째에 DHL WH이 옴
    "DHL WH",
    "DSV Indoor",
    "DSV Al Markaz",
    "Hauler Indoor",
    "DSV Outdoor",
    "DSV MZP",
    "HAULER",
    "JDN MZD",
    "MOSB",
    "AAA Storage",
    "Shifting",
    # 현장 컬럼 (실제 사용 중)
    "MIR",
    "SHU",
    "AGI",
    "DAS",
    "Source_Sheet",
    "Status_WAREHOUSE",
    "Status_SITE",
    "Status_Current",
    "Status_Location",
    "Status_Location_Date",
    "Status_Storage",
    "wh handling",  # Stage 2 원본
    "site  handling",  # 공백 2개 - Stage 2 원본
    "total handling",
    "minus",
    "final handling",
    "SQM",
    "Stack_Status",
]


class FlexibleHeaderMatcher:
    """
    유연한 헤더 매칭 클래스

    기존 core 로직을 활용하여 다양한 헤더 변형을 자동으로 매칭합니다.
    """

    def __init__(self):
        """초기화"""
        self.normalizer = HeaderNormalizer()
        self.registry = HeaderRegistry()
        self.semantic_matcher = SemanticMatcher()

        # 유연한 매칭을 위한 패턴 정의
        self._init_matching_patterns()

    def _init_matching_patterns(self):
        """매칭 패턴 초기화"""
        # 일반적인 헤더 변형 패턴
        self.patterns = {
            # 공백 및 특수문자 변형
            "space_variations": [
                (r"\s+", " "),  # 여러 공백을 하나로
                (r"^\s+|\s+$", ""),  # 앞뒤 공백 제거
            ],
            # 대소문자 변형
            "case_variations": [
                (r"^no\.?$", "no.", re.IGNORECASE),
                (r"^site\s*handling$", "site handling", re.IGNORECASE),
                (r"^wh\s*handling$", "wh handling", re.IGNORECASE),
            ],
            # 특수문자 변형
            "special_chars": [
                (r"\(", "\\("),
                (r"\)", "\\)"),
                (r"\.", "\\."),
                (r"\+", "\\+"),
                (r"\*", "\\*"),
                (r"\?", "\\?"),
                (r"\[", "\\["),
                (r"\]", "\\]"),
            ],
        }

    def normalize_header_name(self, header_name: str) -> str:
        """
        헤더명을 정규화 (기존 HeaderNormalizer 활용)

        Args:
            header_name: 원본 헤더명

        Returns:
            정규화된 헤더명
        """
        try:
            # 기존 HeaderNormalizer 사용
            normalized = self.normalizer.normalize(header_name, expand_abbreviations=False)

            # 추가 정규화 (공백 정리)
            normalized = re.sub(r"\s+", " ", normalized.strip())

            return normalized
        except Exception as e:
            logger.warning(f"HeaderNormalizer 실패, 기본 정규화 사용: {e}")
            return header_name.strip()

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        두 문자열의 유사도를 계산

        Args:
            str1, str2: 비교할 문자열

        Returns:
            유사도 (0.0 ~ 1.0)
        """
        # 정규화
        norm1 = self.normalize_header_name(str1)
        norm2 = self.normalize_header_name(str2)

        # 정확히 일치하는 경우
        if norm1 == norm2:
            return 1.0

        # 대소문자 무시하고 일치하는 경우
        if norm1.lower() == norm2.lower():
            return 0.95

        # SequenceMatcher를 사용한 유사도 계산
        similarity = SequenceMatcher(None, norm1.lower(), norm2.lower()).ratio()

        # 부분 일치 보너스
        if norm1.lower() in norm2.lower() or norm2.lower() in norm1.lower():
            similarity = max(similarity, 0.8)

        return similarity

    def find_best_match(
        self, target_header: str, candidate_headers: List[str], min_similarity: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        대상 헤더에 대한 최적 매칭을 찾습니다

        Args:
            target_header: 매칭할 대상 헤더
            candidate_headers: 후보 헤더 리스트
            min_similarity: 최소 유사도 임계값

        Returns:
            (매칭된_헤더, 유사도) 튜플 또는 None
        """
        best_match = None
        best_similarity = 0.0

        for candidate in candidate_headers:
            similarity = self.calculate_similarity(target_header, candidate)

            if similarity > best_similarity and similarity >= min_similarity:
                best_similarity = similarity
                best_match = candidate

        if best_match:
            logger.debug(
                f"헤더 매칭: '{target_header}' → '{best_match}' (유사도: {best_similarity:.3f})"
            )
            return (best_match, best_similarity)

        return None

    def semantic_match(self, header_name: str, standard_headers: List[str]) -> Optional[str]:
        """
        의미론적 매칭을 사용하여 헤더를 찾습니다

        Args:
            header_name: 매칭할 헤더명
            standard_headers: 표준 헤더 리스트

        Returns:
            매칭된 표준 헤더명 또는 None
        """
        try:
            # HeaderRegistry의 의미론적 매칭 활용
            for standard_header in standard_headers:
                # 정규화된 이름으로 비교
                norm_header = self.normalize_header_name(header_name)
                norm_standard = self.normalize_header_name(standard_header)

                # 의미론적 유사성 확인
                if self.semantic_matcher.is_semantically_similar(norm_header, norm_standard):
                    logger.debug(f"의미론적 매칭: '{header_name}' → '{standard_header}'")
                    return standard_header
        except Exception as e:
            logger.warning(f"의미론적 매칭 실패: {e}")

        return None


class HeaderOrderManager:
    """
    헤더 순서 관리 클래스

    기존 core 로직과 유연한 매칭을 활용하여
    헤더 매칭 및 재정렬을 수행합니다.
    """

    def __init__(self):
        """초기화"""
        self.matcher = FlexibleHeaderMatcher()

    def match_columns_to_standard(
        self,
        current_columns: List[str],
        standard_order: List[str],
        use_semantic_matching: bool = True,
    ) -> Dict[str, str]:
        """
        현재 컬럼들을 표준 헤더와 매칭 (유연한 검색)

        Args:
            current_columns: 현재 DataFrame의 컬럼 리스트
            standard_order: 표준 헤더 순서 리스트
            use_semantic_matching: 의미론적 매칭 사용 여부

        Returns:
            {현재_컬럼: 표준_컬럼} 매핑 딕셔너리
        """
        mapping = {}
        used_standards = set()

        # 1단계: 정확히 일치하는 컬럼 먼저 매핑
        for col in current_columns:
            if col in standard_order:
                mapping[col] = col
                used_standards.add(col)
                logger.debug(f"정확 매칭: '{col}' → '{col}'")

        # 2단계: 정규화된 이름으로 매칭 시도
        unmapped_current = [c for c in current_columns if c not in mapping]
        available_standards = [s for s in standard_order if s not in used_standards]

        for current_col in unmapped_current:
            # 정규화된 이름으로 매칭
            normalized_current = self.matcher.normalize_header_name(current_col)

            for standard_col in available_standards:
                normalized_standard = self.matcher.normalize_header_name(standard_col)

                if normalized_current == normalized_standard:
                    mapping[current_col] = standard_col
                    used_standards.add(standard_col)
                    logger.debug(f"정규화 매칭: '{current_col}' → '{standard_col}'")
                    break

        # 3단계: 유사도 기반 매칭
        if use_semantic_matching:
            unmapped_current = [c for c in current_columns if c not in mapping]
            available_standards = [s for s in standard_order if s not in used_standards]

            for current_col in unmapped_current:
                # 의미론적 매칭 시도
                semantic_match = self.matcher.semantic_match(current_col, available_standards)
                if semantic_match:
                    mapping[current_col] = semantic_match
                    used_standards.add(semantic_match)
                    logger.debug(f"의미론적 매칭: '{current_col}' → '{semantic_match}'")
                    continue

                # 유사도 기반 매칭
                best_match = self.matcher.find_best_match(
                    current_col, available_standards, min_similarity=0.7
                )
                if best_match:
                    matched_col, similarity = best_match
                    mapping[current_col] = matched_col
                    used_standards.add(matched_col)
                    logger.debug(
                        f"유사도 매칭: '{current_col}' → '{matched_col}' (유사도: {similarity:.3f})"
                    )

        # 매칭 결과 로깅
        total_mapped = len(mapping)
        total_current = len(current_columns)
        mapping_rate = (total_mapped / total_current * 100) if total_current > 0 else 0

        logger.info(f"헤더 매칭 완료: {total_mapped}/{total_current}개 ({mapping_rate:.1f}%)")

        return mapping

    def reorder_dataframe(
        self,
        df: pd.DataFrame,
        is_stage2: bool = False,
        keep_unlisted: bool = True,
        use_semantic_matching: bool = True,
    ) -> pd.DataFrame:
        """
        DataFrame의 컬럼을 표준 순서로 재정렬 (유연한 검색)

        Args:
            df: 재정렬할 DataFrame
            is_stage2: Stage 2 출력인 경우 True
            keep_unlisted: 표준 순서에 없는 컬럼을 끝에 추가할지 여부
            use_semantic_matching: 의미론적 매칭 사용 여부

        Returns:
            재정렬된 DataFrame
        """
        standard_order = STAGE2_HEADER_ORDER if is_stage2 else STANDARD_HEADER_ORDER
        current_columns = list(df.columns)

        logger.info(
            f"🔄 헤더 재정렬 시작 ({'Stage 2' if is_stage2 else 'Stage 3'}): {len(current_columns)}개 컬럼"
        )

        # 헤더 매칭 (유연한 검색)
        mapping = self.match_columns_to_standard(
            current_columns, standard_order, use_semantic_matching=use_semantic_matching
        )

        # 표준 순서에 맞춰 컬럼 재정렬
        ordered_columns = []
        for std_col in standard_order:
            # 매핑된 원본 컬럼명 찾기
            original_col = next((k for k, v in mapping.items() if v == std_col), None)
            if original_col and original_col in df.columns:
                ordered_columns.append(original_col)

        # 표준 순서에 없는 컬럼 추가 (끝에)
        remaining_columns = []
        if keep_unlisted:
            remaining_columns = [c for c in current_columns if c not in ordered_columns]

        final_order = ordered_columns + remaining_columns

        logger.info(
            f"✅ 헤더 재정렬 완료: {len(ordered_columns)}개 표준 순서, {len(remaining_columns)}개 추가 컬럼"
        )

        return df[final_order]

    def detect_header_variations(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        DataFrame의 헤더 변형을 감지합니다

        Args:
            df: 분석할 DataFrame

        Returns:
            {표준_헤더: [발견된_변형들]} 딕셔너리
        """
        variations = {}
        current_columns = list(df.columns)

        # 모든 표준 헤더에 대해 변형 검색
        for standard_header in STANDARD_HEADER_ORDER:
            found_variations = []

            for col in current_columns:
                similarity = self.matcher.calculate_similarity(standard_header, col)
                if similarity >= 0.7:  # 70% 이상 유사한 경우
                    found_variations.append((col, similarity))

            if found_variations:
                # 유사도 순으로 정렬
                found_variations.sort(key=lambda x: x[1], reverse=True)
                variations[standard_header] = [var[0] for var in found_variations]

        return variations


# 전역 인스턴스
_manager = None


def get_header_manager() -> HeaderOrderManager:
    """HeaderOrderManager 싱글톤 인스턴스 반환"""
    global _manager
    if _manager is None:
        _manager = HeaderOrderManager()
    return _manager


def reorder_dataframe_columns(
    df: pd.DataFrame,
    is_stage2: bool = False,
    keep_unlisted: bool = True,
    use_semantic_matching: bool = True,
) -> pd.DataFrame:
    """
    DataFrame의 컬럼을 표준 순서로 재정렬 (편의 함수)

    Args:
        df: 재정렬할 DataFrame
        is_stage2: Stage 2 출력인 경우 True
        keep_unlisted: 표준 순서에 없는 컬럼을 끝에 추가할지 여부
        use_semantic_matching: 의미론적 매칭 사용 여부

    Returns:
        재정렬된 DataFrame
    """
    manager = get_header_manager()
    return manager.reorder_dataframe(
        df,
        is_stage2=is_stage2,
        keep_unlisted=keep_unlisted,
        use_semantic_matching=use_semantic_matching,
    )


def validate_sqm_stack_presence(df: pd.DataFrame) -> dict:
    """
    SQM과 Stack_Status 컬럼의 존재 여부와 데이터 품질 확인

    Returns:
        검증 결과 딕셔너리
    """
    result = {
        "sqm_present": "SQM" in df.columns,
        "stack_status_present": "Stack_Status" in df.columns,
        "sqm_calculated_count": 0,
        "stack_parsed_count": 0,
        "warnings": [],
        "column_count": len(df.columns),
    }

    if result["sqm_present"]:
        result["sqm_calculated_count"] = df["SQM"].notna().sum()
        sqm_percentage = (result["sqm_calculated_count"] / len(df) * 100) if len(df) > 0 else 0
        logger.info(
            f"[SUCCESS] SQM: {result['sqm_calculated_count']}개 계산됨 ({sqm_percentage:.1f}%)"
        )
        if result["sqm_calculated_count"] == 0:
            result["warnings"].append("SQM 컬럼은 존재하지만 계산된 값이 없습니다.")
    else:
        result["warnings"].append("[ERROR] SQM 컬럼이 존재하지 않습니다.")
        logger.warning("SQM 컬럼이 존재하지 않습니다.")

    if result["stack_status_present"]:
        result["stack_parsed_count"] = df["Stack_Status"].notna().sum()
        stack_percentage = (result["stack_parsed_count"] / len(df) * 100) if len(df) > 0 else 0
        logger.info(
            f"[SUCCESS] Stack_Status: {result['stack_parsed_count']}개 파싱됨 ({stack_percentage:.1f}%)"
        )
        if result["stack_parsed_count"] == 0:
            result["warnings"].append("Stack_Status 컬럼은 존재하지만 파싱된 값이 없습니다.")
    else:
        result["warnings"].append("[ERROR] Stack_Status 컬럼이 존재하지 않습니다.")
        logger.warning("Stack_Status 컬럼이 존재하지 않습니다.")

    return result


def normalize_header_names_for_stage3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2와 Stage 3 간 헤더명 차이를 정규화 (Stage 3 전용)

    변환:
    - "No" → "no."
    - "wh handling" → "wh_handling_legacy"
    - "site  handling" (공백 2개) → "site handling" (공백 1개)
    - 중복 "no" 컬럼 제거 (no.와 no가 동시에 존재하는 경우)
    """
    renamed = {}

    for col in df.columns:
        if col == "No":
            renamed[col] = "no."
        elif col == "wh handling":
            renamed[col] = "wh_handling_legacy"
        elif col == "site  handling":
            renamed[col] = "site handling"

    if renamed:
        df = df.rename(columns=renamed)
        logger.info(f"[INFO] Stage 3 헤더명 정규화: {len(renamed)}개 컬럼 변경됨")
        for old, new in renamed.items():
            logger.info(f"  - '{old}' → '{new}'")

    # 중복 'no' 컬럼 제거 (no.와 no가 동시에 존재하는 경우)
    if "no" in df.columns and "no." in df.columns:
        df = df.drop(columns=["no"], errors="ignore")
        logger.info("[INFO] 중복 'no' 컬럼 제거 완료 (no. 유지)")

    return df


def normalize_header_names_for_stage2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2 헤더명 정규화

    변환:
    - "No" → "no."
    - "site  handling" (공백 2개) → "site handling" (공백 1개)
    - 중복 "no" 컬럼 제거 (no.와 no가 동시에 존재하는 경우)
    """
    renamed = {}

    for col in df.columns:
        if col == "No":
            renamed[col] = "no."
        elif col == "site  handling":
            renamed[col] = "site handling"

    if renamed:
        df = df.rename(columns=renamed)
        logger.info(f"[INFO] Stage 2 헤더명 정규화: {len(renamed)}개 컬럼 변경됨")
        for old, new in renamed.items():
            logger.info(f"  - '{old}' → '{new}'")

    # 중복 'no' 컬럼 제거 (no.와 no가 동시에 존재하는 경우)
    if "no" in df.columns and "no." in df.columns:
        df = df.drop(columns=["no"], errors="ignore")
        logger.info("[INFO] 중복 'no' 컬럼 제거 완료 (no. 유지)")

    return df


def analyze_header_compatibility(df: pd.DataFrame, is_stage2: bool = False) -> dict:
    """
    DataFrame의 헤더 호환성을 분석합니다

    Args:
        df: 분석할 DataFrame
        is_stage2: Stage 2 출력인 경우 True

    Returns:
        호환성 분석 결과
    """
    manager = get_header_manager()
    standard_order = STAGE2_HEADER_ORDER if is_stage2 else STANDARD_HEADER_ORDER

    # 헤더 변형 감지
    variations = manager.detect_header_variations(df)

    # 매칭 분석
    mapping = manager.match_columns_to_standard(list(df.columns), standard_order)

    analysis = {
        "total_columns": len(df.columns),
        "standard_columns": len(standard_order),
        "matched_columns": len(mapping),
        "matching_rate": (len(mapping) / len(df.columns) * 100) if len(df.columns) > 0 else 0,
        "variations_detected": len(variations),
        "unmatched_columns": [col for col in df.columns if col not in mapping],
        "header_variations": variations,
        "recommendations": [],
    }

    # 권장사항 생성
    if analysis["matching_rate"] < 80:
        analysis["recommendations"].append(
            "헤더 매칭률이 낮습니다. 헤더명을 표준 형식에 맞춰 수정하세요."
        )

    if analysis["variations_detected"] > 0:
        analysis["recommendations"].append(
            f"{analysis['variations_detected']}개의 헤더 변형이 감지되었습니다. 일관된 명명 규칙을 사용하세요."
        )

    if analysis["unmatched_columns"]:
        analysis["recommendations"].append(
            f"{len(analysis['unmatched_columns'])}개의 매칭되지 않은 컬럼이 있습니다: {analysis['unmatched_columns'][:5]}"
        )

    return analysis
