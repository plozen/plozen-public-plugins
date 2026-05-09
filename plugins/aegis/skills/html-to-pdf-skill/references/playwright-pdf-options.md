# page.pdf() 옵션 가이드

Playwright `page.pdf()` 핵심 옵션 정리. 텍스트, hyperlink, 이미지 보존을 위한 올바른 설정 기준.

---

## 필수 옵션 (텍스트, hyperlink 보존에 직결)

### `path`

출력 PDF 경로. 절대 경로 권장.

### `width` / `height`

페이지 크기를 직접 지정한다.

```javascript
width: '13.333in',   // 16:9 가로
height: '7.5in',     // 16:9 세로
```

`@page` CSS와 반드시 일치해야 풀 채움이 된다.

### `preferCSSPageSize: true`

`@page { size: ... }` CSS 규칙을 우선시한다. `width`/`height`와 함께 사용.

### `printBackground: true`

배경 이미지, 배경색을 PDF에 포함한다. 디자인 보존에 필수.

### `landscape: true`

가로 방향 PDF. 16:9 슬라이드는 항상 `true`.

### `margin`

여백 0으로 설정해야 풀 채움이 된다.

```javascript
margin: { top: 0, right: 0, bottom: 0, left: 0 }
```

---

## hyperlink 보존 원리

HTML의 `<a href="...">` 태그는 `page.pdf()`로 변환 시 자동으로 PDF annotation으로 변환된다. 별도 설정 불필요.

**PNG 캡처 흐름을 사용하면 hyperlink가 사라진다.** PNG는 픽셀 이미지이므로 annotation이 포함되지 않는다. 반드시 `page.pdf()` 직접 호출 흐름을 사용해야 한다.

---

## 텍스트 보존 원리

`page.pdf()`는 HTML의 텍스트 요소를 PDF 텍스트 객체로 변환한다. `pdftotext`로 추출 가능.

PNG 캡처 흐름에서는 텍스트가 픽셀로 렌더링되어 추출 불가.

---

## waitUntil 옵션 (goto)

```javascript
await page.goto('file://' + path, { waitUntil: 'networkidle', timeout: 90000 });
```

- `networkidle`: 네트워크 요청이 500ms 이상 없을 때 완료 판정. 웹폰트, 이미지 CDN 로드에 적합.
- 로컬 HTML + 외부 폰트 조합에서 타임아웃이 발생하면 `domcontentloaded`로 전환 후 `fontWaitMs` 늘림.

---

## 한글 웹폰트 로드 대기

```javascript
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(2500);
```

`document.fonts.ready`는 모든 폰트 로드 완료를 Promise로 반환한다. CDN 폰트(Noto Sans KR, Pretendard 등)는 이후 2500ms 추가 대기가 실제 렌더링 안정성에 효과적.

폰트 깨짐(한글 네모)이 발생하면 `fontWaitMs`를 5000으로 늘린다.

---

## 사이즈 프리셋

| 이름 | width | height | 용도 |
|------|-------|--------|------|
| `16:9` | 13.333in | 7.5in | 프레젠테이션, 공모전 출품 |
| `A4` | 8.27in | 11.69in | 보고서, 논문 |
| `A3` | 11.69in | 16.54in | 대형 포스터 |

A4, A3는 기본 방향이 `landscape: false`(세로). 필요 시 `landscape: true`로 가로 전환.
