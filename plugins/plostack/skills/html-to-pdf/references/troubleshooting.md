# 문제 해결 가이드

HTML to PDF 변환 시 발생하는 주요 문제와 진단, 해결 방법.

---

## 텍스트 깨짐 (텍스트 추출 0건)

### 증상

- `pdftotext` 출력이 0건
- PDF 뷰어에서 텍스트 선택 불가
- 파일 크기가 예상보다 작음 (PNG 방식은 보통 1.0~2.0MB, page.pdf() 방식은 3.0~8.0MB)

### 원인

PNG 캡처 흐름으로 변환된 경우. `page.screenshot()`으로 각 페이지를 PNG로 캡처한 후 이미지를 PDF에 삽입한 흐름이다. 텍스트가 픽셀로 변환되므로 선택, 검색, 추출 불가.

### 해결

반드시 `page.pdf()` 직접 호출 흐름을 사용한다.

잘못된 예:
```javascript
// PNG 캡처 후 이미지 삽입 — 텍스트 손실
const buf = await page.screenshot({ type: 'png', fullPage: true });
```

올바른 예:
```javascript
// 직접 PDF 생성 — 텍스트 보존
await page.pdf({ path: outputPath, ... });
```

---

## hyperlink 손실 (PDF annotation 0건)

### 증상

- `pdftohtml` 결과에서 `<a>` 태그 0건
- PDF 뷰어에서 링크 클릭 불가

### 원인 1: PNG 캡처 흐름

PNG는 픽셀 이미지이므로 annotation 포함 불가. "텍스트 깨짐" 섹션과 동일한 원인.

### 원인 2: CSS `pointer-events: none`

HTML에 `a { pointer-events: none; }` 또는 `a { display: none; }` 규칙이 있으면 Playwright가 링크를 PDF annotation으로 변환하지 않을 수 있다.

진단:
```bash
grep -i 'pointer-events\|a {' /path/to/file.html | head -20
```

해결: 인쇄 CSS에서 `pointer-events: auto !important;` 강제 적용.

### 원인 3: 절대 URL이 아닌 경로

상대 경로 `href="./page2.html"` 는 PDF에서 동작하지 않을 수 있다. 절대 URL로 변환 권장.

---

## 폰트 깨짐 (한글 네모 박스)

### 증상

- PDF에서 한글이 네모(□)로 표시
- 일부 글자만 깨지거나 전체 텍스트 깨짐

### 원인

웹폰트(Noto Sans KR, Pretendard, Spoqa Han Sans 등)가 완전히 로드되기 전에 PDF로 변환.

### 해결

`fontWaitMs`를 늘린다. 기본값 2500ms, 재시도 시 5000ms.

```javascript
// convert.js 실행 시
node convert.js --input=file.html --font-wait-ms=5000
```

CDN 폰트가 느린 환경에서는 폰트를 Base64로 인라인 삽입하거나 시스템 폰트로 대체하는 방법도 있다.

---

## 여백이 생기거나 내용이 잘림

### 증상

- 슬라이드 주변에 흰 여백
- 슬라이드 오른쪽 또는 아래가 잘림

### 원인

`@page { size: ... }` 크기와 `page.pdf()` `width`/`height` 불일치.

진단:
```bash
pdfinfo output.pdf | grep 'Page size'
```

### 해결

두 값을 일치시킨다.

```javascript
// @page CSS
@page { size: 13.333in 7.5in; margin: 0; }

// page.pdf() 옵션
width: '13.333in',
height: '7.5in',
preferCSSPageSize: true,
```

---

## 페이지가 분리되지 않음 (슬라이드가 한 페이지에 몰림)

### 증상

- 모든 슬라이드가 첫 페이지에 합쳐져 출력
- 페이지 수가 1

### 원인

페이지 분리 셀렉터가 HTML 구조와 맞지 않음.

진단: HTML 파일에서 실제 슬라이드 컨테이너 클래스 확인.

```bash
grep -o 'class="[^"]*"' /path/to/file.html | sort | uniq | head -30
```

### 해결

`--page-break-selector` 옵션을 실제 클래스로 지정.

```bash
node convert.js --input=file.html --page-break-selector=".page"
node convert.js --input=file.html --page-break-selector="article"
node convert.js --input=file.html --page-break-selector="[data-slide]"
```

---

## 페이지 로드 타임아웃

### 증상

```
Error: Timeout 90000ms exceeded.
```

### 원인

외부 리소스(CDN 이미지, 폰트, 스크립트)가 로드되지 않아 `networkidle` 도달 불가.

### 해결 방법 1: 타임아웃 늘림

```bash
node convert.js --input=file.html --timeout=120000
```

### 해결 방법 2: waitUntil 전략 변경

`convert.js` 내부에서 `networkidle` 대신 `domcontentloaded` 사용 후 `fontWaitMs` 증가.

```javascript
await page.goto('file://' + absInput, { waitUntil: 'domcontentloaded', timeout });
```

---

## pdfinfo / pdftotext / pdftohtml 없음

### 증상

```
WARN: pdfinfo 없음 (apt install poppler-utils). 페이지 수 확인 생략.
```

### 해결

```bash
sudo apt install poppler-utils
```

변환 자체는 정상 동작한다. 검증 단계만 생략된다.

---

## playwright not found

### 증상

```
[html-to-pdf] Playwright를 찾을 수 없습니다.
```

### 해결

```bash
# 해당 디렉터리에서 설치
npm install playwright
npx playwright install chromium

# 또는 전역 설치
npm install -g playwright
npx playwright install chromium
```

---

## 진단 체크리스트

문제 발생 시 순서대로 확인:

1. `pdftotext output.pdf - | wc -c` 텍스트 추출 확인
2. `pdfinfo output.pdf` 페이지 수, 크기 확인
3. HTML에서 실제 슬라이드 컨테이너 클래스 확인
4. `@page` 크기와 `page.pdf()` 크기 일치 여부 확인
5. 폰트 대기 시간 증가 후 재시도
6. 타임아웃 증가 후 재시도
