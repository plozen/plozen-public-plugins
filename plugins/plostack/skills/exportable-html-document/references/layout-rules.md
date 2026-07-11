# Paged HTML Layout Rules

## 목적

브라우저 preview와 PDF/PPTX export가 같은 페이지 구조를 쓰게 한다. 이 문서는 스타일 취향이 아니라 구조 안정성만 다룬다.

## Page Canvas

- 기본값은 작업마다 정한다. 예: `1440px x 1300px`, `1920px x 1080px`, `960px x 540px`.
- `.page`와 `@page` 크기는 반드시 같은 값이다.
- 한 `.page`는 PDF 한 페이지 또는 PPTX 한 슬라이드에 대응한다.
- `.page` 안의 content frame은 별도 CSS 변수로 둔다. 예: `--frame-width`.

## 금지

- `100vh`, `100dvh`를 페이지 높이로 쓰지 않는다.
- PDF-first 문서에서 모바일 breakpoint로 layout을 바꾸지 않는다.
- `@media print`에서 타이포그래피, grid, spacing을 새로 설계하지 않는다.
- A4/Letter 기본값에 맡기지 않는다.
- 특정 팔레트나 포트폴리오 스타일을 재사용하도록 강제하지 않는다.

## 권장 구조

```html
<div class="export-toolbar" data-html-only>
  <button data-export="pdf">PDF</button>
  <button data-export="pptx">PPTX</button>
</div>

<main class="document">
  <section class="page cover-page">...</section>
  <section class="page index-page">...</section>
  <section class="page content-page">...</section>
</main>
```

```css
:root {
  --page-width: 1440px;
  --page-height: 1300px;
}

@page {
  size: 1440px 1300px;
  margin: 0;
}

.document {
  width: var(--page-width);
  margin: 0 auto;
}

.page {
  width: var(--page-width);
  height: var(--page-height);
  break-after: page;
  overflow: hidden;
}

.page:last-child {
  break-after: auto;
}
```

## 선택 기준

- PDF 제출물이 주 목적이면 portrait/folio형 page canvas를 선택한다.
- 발표가 주 목적이면 16:9 slide canvas를 선택한다.
- PDF와 PPTX가 둘 다 필요하면 같은 source data에서 PDF용 page canvas와 PPT용 slide canvas를 분리할 수 있다.
