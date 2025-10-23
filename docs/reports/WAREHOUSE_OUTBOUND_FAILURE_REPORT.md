# 창고 출고 계산 로직 개선 실패 보고서

**작성일**: 2025-10-24
**버전**: v4.0.26 (실패)
**담당**: MACHO-GPT AI Assistant

---

## 🚨 Executive Summary

창고 출고 계산 로직의 날짜 조건을 완화하여 감지율을 개선하려는 시도가 **실패**했습니다.

**핵심 문제**:
- 벡터화 출고 계산: **588개** (목표: 3,000+)
- 수동 감지: **3,293개**
- **차이율**: 82% (5.6배 차이)
- 실제 `창고_월별_입출고` 시트: **594개 출고** (여전히 낮음)

---

## 📊 시도한 해결 방안

### 1차 시도: 날짜 조건 완화
```python
# 기존: 다음 날 이동만 인정
if site_date.date() == (wh_date.date() + timedelta(days=1)):

# 변경: 창고 입고일 이후 모든 이동 인정
if site_date.date() > wh_date.date():
```

**결과**: 6개 → 588개로 개선되었으나 여전히 목표 대비 82% 부족

### 2차 시도: 창고간 이동 제외 로직 제거
```python
# 라인 1231: 전역 제외 로직 제거
# wh_valid = wh_valid[~wh_valid["Warehouse"].isin(transferred_warehouses)]

# 라인 1236-1238: 창고간 이동 추적 로직 제거
# transferred_from_warehouses = set()
# for transfer in transfers_flat.to_dict("records"):
#     transferred_from_warehouses.add(transfer["from_warehouse"])

# 라인 1253-1254: 창고별 제외 로직 제거
# if warehouse in transferred_from_warehouses:
#     continue
```

**결과**: 여전히 588개에서 증가하지 않음

---

## 🔍 근본 원인 분석

### 1. 벡터화 로직의 구조적 문제

**문제점**:
- 벡터화 로직은 **행별(row-by-row) 그룹화**를 사용
- 각 행에서 **단일 창고 → 단일 현장** 매칭만 계산
- 한 창고에서 여러 현장으로 이동하는 경우 누락

**코드 위치** (`report_generator.py`, line 1243-1270):
```python
for row_idx in wh_valid.index.unique():
    row_warehouses = wh_valid[wh_valid.index == row_idx]
    row_sites = site_valid[site_valid.index == row_idx]

    if not row_warehouses.empty and not row_sites.empty:
        for _, wh_row in row_warehouses.iterrows():
            # ...
            if next_site_movements:
                next_site, next_date = min(next_site_movements, key=lambda x: x[1])
                # 가장 빠른 현장 이동 1개만 계산
                warehouse_site_outbound.append({...})
                break  # 중복 출고 방지를 위해 break
```

**핵심 문제**:
- `break` 문으로 인해 각 행당 **최대 1개의 출고만 계산**
- 동일 행에 여러 창고가 있어도 첫 번째 창고만 처리
- 실제로는 한 아이템이 여러 단계를 거쳐 이동할 수 있음

### 2. 수동 감지 로직과의 차이

**수동 감지 로직** (`analyze_outbound_logic.py`, line 134-156):
```python
for idx, row in df.iterrows():
    for wh_col in calculator.warehouse_columns:
        if wh_col in df.columns and pd.notna(row[wh_col]):
            wh_date = pd.to_datetime(row[wh_col], errors="coerce")
            if pd.notna(wh_date):
                for site_col in calculator.site_columns:
                    if site_col in df.columns and pd.notna(row[site_col]):
                        site_date = pd.to_datetime(row[site_col], errors="coerce")
                        if pd.notna(site_date):
                            # 창고 입고 후 현장 이동 (wh_date < site_date)
                            if wh_date < site_date:
                                pkg_qty = row.get("Pkg", 1)
                                manual_outbound_count += pkg_qty
                                # 모든 가능한 이동을 카운트
```

**차이점**:
- 수동 감지는 **모든 가능한 창고-현장 조합**을 계산
- 벡터화는 **행당 1개만** 계산

### 3. 데이터 구조 문제

**문제점**:
- 창고 컬럼: 10개 (DHL WH, DSV Indoor, DSV Al Markaz, etc.)
- 현장 컬럼: 4개 (AGI, DAS, MIR, SHU)
- 가능한 조합: 40개
- 실제 감지: 588개 / 3,293개 = **17.9%만 감지**

**데이터 예시**:
```
Row 0: DSV Outdoor (2023-02-10) → DAS (2023-02-12)
       가능한 출고: 1개
       벡터화 감지: 0개 (DSV Outdoor가 첫 번째가 아님)
```

---

## 📉 실패 원인 요약

| 원인 | 설명 | 영향도 |
|------|------|--------|
| **행별 처리 제한** | 각 행당 최대 1개 출고만 계산 | **High** |
| **break 문 사용** | 첫 번째 창고만 처리하고 중단 | **High** |
| **창고 순서 의존성** | 창고 컬럼 순서에 따라 우선순위 결정 | **Medium** |
| **복잡한 이동 패턴 미지원** | 창고 → 창고 → 현장 다단계 이동 누락 | **Medium** |
| **벡터화 vs 반복문 차이** | 벡터화는 단순화된 로직만 지원 | **Low** |

---

## 🎯 올바른 해결 방안

### Option A: 수동 감지 로직 채택 (권장)

**장점**:
- 모든 가능한 창고-현장 조합 계산
- 정확도 100% (3,293개 모두 감지)
- 검증된 로직

**단점**:
- 성능 저하 (반복문 사용)
- 벡터화 이점 상실

