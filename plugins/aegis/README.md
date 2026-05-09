# Aegis

Aegis는 Codex와 Claude Code에서 사용할 수 있는 공개 디자인, 문서 제작, 전달 오케스트레이션 스킬팩입니다.

포함 범위:

- 프리미엄 앱 UI 생성
- 랜딩페이지 생성과 개선
- 완전한 HTML 출력 강제
- HTML-to-PDF 변환
- PPTX 프레젠테이션 생성
- 작업 트리 우선 에이전트 전달 흐름
- 리뷰, QA, 커밋, 브랜치 푸시, PR, 병합, 최종 푸시, 정리 관문

주요 스킬:

- `brainstorming-skill`
- `orchestration-harness-skill`
- `app-design-skill`
- `landing-gen-skill`
- `landing-upgrade-skill`
- `design-quality-skill`
- `full-output-skill`
- `html-to-pdf-skill`
- `pptx-generator-skill`

Aegis는 자체 완결형 스킬팩을 지향합니다. 로컬 메모리 파일, 외부 지식 저장소, 작업 공간 전용 하네스 노트에 의존하지 않습니다. 오케스트레이션 스킬은 작업 트리 우선, 독립 리뷰/QA 관문, 자동 커밋/브랜치 푸시/PR 생성, PR 확인, 팀장 소유 병합/최종 푸시/작업 트리 정리 흐름을 사용합니다.

## Codex 설치

PLOZEN public marketplace를 등록한 뒤 설치합니다.

```bash
codex plugin marketplace add plozen/plozen-public-plugins
```

그 다음 Codex에서 plugin directory를 열고 Aegis를 설치합니다.

```text
/plugins
```

개발 중 로컬 스킬 탐색이 필요하면 아래처럼 연결합니다.

```bash
git clone https://github.com/plozen/plozen-public-plugins.git ~/.codex/plozen-public-plugins
mkdir -p ~/.agents/skills
ln -s ~/.codex/plozen-public-plugins/plugins/aegis/skills ~/.agents/skills/aegis
```

심볼릭 링크를 추가한 뒤 Codex를 재시작합니다.

## Claude Code 설치

PLOZEN public marketplace를 등록한 뒤 플러그인을 설치합니다.

```text
/plugin marketplace add plozen/plozen-public-plugins
/plugin install aegis@plozen-public-plugins
```

## 업데이트

로컬 Codex 스킬 탐색 기준:

```bash
cd ~/.codex/plozen-public-plugins && git pull
```

마켓플레이스 설치는 사용하는 클라이언트의 플러그인 업데이트 흐름을 따릅니다.
