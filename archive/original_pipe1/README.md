# pipe1 - 데이터 동기화 및 Post-AGI 컬럼 처리

**HVDC 파이프라인 1-2단계 처리 모듈**

---

## 📋 개요

`pipe1` 폴더는 HVDC 파이프라인의 1-2단계를 담당합니다:
1. **데이터 동기화**: Master 파일과 Warehouse 파일 간 동기화
2. **Post-AGI 컬럼 처리**: AGI 이후 13개 컬럼 자동 계산

---

## 📁 파일 구조

```
pipe1/
├── data_synchronizer_v29.py          # 데이터 동기화 메인 스크립트
├── post_agi_column_processor.py      # Post-AGI 컬럼 처리 스크립트
├── CASE LIST.xlsx                    # Master 파일 (입력)
├── HVDC WAREHOUSE_HITACHI(HE).xlsx  # Warehouse 파일 (입력/출력)
├── HVDC WAREHOUSE_HITACHI(HE).synced.xlsx  # 동기화 결과 (중간)
├── DATA_SYNCHRONIZER_GUIDE.md        # 동기화 상세 가이드
├── POST_AGI_COLUMN_GUIDE.md          # Post-AGI 컬럼 상세 가이드
└── README.md                         # 이 파일
```

---

## 🚀 빠른 실행

### 1단계: 데이터 동기화
```bash
cd pipe1
python data_synchronizer_v29.py --master "CASE LIST.xlsx" --warehouse "HVDC WAREHOUSE_HITACHI(HE).xlsx"
```

**결과**:
- `HVDC WAREHOUSE_HITACHI(HE).synced.xlsx`: 동기화된 파일
- 색상 표시: 🟠 주황색 (날짜 변경), 🟡 노란색 (신규 케이스)

### 2단계: Post-AGI 컬럼 계산
```bash
python post_agi_column_processor.py
```

**결과**:
- `HVDC WAREHOUSE_HITACHI(HE).xlsx`: Post-AGI 컬럼이 추가된 파일
- 13개 컬럼 자동 계산 (Status_WAREHOUSE, Status_SITE, 등)

---

## 🔧 주요 스크립트

### data_synchronizer_v29.py
**기능**: Master와 Warehouse 데이터 동기화
- Case NO 기준 매칭
- 날짜/비날짜 컬럼별 다른 처리 규칙
- 색상 표시로 변경 사항 시각화
- 상세한 변경 로그 생성

**사용법**:
```bash
python data_synchronizer_v29.py --master "CASE LIST.xlsx" --warehouse "HVDC WAREHOUSE_HITACHI(HE).xlsx"
```

**옵션**:
- `--master`: Master 파일 경로
- `--warehouse`: Warehouse 파일 경로
- `--case-col-m`: Master Case NO 컬럼명
- `--case-col-w`: Warehouse Case NO 컬럼명
- `--excel-out`: 출력 Excel 파일 경로
- `--json-out`: 출력 JSON 파일 경로
- `--no-backup`: 백업 파일 생성 안 함
- `--verbose`: 상세 로그 출력

### post_agi_column_processor.py
**기능**: AGI 이후 13개 컬럼 자동 계산
- Excel 공식을 Python pandas로 변환
- 벡터화 연산으로 고성능 처리 (10배 빠름)
- 원본 컬럼명 보존 (공백 2개)

**사용법**:
```bash
python post_agi_column_processor.py
```

**입력**: `HVDC WAREHOUSE_HITACHI(HE).synced.xlsx`
**출력**: `HVDC WAREHOUSE_HITACHI(HE).xlsx`

---

## 📊 처리되는 컬럼

### 동기화 규칙
- **날짜 컬럼**: Master 값이 항상 우선 (🟠 주황색 표시)
- **비날짜 컬럼**: Master 값이 null이 아니고 다르면 덮어쓰기
- **신규 케이스**: Warehouse에 없는 Case NO는 새로 추가 (🟡 노란색 표시)

