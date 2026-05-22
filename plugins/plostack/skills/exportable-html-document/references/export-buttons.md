# Export Buttons

## 원칙

HTML preview의 export 버튼은 편의 UI다. PDF/PPTX 산출물에는 포함하지 않는다.

## 기본 HTML

```html
<div class="export-toolbar" data-html-only>
  <button type="button" data-export="pdf">PDF 다운로드</button>
  <button type="button" data-export="pptx">PPTX 다운로드</button>
</div>
```

```css
.export-toolbar {
  position: sticky;
  top: 0;
  z-index: 1000;
}

@media print {
  .export-toolbar {
    display: none;
  }
}
```

## PDF 버튼

- 간단 preview는 `window.print()`를 사용해도 된다.
- 자동 파일 생성, 경로 저장, 검증이 필요하면 `html-to-pdf` 또는 Playwright `page.pdf()`를 사용한다.
- PDF export 전에 `page.emulateMedia({ media: "print" })`와 `preferCSSPageSize: true`, `printBackground: true`를 확인한다.

## PPTX 버튼

- 브라우저 안에서 생성할 때는 PptxGenJS를 사용한다.
- HTML page를 이미지로 캡처해 slide에 넣는 방식은 시각 fidelity가 높지만 편집성이 낮다.
- PptxGenJS로 text/shape를 다시 생성하는 방식은 편집 가능하지만 HTML/CSS와 완전히 같지 않을 수 있다.
- 변환 전략은 `html-to-pptx`에서 결정한다.
- 최종 납품물에는 alert, TODO, placeholder-only export button을 남기지 않는다. 실제 PPTX 생성이 범위 밖이면 버튼을 제거하거나 비활성 상태와 생략 사유를 보고한다.
