# PLOZEN Public Plugins

PLOZEN 공개 플러그인 마켓플레이스입니다.

이 repo는 하나의 skills source of truth를 두고 runtime별 manifest를 분리합니다.

- `manifest`: 플러그인/마켓플레이스 정보를 적는 설정 파일
- `runtime`: 플러그인을 실행하는 환경
- `source of truth`: 가장 기준이 되는 원본

## 구조

```text
plozen-public-plugins/
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── .opencode/marketplace.json
├── .hermes/marketplace.json
└── plugins/
    └── aegis/
        ├── .codex-plugin/plugin.json
        ├── .claude-plugin/plugin.json
        └── skills/
```

## Codex

```bash
codex plugin marketplace add plozen/plozen-public-plugins
```

## Claude Code

```text
/plugin marketplace add plozen/plozen-public-plugins
/plugin install aegis@plozen-public-plugins
```

## OpenClaw / Hermes

`.opencode/marketplace.json`과 `.hermes/marketplace.json`은 호환 manifest 후보입니다. 각 runtime의 실제 manifest schema가 확인되면 이 파일을 해당 형식에 맞춰 조정합니다.

## 포함 플러그인

- `aegis`: 공개 디자인, 문서 제작, HTML/PDF/PPTX, 전달 오케스트레이션 스킬팩
