# -*- coding: utf-8 -*-
"""
Stack_Status 파싱 유틸
- 규칙:
  1) 'Not stackable' 계열 → 0
  2) 'on top only' 계열 → 1
  3) 숫자 표기(x2, 2 tier, / 3, 3 pcs, 1X 등) → 해당 숫자(최대값)
  4) 하중 표기(예: 600kg/m2, kg/m3 등)는 '단수' 판단에서 제외
  5) 위 모두에 해당 없으면 → 1
  6) 공백/NaN → None
"""
from __future__ import annotations
import re
from typing import Optional, Iterable

# --- 패턴 준비 ----------------------------------------------------------------
# 오타/대소문자/공백 변형을 감안해 넉넉히 커버
_NOT_STACK_PATTERNS: Iterable[re.Pattern] = tuple(
    re.compile(p, re.I)
    for p in [
        r"\bnot\s*stackable\b",
        r"\bnon[-\s]*stackable\b",
        r"\bno\s*stack(ing)?\b",
        r"\bnot\s*satckable\b",  # 오타 케이스
    ]
)

_TOP_ONLY_PATTERNS: Iterable[re.Pattern] = tuple(
    re.compile(p, re.I)
    for p in [
        r"\bonly\s+on\s+top\b",
        r"\bon\s+top\s+only\b",
        r"\bstackable\s+on\s+top\b",
    ]
)

# 하중 표기(숫자 오염 방지용): 600kg/m2, 600 kg / m3, kg/㎡ 등
_WEIGHT_PATTERNS: Iterable[re.Pattern] = tuple(
    re.compile(p, re.I)
    for p in [
        r"\b\d+\s*kg\s*/\s*m\s*\d*\b",      # 600kg/m2, 600 kg/m
        r"\b\d+\s*kg\s*/\s*㎡\b",            # 600kg/㎡
        r"\b\d+\s*kg\s*/\s*m\^?\d\b",        # 600kg/m^2
        r"\b\d+\s*kg\b",                     # 단독 kg 표기(보수적으로 제거)
    ]
)

# 단수 추출(여러 숫자가 있으면 '최대값' 채택)
# - x2 / X3 / 1X / 2 x 등
_XNUM_PAT   = re.compile(r"(?:\b[xX]\s*(\d+))|(?:\b(\d+)\s*[xX]\b)")
# - 2 pcs / 3 pc / 4 piece(s)
_PCS_PAT    = re.compile(r"\b(\d+)\s*(?:pcs?|pieces?)\b", re.I)
# - 2 tier / 3 tiers
_TIER_PAT   = re.compile(r"\b(\d+)\s*tier[s]?\b", re.I)
# - / 2  (예: 'Stackable / 2' 'Stackable / 3 pcs')
_SLASH_PAT  = re.compile(r"/\s*(\d+)\b")
# - 고립 숫자(맨 마지막 안전망). kg/m2 처리는 사전 제거로 회피
_NUM_PAT    = re.compile(r"\b(\d+)\b")


def _strip_weights(text: str) -> str:
    """하중 관련 토큰(kg/m2 등)을 제거해 단수 추출시 숫자 오염을 방지."""
    s = text
    for pat in _WEIGHT_PATTERNS:
        s = pat.sub(" ", s)
    return s


def parse_stack_status(value: object) -> Optional[int]:
    """
    입력: 임의 오브젝트(문자열 가정). NaN/공백은 None.
    출력: 0(불가능) 또는 1..n(단수), 판단 불가(None)
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None

    s_lower = s.lower()

    # 1) 명시적 비적재
    for pat in _NOT_STACK_PATTERNS:
        if pat.search(s_lower):
            return 0

    # 2) on top only 계열
    for pat in _TOP_ONLY_PATTERNS:
        if pat.search(s_lower):
            return 1

    # 3) 하중 표기 제거 후 숫자 후보 수집
    cleaned = _strip_weights(s_lower)
    nums = []

    for pat in (_XNUM_PAT, _PCS_PAT, _TIER_PAT, _SLASH_PAT, _NUM_PAT):
        for m in pat.finditer(cleaned):
            # _XNUM_PAT는 그룹이 2개일 수 있음 → 첫 번째 매칭된 그룹을 사용
            g = next((g for g in m.groups() if g), None)
            if g:
                try:
                    n = int(g)
                    nums.append(n)
                except Exception:
                    pass

    if nums:
        return max(nums)

    # 4) 숫자 없으면 1단
    return 1


# ------------------------------------------------------------------------------
# 벡터라이즈 헬퍼 (판다스 의존 없음: 호출부에서 apply/map로 사용)
def map_stack_status(series_like) -> "SeriesLike":
    """
    pandas Series에 바로 .map(parse_stack_status) 대신 사용할 수 있는 헬퍼.
    의존성 줄이려 타입 힌트는 느슨하게 둠.
    """
    return series_like.map(parse_stack_status)
