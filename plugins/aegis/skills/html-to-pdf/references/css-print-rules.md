# CSS 인쇄 규칙

HTML to PDF 변환 시 풀 채움, 그림자 제거, 페이지 분리를 위한 CSS 규칙.

---

## @page 규칙 (크기 강제)

```css
@page {
  size: 13.333in 7.5in;   /* 16:9 기본값. A4: 8.27in 11.69in */
  margin: 0;
  padding: 0;
}
```

`@page`에서 지정한 크기와 `page.pdf()`의 `width`/`height`가 일치해야 한다. 불일치 시 여백이 생기거나 내용이 잘린다.

---

## @media print 블록

인쇄 모드에서만 적용되는 규칙. `page.pdf()` 호출 시 Playwright가 인쇄 모드를 활성화한다.

```css
@media print {
  /* HTML, body 초기화 */
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: white !important;
    width: 13.333in !important;
  }

  /* 미리보기 UI 요소 숨김 */
  .controls,
  .dl-btn,
  body > h1,
  body > p,
  body > header,
  .slide-label {
    display: none !important;
  }

  /* 슬라이드 컨테이너 페이지 분리 */
  .slide-wrapper {
    margin: 0 !important;
    padding: 0 !important;
    page-break-after: always;   /* 구형 브라우저 호환 */
    break-after: page;           /* 표준 */
    width: 13.333in !important;
    height: 7.5in !important;
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    overflow: hidden !important;
    display: block !important;
  }

  /* 마지막 슬라이드는 page-break 없음 */
  .slide-wrapper:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  /* 슬라이드 내부 요소 */
  .slide {
    margin: 0 !important;
    padding: 0 !important;
    width: 13.333in !important;
    height: 7.5in !important;
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    overflow: hidden !important;
    page-break-inside: avoid;
    break-inside: avoid;
  }
}
```

---

## 스크린 모드 추가 태그 (미리보기 UI 숨김)

`@media print` 밖에서도 UI 요소를 숨겨 렌더링 간섭을 방지한다. `page.addStyleTag()`로 두 번째 태그로 주입.

```css
.controls,
.dl-btn,
body > h1,
body > p,
.slide-label {
  display: none !important;
}

html, body {
  margin: 0 !important;
  padding: 0 !important;
  background: white !important;
}

.slide-wrapper,
.slide {
  box-shadow: none !important;
  border: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
```

---

## 자주 쓰이는 페이지 분리 셀렉터

| HTML 구조 | 셀렉터 | 비고 |
|-----------|--------|------|
| `.slide-wrapper > .slide` | `.slide-wrapper` | 여가부 공모전 출품안 구조 |
| `.page` | `.page` | 일반 multi-page HTML |
| `.section` | `.section` | 섹션 기반 구조 |
| `article` | `article` | 블로그, 보고서 |
| `[data-page]` | `[data-page]` | 데이터 속성 기반 |

셀렉터는 `convert.js`의 `--page-break-selector` 옵션으로 지정한다.

---

## 체크리스트

변환 전 CSS 확인 항목:

- [ ] `@page { size: ... }` 크기와 `page.pdf()` width/height 일치
- [ ] `@media print` 블록에서 UI 요소(버튼, 라벨) `display: none`
- [ ] `box-shadow`, `border-radius` 제거 (PDF 렌더링 아티팩트 방지)
- [ ] 슬라이드 컨테이너에 `page-break-after: always` 적용
- [ ] 마지막 슬라이드에 `page-break-after: auto` 적용
- [ ] `overflow: hidden` 으로 내용 잘림 방지
