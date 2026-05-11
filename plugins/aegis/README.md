# Aegis

Aegis는 Codex와 Claude Code에서 사용할 수 있는 공개 디자인, 문서 제작, 전달 오케스트레이션 스킬팩입니다.

포함 범위:

- 프리미엄 디자인 품질 게이트와 `DESIGN.md` 관리
- 랜딩페이지 생성과 개선
- 웹앱 UI 설계와 구현
- 모바일 앱 UI 설계와 구현
- HTML-to-PDF 변환
- PPTX 프레젠테이션 생성
- 작업 트리 우선 전달 흐름
- 리뷰, QA, 검증, 브랜치, PR, 병합, 정리 관문

주요 스킬:

- `brainstorming`
- `public-orchestration-harness`
- `design-quality`
- `landing-page-design`
- `web-app-design`
- `mobile-app-design`
- `html-to-pdf`
- `pptx-generator`

Aegis는 자체 완결형 스킬팩을 지향합니다. 로컬 메모리 파일, 외부 지식 저장소, 작업 공간 전용 하네스 노트에 의존하지 않습니다. 오케스트레이션 스킬은 작업 트리 우선, 독립 리뷰/QA 관문, 검증, PR 확인, 팀장 소유 병합/정리 흐름을 사용합니다. 커밋, 푸시, PR, 병합은 사용자 요청 또는 저장소 정책이 있을 때만 수행합니다.

## Codex 설치

PLOZEN public marketplace를 등록합니다.

```bash
codex plugin marketplace add plozen/plozen-public-plugins
```

Git marketplace로 등록된 경우 runtime cache를 갱신합니다.

```bash
codex plugin marketplace upgrade plozen-public-plugins
```

그 다음 Codex에서 plugin directory를 열고 Aegis를 활성화합니다.

```text
/plugins
```

개발 중 local source를 직접 등록하려면 저장소 경로를 marketplace source로 추가합니다.

```bash
git clone https://github.com/plozen/plozen-public-plugins.git ~/.codex/plozen-public-plugins
codex plugin marketplace add ~/.codex/plozen-public-plugins
```

local source 등록은 `upgrade` 대상이 아니므로, 변경 후 runtime cache 검증으로 반영 상태를 확인합니다. 등록 또는 cache 갱신 후에는 새 Codex 세션에서 plugin 목록을 확인합니다.

## Claude Code 설치

PLOZEN public marketplace를 등록한 뒤 플러그인을 설치합니다.

```text
/plugin marketplace add plozen/plozen-public-plugins
/plugin install aegis@plozen-public-plugins
```

## 업데이트

Git marketplace 설치 기준:

```bash
codex plugin marketplace upgrade plozen-public-plugins
```

로컬 source를 직접 등록한 경우:

```bash
cd ~/.codex/plozen-public-plugins
git pull
```

그 다음 runtime cache 반영 상태를 검증합니다.
