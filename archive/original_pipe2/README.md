# pipe2 - 종합 보고서 생성 및 이상치 탐지

**HVDC 파이프라인 3-5단계 처리 모듈**

---

## 📋 개요

`pipe2` 폴더는 HVDC 파이프라인의 3-5단계를 담당합니다:
3. **파일 복사**: pipe1에서 처리된 파일 복사
4. **종합 보고서 생성**: 최종 Excel 보고서 생성
5. **이상치 탐지**: 이상치 탐지 및 색상 시각화

---

## 📁 파일 구조

```
pipe2/
├── hvdc_excel_reporter_final_sqm_rev (1).py  # 종합 보고서 생성 스크립트
├── HVDC WAREHOUSE_HITACHI(HE).xlsx          # pipe1에서 복사된 파일 (입력)
├── HVDC_입고로직_종합리포트_*.xlsx           # 최종 보고서 (출력)
├── HVDC_입고로직_종합리포트_*.backup_*.xlsx  # 백업 파일 (자동 생성)
├── PIPELINE_USER_GUIDE.md                   # 전체 파이프라인 가이드
├── PIPELINE_EXECUTION_REPORT_*.md           # 실행 보고서
└── README.md                                # 이 파일
```

---

## 🚀 빠른 실행

### 3단계: 파일 복사
```bash
# pipe1에서 pipe2로 복사
cp "../pipe1/HVDC WAREHOUSE_HITACHI(HE).xlsx" "."
```

### 4단계: 종합 보고서 생성
```bash
cd pipe2
python "hvdc_excel_reporter_final_sqm_rev (1).py"
```

**결과**:
- `HVDC_입고로직_종합리포트_YYYYMMDD_HHMMSS_v3.0-corrected.xlsx`: 최종 보고서
- 크기: 약 2.4MB
- 시트: 통합_원본데이터_Fixed, Summary, Analysis 등

### 5단계: 이상치 탐지 및 색상 표시
```bash
cd ../hitachi/anomaly_detector
python anomaly_detector.py --input "../../pipe2/HVDC_입고로직_종합리포트_*.xlsx" --sheet "통합_원본데이터_Fixed" --visualize
```

**결과**:
- 원본 파일에 색상 표시
- 백업 파일 자동 생성
- 이상치 508건 탐지 및 시각화

---

## 🔧 주요 스크립트

### hvdc_excel_reporter_final_sqm_rev (1).py
**기능**: 종합 Excel 보고서 생성
- 원본 데이터를 다양한 시트로 분석
- SQM 계산 및 통계 생성
- 차트 및 시각화 포함

**사용법**:
```bash
python "hvdc_excel_reporter_final_sqm_rev (1).py"
```

**입력**: `HVDC WAREHOUSE_HITACHI(HE).xlsx`
**출력**: `HVDC_입고로직_종합리포트_*.xlsx`

### anomaly_detector.py (hitachi/anomaly_detector/)
**기능**: 이상치 탐지 및 색상 시각화
- 규칙 기반, ML, 하이브리드 탐지
- Excel 셀에 색상 표시
- 상세한 분석 보고서 생성

**사용법**:
```bash
cd ../hitachi/anomaly_detector
python anomaly_detector.py --input "../../pipe2/HVDC_입고로직_종합리포트_*.xlsx" --sheet "통합_원본데이터_Fixed" --visualize
```

**옵션**:
- `--input`: 입력 Excel 파일 경로
- `--sheet`: 시트명 (기본: "Case List")
- `--visualize`: 색상 표시 활성화
- `--excel-out`: 출력 Excel 파일 경로
- `--json-out`: 출력 JSON 파일 경로
- `--verbose`: 상세 로그 출력

---

## 📊 생성되는 보고서

### 종합 보고서 구성
1. **통합_원본데이터_Fixed**: 원본 데이터 (이상치 탐지 대상)
2. **Summary**: 요약 정보
3. **Analysis**: 분석 결과
4. **Charts**: 차트 및 시각화
5. **Statistics**: 통계 정보
6. **색상 범례**: 이상치 색상 설명

### 이상치 탐지 결과
- 🔴 **빨간색**: 시간 역전 (397건)
- 🟠 **주황색**: ML 이상치 높음/치명적 (115건)
- 🟡 **노란색**: ML 이상치 보통/낮음
- 🟣 **보라색**: 데이터 품질 (1건)

---

## 🎨 색상 시스템

### 색상 코드
```python
# ARGB 형식 (8자리)
TIME_REVERSAL = "FFFF0000"      # 빨간색
ML_OUTLIER_HIGH = "FFFFC000"    # 주황색 (높음/치명적)
ML_OUTLIER_LOW = "FFFFFF00"     # 노란색 (보통/낮음)
DATA_QUALITY = "FFCC99FF"       # 보라색
EXCESSIVE_DWELL = "FFFFC000"    # 주황색
```

