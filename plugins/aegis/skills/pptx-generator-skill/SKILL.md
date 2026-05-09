---
name: pptx-generator-skill
description: PPT, PPTX, PowerPoint, 발표 자료, 프레젠테이션, 슬라이드, 피치덱을 HTML/CSS/JavaScript와 PptxGenJS로 생성해야 할 때 사용한다.
---

# PPTX 생성 스킬

## 목적

PptxGenJS를 사용해 전문적인 PowerPoint 파일을 생성한다. 기본 방식은 단일 HTML 파일이다. 브라우저에서 슬라이드 미리보기를 보고, 버튼 클릭으로 `.pptx`를 다운로드할 수 있어야 한다.

## 아키텍처

단일 HTML 파일 안에 아래 요소를 모두 넣는다.

- PptxGenJS CDN: `https://cdn.jsdelivr.net/gh/gitbrent/PptxGenJS/dist/pptxgen.bundle.js`
- HTML/CSS 기반 슬라이드 미리보기
- `generatePPTX()` 함수
- 다운로드 버튼
- 모든 스타일, 레이아웃, 생성 로직

사용자는 HTML을 열어 슬라이드를 확인하고, 만족하면 PPTX를 바로 내려받을 수 있어야 한다.

## 디자인 철학

프레젠테이션은 시각 커뮤니케이션이다. 프리미엄 UI를 만들 때와 같은 기준을 적용한다.

- 타이포그래피: Arial, Calibri, 기본 시스템 폰트에 기대지 않는다. 제목용 display font와 읽기 좋은 본문 폰트를 조합한다.
- 색상: 2-3개 주요 색과 1-2개 accent로 일관된 팔레트를 만든다. CSS 변수로 관리한다.
- 레이아웃: 대칭 그리드만 쓰지 말고 비대칭, 넓은 여백, 겹침, 큰 크기 대비를 활용한다.
- 질감: gradient, pattern, shadow, layered element로 깊이를 만든다.
- 일관성: 모든 슬라이드는 같은 색상 체계, 타이포 계층, 공간 리듬을 공유한다.

## HTML 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>발표 제목</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=...');

    :root {
      --color-primary: #...;
      --color-accent: #...;
      --slide-width: 960px;
      --slide-height: 540px;
    }
  </style>
</head>
<body>
  <div class="controls">
    <h1>발표 제목</h1>
    <button onclick="generatePPTX()">PPTX 다운로드</button>
  </div>

  <div class="slide slide-1">...</div>
  <div class="slide slide-2">...</div>

  <script src="https://cdn.jsdelivr.net/gh/gitbrent/PptxGenJS/dist/pptxgen.bundle.js"></script>
  <script>
    function generatePPTX() {
      const pptx = new PptxGenJS();
      pptx.layout = 'LAYOUT_WIDE';
      const slide = pptx.addSlide();
      slide.addText('제목', { x: 0.5, y: 0.5, w: 12, h: 1.2 });
      pptx.writeFile({ fileName: 'presentation.pptx' });
    }
  </script>
</body>
</html>
```

## PptxGenJS 핵심 참고

전체 API는 `references/pptxgenjs-api.md`를 읽는다.

- `pptx.layout = 'LAYOUT_WIDE'`: 13.33 x 7.5 inch, 16:9
- 위치와 크기 단위는 inch
- `slide.addText(text, options)`: 텍스트, bullet, numbering
- `slide.addShape(shapeType, options)`: 사각형, 원, 화살표, 선
- `slide.addImage(options)`: URL, base64, data URI 이미지
- `slide.addChart(chartType, data, options)`: bar, pie, line, doughnut
- `slide.addTable(rows, options)`: 표
- `slide.background = { color, fill, image }`: 배경
- 색상 값은 `#` 없는 hex를 사용한다. 예: `003366`

## 슬라이드 패턴

- Title Slide: 40-60pt 큰 제목, 짧은 부제, 강한 배경, 최소 요소
- Section Divider: 주제 전환을 알리는 한 문장 또는 키워드
- Content Slide: 50/50 또는 60/40 split. 핵심 bullet은 4-5개 이하
- Data Slide: 데이터 제목이 아니라 insight를 제목으로 쓴다. chart가 60-70%를 차지한다.
- Quote Slide: 큰 인용문, 출처, 드라마틱한 배경
- Closing Slide: 감사, Q&A, 연락처. title slide와 에너지를 맞춘다.

## 작업 흐름

1. 요청 이해: 주제, 대상, 슬라이드 수, 각 슬라이드 내용 확인
2. 미학 방향 선택: 목적과 청중에 맞는 visual theme 결정
3. 슬라이드 구조 계획: title, divider, content, data, quote, closing 등으로 매핑
4. HTML 작성: 미리보기와 `generatePPTX()`를 함께 구현
5. fidelity 확인: HTML preview와 PPTX 출력이 최대한 비슷해야 한다.

## 주의사항

- Google Fonts는 HTML preview에서 보이지만 PPTX는 사용자 시스템 폰트에 의존한다. PPTX에는 유사한 시스템 폰트를 매핑하거나 설치 필요 폰트를 알려준다.
- PptxGenJS 색상은 `#` 없이 쓴다.
- 기본은 `LAYOUT_WIDE` 16:9다.
- 일반 발표는 8-15장이 적당하다. 장수보다 슬라이드 품질을 우선한다.
- 사용자가 한국어로 요청하면 슬라이드 내용도 한국어로 작성한다.
- HTML 미리보기 페이지 배경은 슬라이드와 대비되도록 어둡게 두면 좋다.

## 참조 스크립트

`scripts/` 폴더에는 실제 사용했던 코드가 있다.

- `scripts/gen-pptx.js`: 12슬라이드 16:9 PPT 생성 예시
- `scripts/dl_pptx.js`: Playwright로 HTML의 다운로드 버튼을 눌러 PPTX를 저장하는 헬퍼

현재 스크립트는 사례 기반이며 일반화되어 있지 않다. 새 작업에서는 구조와 패턴만 참고한다.
