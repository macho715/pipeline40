# 헤더 순서 표준화 가이드 (유연한 검색 기능)

## 개요

Stage 2와 Stage 3 출력 파일의 헤더 순서를 통일하여 데이터 분석 및 비교 작업의 일관성을 확보합니다.
기존 core 로직(HeaderNormalizer, HeaderRegistry, SemanticMatcher)을 활용한 **유연한 헤더 검색 기능**을 통해
다양한 헤더 변형을 자동으로 매칭하고 정렬합니다.

## 주요 특징

### 🔍 유연한 헤더 검색
- **정확 매칭**: 정확히 일치하는 헤더 우선 매칭
- **정규화 매칭**: HeaderNormalizer를 사용한 정규화된 이름 매칭
- **의미론적 매칭**: SemanticMatcher를 활용한 의미적 유사성 매칭
- **유사도 매칭**: SequenceMatcher를 사용한 문자열 유사도 기반 매칭

### 🎯 자동 헤더 변형 감지
- 공백 및 특수문자 변형 자동 처리
- 대소문자 변형 자동 처리
- 부분 일치 보너스 적용
- 헤더 변형 패턴 자동 감지 및 보고

### 📊 호환성 분석
- 헤더 매칭률 실시간 계산
- 매칭되지 않은 컬럼 자동 감지
- 권장사항 자동 생성
- 상세한 분석 리포트 제공

## 표준 헤더 순서 (64개 컬럼)

### 기본 정보 (1-9)
1. no.
2. Shipment Invoice No.
3. HVDC CODE (Stage 3에서 추가)
4. Site
5. EQ No
6. Case No.
7. Pkg
8. Storage
9. Description

### 치수 정보 (10-16)
10. L(CM)
11. W(CM)
12. H(CM)
13. CBM
14. N.W(kgs)
15. G.W(kgs)
16. Stack

### 무역/운송 정보 (17-25)
17. HS Code
18. Currency
19. Price
20. Vessel
21. COE
22. POL
23. POD
24. ETD/ATD
25. ETA/ATA

### 창고 정보 (26-35)
26. DHL WH
27. DSV Indoor
28. DSV Al Markaz
29. Hauler Indoor
30. DSV Outdoor
31. DSV MZP
32. HAULER
33. JDN MZD
34. MOSB
35. AAA Storage

### 추가 작업/현장 (36-41)
36. Shifting
37. MIR (현장)
38. SHU (현장)
39. AGI (현장)
40. DAS (현장)
41. Source_Sheet

### 상태 정보 (42-47)
42. Status_WAREHOUSE
43. Status_SITE
44. Status_Current
45. Status_Location
46. Status_Location_Date
47. Status_Storage

### Handling 정보 (48-52)
48. wh_handling_legacy (Stage 3) / wh handling (Stage 2)
49. site handling (공백 1개, Stage 3) / site  handling (공백 2개, Stage 2)
50. total handling
51. minus
52. final handling

### 계산 컬럼 (53-54)
53. SQM (Stage 2에서 계산)
54. Stack_Status (Stage 2에서 계산)

### Stage 3 추가 컬럼 (55-63)
55. Vendor
56. Source_File
57. Status_Location_YearMonth
58. site_handling_original
59. total_handling_original
60. wh_handling_original
61. FLOW_CODE
62. FLOW_DESCRIPTION
63. Final_Location

### 파생 정보 (64)
64. 입고일자

## 사용 방법

### Stage 2에서 사용
```python
from core.standard_header_order import (
    reorder_dataframe_columns,
    normalize_header_names_for_stage2,
    analyze_header_compatibility
)

# 헤더명 정규화
df = normalize_header_names_for_stage2(df)

# 헤더 호환성 분석
compatibility = analyze_header_compatibility(df, is_stage2=True)
print(f"매칭률: {compatibility['matching_rate']:.1f}%")

# 표준 순서로 재정렬 (유연한 검색)
df = reorder_dataframe_columns(df, is_stage2=True, use_semantic_matching=True)
```

### Stage 3에서 사용
```python
from core.standard_header_order import (
    reorder_dataframe_columns,
    normalize_header_names_for_stage3,
    analyze_header_compatibility
)

# 헤더명 정규화
df = normalize_header_names_for_stage3(df)

# 헤더 호환성 분석
compatibility = analyze_header_compatibility(df, is_stage2=False)
print(f"매칭률: {compatibility['matching_rate']:.1f}%")

# 표준 순서로 재정렬 (유연한 검색)
df = reorder_dataframe_columns(df, is_stage2=False, use_semantic_matching=True)
```

## 유연한 검색 기능 상세

### 1. FlexibleHeaderMatcher 클래스

```python
class FlexibleHeaderMatcher:
    """유연한 헤더 매칭 클래스"""

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """두 문자열의 유사도를 계산 (0.0 ~ 1.0)"""

    def find_best_match(self, target_header: str, candidate_headers: List[str]) -> Optional[Tuple[str, float]]:
        """대상 헤더에 대한 최적 매칭을 찾습니다"""

    def semantic_match(self, header_name: str, standard_headers: List[str]) -> Optional[str]:
        """의미론적 매칭을 사용하여 헤더를 찾습니다"""
```

### 2. HeaderOrderManager 클래스

