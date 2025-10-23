# 헤더 매칭 시스템 통합 가이드 (HVDC Pipeline Core Module)

## 📚 목차

1. [시스템 개요](#시스템-개요)
2. [핵심 개념](#핵심-개념)
3. [빠른 시작](#빠른-시작)
4. [스테이지별 통합 예제](#스테이지별-통합-예제)
5. [고급 사용법](#고급-사용법)
6. [문제 해결](#문제-해결)
7. [마이그레이션 가이드](#마이그레이션-가이드)

---

## 시스템 개요

### 무엇이 개선되었나요?

**기존 방식의 문제점:**
```python
# ❌ 하드코딩된 컬럼명 - 엑셀 형식이 바뀌면 코드 수정 필요
if 'Case No.' in df.columns:
    case_col = 'Case No.'
elif 'CASE NO' in df.columns:
    case_col = 'CASE NO'
else:
    raise ValueError("Case number column not found")
```

**새로운 방식의 장점:**
```python
# ✅ 의미 기반 매칭 - 엑셀 형식이 바뀌어도 자동으로 찾음
from core import find_header_by_meaning

case_col = find_header_by_meaning(df, "case_number", required=True)
# "Case No.", "CASE_NUMBER", "case-no" 등 모두 자동 인식
```

### 시스템 구조

```
core/
├── __init__.py                 # 모듈 진입점
├── header_normalizer.py        # 헤더명 정규화 (대소문자, 공백, 특수문자 처리)
├── header_detector.py          # 자동 헤더 행 탐지
├── header_registry.py          # 의미 기반 헤더 정의 (semantic mapping)
└── semantic_matcher.py         # 실제 매칭 엔진
```

---

## 핵심 개념

### 1. Semantic Key (의미 키)

코드 내부에서 사용하는 표준화된 헤더 식별자입니다.

```python
# 예시 Semantic Keys:
# - case_number    : 케이스 번호를 의미
# - eta_ata        : 도착 예정/실제 일자를 의미
# - dhl_warehouse  : DHL 창고 일자를 의미
```

### 2. Aliases (별칭)

실제 엑셀 파일에서 나타날 수 있는 모든 헤더 변형입니다.

```python
# "case_number"의 aliases:
# - "Case No.", "CASE NO", "case number", "Case_No", 
#   "CaseNo", "case-no", "케이스번호" 등
```

### 3. Normalization (정규화)

다양한 형태의 헤더명을 비교 가능한 표준 형태로 변환합니다.

```python
# 모두 "casenumber"로 정규화됨:
"Case No."  → "casenumber"
"CASE_NO"   → "casenumber"
"case-no"   → "casenumber"
"  Case  Number  " → "casenumber"
```

### 4. Confidence Score (신뢰도)

매칭 결과의 정확도를 나타냅니다 (0.0 ~ 1.0).

- **1.0 (Exact)**: 정규화된 이름이 정확히 일치
- **0.7-0.9 (Partial)**: 부분 일치 (예: "caseno" vs "casenumber")
- **< 0.7**: 신뢰도 낮음, 수동 확인 필요

---

## 빠른 시작

### 기본 사용법

```python
from core import find_header_by_meaning
import pandas as pd

# 엑셀 파일 읽기
df = pd.read_excel("data.xlsx")

# 필요한 컬럼 찾기
case_col = find_header_by_meaning(df, "case_number", required=True)
eta_col = find_header_by_meaning(df, "eta_ata")
desc_col = find_header_by_meaning(df, "description")

# 찾은 컬럼으로 데이터 접근
print(df[case_col].head())
```

### 여러 컬럼 한번에 찾기

```python
from core import SemanticMatcher

matcher = SemanticMatcher()

# 필요한 semantic keys 정의
semantic_keys = [
    "case_number",
    "description", 
    "eta_ata",
    "dhl_warehouse",
    "dsv_indoor"
]

# 한번에 매칭
report = matcher.match_dataframe(df, semantic_keys)

# 결과 확인
report.print_summary()

# 각 컬럼 가져오기
case_col = report.get_column_name("case_number")
eta_col = report.get_column_name("eta_ata")
```

### 자동 헤더 행 탐지

```python
from core import detect_header_row
import pandas as pd

# 헤더가 몇 번째 행에 있는지 자동 탐지
header_row, confidence = detect_header_row("data.xlsx")

print(f"헤더는 {header_row}번째 행에 있습니다 (신뢰도: {confidence:.0%})")

# 올바른 헤더 행으로 다시 읽기
df = pd.read_excel("data.xlsx", header=header_row)
```

---

## 스테이지별 통합 예제

### Stage 1: Data Synchronizer

**기존 코드 (하드코딩):**
```python
# ❌ 문제: 컬럼명이 바뀌면 코드 수정 필요
def _case_col(self, df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if "case" in str(col).lower():
            return col
    return None
```

**개선된 코드 (의미 기반):**
```python
from core import find_header_by_meaning

# ✅ 해결: 어떤 형태로 써도 자동 인식
def _case_col(self, df: pd.DataFrame) -> Optional[str]:
    return find_header_by_meaning(df, "case_number", required=False)
```

**완전한 통합 예제:**
```python
from core import SemanticMatcher
import pandas as pd

class DataSynchronizerV30:
    def __init__(self):
        # 의미 기반 매칭 엔진 초기화
        self.matcher = SemanticMatcher()
        
        # 이 스테이지에서 필요한 semantic keys
        self.required_keys = [
            "case_number",
            "item_number",
        ]
        
        self.date_keys = [
            "etd_atd",
            "eta_ata", 
            "dhl_warehouse",
            "dsv_indoor",
            "dsv_outdoor",
            # ... 등
        ]
    
    def load_and_match_headers(self, file_path: str):
        """파일을 로드하고 필요한 헤더를 모두 찾습니다."""
        
        # 엑셀 파일 읽기 (헤더 자동 탐지)
        from core import detect_header_row
        
        header_row, conf = detect_header_row(file_path)
        df = pd.read_excel(file_path, header=header_row)
        
        # 필요한 모든 헤더 한번에 매칭
        all_keys = self.required_keys + self.date_keys
        report = self.matcher.match_dataframe(df, all_keys)
        
        # 필수 헤더 검증
        for key in self.required_keys:
            if not report.get_column_name(key):
                raise ValueError(f"필수 헤더 '{key}'를 찾을 수 없습니다")
        
        # 매칭 결과 출력 (디버깅용)
        report.print_summary()
        
        return df, report
    
    def synchronize(self, master_file: str, warehouse_file: str):
        """마스터와 창고 데이터를 동기화합니다."""
        
        # 파일 로드 및 헤더 매칭
        master_df, master_report = self.load_and_match_headers(master_file)
        wh_df, wh_report = self.load_and_match_headers(warehouse_file)
        
        # 매칭된 컬럼명으로 작업
        master_case_col = master_report.get_column_name("case_number")
        wh_case_col = wh_report.get_column_name("case_number")
        
        # 동기화 로직 실행
        for idx, row in master_df.iterrows():
            case_no = row[master_case_col]
            
            # Date keys 처리
            for semantic_key in self.date_keys:
                master_col = master_report.get_column_name(semantic_key)
                wh_col = wh_report.get_column_name(semantic_key)
                
                if master_col and wh_col:
                    # 실제 컬럼명으로 데이터 접근
                    master_value = row[master_col]
                    # ... 동기화 로직 ...
```

### Stage 2: Derived Columns

**개선된 코드:**
```python
from core import SemanticMatcher, HVDC_HEADER_REGISTRY
import pandas as pd

class DerivedColumnsProcessorV2:
    def __init__(self):
        self.matcher = SemanticMatcher()
        
        # Registry에서 창고/사이트 컬럼 목록 가져오기
        from core.header_registry import HeaderCategory
        
        warehouse_defs = HVDC_HEADER_REGISTRY.get_by_category(
            HeaderCategory.LOCATION
        )
        
        self.warehouse_keys = [
            d.semantic_key for d in warehouse_defs 
            if 'warehouse' in d.description.lower() or 'storage' in d.description.lower()
        ]
        
        self.site_keys = [
            d.semantic_key for d in warehouse_defs
            if 'site' in d.description.lower() or d.semantic_key in ['mir', 'shu', 'agi', 'das']
        ]
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """파생 컬럼을 계산합니다."""
        
        # 필요한 모든 location 헤더 찾기
        location_keys = self.warehouse_keys + self.site_keys
        report = self.matcher.match_dataframe(df, location_keys)
        
        # Status_WAREHOUSE 계산
        warehouse_cols = [
            report.get_column_name(key) 
            for key in self.warehouse_keys
            if report.get_column_name(key)
        ]
        
        df['Status_WAREHOUSE'] = df[warehouse_cols].apply(
            self._find_latest_date, axis=1
        )
        
        # Status_SITE 계산
        site_cols = [
            report.get_column_name(key)
            for key in self.site_keys
            if report.get_column_name(key)
        ]
        
        df['Status_SITE'] = df[site_cols].apply(
            self._find_latest_date, axis=1
        )
        
        return df
```

### Stage 3 & 4: Report & Anomaly Detection

**개선된 코드:**
```python
from core import SemanticMatcher
import pandas as pd

class ReportGeneratorV2:
    def __init__(self):
        self.matcher = SemanticMatcher()
    
    def generate_report(self, input_file: str, output_file: str):
        """보고서를 생성합니다."""
        
        # 데이터 로드 및 헤더 매칭
        from core import detect_header_row
        
        header_row, _ = detect_header_row(input_file)
        df = pd.read_excel(input_file, header=header_row)
        
        # 필요한 모든 컬럼 매칭
        required_keys = [
            "case_number",
            "description",
            "status_current",
            "status_location",
            # ... 등
        ]
        
        report = self.matcher.match_dataframe(df, required_keys)
        
        # 매칭 실패한 필수 컬럼 확인
        missing = [k for k in required_keys if not report.get_column_name(k)]
        if missing:
            print(f"경고: 다음 컬럼을 찾을 수 없습니다: {missing}")
        
        # 보고서 생성 로직
        # ...
```

---

## 고급 사용법

### 1. 커스텀 Registry 정의

```python
from core import HeaderRegistry, HeaderDefinition, HeaderCategory

# 새로운 레지스트리 생성
custom_registry = HeaderRegistry()

# 커스텀 헤더 정의 추가
custom_registry.register(HeaderDefinition(
    semantic_key="my_custom_field",
    category=HeaderCategory.METADATA,
    aliases=[
        "Custom Field",
        "CustomField",
        "custom_field",
        "맞춤필드"
    ],
    description="프로젝트별 커스텀 필드",
    required=False,
    data_type="str"
))

# 커스텀 레지스트리로 매칭
from core import SemanticMatcher
matcher = SemanticMatcher(registry=custom_registry)
```

### 2. 매칭 신뢰도 조정

```python
from core import SemanticMatcher

# 낮은 신뢰도도 허용 (더 관대한 매칭)
relaxed_matcher = SemanticMatcher(
    min_confidence=0.5,    # 기본값: 0.7
    allow_partial=True     # 부분 매칭 허용
)

# 높은 신뢰도만 허용 (엄격한 매칭)
strict_matcher = SemanticMatcher(
    min_confidence=0.9,
    allow_partial=False    # 정확한 매칭만
)
```

### 3. 매칭 결과 분석

```python
from core import SemanticMatcher

matcher = SemanticMatcher()
report = matcher.match_dataframe(df, semantic_keys)

# 상세 리포트 출력
report.print_summary()

# 개별 매칭 결과 확인
for result in report.results:
    print(f"Key: {result.semantic_key}")
    print(f"  Matched: {result.matched}")
    print(f"  Column: {result.column_name}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Match Type: {result.match_type}")
    
    if result.alternatives:
        print(f"  Alternatives:")
        for alt_col, alt_score in result.alternatives:
            print(f"    - {alt_col} ({alt_score:.1%})")
```

### 4. 헤더 위치 검증

```python
from core import HeaderDetector

# 예상되는 컬럼 목록으로 검증
detector = HeaderDetector()
expected_columns = ["Case No", "Description", "ETA"]

header_row, confidence = detector.detect_with_column_names(
    df, 
    expected_columns
)

if confidence < 0.8:
    print(f"경고: 헤더 탐지 신뢰도가 낮습니다 ({confidence:.0%})")
    print(f"행 {header_row}가 헤더인지 수동으로 확인하세요")
```

---

## 문제 해결

### 문제 1: 필요한 컬럼을 찾을 수 없음

**증상:**
```
ValueError: Required column 'case_number' not found in DataFrame
```

**해결 방법:**

1. **사용 가능한 컬럼 확인:**
```python
print("Available columns:", df.columns.tolist())
```

2. **매칭 리포트 확인:**
```python
report = matcher.match_dataframe(df, ["case_number"])
report.print_summary()
```

3. **Registry에 새 별칭 추가:**
```python
# core/header_registry.py 파일 수정
# "case_number"의 aliases에 새로운 변형 추가
aliases=[
    # ... 기존 별칭들 ...
    "Your New Column Name",  # 새로 추가
]
```

### 문제 2: 잘못된 컬럼이 매칭됨

**증상:**
```
# "description"을 찾으려 했는데 "descriptor"가 매칭됨
```

**해결 방법:**

1. **신뢰도 임계값 높이기:**
```python
strict_matcher = SemanticMatcher(min_confidence=0.9)
```

2. **부분 매칭 비활성화:**
```python
exact_matcher = SemanticMatcher(allow_partial=False)
```

3. **명시적 우선순위 설정:**
```python
# Registry에서 더 정확한 별칭을 앞에 배치
aliases=[
    "Description",        # 정확한 매칭 (우선순위 높음)
    "Desc",
    "Detail",            # 부분 매칭 (우선순위 낮음)
]
```

### 문제 3: 헤더가 자동 탐지되지 않음

**증상:**
```
# detect_header_row가 잘못된 행을 반환함
```

**해결 방법:**

1. **수동으로 헤더 행 지정:**
```python
# 자동 탐지 대신 알려진 헤더 행 사용
df = pd.read_excel("data.xlsx", header=2)  # 3번째 행이 헤더
```

2. **탐지 범위 확대:**
```python
from core import HeaderDetector

detector = HeaderDetector(
    max_search_rows=50,    # 기본값: 20
    min_confidence=0.6     # 기본값: 0.7
)

header_row, conf = detector.detect_from_file("data.xlsx")
```

3. **예상 컬럼으로 검증:**
```python
expected = ["Case No", "ETA", "Description"]
header_row, conf = detect_header_row(
    "data.xlsx", 
    expected_columns=expected
)
```

---

## 마이그레이션 가이드

### 기존 코드를 새 시스템으로 마이그레이션하기

#### Step 1: Core 모듈 Import 추가

```python
# 파일 상단에 추가
from core import (
    find_header_by_meaning,
    SemanticMatcher,
    detect_header_row,
    HVDC_HEADER_REGISTRY
)
```

#### Step 2: 하드코딩된 컬럼명 찾기

검색 패턴:
- `if 'Case No' in df.columns:`
- `df['Case No.']`
- `for col in ['Case No', 'CASE_NUMBER']:`

#### Step 3: 의미 기반 매칭으로 교체

**변경 전:**
```python
# 하드코딩된 방식
case_col = 'Case No.'
if case_col not in df.columns:
    case_col = 'CASE_NUMBER'
if case_col not in df.columns:
    raise ValueError("Case column not found")

data = df[case_col]
```

**변경 후:**
```python
# 의미 기반 방식
case_col = find_header_by_meaning(df, "case_number", required=True)
data = df[case_col]
```

#### Step 4: 컬럼명 리스트 통합

**변경 전:**
```python
DATE_COLUMNS = [
    "ETD/ATD",
    "ETA/ATA", 
    "DHL Warehouse",
    # ...
]

for col in DATE_COLUMNS:
    if col in df.columns:
        # 처리...
```

**변경 후:**
```python
# Semantic keys 사용
date_keys = [
    "etd_atd",
    "eta_ata",
    "dhl_warehouse",
    # ...
]

matcher = SemanticMatcher()
report = matcher.match_dataframe(df, date_keys)

for key in date_keys:
    col = report.get_column_name(key)
    if col:
        # 처리...
```

#### Step 5: 테스트

```python
# 다양한 엑셀 형식으로 테스트
test_files = [
    "data_standard.xlsx",      # 표준 형식
    "data_uppercase.xlsx",     # 대문자
    "data_underscores.xlsx",   # 언더스코어
    "data_spaces.xlsx",        # 공백
]

for file in test_files:
    try:
        df = pd.read_excel(file)
        report = matcher.match_dataframe(df, required_keys)
        print(f"✓ {file}: {report.successful_matches}/{len(required_keys)} matched")
    except Exception as e:
        print(f"✗ {file}: {e}")
```

---

## 추가 리소스

### 관련 파일

- `core/__init__.py` - 모듈 진입점
- `core/header_normalizer.py` - 정규화 로직
- `core/header_detector.py` - 자동 탐지 로직
- `core/header_registry.py` - 의미 정의
- `core/semantic_matcher.py` - 매칭 엔진

### 테스트 실행

```bash
# 각 모듈 개별 테스트
python -m core.header_normalizer
python -m core.header_detector
python -m core.header_registry
python -m core.semantic_matcher
```

### 새로운 헤더 추가하기

1. `core/header_registry.py` 파일 열기
2. `_initialize_definitions()` 메소드 찾기
3. 적절한 카테고리에 `HeaderDefinition` 추가:

```python
self.register(HeaderDefinition(
    semantic_key="my_new_field",
    category=HeaderCategory.METADATA,
    aliases=[
        "My Field",
        "MY_FIELD",
        "my_field",
        "MyField"
    ],
    description="설명",
    required=False,
    data_type="str"
))
```

---

## 요약

### 핵심 장점

1. **Zero Hardcoding** - 컬럼명을 코드에 직접 쓰지 않음
2. **자동 적응** - 다양한 엑셀 형식을 자동으로 인식
3. **중앙 관리** - 모든 헤더 정의가 Registry에 집중
4. **유지보수 용이** - 새 형식 추가 시 Registry만 수정
5. **강력한 매칭** - 대소문자, 공백, 특수문자 모두 처리

### 사용 흐름

```
1. 엑셀 파일 로드
   ↓
2. 헤더 행 자동 탐지 (detect_header_row)
   ↓
3. 필요한 컬럼 정의 (semantic keys)
   ↓
4. 의미 기반 매칭 (SemanticMatcher)
   ↓
5. 매칭된 실제 컬럼명으로 작업
```

이 시스템을 사용하면 **엑셀 형식이 바뀌어도 코드 수정 없이** 파이프라인이 계속 작동합니다!