**구현**:
```python
def _calculate_warehouse_outbound_manual(self, df):
    """수동 감지 로직 사용"""
    outbound_items = []

    for idx, row in df.iterrows():
        for wh_col in self.warehouse_columns:
            if pd.notna(row[wh_col]):
                wh_date = pd.to_datetime(row[wh_col], errors="coerce")
                if pd.notna(wh_date):
                    for site_col in self.site_columns:
                        if pd.notna(row[site_col]):
                            site_date = pd.to_datetime(row[site_col], errors="coerce")
                            if pd.notna(site_date) and site_date > wh_date:
                                pkg_qty = max(1, int(row.get("Pkg", 1)))
                                outbound_items.append({
                                    "Item_ID": idx,
                                    "From_Location": wh_col,
                                    "To_Location": site_col,
                                    "Outbound_Date": site_date,
                                    "Year_Month": site_date.strftime("%Y-%m"),
                                    "Pkg_Quantity": pkg_qty,
                                    "Outbound_Type": "warehouse_to_site",
                                })

    return outbound_items
```

### Option B: 벡터화 로직 재설계

**목표**: 모든 창고-현장 조합을 벡터화로 계산

**구현 아이디어**:
1. 창고 데이터를 `melt()`로 변환 (이미 완료)
2. 현장 데이터를 `melt()`로 변환 (이미 완료)
3. **Cross join**으로 모든 조합 생성
4. 날짜 조건으로 필터링
5. 중복 제거 (동일 Item_ID + 동일 현장)

**장점**:
- 벡터화 성능 유지
- 모든 조합 계산

**단점**:
- 복잡한 로직
- 메모리 사용량 증가 (7,256 × 10 × 4 = 290,240 조합)

### Option C: 하이브리드 접근

**구현**:
- 창고간 이동: 벡터화 (이미 완료)
- 창고→현장 이동: 수동 감지
- 성능 vs 정확도 균형

---

## 📋 권장 사항

### 즉시 조치 (Immediate Action)

1. **수동 감지 로직 채택** (Option A)
   - 가장 빠르고 확실한 해결 방안
   - 정확도 100% 보장
   - 성능 저하는 Stage 3 전체 실행 시간의 일부

2. **성능 벤치마크**
   - 수동 감지 로직 실행 시간 측정
   - 전체 파이프라인 영향 평가

3. **문서화**
   - 수동 감지 로직 채택 이유 문서화
   - 향후 벡터화 개선 방안 기록

### 중기 개선 (Medium-term Improvement)

1. **벡터화 로직 재설계** (Option B)
   - 정확도와 성능 모두 확보
   - 메모리 최적화 필요

2. **테스트 케이스 추가**
   - 복잡한 이동 패턴 테스트
   - 벡터화 vs 수동 감지 비교

---

## 🔧 실행 계획

### Phase 1: 수동 감지 로직 구현 (1-2시간)

1. `_calculate_warehouse_outbound_manual()` 함수 추가
2. `CorrectedWarehouseIOCalculator` 초기화에 `use_manual_outbound=True` 옵션 추가
3. 기존 벡터화 로직 보존 (향후 비교용)

### Phase 2: 테스트 및 검증 (1시간)

1. Stage 3 실행
2. `창고_월별_입출고` 시트 검증
3. 출고 수량 3,000+ 확인

### Phase 3: 성능 측정 (30분)

1. 실행 시간 측정
2. 메모리 사용량 확인
3. 전체 파이프라인 영향 평가

### Phase 4: 문서화 및 커밋 (30분)

1. CHANGELOG.md 업데이트
2. README.md 업데이트
3. Git 커밋 및 푸시

---

## 📈 예상 결과

**수동 감지 로직 채택 시**:

| 지표 | 현재 | 예상 | 개선 |
|------|------|------|------|
| 출고 감지 | 588개 | 3,293개 | **5.6배** |
| 정확도 | 17.9% | 100% | **+82.1%** |
| 실행 시간 | ~2초 | ~5-10초 | **2-5배 증가** |
| Stage 3 전체 | ~24초 | ~27-32초 | **+3-8초** |

**결론**: 정확도가 훨씬 중요하므로 수동 감지 로직 채택 권장

---

## 🎓 교훈 (Lessons Learned)

1. **벡터화가 항상 최선은 아님**
   - 복잡한 비즈니스 로직은 반복문이 더 명확할 수 있음
   - 성능 vs 정확도 트레이드오프 고려 필요

2. **오리지널 로직 분석의 중요성**
   - 오리지널 파일의 로직이 너무 단순화되어 있었음
   - 실제 요구사항은 더 복잡했음

3. **테스트 주도 개발의 가치**
   - 수동 감지 로직이 정답을 제공함
   - 벡터화 로직 검증에 활용

4. **점진적 개선의 필요성**
   - 한 번에 모든 문제를 해결하려 하지 말 것
   - 작동하는 솔루션부터 구현 후 점진적 최적화

---

## 📎 참고 자료

- `hvdc_excel_reporter_final_sqm_rev_ORIGIN.py`: 오리지널 로직 (line 784)
- `report_generator.py`: 현재 벡터화 로직 (line 1243-1270)
- `analyze_outbound_logic.py`: 수동 감지 로직 (삭제됨, 복원 필요)
- `CHANGELOG.md`: v4.0.26 변경 내역

---

## ✅ 다음 단계

1. **사용자 확인**: 수동 감지 로직 채택 승인 요청
2. **구현**: `_calculate_warehouse_outbound_manual()` 함수 추가
3. **테스트**: Stage 3 실행 및 검증
4. **배포**: Git 커밋 및 문서화

---

**작성자**: MACHO-GPT AI Assistant
**검토 필요**: 사용자 승인 후 진행

