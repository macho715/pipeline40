@echo off
chcp 65001 >nul
echo ========================================
echo HVDC 파이프라인 v4.0.25
echo Samsung C&T Logistics | ADNOC-DSV
echo ========================================
echo.

cd /d "%~dp0"

echo [%date% %time%] 파이프라인 실행 시작...
echo.

echo Stage 1: Data Synchronization 실행 중...
python run_pipeline.py --stage 1
if %errorlevel% neq 0 (
    echo 오류: Stage 1 실행 실패
    pause
    exit /b 1
)
echo Stage 1 완료!
echo.

echo 파일 복사 중...
copy "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_v3.4.xlsx" "data\processed\synced\synced_for_stage2.xlsx" >nul
echo 파일 복사 완료! (Stage 2 입력 파일 준비)
echo.

echo Stage 2-3: Derived Columns & Report Generation 실행 중... (벡터화 최적화)
python run_pipeline.py --stage 2,3
if %errorlevel% neq 0 (
    echo 오류: Stage 2-3 실행 실패
    pause
    exit /b 1
)
echo Stage 2-3 완료!
echo.

echo Stage 4: Balanced Boost 이상치 탐지 실행 중... (색상 적용 포함)
REM Balanced Boost 튜닝 옵션:
REM --contamination 0.01  # 보수적 (1% 이상치)
REM --contamination 0.02  # 권장 (2% 이상치, 기본값)
REM --contamination 0.05  # 공격적 (5% 이상치)
python run_pipeline.py --stage 4
if %errorlevel% neq 0 (
    echo 오류: Stage 4 실행 실패
    pause
    exit /b 1
)
echo Stage 4 완료! (Balanced Boost 이상치 색상 적용됨)
echo.

echo ========================================
echo 파이프라인 실행 완료!
echo ========================================
echo.
echo 생성된 파일들:
echo - Synced 파일: data\processed\synced\
echo - Derived 파일: data\processed\derived\
echo - 보고서: data\processed\reports\
echo - 이상치 보고서: data\anomaly\
echo.
pause
