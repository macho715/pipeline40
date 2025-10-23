# Stage 3 헤더 매니저 통합 업데이트

- Core 모듈(`scripts/core/header_manager.py`)에서 헤더 정규화/동의어/위치 감지를 중앙 집중화했습니다.
- Stage 1 동기화와 Stage 3 리포트는 동일한 매칭 로직을 사용하므로 헤더 명칭이 바뀌어도 Core 설정만 수정하면 됩니다.
- 창고/현장 컬럼은 `HeaderRegistry` 그룹 메타데이터를 통해 동적으로 탐지되어 하드코딩 목록을 유지할 필요가 없습니다.
