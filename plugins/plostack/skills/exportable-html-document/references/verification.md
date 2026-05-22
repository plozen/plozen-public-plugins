# Exportable HTML Verification

## Screen / Print Layout

Playwright로 screen과 print 계산값을 비교한다.

필수 확인:

- `.page` count
- `.page` width/height
- 주요 frame width/height
- 대표 heading font-size
- 주요 grid template
- 각 `.page`의 `scrollHeight - clientHeight`

overflow가 0보다 크면 해당 page의 content가 잘렸을 가능성이 있다.

## PDF

필수 확인:

```bash
pdfinfo output.pdf
pdftotext output.pdf - | wc -c
pdftohtml -xml -i -stdout output.pdf > /tmp/pdf_check.xml
grep -c '<a ' /tmp/pdf_check.xml
```

Pass 기준:

- PDF page 수 = `.page` 수.
- `pdftotext` 결과가 0이 아니다.
- 링크가 필요한 문서라면 hyperlink count가 0이 아니다.
- `pdftoppm`으로 첫 페이지와 마지막 페이지를 렌더링해 toolbar가 없는지 확인한다.

## PPTX

필수 확인:

- 생성 파일이 존재한다.
- slide 수 = `.page` 수 또는 사전에 정한 slide 수.
- 버튼/toolbar가 slide에 포함되지 않는다.
- 이미지 기반 PPTX면 최소 첫/마지막 slide preview를 확인한다.
- 편집 가능 PPTX면 주요 텍스트가 slide shape/text로 생성됐는지 확인한다.

도구가 없으면 검증은 `SKIP`이 아니라 `UNVERIFIED`로 보고한다.