```python
class HeaderOrderManager:
    """헤더 순서 관리 클래스"""

    def match_columns_to_standard(self, current_columns: List[str], standard_order: List[str]) -> Dict[str, str]:
        """현재 컬럼들을 표준 헤더와 매칭 (유연한 검색)"""

    def reorder_dataframe(self, df: pd.DataFrame, is_stage2: bool = False, use_semantic_matching: bool = True) -> pd.DataFrame:
        """DataFrame의 컬럼을 표준 순서로 재정렬 (유연한 검색)"""

    def detect_header_variations(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """DataFrame의 헤더 변형을 감지합니다"""
```

### 3. 매칭 전략

1. **정확 매칭** (우선순위 1)
   - 정확히 일치하는 헤더명 매칭
   - 대소문자 구분

2. **정규화 매칭** (우선순위 2)
   - HeaderNormalizer를 사용한 정규화
   - 공백 정리, 약어 확장

3. **의미론적 매칭** (우선순위 3)
   - SemanticMatcher를 활용한 의미적 유사성
   - 도메인 지식 기반 매칭

4. **유사도 매칭** (우선순위 4)
   - SequenceMatcher를 사용한 문자열 유사도
   - 70% 이상 유사한 경우 매칭

## 주의사항

### 1. 헤더명 차이
Stage 2와 Stage 3 간 일부 헤더명이 다름:
- "No" → "no."
- "wh handling" → "wh_handling_legacy"
- "site  handling" (공백 2개) → "site handling" (공백 1개)

### 2. Stage 전용 컬럼
- **Stage 2 전용**: SCT Ref.No, no (소문자)
- **Stage 3 전용**: HVDC CODE, Vendor, Source_File, FLOW_CODE, FLOW_DESCRIPTION, Final_Location, 입고일자

### 3. SQM 및 Stack_Status
- Stage 2에서 계산되어야 하며, Stage 3에서는 이를 그대로 사용
- 자동 검증 기능으로 존재 여부 및 데이터 품질 확인

### 4. 유연한 검색 설정
```python
# 의미론적 매칭 사용 (기본값: True)
df = reorder_dataframe_columns(df, is_stage2=True, use_semantic_matching=True)

# 매칭되지 않은 컬럼을 끝에 추가 (기본값: True)
df = reorder_dataframe_columns(df, is_stage2=True, keep_unlisted=True)
```

## 기술적 세부사항

### 1. 기존 core 로직 활용
- **HeaderNormalizer**: 헤더명 정규화 및 약어 확장
- **HeaderRegistry**: 의미론적 헤더 정의 및 매칭
- **SemanticMatcher**: 의미적 유사성 계산

### 2. 유사도 계산 알고리즘
```python
def calculate_similarity(self, str1: str, str2: str) -> float:
    # 1. 정확 일치 (1.0)
    if norm1 == norm2:
        return 1.0

    # 2. 대소문자 무시 일치 (0.95)
    if norm1.lower() == norm2.lower():
        return 0.95

    # 3. SequenceMatcher 유사도
    similarity = SequenceMatcher(None, norm1.lower(), norm2.lower()).ratio()

    # 4. 부분 일치 보너스 (0.8)
    if norm1.lower() in norm2.lower() or norm2.lower() in norm1.lower():
        similarity = max(similarity, 0.8)

    return similarity
```

### 3. 매칭 결과 로깅
```python
logger.info(f"헤더 매칭 완료: {total_mapped}/{total_current}개 ({mapping_rate:.1f}%)")
logger.debug(f"헤더 매칭: '{target_header}' → '{matched_header}' (유사도: {similarity:.3f})")
```

## 성능 최적화

### 1. 매칭 순서 최적화
- 정확 매칭을 먼저 수행하여 빠른 처리
- 정규화 매칭으로 대부분의 케이스 해결
- 의미론적 매칭은 선택적 사용

### 2. 캐싱 전략
- HeaderNormalizer 결과 캐싱
- 매칭 결과 캐싱
- 싱글톤 패턴으로 인스턴스 재사용

### 3. 메모리 효율성
- 대용량 DataFrame 처리 시 청크 단위 처리
- 불필요한 복사본 생성 최소화

## 문제 해결

### 1. 매칭률이 낮은 경우
```python
compatibility = analyze_header_compatibility(df, is_stage2=True)
if compatibility['matching_rate'] < 80:
    print("권장사항:")
    for rec in compatibility['recommendations']:
        print(f"  - {rec}")
```

### 2. 헤더 변형 감지
```python
variations = manager.detect_header_variations(df)
for standard_header, found_variations in variations.items():
    print(f"{standard_header}: {found_variations}")
```

### 3. 디버깅 모드 활성화
```python
import logging
logging.getLogger('core.standard_header_order').setLevel(logging.DEBUG)
```

## 업데이트 이력

### v1.0 (2025-01-24)
- 기본 헤더 순서 표준화 기능 구현
- Stage 2/3 간 헤더명 차이 처리
- SQM/Stack_Status 검증 기능

### v2.0 (2025-01-24) - 현재
- 유연한 헤더 검색 기능 추가
- 기존 core 로직 통합 (HeaderNormalizer, HeaderRegistry, SemanticMatcher)
- 호환성 분석 및 권장사항 자동 생성
- 상세한 로깅 및 디버깅 지원

## 관련 파일

- `4.0.0/scripts/core/standard_header_order.py`: 메인 구현 파일
- `4.0.0/scripts/stage2_derived/derived_columns_processor.py`: Stage 2 통합
- `4.0.0/scripts/stage3_report/report_generator.py`: Stage 3 통합
- `4.0.0/scripts/core/header_normalizer.py`: 헤더 정규화 로직
- `4.0.0/scripts/core/header_registry.py`: 헤더 레지스트리
- `4.0.0/scripts/core/semantic_matcher.py`: 의미론적 매칭 로직
