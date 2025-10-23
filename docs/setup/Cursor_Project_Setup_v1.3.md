# 🚀 ChatGPT × Cursor 프로젝트 세팅 – 운영 지침 v1.3 (Auto‑Setup + Config Patch 통합)

> **Purpose:** 새 프로젝트 시작 전 주제 1줄만 입력하면 Cursor 룰(.mdc)·CI·CODEOWNERS·plan.md·pre‑commit·Workspace 설정을 자동 생성·적용하는 단일 가이드입니다.  
> **통합 기준:** Rule Pack v4.1.1 · Auto‑Setup v1 · Config Patch v1.  
> **업데이트:** 사전 Mini‑Brief + Auto Research + `.cursorrules.yaml` 집계 파일 추가.

---

## 1️⃣ Exec Summary
- **Before coding:** 주제 1줄 → **Mini‑Brief(≤10m)** → Auto Research(domain/python/owners/품질/보안 임계값) → 맞춤 세팅(rules/CI/Workspace).
- **SoT:** plan.md (“go” → 다음 미체크 테스트 Red→Green→Refactor).
- **Gate:** cov ≥85.00, lint 0, bandit High 0, CODEOWNERS 2인 승인.
- **Style:** KR concise + EN-inline, 2‑dec, 섹션 순서 ExecSummary→Visual→Options→Roadmap→Automation→QA.
- **Scope Guard:** src/** 한정, 불확실 정보는 “가정:” 표시.

---

## 2️⃣ Visual (세팅 구성 요약)

| Layer | 파일 | 설명 |
|:--|:--|:--|
| Core | .cursor/rules/000-core.mdc | 톤/NDA/2-dec/편집경계 |
| TDD | .cursor/rules/010-tdd-tidy.mdc | SoT/TDD 루프/SLA |
| Git | .cursor/rules/030-commits-branches.mdc | CC 규칙/Trunk/PR Gate |
| CI/CD | .cursor/rules/040-ci-cd.mdc | cov85/lint0/security |
| Python | .cursor/rules/100-python.mdc | Excel IO/XlsxWriter/openpyxl |
| Domain | .cursor/rules/300-logistics-domain.mdc | ΔRate10%/ETA24h/Pressure≤4.00t/m²/Cert30d |
| Aggregator | .cursorrules.yaml | 모든 룰팩 집계(단일 소스) |
| CI | .github/workflows/ci.yml | 테스트·보안 파이프라인 |
| Hook | .pre-commit-config.yaml | black/isort/flake8/bandit |
| Owner | CODEOWNERS | 2인 승인 |
| SoT | plan.md | 테스트 큐 |
| Profile | config/project_profile.yaml | Mini‑Brief/Auto Research 결과 |
| Workspace | .cursor/config/workspace.json 외 | 탭·훅 자동 구성(Config Patch v1) |

---

## 3️⃣ `.cursorrules.yaml` 예시

```yaml
version: 1.3
style:
  language: "KR concise + EN-inline"
  number_format: "2-dec"
  section_order: ["ExecSummary","Visual","Options","Roadmap","Automation","QA"]
scope_guard:
  allowed_paths: ["src/**"]
tdd:
  source_of_truth: "plan.md"
  go_behavior: "next_unmarked_test"
  loop: ["Red","Green","Refactor"]
  test_sla: {unit_s: 0.20, integration_s: 2.00, e2e_min: 5.00}
git:
  commits: "Conventional Commits"
  branch_model: "Trunk + short-lived feature/*"
  approvals_required: 2
ci_quality_security:
  coverage_min: 85.00
  linters: ["black","flake8","isort"]
  security: ["bandit","pip-audit --strict","ggshield"]
python_excel:
  excel_new: "XlsxWriter"
  excel_edit: "openpyxl"
  pandas_role: "IO layer"
  sheet_update: 'if_sheet_exists="replace"'
domain:
  type: "generic"
  logistics_defaults:
    rate_change_pct: 10.00
    eta_delay_h: 24.00
    pressure_t_per_m2_max: 4.00
    cert_expiry_days_min: 30.00
workspace:
  config_patch: "v1"
  docs_autoload: ["Cursor_Project_AutoSetup_Guide.md","README.md"]
hallucination_ban:
  tag: "가정:"
```

---

## 4️⃣ 설치 절차

```bash
# 1️⃣ 워크스페이스 자동 구성 (Config Patch v1)
unzip cursor_config_patch_v1.zip -d .
python tools/init_settings.py

# 2️⃣ 프로젝트 프로필 + 룰팩 생성
python - <<'PY'
from pathlib import Path, yaml
Path('config').mkdir(exist_ok=True)
profile = {
    "topic": "Your Project One-Liner",
    "domain": "generic",
    "python": "3.11",
    "codeowners": ["@org/team"],
    "quality": {"coverage_min": 85.00, "lint_zero_warn": True},
    "security": {"bandit_high_zero": True, "pip_audit_strict": True}
}
Path("config/project_profile.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
print("Project profile created.")
PY

# 3️⃣ pre-commit 훅 설치
pip install pre-commit
pre-commit install && pre-commit install --hook-type commit-msg
```

---

## 5️⃣ QA 체크리스트

| 항목 | 목표 | 상태 |
|--|--|--|
| Coverage | ≥85.00% | ☐ |
| Lint/Format | 경고 0 | ☐ |
| Bandit High | 0 | ☐ |
| CODEOWNERS 승인 | 2인 | ☐ |
| Test SLA | unit≤0.2s | ☐ |
| 파이프라인 시간 | ≤5m | ☐ |

---

## 6️⃣ Slash 명령어
```
/automate pre-commit+ci
/redo step rules-tune --target .cursor/rules/300-logistics-domain.mdc
/switch_mode PRIME + /logi-master --deep report
```

---

## 7️⃣ 요약
> “주제만 주면 규칙·CI·Workspace까지 자동 구성하고, TDD/PR Gate를 즉시 가동한다.”
