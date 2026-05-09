# Aegis

Aegis는 Codex와 Claude Code에서 사용할 수 있는 공개 디자인, 문서 제작, delivery 오케스트레이션 스킬팩입니다.

포함 범위:

- 프리미엄 앱 UI 생성
- 랜딩페이지 생성과 개선
- 완전한 HTML 출력 강제
- HTML-to-PDF 변환
- PPTX 프레젠테이션 생성
- worktree-first agentic delivery
- review, QA, commit, branch push, PR, merge, final push, cleanup gate

주요 스킬:

- `orchestration-harness-skill`
- `app-design-skill`
- `landing-gen-skill`
- `landing-upgrade-skill`
- `design-quality-skill`
- `full-output-skill`
- `html-to-pdf-skill`
- `pptx-generator-skill`

Aegis는 self-contained 스킬팩을 지향합니다. local memory file, 외부 knowledge store, workspace-specific harness note에 의존하지 않습니다. 오케스트레이션 스킬은 worktree 우선, 독립 review/QA gate, 자동 commit/branch push/PR 생성, PR 확인, 팀장 소유 merge/final push/worktree cleanup 흐름을 사용합니다.

## Codex 설치

PLOZEN public marketplace를 등록한 뒤 설치합니다.

```bash
codex plugin marketplace add /home/mhhan/.codex/plugins/plozen-public-plugins
```

그 다음 Codex에서 plugin directory를 열고 Aegis를 설치합니다.

```text
/plugins
```

개발 중 local skill discovery가 필요하면 아래처럼 연결합니다.

```bash
mkdir -p ~/.agents/skills
ln -s /home/mhhan/.codex/plugins/plozen-public-plugins/plugins/aegis/skills ~/.agents/skills/aegis
```

symlink를 추가한 뒤 Codex를 재시작합니다.

## Claude Code 설치

PLOZEN public marketplace를 등록한 뒤 플러그인을 설치합니다.

```text
/plugin marketplace add /home/mhhan/.codex/plugins/plozen-public-plugins
/plugin install aegis@plozen-public-plugins
```

## 업데이트

local Codex skill discovery 기준:

```bash
cd /home/mhhan/.codex/plugins/plozen-public-plugins && git pull
```

marketplace install은 사용하는 client의 plugin update 흐름을 따릅니다.
