# HVDC Excel Toolkit (Ready-to-Run)

업로드해주신 3개 스크립트를 **러너블 패키지**로 묶고,
다음 보강을 적용했습니다.

- 컬럼 **공백 정규화** 및 동의어 매핑(`AAA  Storage`→`AAA Storage`, `site  handling`↔`site handling`)
- **“다음 날만 출고”** 규칙을 코드로 엄밀 반영
- 간단한 **CLI** (`hvdc-cli`) 제공
- 샘플 **config/** 추가

## 빠른 시작

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1) 파생 컬럼(Stage 2)
```bash
python -m hvdc_excel_toolkit.cli derive --input <synced.xlsx> --output ./derived.xlsx
```

### 2) 리포터(로더 확인)
```bash
python -m hvdc_excel_toolkit.cli report --hitachi ./HVDC WAREHOUSE_HITACHI(HE).xlsx --simense ./HVDC WAREHOUSE_SIMENSE(SIM).xlsx --output-dir ./out
```

**주의:** 리포팅 전체 플로우는 원본 모듈의 내부 API에 의존합니다.  
CLI는 데이터 적재 확인과 파생 처리용 최소 경로를 제공합니다.

## 패치 내용 요약
- 컬럼 정규화/동의어: `hvdc_excel_toolkit/utils.py`
- 리포터:
  - Excel 로드 직후 정규화 적용
  - 결합 후 한 번 더 정규화
  - `site_date > warehouse_date` → 정확히 **+1일** (`date()==date()+1`)
- 파생 처리:
  - 입력 정규화/동의어 적용
  - `site handling` / `site  handling` **양쪽 컬럼 동시 보장**

## 요구사항
- Python 3.9+
- Excel 엔진: openpyxl

## 라이선스
사내 사용 목적의 번들입니다.