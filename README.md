# PLOZEN Public Plugins

PLOZEN 공개 플러그인 마켓플레이스입니다.

이 저장소는 하나의 플러그인 원본을 두고 runtime별 manifest를 분리합니다.

- `manifest`: 플러그인과 마켓플레이스 정보를 적는 설정 파일
- `runtime`: Codex, Claude Code, OpenClaw, Hermes 같은 실행 환경
- `source of truth`: 실제 스킬과 플러그인 파일의 기준 원본

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

Git marketplace로 등록합니다.

```bash
codex plugin marketplace add plozen/plozen-public-plugins
```

Git marketplace로 등록된 경우 아래 명령으로 runtime cache를 갱신합니다.

```bash
codex plugin marketplace upgrade plozen-public-plugins
```

로컬 source로 등록하는 개발 환경에서는 `upgrade` 대상이 아니므로, 변경 후 cache 검증 명령으로 반영 상태를 확인합니다.

Codex CLI는 marketplace 관리 명령을 제공하고, 플러그인 활성화는 Codex의 plugin UI 또는 설정 파일에서 관리합니다.

## Claude Code

```text
/plugin marketplace add plozen/plozen-public-plugins
/plugin install aegis@plozen-public-plugins
```

## OpenClaw / Hermes

`.opencode/marketplace.json`과 `.hermes/marketplace.json`은 호환 manifest 후보입니다. 각 runtime의 실제 manifest schema가 확인되면 이 파일을 해당 형식에 맞춰 조정합니다.

## Runtime Cache 검증

로컬 source와 Codex runtime cache가 같은지 확인합니다.

```bash
VERSION="$(python3 -c 'import json; print(json.load(open("plugins/aegis/.codex-plugin/plugin.json"))["version"])')"
test -d "$HOME/.codex/plugins/cache/plozen-public-plugins/aegis/$VERSION"
diff -qr plugins/aegis "$HOME/.codex/plugins/cache/plozen-public-plugins/aegis/$VERSION"
```

## 포함 플러그인

- `aegis`: 공개 디자인, 문서 제작, HTML/PDF/PPTX, 전달 오케스트레이션 스킬팩
