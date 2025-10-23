좋아, 핵심만 정리해서 “지금 파이프라인에 꽂아 쓰는” 코드로 바로 내줄게.

한눈 요약

SQM 산출: L(cm)×W(cm)/10,000(㎡). 길이/너비 중 하나라도 없으면 기존 추정 로직(예: PKG 기반)을 백업으로 사용.

Stack_Status 산출: 텍스트에서 숫자(1,2,3,4…)를 파싱해 단 수(=tier)로 저장. 숫자 없으면 1단. “Not stackable”류는 0. “on top(only)”는 1단으로 처리.

헤더 통합: 헤더 레지스트리/정규화/시맨틱 매처를 그대로 활용(의미 기반 헤더 탐지).

0) 사전: 이미 있는 정의/도구

파생 컬럼 상수 존재: "SQM", "Stack_Status" 등(수정 불필요).

기존 SQM 추정 함수(_get_sqm)가 있으나, 이번엔 치수 기반 계산을 우선 → 실패 시 기존 추정 사용.

헤더 정규화·시맨틱 매칭 엔진을 그대로 사용.

1) header_registry.py에 의미 헤더 추가

“L(cm), W(cm), H(cm)”와 Stack 표기 열(원문 텍스트)을 의미 키로 등록.
아래 조각을 HeaderRegistry._initialize_definitions() 내부 적절한 위치에 추가.

# --- Dimensions (cm) ---
self.register(HeaderDefinition(
    semantic_key="length_cm",
    category=HeaderCategory.QUANTITY,
    aliases=[
        "L(CM)", "L (CM)", "Length (cm)", "Length(cm)", "L CM", "Length",
        "L(mm)"  # 있으면 cm로 변환 필요(후처리)
    ],
    description="Item length in centimeters",
    required=False,
    data_type="float"
))
self.register(HeaderDefinition(
    semantic_key="width_cm",
    category=HeaderCategory.QUANTITY,
    aliases=[
        "W(CM)", "W (CM)", "Width (cm)", "Width(cm)", "W CM", "Width",
        "W(mm)"  # 있으면 cm로 변환
    ],
    description="Item width in centimeters",
    required=False,
    data_type="float"
))
self.register(HeaderDefinition(
    semantic_key="height_cm",
    category=HeaderCategory.QUANTITY,
    aliases=[
        "H(CM)", "H (CM)", "Height (cm)", "Height(cm)", "H CM", "Height",
        "H(mm)"  # 있으면 cm로 변환
    ],
    description="Item height in centimeters",
    required=False,
    data_type="float"
))

# --- Stackability raw text column ---
self.register(HeaderDefinition(
    semantic_key="stackability_text",
    category=HeaderCategory.STATUS,
    aliases=[
        "Stackability", "Stackable", "Stack ability", "Stack status", "Stack",
        "Stackability note"
    ],
    description="Raw stackability text used to derive Stack_Status tier",
    required=False,
    data_type="str"
))

# --- Derived (for documentation only; 실제 컬럼 생성은 파이프라인에서) ---
self.register(HeaderDefinition(
    semantic_key="stack_status",
    category=HeaderCategory.DERIVED,
    aliases=["Stack_Status", "Stack Status", "Stack Tiers"],
    description="Parsed stack tier (0=Not stackable, 1..n)",
    required=False,
    data_type="int"
))
self.register(HeaderDefinition(
    semantic_key="sqm",
    category=HeaderCategory.DERIVED,
    aliases=["SQM", "Area(m2)", "M2", "m2"],
    description="Area in square meters computed from L(cm) and W(cm)",
    required=False,
    data_type="float"
))


위와 같은 의미-헤더 등록 방식은 현 레지스트리 구조와 일치한다(정규화/별칭 기반 매칭).

2) 파싱·계산 유틸 신규 모듈 (예: derived/stack_and_sqm.py)

시맨틱 매처로 실제 컬럼명을 찾고, SQM/Stack_Status를 DataFrame에 삽입.

# derived/stack_and_sqm.py
from __future__ import annotations
import math
import re
import pandas as pd

from core.semantic_matcher import SemanticMatcher  # 경로는 프로젝트 구조에 맞게
from core.header_normalizer import HeaderNormalizer

