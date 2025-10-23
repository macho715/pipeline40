# HVDC 파이프라인 전체 실행 PowerShell 스크립트
# 실행 방법: PowerShell에서 .\run_full_pipeline.ps1

param(
    [switch]$Verbose = $false
)

# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HVDC 파이프라인 v4.0.17 - Stage 3 벡터화 최적화" -ForegroundColor Cyan
Write-Host "Samsung C&T Logistics | ADNOC-DSV" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리를 스크립트 위치로 변경
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

$StartTime = Get-Date
Write-Host "[$($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))] 파이프라인 실행 시작..." -ForegroundColor Green
Write-Host ""

try {
    # Stage 1: Data Synchronization
    Write-Host "Stage 1: Data Synchronization 실행 중..." -ForegroundColor Yellow
    $Stage1Start = Get-Date
    python run_pipeline.py --stage 1
    if ($LASTEXITCODE -ne 0) {
        throw "Stage 1 실행 실패 (Exit Code: $LASTEXITCODE)"
    }
    $Stage1Duration = (Get-Date) - $Stage1Start
    Write-Host "Stage 1 완료! (소요시간: $($Stage1Duration.TotalSeconds.ToString('F1'))초)" -ForegroundColor Green
    Write-Host ""

    # 파일 복사
    Write-Host "파일 복사 중..." -ForegroundColor Yellow
    $SyncedFile = "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_v3.4.xlsx"

    if (Test-Path $SyncedFile) {
        Copy-Item $SyncedFile "data\processed\synced\synced_for_stage2.xlsx" -Force
        Write-Host "파일 복사 완료! (Stage 2 입력 파일 준비)" -ForegroundColor Green
    }
    else {
        throw "Synced 파일을 찾을 수 없습니다: $SyncedFile"
    }
    Write-Host ""

    # Stage 2-3: Derived Columns & Report Generation (벡터화 최적화)
    Write-Host "Stage 2-3: Derived Columns & Report Generation 실행 중... (벡터화 최적화)" -ForegroundColor Yellow
    $Stage23Start = Get-Date
    python run_pipeline.py --stage 2, 3
    if ($LASTEXITCODE -ne 0) {
        throw "Stage 2-3 실행 실패 (Exit Code: $LASTEXITCODE)"
    }
    $Stage23Duration = (Get-Date) - $Stage23Start
    Write-Host "Stage 2-3 완료! (소요시간: $($Stage23Duration.TotalSeconds.ToString('F1'))초)" -ForegroundColor Green
    Write-Host ""

    # Stage 4: Balanced Boost Anomaly Detection
    Write-Host "Stage 4: Balanced Boost 이상치 탐지 실행 중... (색상 적용 포함)" -ForegroundColor Yellow
    $Stage4Start = Get-Date
    python run_pipeline.py --stage 4
    if ($LASTEXITCODE -ne 0) {
        throw "Stage 4 실행 실패 (Exit Code: $LASTEXITCODE)"
    }
    $Stage4Duration = (Get-Date) - $Stage4Start
    Write-Host "Stage 4 완료! (Balanced Boost 이상치 색상 적용됨, 소요시간: $($Stage4Duration.TotalSeconds.ToString('F1'))초)" -ForegroundColor Green
    Write-Host ""

    # 전체 실행 시간 계산
    $TotalDuration = (Get-Date) - $StartTime

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "파이프라인 실행 완료!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "실행 시간 요약:" -ForegroundColor White
    Write-Host "  Stage 1: $($Stage1Duration.TotalSeconds.ToString('F1'))초" -ForegroundColor Gray
    Write-Host "  Stage 2-3: $($Stage23Duration.TotalSeconds.ToString('F1'))초" -ForegroundColor Gray
    Write-Host "  Stage 4: $($Stage4Duration.TotalSeconds.ToString('F1'))초" -ForegroundColor Gray
    Write-Host "  총 시간: $($TotalDuration.TotalSeconds.ToString('F1'))초" -ForegroundColor White
    Write-Host ""
    Write-Host "생성된 파일들:" -ForegroundColor White
    Write-Host "  Synced 파일: data\processed\synced\" -ForegroundColor Gray
    Write-Host "  Derived 파일: data\processed\derived\" -ForegroundColor Gray
    Write-Host "  보고서: data\processed\reports\" -ForegroundColor Gray
    Write-Host "  이상치 보고서: data\anomaly\" -ForegroundColor Gray
    Write-Host ""

}
catch {
    Write-Host "오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "파이프라인 실행이 중단되었습니다." -ForegroundColor Red
    exit 1
}

Write-Host "스크립트 실행 완료!" -ForegroundColor Green
