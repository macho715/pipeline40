
# 🚀 Cursor Project Auto‑Setup v1 — Single‑File Pack (KR+EN)

> **Purpose:** 새 프로젝트 주제만 입력하면 `.cursor/rules/*.mdc`, `.github/workflows/ci.yml`, `CODEOWNERS`, `plan.md`, `.pre-commit-config.yaml` 등을 바로 만들도록 안내하는 **단일 Markdown 가이드**. Rule Pack v4.1.1 정책 반영.

---

## 1) Exec Summary
- SoT = **plan.md**, “go” → **다음 미체크 테스트** → **Red→Green→Refactor**.
- Trunk + Conventional Commits, **coverage ≥ 85.00**, lint 0, bandit High 0, **CODEOWNERS 2인 승인**.
- KR concise + EN inline, **2‑dec**, 섹션 순서: ExecSummary → Visual → Options → Roadmap → Automation → QA.
- Logistics 옵션: ΔRate 10.00% / ETA 24.00h / Pressure ≤ 4.00 t/m² / Cert 30d + **FANR·MOIAT Human Gate**.

---

## 2) Visual (구성)
| Layer | File | Role |
|---|---|---|
| Core | `.cursor/rules/000-core.mdc` | 톤/NDA/2‑dec/섹션/편집경계 |
| TDD | `.cursor/rules/010-tdd-tidy.mdc` | SoT·TDD 루프·SLA |
| Git | `.cursor/rules/030-commits-branches.mdc` | CC 규칙·Trunk·PR Gate |
| CI/CD | `.cursor/rules/040-ci-cd.mdc` | cov 85·lint·security |
| Python | `.cursor/rules/100-python.mdc` | XlsxWriter/openpyxl/pandas |
| Domain | `.cursor/rules/300-logistics-domain.mdc` | 물류 트리거/용어/Human Gate |
| CI | `.github/workflows/ci.yml` | GitHub Actions |
| Hooks | `.pre-commit-config.yaml` | black/flake8/isort/bandit/ggshield |
| Owners | `CODEOWNERS` | 리뷰 2인 |
| Queue | `plan.md` | 테스트 큐(SoT) |

---

## 3) YAML Settings Snapshot
```yaml
user_rules_settings_v4_1_1:
  output:
    language: "KR concise + EN-inline"
    number_format: "2-dec"
    section_order: ["ExecSummary","Visual","Options","Roadmap","Automation","QA"]
  edit_scope:
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
  domain_hvdc:
    triggers:
      rate_change_pct: 10.00
      eta_delay_h: 24.00
      pressure_t_per_m2_max: 4.00
      cert_expiry_days_min: 30.00
    human_gate: ["FANR","MOIAT"]
  modes: ["PRIME","ORACLE","ZERO","LATTICE","RHYTHM","COST-GUARD"]
```

---

## 4) Setup Guide
```bash
git init -b main
unzip cursor_project_auto_setup_v1.zip -d .
python tools/generate_rules.py --topic "HVDC Logistics Optimizer" --domain logistics --owner "@org/eng-core"
pip install pre-commit
pre-commit install && pre-commit install --hook-type commit-msg
git add . && git commit -m "chore: bootstrap cursor settings"
git push -u origin main
```

---

## 5) QA Checklist
| 항목 | 목표 | 상태 |
|--|--|--|
| Coverage | ≥ 85.00% | ☐ |
| Lint/Format | 경고 0 | ☐ |
| Bandit High | 0 | ☐ |
| CODEOWNERS 승인 | 2인 | ☐ |
| Test SLA | unit ≤ 0.2s | ☐ |

---

## 6) Slash Commands
```
/automate pre-commit+ci
/switch_mode PRIME + /logi-master --deep report
/redo step rules-tune --target .cursor/rules/300-logistics-domain.mdc
```

> **한 줄 요약:** “주제만 주면 규칙·CI·문서 세트를 즉시 생성해 TDD/PR 게이트까지 맞춘다.”