### Post-AGI 컬럼 (13개)
1. `Status_WAREHOUSE`: 창고 데이터 존재 여부
2. `Status_SITE`: 현장 데이터 존재 여부
3. `Status_Current`: 현재 상태 판별
4. `Status_Location`: 최신 위치
5. `Status_Location_Date`: 최신 날짜
6. `Status_Storage`: 창고/현장 분류
7. `wh handling`: 창고 핸들링 횟수
8. `site  handling`: 현장 핸들링 횟수 (공백 2개)
9. `total handling`: 총 핸들링
10. `minus`: 현장-창고 차이
11. `final handling`: 최종 핸들링
12. `SQM`: 면적 계산
13. `Stack_Status`: 적재 상태

---

## ⚠️ 주의사항

### 필수 파일
- `CASE LIST.xlsx`: Master 파일 (최신 데이터)
- `HVDC WAREHOUSE_HITACHI(HE).xlsx`: Warehouse 파일 (기존 데이터)

### 컬럼명 정확성
- `site  handling` (공백 2개) - 정확히 일치해야 함
- `AAA  Storage` (공백 2개) - 정확히 일치해야 함

### 메모리 요구사항
- 5,810행 × 57컬럼 ≈ 150MB
- 충분한 메모리 확보 필요

---

## 🐛 문제 해결

### 1. 파일을 찾을 수 없음
```
FileNotFoundError: [Errno 2] No such file or directory
```
**해결방법**:
- 파일 경로 확인
- 파일명 대소문자 확인
- 현재 디렉토리 확인

### 2. Case NO 매칭 실패
```
WARNING: Case NO 매칭 실패: CASE123
```
**해결방법**:
- Case NO 형식 확인
- 정규화 규칙 확인
- 수동으로 Case NO 정리

### 3. 컬럼명 오류
```
KeyError: 'site  handling'
```
**해결방법**:
- 원본 파일의 컬럼명 확인
- 공백 개수 정확히 확인 (2개)
- Excel에서 직접 확인

### 4. 메모리 부족
```
MemoryError: Unable to allocate array
```
**해결방법**:
- 다른 프로그램 종료
- 가상 메모리 증가
- 데이터 청크 단위 처리

---

## 📈 성능 정보

### 처리 시간 (5,810행 기준)
- **1단계 (동기화)**: 5초
- **2단계 (Post-AGI)**: 0.5초
- **총 시간**: 5.5초

### 메모리 사용량
- **동기화**: 100MB
- **Post-AGI**: 150MB
- **최대**: 150MB

### 최적화 팁
1. **벡터화 연산**: `apply()` 대신 `notna().sum()`
2. **메모리 관리**: 불필요한 컬럼 제거
3. **SSD 사용**: I/O 성능 향상

---

## 📚 상세 가이드

### 데이터 동기화 가이드
- **파일**: `DATA_SYNCHRONIZER_GUIDE.md`
- **내용**: 동기화 규칙, 색상 표시, 커맨드 옵션, 고급 사용법

### Post-AGI 컬럼 가이드
- **파일**: `POST_AGI_COLUMN_GUIDE.md`
- **내용**: 13개 컬럼 상세, Excel 공식 변환, 성능 최적화

### 전체 파이프라인 가이드
- **파일**: `../pipe2/PIPELINE_USER_GUIDE.md`
- **내용**: 전체 파이프라인 개요 및 실행 방법

---

## 🔄 다음 단계

pipe1 처리 완료 후:
1. **pipe2로 복사**: `HVDC WAREHOUSE_HITACHI(HE).xlsx`를 `../pipe2/`로 복사
2. **종합 보고서 생성**: `../pipe2/hvdc_excel_reporter_final_sqm_rev (1).py` 실행
3. **이상치 탐지**: `../hitachi/anomaly_detector/anomaly_detector.py` 실행

---

## 📞 지원

### 기술 지원
- **담당자**: AI Development Team
- **이메일**: hvdc-support@company.com
- **문서 위치**: `pipe1/README.md`

### 관련 문서
- `DATA_SYNCHRONIZER_GUIDE.md`: 데이터 동기화 상세
- `POST_AGI_COLUMN_GUIDE.md`: Post-AGI 컬럼 처리 상세
- `../pipe2/PIPELINE_USER_GUIDE.md`: 전체 파이프라인 가이드

---

**문서 끝**

생성 일시: 2025-10-18 23:15:00
파일 크기: ~12KB
총 페이지: 약 6페이지 (A4 기준)
