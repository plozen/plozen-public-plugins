---
name: html-to-pdf-skill
description: HTML 파일을 PDF로 변환해야 하며 텍스트, hyperlink, 이미지, 디자인을 보존해야 할 때 사용한다. "/html-to-pdf", "/html-pdf", "HTML PDF 변환", "PDF로 변환", "PDF 만들어", "page.pdf" 요청에 사용한다.
---

# HTML to PDF 변환 스킬

## 목적

Playwright의 `page.pdf()`를 직접 호출해 HTML을 PDF로 변환한다. PNG 캡처 방식이 아니라 텍스트 객체, hyperlink annotation, 이미지, 배경을 보존하는 PDF를 만든다.

## 사용 시점

| 명시 트리거 | 암묵 트리거 |
|---|---|
| `/html-to-pdf` | HTML 파일을 PDF로 내보내야 할 때 |
| `/html-pdf` | 공모전, 보고서, 프레젠테이션 PDF 출력 |
| `HTML PDF 변환` | 텍스트와 링크 보존이 중요한 PDF |
| `HTML을 PDF로` | 슬라이드 HTML을 PDF로 변환 |
| `PDF로 변환` | |
| `PDF 만들어` | |
| `PDF 출력` | |
| `page.pdf` | |

사용하지 않는 경우:

- 이미지 캡처 요청은 Playwright screenshot을 사용한다.
- DOCX 변환은 별도 도구를 사용한다.
- PPTX 생성은 `pptx-generator-skill`을 사용한다.
- 기존 PDF 편집은 PDF 편집 도구를 사용한다.

## 사전 요구 사항

`scripts/convert.js`는 `playwright`, `playwright-core` 순서로 모듈을 찾는다. 없으면 설치 후 재시도한다.

```bash
npm install playwright
npx playwright install chromium
```

검증에는 `poppler-utils`가 있으면 좋다. 없으면 변환은 계속하고 검증 일부만 건너뛴다.

```bash
sudo apt install poppler-utils
```

## 참조 파일

실행 전에 필요한 항목만 읽는다.

- `references/playwright-pdf-options.md`: `page.pdf()` 옵션
- `references/css-print-rules.md`: 풀 채움, 그림자 제거, 페이지 분리 CSS
- `references/troubleshooting.md`: 텍스트 깨짐, 폰트 누락, hyperlink 손실 진단

단계를 건너뛰거나 합치지 않는다.

## 0단계: 입력 확인

확인할 항목:

| 항목 | 기본값 |
|---|---|
| HTML 경로 | 필수 |
| PDF 출력 경로 | HTML과 같은 경로의 `.pdf` |
| 페이지 크기 | `16:9` |
| 방향 | landscape |
| 페이지 분리 셀렉터 | `.slide-wrapper` |
| 폰트 대기 시간 | 2500ms |

HTML 경로가 명확하고 출력 경로를 추론할 수 있으면 바로 변환한다. 빠진 항목이 있으면 필요한 것만 한 번에 묻는다.

## 1단계: 변환

```bash
node /경로/html-to-pdf-skill/scripts/convert.js \
  --input="/path/to/file.html" \
  --output="/path/to/file.pdf" \
  --page-size=16:9 \
  --page-break-selector=".slide-wrapper" \
  --font-wait-ms=2500
```

주요 옵션:

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--input` | 필수 | HTML 절대 경로 |
| `--output` | input의 `.pdf` | 출력 PDF |
| `--page-size` | `16:9` | `16:9`, `A4`, `A3`, `WxH` |
| `--landscape` | `true` | `false`면 세로 |
| `--page-break-selector` | `.slide-wrapper` | 페이지 분리 CSS selector |
| `--font-wait-ms` | `2500` | 폰트 로드 추가 대기 |
| `--print-background` | `true` | 배경 출력 |
| `--no-validation` | `false` | 검증 생략 |

## 2단계: 검증

도구가 없으면 해당 검증만 `SKIP`으로 기록한다.

### 파일 생성

```bash
ls -lh /path/to/output.pdf
```

### 페이지 수와 크기

```bash
pdfinfo /path/to/output.pdf
```

확인 항목: Pages, Page size

### 텍스트 추출

```bash
pdftotext /path/to/output.pdf - | wc -c
```

0이면 PNG 캡처 흐름으로 생성됐을 가능성이 있으므로 경고한다.

### hyperlink 수

```bash
pdftohtml -xml /path/to/output.pdf /tmp/pdf_check
grep -c '<a ' /tmp/pdf_check.xml || echo "0"
```

0이면 `<a href>` annotation이 누락됐을 수 있으므로 경고한다.

## 3단계: 보고

```markdown
## HTML to PDF 변환 완료

- 입력: {HTML 경로}
- 출력: {PDF 경로}
- 파일 크기: {크기}
- 페이지 수: {N}
- 텍스트 추출: {OK / 경고}
- hyperlink: {N개 / 경고}

검증 결과: PASS | WARN | FAIL
```

경고가 있으면 `references/troubleshooting.md`에서 해당 항목을 찾아 원인과 조치도 함께 쓴다.

## 오류 처리

- `playwright not found`: 설치 후 재시도
- timeout: `--timeout=120000` 옵션으로 재시도
- 한글 폰트 깨짐: `--font-wait-ms=5000`으로 늘려 재시도
- `pdfinfo`/`pdftotext` 없음: 검증 도구 없음으로 기록하고 변환은 유지
- 텍스트 0건: PNG 캡처 가능성. troubleshooting의 텍스트 섹션 확인
- hyperlink 0건: troubleshooting의 hyperlink 섹션 확인

## 배경

2026-05-03 여가부 공모전 출품 작업에서 `page.pdf()` 직접 변환은 텍스트와 14개 hyperlink를 보존했지만, PNG 캡처 흐름은 텍스트 객체와 hyperlink를 잃었다. 이 스킬은 텍스트와 링크가 살아있는 PDF 변환 흐름을 재사용하기 위한 것이다.