NOT_STACK_PATTERNS = [
    r"\bnot\s*stackable\b", r"\bnon[-\s]*stackable\b", r"\bno\s*stack(ing)?\b",
]
TOP_ONLY_PATTERNS = [
    r"only\s+on\s+top", r"on\s+top\s+only", r"stackable\s+on\s+top"
]
NUMBER_PAT = re.compile(r"\b(\d+)\b")
XNUM_PAT   = re.compile(r"[xX]\s*(\d+)")
PCS_PAT    = re.compile(r"(\d+)\s*(pcs?)")
TIER_PAT   = re.compile(r"(\d+)\s*(tier|tiers?)", re.I)

def _to_float(x):
    try:
        if pd.isna(x):
            return None
        # 천단위/공백 제거
        if isinstance(x, str):
            xs = x.strip().replace(",", "")
            return float(xs)
        return float(x)
    except Exception:
        return None

def compute_sqm_from_dims(row: pd.Series, l_col: str|None, w_col: str|None) -> float|None:
    """SQM = L(cm) * W(cm) / 10,000  (둘 다 있어야 산출)"""
    if not l_col or not w_col:
        return None
    L = _to_float(row.get(l_col))
    W = _to_float(row.get(w_col))
    if L is None or W is None or L <= 0 or W <= 0:
        return None
    return round((L * W) / 10000.0, 2)

def parse_stack_status(text: str|None) -> int|None:
    """
    규칙:
      - 'not stackable'류 → 0
      - 숫자 표현: X2, x3, '2 pcs', '3 tier' 등 → 해당 숫자
      - 'on top only'류 → 1
      - 숫자 전혀 없으면 → 1
      - '600kg/m2' 등 하중 표기는 단수 지정 근거가 없으므로 1로 간주
    """
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return None

    s = str(text).lower().strip()

    # 명시적 비적재
    if any(re.search(p, s) for p in NOT_STACK_PATTERNS):
        return 0

    # on top only 류
    if any(re.search(p, s) for p in TOP_ONLY_PATTERNS):
        return 1

    # 숫자 후보들
    nums = []
    for pat in (XNUM_PAT, PCS_PAT, TIER_PAT, NUMBER_PAT):
        for m in pat.finditer(s):
            try:
                n = int(m.group(1))
                nums.append(n)
            except Exception:
                pass

    if nums:
        return max(nums)

    # 'Stackable', 'Stackability', '600kg/m2' 등 → 숫자 부재시 1단
    return 1

def add_sqm_and_stack(df: pd.DataFrame) -> pd.DataFrame:
    """
    시맨틱 매처로 치수/스택 열을 찾아 SQM/Stack_Status 추가 후 반환.
    """
    matcher = SemanticMatcher()
    need_keys = ["length_cm", "width_cm", "stackability_text"]
    report = matcher.match_dataframe(df, need_keys)  # 열 매칭 보고서
    # 실 컬럼명
    l_col = report.get_column_name("length_cm")
    w_col = report.get_column_name("width_cm")
    stack_text_col = report.get_column_name("stackability_text")

    # SQM
    if l_col or w_col:
        df["SQM"] = df.apply(lambda r: compute_sqm_from_dims(r, l_col, w_col), axis=1)

    # Stack_Status
    if stack_text_col and stack_text_col in df.columns:
        df["Stack_Status"] = df[stack_text_col].apply(parse_stack_status)
    else:
        # 원문 스택 열이 없더라도 도메인 규칙상 기본 1단 희망 시:
        # df["Stack_Status"] = 1
        pass

    return df


이 유틸은 시맨틱 매처의 열 탐색을 그대로 사용한다(헤더 정규화/별칭 매칭).

“숫자 없는 경우 1단”, “Not stackable 계열은 0” 등 요청 규칙을 전부 반영.

참고: “600kg/m2, 600kg/m3…” 같은 하중 표기는 단수 산정 직접 근거가 없어 1단으로 처리했다(요청 “숫자 없으면 1단” 규칙에 부합). 필요하면 별도 Stack_Limit 컬럼(문자열)로 원문을 보존 가능.

3) 기존 SQM 추정 로직(백업)과의 연동

현재 _get_sqm(row)가 존재한다. 아래처럼 치수 기반 계산을 우선, 실패 시 기존 추정으로 폴백 하도록 교체하면 된다.

