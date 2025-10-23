
# ⚙️ Cursor Config Patch v1 — Project Installation Guide

> **Purpose:**  
> 이 패치는 Cursor 프로젝트의 초기 워크스페이스를 자동 설정합니다.  
> 탭 구성, 문서 자동 로드, Git 초기화, pre-commit 훅 설치를 포함하여  
> 새 프로젝트가 즉시 실행 가능한 상태로 준비됩니다.

---

## 📦 Download  
[**Download: cursor_config_patch_v1.zip**](sandbox:/mnt/data/cursor_config_patch_v1.zip)

---

## 📁 포함 파일

| 파일 | 설명 | 기능 |
|------|------|------|
| `tools/init_settings.py` | 워크스페이스 자동 초기화 스크립트 | 탭 구성, git init, pre-commit 설치 |
| `.cursor/config/workspace.json` | Active Tabs 및 명령 설정 시드 | Docs/Code/Git/Rules/Terminals 자동 구성 |
| `.cursor/rules/active_mode.mdc` | 탭 정책 정의 | Docs/Rules/Git/Terminals 동작 정책 |
| `.cursor/hooks/preload_docs.yaml` | 시작 문서 자동 로드 | Guide 및 README 자동 오픈 |
| `README_CONFIG_PATCH.md` | 사용 설명서 | 설치 및 적용 방법 안내 |

---

## 🧰 주요 기능 요약

### 1. **Workspace 자동 초기화**
- `tools/init_settings.py` 실행 시 다음이 자동 수행됩니다:
  - `.cursor/config/workspace.json` 생성  
  - Git 저장소 초기화 (`git init -b main`)  
  - `pre-commit` 및 `commit-msg` 훅 설치  
  - `.venv` 가상환경 생성 및 활성화

### 2. **탭 구성 (Active Tabs)**
```json
{
  "active_tabs": ["Docs", "Code", "Git", "Rules", "Terminals"],
  "docs_default": ["Cursor_Project_AutoSetup_Guide.md", "README.md"],
  "rules_path": ".cursor/rules/",
  "git_auto_init": true,
  "terminal_commands": [
    "python -m venv .venv",
    "source .venv/bin/activate",
    "pip install pre-commit && pre-commit install",
    "pre-commit install --hook-type commit-msg"
  ]
}
```
- 프로젝트를 열면 위 설정에 따라 탭이 자동 배치됩니다.

### 3. **자동 문서 로드**
- `.cursor/hooks/preload_docs.yaml`에 지정된 문서가 시작 시 자동으로 열립니다.
```yaml
preload_docs:
  - path: "Cursor_Project_AutoSetup_Guide.md"
    open_on_start: true
  - path: "README.md"
    open_on_start: true
```

### 4. **탭별 동작 정책 (`active_mode.mdc`)**
```md
---
description: Cursor Active Tabs & Mode별 자동 동작 정책
globs: ["**/*"]
alwaysApply: true
---
- Active Tabs: Docs, Code, Git, Rules, Terminals
- Docs 탭: Guide 및 README 자동 로드
- Rules 탭: .mdc 규칙 자동 인식
- Git 탭: commit-msg 훅 적용 (Conventional Commit)
- Terminals 탭: pytest / lint / pre-commit 단축 명령
```

---

## ⚙️ 설치 방법

```bash
# 1️⃣ 패치 압축 해제
unzip cursor_config_patch_v1.zip -d .

# 2️⃣ 초기 설정 스크립트 실행
python tools/init_settings.py

# 3️⃣ Cursor 재시작
# 탭/문서/훅이 자동 적용됩니다.
```

---

## 🧭 적용 결과
- **Active Tabs:** Docs / Code / Git / Rules / Terminals 자동 구성  
- **Docs 탭:** `Cursor_Project_AutoSetup_Guide.md`, `README.md` 자동 오픈  
- **Rules 탭:** `.cursor/rules/*.mdc` 자동 로드  
- **Git:** pre-commit 훅 + commit-msg 규칙 활성화  
- **Terminals:** pytest/lint 명령 단축 실행 가능  

---

## ✅ 검증 체크리스트
| 항목 | 확인 |
|------|------|
| `.cursor/config/workspace.json` 생성 여부 | ☐ |
| pre-commit 훅 설치 성공 | ☐ |
| Docs 탭에서 Guide 자동 로드 | ☐ |
| Git 탭 commit-msg 훅 정상 작동 | ☐ |
| Terminals 탭 명령 실행 확인 | ☐ |

---

## 📄 버전 정보
- **Package:** Cursor Config Patch v1  
- **작성일:** 2025-10-18  
- **Author:** MACHO-GPT | HVDC Logistics Automation Team  
- **Compatibility:** Cursor IDE ≥ v0.36.0

---

> 📌 **요약:**  
> “이 패치는 Cursor 워크스페이스를 완전히 자동화해,  
> 새 프로젝트를 생성하자마자 CI/Rule/Doc 환경이 즉시 동작하도록 구성한다.”
