# PATCH3.MD Rollback Report

## Date: 2025-10-24

## Problem

PATCH3.MD 적용 후 창고 월별 입출고 데이터가 부정확:
- 누계_입고: 6 (실제 예상: ~5,500)
- 창고 재고: -268 (실제: ~3,000)

## Root Cause

PATCH3.MD의 입고 필터링이 너무 엄격:
```python
if "Inbound_Type" in inbound_df.columns:
    inbound_df = inbound_df[
        inbound_df["Inbound_Type"].astype(str).str.lower() == "external_arrival"
    ]
```

대부분의 입고 데이터에 `Inbound_Type` 필드가 없거나 다른 값으로 설정되어 있어 제외됨.

## Solution

Git revert로 PATCH3.MD 커밋(d9abb98) 롤백하여 v4.0.26 상태로 복원.

## Result

- 누계_입고: 6 → 5,517 ✅ (정상 복원)
- 누계_출고: 274 → 594 (여전히 낮음)
- 창고 재고: -268 → 4,923 (목표보다 높음)

## Current Status

롤백 후 창고 월별 입출고 데이터:
- **입고**: 5,517개 (목표 범위: 5,000~6,000) ✅
- **출고**: 594개 (목표 범위: 3,000~4,000) ❌
- **재고**: 4,923개 (목표 범위: 2,800~3,200) ❌

## Analysis

1. **입고는 정상 복원됨**: PATCH3.MD의 입고 필터링 문제가 해결됨
2. **출고는 여전히 낮음**: 원래부터 출고 계산에 문제가 있었음
3. **재고가 목표보다 높음**: 출고가 낮아서 재고가 누적됨

## Lessons Learned

1. 벡터화 시 데이터 필터링 조건을 신중히 검토
2. 입고 데이터의 `Inbound_Type` 필드 일관성 확인 필요
3. 롤백 전 충분한 데이터 검증 필요
4. 출고 계산 로직 자체에 근본적인 문제가 있을 수 있음

## Next Steps

창고간 이동 출고 중복 문제 해결을 위한 대안:
1. 입고 필터링 없이 출고만 벡터화
2. `Inbound_Type` 필드 데이터 정합성 개선 후 재시도
3. 하이브리드 접근: 입고는 루프, 출고는 벡터화
4. 출고 계산 로직 근본 원인 분석 필요