### 적용 규칙
- **시간 역전**: 해당 날짜 컬럼만 색칠
- **ML 이상치**: 전체 행 색칠
- **데이터 품질**: 전체 행 색칠
- **과도 체류**: 전체 행 색칠

### 색상 확인 방법
```python
import openpyxl

# Excel 파일 열기
wb = openpyxl.load_workbook("HVDC_입고로직_종합리포트_*.xlsx")
ws = wb["통합_원본데이터_Fixed"]

# 색상 통계
color_stats = {}
for row in range(2, ws.max_row + 1):
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=row, column=col)
        if cell.fill and hasattr(cell.fill.start_color, 'rgb'):
            rgb = str(cell.fill.start_color.rgb)
            if rgb not in ["00000000", "FFFFFFFF"]:
                color_stats[rgb] = color_stats.get(rgb, 0) + 1

print("색상 분포:", color_stats)
```

---

## ⚠️ 주의사항

### 필수 파일
- `HVDC WAREHOUSE_HITACHI(HE).xlsx`: pipe1에서 복사된 파일
- `hitachi/anomaly_detector/anomaly_detector.py`: 이상치 탐지 스크립트

### 메모리 요구사항
- 5,810행 × 57컬럼 ≈ 200MB
- 충분한 메모리 확보 필요

### Excel 파일 형식
- `.xlsx` 형식만 지원
- VBA 매크로는 보존되지 않음

### 색상 표시 제한
- 최대 65,536행 지원
- 색상은 Excel에서만 확인 가능

---

## 🐛 문제 해결

### 1. 파일을 찾을 수 없음
```
FileNotFoundError: [Errno 2] No such file or directory
```
**해결방법**:
- pipe1에서 파일이 제대로 복사되었는지 확인
- 파일 경로 확인
- 파일명 대소문자 확인

### 2. 보고서 생성 실패
```
ValueError: 로드할 데이터 파일이 없습니다.
```
**해결방법**:
- `HVDC WAREHOUSE_HITACHI(HE).xlsx` 파일 존재 확인
- 파일 권한 확인
- 파일이 손상되지 않았는지 확인

### 3. 색상 표시 안됨
**해결방법**:
- `--visualize` 옵션 확인
- Excel에서 색상 확인
- `openpyxl` 버전 확인

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
- **3단계 (복사)**: 0.1초
- **4단계 (보고서)**: 30초
- **5단계 (이상치)**: 15초
- **총 시간**: 45.1초

### 메모리 사용량
- **보고서 생성**: 200MB
- **이상치 탐지**: 200MB
- **최대**: 200MB

### 최적화 팁
1. **SSD 사용**: HDD 대비 3배 빠름
2. **메모리 증설**: 16GB 이상 권장
3. **불필요한 프로그램 종료**: 메모리 확보
4. **벡터화 연산**: pandas 벡터화 활용

---

## 📊 결과 검증

### 파일 크기 확인
```bash
# 최종 보고서 크기 확인 (약 2.4MB)
ls -la HVDC_입고로직_종합리포트_*.xlsx

# 백업 파일 확인
ls -la HVDC_입고로직_종합리포트_*.backup_*.xlsx
```

### 색상 표시 확인
```bash
# 색상 검증 스크립트 실행
cd ../hitachi/anomaly_detector
python verify_colors_detailed.py --input "../../pipe2/HVDC_입고로직_종합리포트_*.xlsx" --sheet "통합_원본데이터_Fixed"
```

### 데이터 일관성 확인
```bash
# pipe1과 pipe2 데이터 일관성 확인
python check_consistency.py
```

---

## 📚 상세 가이드

### 전체 파이프라인 가이드
- **파일**: `PIPELINE_USER_GUIDE.md`
- **내용**: 전체 파이프라인 개요, 단계별 상세 설명, 고급 사용법

### 이상치 탐지 가이드
- **파일**: `../hitachi/anomaly_detector/ANOMALY_DETECTION_GUIDE.md`
- **내용**: 탐지 알고리즘, 색상 시스템, 성능 최적화

### 실행 보고서
- **파일**: `PIPELINE_EXECUTION_REPORT_*.md`
- **내용**: 실제 실행 결과, 문제 해결 과정, 성능 분석

---

## 🔄 이전 단계

pipe2 실행 전에 필요한 단계:
1. **pipe1 실행**: 데이터 동기화 및 Post-AGI 컬럼 계산
2. **파일 복사**: pipe1 결과를 pipe2로 복사

---

## 📞 지원

### 기술 지원
- **담당자**: AI Development Team
- **이메일**: hvdc-support@company.com
- **문서 위치**: `pipe2/README.md`

### 관련 문서
- `PIPELINE_USER_GUIDE.md`: 전체 파이프라인 가이드
- `../hitachi/anomaly_detector/ANOMALY_DETECTION_GUIDE.md`: 이상치 탐지 가이드
- `../pipe1/README.md`: pipe1 모듈 가이드

---

**문서 끝**

생성 일시: 2025-10-18 23:20:00
파일 크기: ~15KB
총 페이지: 약 8페이지 (A4 기준)
