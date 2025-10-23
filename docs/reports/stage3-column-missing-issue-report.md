# Stage 3 Total sqm 및 Stack_Status 컬럼 누락 문제 보고서

**작성일**: 2025-10-23
**버전**: v4.0.22
**작성자**: MACHO-GPT v3.4-mini

## 📋 Executive Summary

Stage 3 실행 시 `Stack_Status`와 `Total sqm` 컬럼이 DataFrame에는 정상적으로 추가되지만, 최종 Excel 출력 파일에는 누락되는 문제가 발생했습니다. 이는 Excel 저장 과정에서 2개 컬럼이 잘리는 현상으로 확인되었습니다.

## 🔍 문제 진단

### 1. 증상
- **DataFrame 상태**: 66개 컬럼 (Total sqm, Stack_Status 포함) ✅
- **Excel 출력**: 64개 컬럼 (Total sqm, Stack_Status 누락) ❌
- **누락 컬럼**: `Total sqm` (53번째), `Stack_Status` (52번째)

### 2. 원인 분석

#### 2.1 DataFrame 처리 과정
```python
# report_generator.py 3370-3377줄
combined_normalized["Stack_Status"] = _calculate_stack_status(combined_normalized, "Stack")
combined_normalized["Total sqm"] = _calculate_total_sqm(combined_normalized)

# 디버그 로그 확인
# - 컬럼 추가 후: 66개 컬럼, Total sqm/Stack_Status 존재 ✅
# - 재정렬 후: 66개 컬럼, Total sqm/Stack_Status 유지 ✅
# - Excel 저장 전: 66개 컬럼, Total sqm/Stack_Status 존재 ✅
```

#### 2.2 Excel 저장 과정
```python
# report_generator.py 3481줄
combined_reordered.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)

# 디버그 로그 확인
# - Excel 저장 시도: 66개 컬럼 ✅
# - Excel 저장 완료: 성공 메시지 ✅
# - 하지만 실제 파일: 64개 컬럼만 저장됨 ❌
```

### 3. 가능한 원인

#### 3.1 Excel 저장 시 컬럼 제한
- **가설**: Excel 저장 시 컬럼 수 제한 (64개) 또는 특정 컬럼명 문제
- **증거**: DataFrame 66개 → Excel 64개 (2개 누락)

#### 3.2 컬럼명 문제
- **가설**: `Total sqm` (공백 포함) 또는 `Stack_Status` 컬럼명이 Excel 저장 시 문제 발생
- **증거**: 컬럼명에 특수문자나 공백이 포함됨

#### 3.3 Excel Writer 문제
- **가설**: `pd.ExcelWriter`에서 특정 컬럼을 자동으로 제외
- **증거**: 저장 과정에서 오류 없이 완료되지만 컬럼 누락

## 🔧 시도한 해결 방법

### 1. 디버그 로깅 추가
```python
# report_generator.py에 추가된 디버그 코드
logger.info(f"[DEBUG] Excel 저장 전 최종 컬럼 검증:")
logger.info(f"  - combined_reordered 컬럼 수: {len(combined_reordered.columns)}")
logger.info(f"  - Total sqm 존재: {'Total sqm' in combined_reordered.columns}")
logger.info(f"  - Stack_Status 존재: {'Stack_Status' in combined_reordered.columns}")
logger.info(f"  - Total sqm 위치: {list(combined_reordered.columns).index('Total sqm')}")
logger.info(f"  - Stack_Status 위치: {list(combined_reordered.columns).index('Stack_Status')}")
```

### 2. Excel 저장 오류 처리
```python
# report_generator.py에 추가된 오류 처리
try:
    combined_reordered.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)
    logger.info("[SUCCESS] Excel 저장 완료")
except Exception as e:
    logger.error(f"[ERROR] Excel 저장 실패: {e}")
    # 컬럼명을 안전하게 변경하여 재시도
    safe_df = combined_reordered.copy()
    safe_df.columns = [str(col).replace(' ', '_').replace('.', '_') for col in safe_df.columns]
    safe_df.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)
```