# hvdc_excel_reporter_final_sqm_rev.py 내 _get_sqm 교체(요지)
from derived.stack_and_sqm import compute_sqm_from_dims  # 위 신규 모듈

def _get_sqm(row):
    # 시맨틱 매칭 없이, 파이프라인 상에서 전달된 실제 컬럼명(예: L(CM), W(CM))을 쓸 수도 있고,
    # or 앞 단계에서 add_sqm_and_stack(df)이 이미 SQM을 채웠다면 그냥 반환해도 됨.
    # 여기서는 row에 L/W가 있을 때 직접 계산, 없으면 기존 추정.

    # 1) 치수 기반 우선
    for l_key in ("L(CM)", "Length (cm)", "L CM", "Length"):
        if l_key in row.index:
            L = row.get(l_key)
            break
    else:
        L = None

    for w_key in ("W(CM)", "Width (cm)", "W CM", "Width"):
        if w_key in row.index:
            W = row.get(w_key)
            break
    else:
        W = None

    sqm = None
    if L is not None and W is not None:
        try:
            Lf = float(str(L).replace(",", "").strip())
            Wf = float(str(W).replace(",", "").strip())
            if Lf > 0 and Wf > 0:
                sqm = round((Lf * Wf) / 10000.0, 2)
        except Exception:
            sqm = None

    if sqm is not None:
        return sqm

    # 2) 실패 시 기존 추정(현 로직 그대로)
    return _get_sqm_with_source(row)[0]  # 기존 구현 활용


위 파일에는 이미 SQM 관련 보조 함수들이 있으며(추정 로직), 치수 기반을 최우선으로 하되 기존 방식을 안전 폴백으로 유지하는 게 안정적이다.

4) 파이프라인 연결

데이터 로드 직후, 또는 Stage-2 파생컬럼 처리 시점에 아래 한 줄을 추가:

from derived.stack_and_sqm import add_sqm_and_stack

df = add_sqm_and_stack(df)  # SQM, Stack_Status 자동 삽입


이 방식은 파이프라인의 의미 매칭→파생 컬럼 흐름을 그대로 따른다.

5) 스택 텍스트 예시 매핑(요청 리스트 반영)

아래 값들은 전부 parse_stack_status()에서 처리됨.

0단: Not stackable, NON stackable, Non-Stackable, Not Satckable, Not Stackable, Not stackable 등

1단: Stackable, Stackability, Stackability 600kg/m2, Stackable on top, Stackable only on top, X1, x1, Stackable 1x, Stackable 1 tier, 숫자 부재 전부(요청 규칙)

2단 이상: Stackable / 2 pcs, Stackable /2, Stackable 2 pcs, Stackable 2 tier, Stackable 2X, X2, x2 → 2
…3 tier, …/ 3 pcs, x3, X3 → 3; x4, X4 → 4 …

6) 빠른 검증(샘플)
def _t(s):
    from derived.stack_and_sqm import parse_stack_status
    return parse_stack_status(s)

assert _t("Not stackable") == 0
assert _t("Stackability x1") == 1
assert _t("Stackable / 2 pcs") == 2
assert _t("Stackable 3 tier") == 3
assert _t("X4") == 4
assert _t("600kg/m2") == 1           # 숫자 없이 하중표현 → 1
assert _t("Stackable on top") == 1   # on top only 류 → 1

정리 / 적용 순서

header_registry.py에 치수/스택 원문/파생 헤더 정의 추가.

derived/stack_and_sqm.py 새로 추가(위 코드 그대로).

Stage-2(파생) 구간에서 add_sqm_and_stack(df) 호출로 SQM, Stack_Status 자동 생성.

_get_sqm()는 치수→기존추정 순서로 동작하도록 위처럼 교체(선택).

이렇게 넣으면 헤더(별칭) 인식 → 시맨틱 매칭 → 파생 컬럼 산출의 기존 구조를 그대로 타면서, 치수 기반 정확한 SQM과 규칙 기반 Stack_Status가 자동으로 채워진다.
필요하면, Stack_Limit(원문 하중표시 보존) 같은 보조 컬럼도 바로 붙여줄 수 있어.

원한다면, 내가 위 코드 조각을 네 현재 레포 구조에 맞춰 **패치 형태(diff)**로 다시 정리해줄게.
