---
name: html-to-pptx
description: 이미 존재하는 HTML page/slide 문서를 PPTX로 변환하거나, HTML preview의 PPTX 다운로드 버튼을 구현해야 할 때 사용한다. 새 발표자료를 처음부터 기획/작성하는 요청은 pptx-generator를 사용한다.
---

# HTML to PPTX

## 역할

이미 만들어진 HTML/CSS/JavaScript slide/page preview를 PPTX 파일로 내보낸다. 이 스킬은 `pptx-generator`를 대체 삭제하지 않고, HTML 원본이 있는 PPTX export 요청을 더 명확히 라우팅하는 wrapper다.

## 사용 시점

- 기존 HTML slide deck에서 PPTX를 다운로드해야 한다.
- 기존 `.page` 또는 `.slide` 기반 HTML 문서를 PPTX로 변환한다.
- 이미 만든 PDF/PPTX export HTML 문서에서 PPTX 경로를 구현한다.
- 시각 fidelity와 편집 가능성 중 어느 PPTX 전략을 쓸지 선택해야 한다.

사용하지 않는 경우:

- 새 발표자료를 처음부터 기획/생성하는 요청은 `pptx-generator`를 사용한다.
- PDF export는 `html-to-pdf`.
- PDF/PPTX 원본 HTML 구조 설계는 `exportable-html-document`.

## 변환 전략

1. Editable PPTX
   - PptxGenJS로 text, shape, image, table을 생성한다.
   - 발표자료, 수정 가능한 납품물이 필요할 때 기본값이다.
   - HTML/CSS preview와 완전 동일하진 않을 수 있다.

2. Image-based PPTX
   - 각 `.page` 또는 `.slide`를 screenshot으로 캡처해 slide background/image로 넣는다.
   - 시각 동일성이 우선이고 편집성이 덜 중요할 때 사용한다.
   - 텍스트 편집은 불가능하거나 제한된다.

3. Hybrid PPTX
   - 배경/복잡한 장식은 이미지로, 주요 텍스트와 링크는 PptxGenJS 객체로 생성한다.
   - 시간 여유가 있고 시각 fidelity와 편집성을 모두 어느 정도 원할 때 사용한다.

## 기본 흐름

1. Source 확인: `.slide`, `.page`, 또는 data-driven renderer인지 확인한다.
2. Strategy 선택: editable, image-based, hybrid 중 하나를 명시한다.
3. `pptx-generator`를 읽고 PptxGenJS 생성 규칙을 따른다.
4. HTML preview의 PPTX 버튼이 같은 생성 함수를 호출하게 한다.
5. PPTX 파일을 생성하고 slide count, 첫/마지막 slide, 주요 텍스트/이미지 포함 여부를 확인한다.

## PptxGenJS 연결 규칙

- 전체 API나 구체 코드가 필요하면 `../pptx-generator/SKILL.md`와 `../pptx-generator/references/pptxgenjs-api.md`를 읽는다.
- 기본 16:9 발표자료는 `pptx.layout = "LAYOUT_WIDE"`를 사용한다.
- PptxGenJS 색상은 `#` 없는 hex를 쓴다.
- Google Fonts는 PPTX에 직접 내장되지 않는다. 시스템 폰트 fallback을 명시한다.

## 검증

필수 evidence:

- PPTX 파일 생성 경로.
- slide count와 source page/slide count 비교.
- 생성 버튼이 HTML preview에 있고, export 산출물에는 toolbar가 포함되지 않음.
- editable 전략이면 주요 텍스트가 image-only가 아닌 text/shape 객체로 생성됐는지 확인.
- image-based 전략이면 첫/마지막 slide screenshot fidelity를 확인.

## 보고

완료 보고에는 아래를 포함한다.

- 사용 전략: editable / image-based / hybrid
- HTML source 경로
- PPTX output 경로
- source page/slide 수와 PPTX slide 수
- 남은 fidelity 또는 편집성 tradeoff
