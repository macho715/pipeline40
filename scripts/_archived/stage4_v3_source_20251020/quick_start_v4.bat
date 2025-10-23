@echo off
REM ============================================================================
REM HVDC Anomaly Detector v4.0 - Quick Start
REM Windows 11 최적화 배치 파일
REM ============================================================================

echo.
echo ================================================================================
echo    HVDC Anomaly Detector v4.0 - Quick Start
echo    System: Intel i7-1165G7 + 32GB RAM + Windows 11
echo ================================================================================
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"
echo [INFO] Working Directory: %CD%
echo.

REM Python 확인
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

python --version
echo.

REM ============================================================================
REM 메뉴 선택
REM ============================================================================

:MENU
echo.
echo [1] Install Dependencies (First Time)
echo [2] Run Quick Test (100 samples)
echo [3] Run Full Test (1000 samples)
echo [4] Process Real Data (Excel input)
echo [5] Benchmark v3 vs v4
echo [6] Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto QUICK_TEST
if "%choice%"=="3" goto FULL_TEST
if "%choice%"=="4" goto REAL_DATA
if "%choice%"=="5" goto BENCHMARK
if "%choice%"=="6" goto END
echo [ERROR] Invalid choice!
goto MENU

REM ============================================================================
REM 1. 의존성 설치
REM ============================================================================
:INSTALL
echo.
echo ============================================================================
echo    Installing Dependencies
echo ============================================================================
echo.

REM 가상환경 생성 (선택)
set /p use_venv="Create virtual environment? (y/n): "
if /i "%use_venv%"=="y" (
    echo [INFO] Creating virtual environment...
    python -m venv venv_v4
    call venv_v4\Scripts\activate.bat
)

REM 최소 설치 vs 전체 설치
echo.
echo Installation Options:
echo [1] Minimal (no Deep Learning) - Fast
echo [2] Full (with Deep Learning) - Recommended
echo.
set /p install_type="Select (1-2): "

if "%install_type%"=="1" (
    echo [INFO] Installing minimal dependencies...
    pip install numpy pandas openpyxl scikit-learn pyod xgboost lightgbm
) else (
    echo [INFO] Installing full dependencies...
    pip install -r requirements_v4.txt
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Installation complete!
) else (
    echo [ERROR] Installation failed!
)

pause
goto MENU

REM ============================================================================
REM 2. 빠른 테스트
REM ============================================================================
:QUICK_TEST
echo.
echo ============================================================================
echo    Quick Test (100 samples)
echo ============================================================================
echo.

python test_v4.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Test passed!
) else (
    echo [ERROR] Test failed!
)

pause
goto MENU

REM ============================================================================
REM 3. 전체 테스트
REM ============================================================================
:FULL_TEST
echo.
echo ============================================================================
echo    Full Test (1000 samples)
echo ============================================================================
echo.

python -c "from test_v4 import *; test_v4_full_features()"

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Test passed!
) else (
    echo [ERROR] Test failed!
)

pause
goto MENU

REM ============================================================================
REM 4. 실제 데이터 처리
REM ============================================================================
:REAL_DATA
echo.
echo ============================================================================
echo    Process Real Data
echo ============================================================================
echo.

set /p input_file="Enter Excel file path: "
if not exist "%input_file%" (
    echo [ERROR] File not found: %input_file%
    pause
    goto MENU
)

set /p sheet_name="Enter sheet name (default: 통합_원본데이터_Fixed): "
if "%sheet_name%"=="" set sheet_name=통합_원본데이터_Fixed

set /p output_dir="Enter output directory (default: .\output): "
if "%output_dir%"=="" set output_dir=.\output

if not exist "%output_dir%" mkdir "%output_dir%"

echo.
echo Processing Options:
echo [1] Fast Mode (no DL, no SHAP) - ~12s per 1000 records
echo [2] Balanced Mode (with Boosting) - ~20s per 1000 records
echo [3] Full Mode (DL + SHAP) - ~35s per 1000 records
echo.
set /p mode="Select mode (1-3): "

set dl_flag=--no-dl
set shap_flag=--no-shap

if "%mode%"=="2" (
    set dl_flag=--no-dl
    set shap_flag=--no-shap
)
if "%mode%"=="3" (
    set dl_flag=
    set shap_flag=
)

echo.
echo [INFO] Processing...
python anomaly_detector_v4.py ^
    --input "%input_file%" ^
    --sheet "%sheet_name%" ^
    --excel-out "%output_dir%\anomalies_v4.xlsx" ^
    --json-out "%output_dir%\anomalies_v4.json" ^
    %dl_flag% %shap_flag%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Processing complete!
    echo Output: %output_dir%\anomalies_v4.xlsx
    echo         %output_dir%\anomalies_v4.json
    
    REM 자동으로 Excel 열기
    set /p open_excel="Open Excel? (y/n): "
    if /i "%open_excel%"=="y" (
        start "" "%output_dir%\anomalies_v4.xlsx"
    )
) else (
    echo [ERROR] Processing failed!
)

pause
goto MENU

REM ============================================================================
REM 5. 벤치마크
REM ============================================================================
:BENCHMARK
echo.
echo ============================================================================
echo    Benchmark: v3 vs v4
echo ============================================================================
echo.

python -c "from test_v4 import benchmark_v3_vs_v4; benchmark_v3_vs_v4()"

pause
goto MENU

REM ============================================================================
REM 종료
REM ============================================================================
:END
echo.
echo Thank you for using HVDC Anomaly Detector v4.0!
echo.
pause
exit /b 0
