---
name: exportable-html-document
description: PDF/PPTX export를 전제로 HTML을 원본 미리보기로 설계해야 할 때 사용한다. 포트폴리오, 케이스북, 제안서, 이력서, 경력기술서, 발표 브리프, PDF/PPTX 다운로드 버튼이 있는 HTML 문서에 사용하며 일반 랜딩페이지나 웹앱 UI와 구분한다.
---

# Exportable HTML Document

## 역할

HTML을 최종 웹페이지가 아니라 PDF/PPTX로 내보낼 수 있는 문서 원본으로 만든다. 디자인 스타일을 고정하지 않고, 산출물 구조와 검증 절차만 강제한다.

## 사용 시점

다음 중 하나라도 해당하고 새 HTML 문서를 작성하거나 문서 구조를 재설계하는 단계라면 먼저 이 스킬로 분기한다.

- PDF/PPTX 제출/공유물을 전제로 포트폴리오, 케이스북, 제안서, 이력서, 경력기술서, 보고서, 발표 브리프 HTML 문서를 만든다.
- 최종 산출물이 PDF 또는 PPTX 제출/공유물이다.
- 새 문서 authoring 단계에서 HTML preview용 PDF/PPTX export toolbar UX를 설계한다.
- "포트폴리오 페이지"라는 표현이 있어도 최종 사용처가 제출, 공유, PDF, PPTX다.

사용하지 않는 경우:

- 반응형 마케팅 웹페이지가 최종물이면 `landing-page-design`.
- 반복 조작 UI, 관리자, 대시보드가 최종물이면 `web-app-design`.
- React Native/Expo 모바일 앱 화면이면 `mobile-app-design`.
- 이미 있는 HTML을 PDF로 변환만 하면 `html-to-pdf`.
- 이미 있는 HTML/slide source를 PPTX로 변환하거나 PPTX 다운로드 버튼/경로만 구현하면 `html-to-pptx`.

## 기본 흐름

1. Output Format Gate: HTML이 최종 웹페이지인지, PDF/PPTX 원본인지 먼저 판정한다.
2. Source Data: 본문 원천, 링크, 증빙, 민감정보 제외 범위를 확정한다.
3. Page Plan: cover, index, section/case, optional end note 같은 `.page` 목록을 정한다.
4. Paged HTML: 한 화면 단위를 `.page`로 만들고 `@page` 크기와 일치시킨다.
5. Export Toolbar: 필요하면 HTML preview에만 PDF/PPTX 버튼을 둔다.
6. Export: PDF는 `html-to-pdf`, PPTX는 `html-to-pptx`로 넘긴다.
7. Verification: screen/print/PDF/PPTX 결과가 page count와 layout 기준을 통과해야 완료한다.

## Paged HTML 불변 조건

자세한 규칙은 `references/layout-rules.md`를 읽는다.

필수 조건:

- 각 산출 페이지는 `.page` 하나다.
- `.page`와 `@page`의 width/height는 같은 값을 사용한다.
- `100vh`, `100dvh`를 page height로 쓰지 않는다.
- PDF-first 문서에는 기본 반응형 breakpoint를 넣지 않는다. 작은 창은 가로 스크롤로 본다.
- `@media print`는 page size, 색상 보존, toolbar 숨김 정도만 담당한다.
- 특정 팔레트, 폰트, 번호 스타일, 커버 스타일을 이 스킬에서 강제하지 않는다.

최소 CSS 골격:

```css
:root {
  --page-width: 1440px;
  --page-height: 1300px;
}

@page {
  size: 1440px 1300px;
  margin: 0;
}

body {
  min-width: var(--page-width);
}

.page {
  width: var(--page-width);
  height: var(--page-height);
  break-after: page;
  overflow: hidden;
}

@media print {
  .export-toolbar {
    display: none;
  }
}
```

## Export Toolbar

버튼 구현 패턴은 `references/export-buttons.md`를 읽는다.

- toolbar는 HTML preview에서만 보인다.
- PDF/PPTX 산출물에 toolbar가 들어가면 fail이다.
- PDF 자동 생성은 로컬/CI에서는 `html-to-pdf` 또는 Playwright `page.pdf()`를 사용한다.
- 브라우저 버튼은 환경에 따라 `window.print()` 또는 로컬 export endpoint/script를 호출한다.
- PPTX는 기본적으로 `html-to-pptx`로 넘긴다.

## 검증

검증 명령과 기준은 `references/verification.md`를 읽는다.

필수 evidence:

- screen과 print computed layout 비교.
- `.page` 수와 PDF page 수 일치.
- PDF 텍스트 추출 0이 아님.
- PDF hyperlink annotation이 필요한 링크 수만큼 존재.
- PPTX를 생성했다면 slide 수와 `.page` 수 일치.
- toolbar가 PDF/PPTX에 포함되지 않음.

## 완료 보고

완료 보고에는 아래를 포함한다.

- HTML preview 경로
- PDF/PPTX 산출 경로
- page count
- screen/print layout 일치 여부
- PDF text/link 검증 결과
- PPTX slide 검증 결과 또는 생략 사유