### 3. 컬럼 위치 확인
```python
# 52-54번째 컬럼 확인
# DataFrame: ['final handling', 'Stack_Status', 'Total sqm', 'Vendor']
# Excel 파일: ['final handling', 'SQM', 'Vendor']
# → Stack_Status와 Total sqm이 SQM으로 대체됨
```

## 📊 테스트 결과

### 1. Stage 3 실행 결과
```
[DEBUG] Excel 저장 전 최종 컬럼 검증:
  - combined_reordered 컬럼 수: 66
  - Total sqm 존재: True
  - Stack_Status 존재: True
  - Total sqm 위치: 53
  - Stack_Status 위치: 52

[DEBUG] Excel 저장 시도: 66개 컬럼
[SUCCESS] Excel 저장 완료

[DEBUG] Excel 저장 후 검증:
  - combined_reordered 컬럼 수: 66
  - 'Total sqm' 존재: True
  - 'Stack_Status' 존재: True
```

### 2. Excel 파일 검증 결과
```python
# 새로 생성된 파일 확인
Total columns: 64
Has Total sqm: False
Has Stack_Status: False
Column 52-54: ['final handling', 'SQM', 'Vendor']
```

## 🚨 핵심 문제

**DataFrame과 Excel 파일 간의 불일치**:
- DataFrame에는 66개 컬럼이 존재
- Excel 파일에는 64개 컬럼만 저장됨
- `Total sqm`과 `Stack_Status` 컬럼이 Excel 저장 과정에서 누락됨

## 💡 추천 해결 방안

### 1. Excel 저장 방식 변경
```python
# 현재 방식
combined_reordered.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)

# 개선된 방식
combined_reordered.to_excel(
    writer,
    sheet_name="통합_원본데이터_Fixed",
    index=False,
    engine='openpyxl'  # 명시적 엔진 지정
)
```

### 2. 컬럼명 안전화
```python
# 컬럼명을 Excel 호환 형식으로 변경
safe_columns = []
for col in combined_reordered.columns:
    safe_col = str(col).replace(' ', '_').replace('.', '_').replace('(', '').replace(')', '')
    safe_columns.append(safe_col)
combined_reordered.columns = safe_columns
```

### 3. Excel 저장 후 검증
```python
# Excel 저장 후 실제 파일을 다시 읽어서 검증
saved_df = pd.read_excel(excel_file, sheet_name="통합_원본데이터_Fixed")
if 'Total_sqm' not in saved_df.columns or 'Stack_Status' not in saved_df.columns:
    logger.error("Excel 저장 후 컬럼 누락 감지!")
    # 재시도 로직
```

## 📈 영향도 분석

### 1. 기능적 영향
- **심각도**: HIGH
- **영향**: Stage 3 출력에서 `Total sqm`과 `Stack_Status` 정보 누락
- **사용자 영향**: 창고 적재 효율 분석 불가능

### 2. 데이터 무결성
- **DataFrame**: 정상 (66개 컬럼)
- **Excel 출력**: 불완전 (64개 컬럼)
- **일관성**: DataFrame과 Excel 간 불일치

## 🔄 다음 단계

### 1. 즉시 조치
1. Excel 저장 방식 변경 (엔진 명시)
2. 컬럼명 안전화 적용
3. 저장 후 검증 로직 추가

### 2. 장기 개선
1. Excel 저장 과정 모니터링 강화
2. 컬럼 누락 자동 감지 및 복구
3. 테스트 케이스 추가

## 📝 결론

Stage 3에서 `Total sqm`과 `Stack_Status` 컬럼이 DataFrame에는 정상적으로 추가되지만, Excel 저장 과정에서 누락되는 문제가 확인되었습니다. 이는 Excel 저장 시 컬럼 제한이나 컬럼명 문제로 추정되며, 저장 방식 변경과 컬럼명 안전화를 통해 해결할 수 있을 것으로 판단됩니다.

**우선순위**: HIGH
**예상 해결 시간**: 2-4시간
**필요 리소스**: 개발자 1명, 테스트 환경
