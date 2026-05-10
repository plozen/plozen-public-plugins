# PptxGenJS API 빠른 참조

PPTX 생성 스킬에서 자주 쓰는 PptxGenJS 사용법이다. 전체 API를 모두 대체하려는 문서가 아니라, 슬라이드 생성 중 바로 참조할 핵심 옵션을 정리한다.

## 목차

1. 프레젠테이션 설정
2. Slide Master
3. 텍스트
4. 도형
5. 이미지
6. 차트
7. 표
8. 미디어
9. 내보내기
10. 디자인 패턴

## 프레젠테이션 설정

```javascript
const pptx = new PptxGenJS();

// Layout preset
pptx.layout = 'LAYOUT_WIDE';    // 13.33 x 7.5 inch, 권장 기본값
pptx.layout = 'LAYOUT_16x9';    // 10 x 5.625 inch
pptx.layout = 'LAYOUT_16x10';   // 10 x 6.25 inch
pptx.layout = 'LAYOUT_4x3';     // 10 x 7.5 inch

// Custom layout
pptx.defineLayout({ name: 'CUSTOM', width: 13.33, height: 7.5 });

// Metadata
pptx.author = 'Name';
pptx.company = 'Company';
pptx.subject = 'Subject';
pptx.title = 'Title';
```

## Slide Master

반복되는 배경, footer, logo, slide number를 master로 정의한다.

```javascript
pptx.defineSlideMaster({
  title: 'MASTER_TITLE',
  background: { color: '003366' },
  objects: [
    { rect: { x: 0, y: 6.9, w: '100%', h: 0.6, fill: { color: '003366' } } },
    { image: { x: 11.3, y: 0.2, w: 1.5, h: 0.5, path: 'logo.png' } },
    { text: {
        text: 'Confidential',
        options: { x: 0, y: 7.0, w: '100%', h: 0.4, fontSize: 8, color: 'FFFFFF', align: 'center' }
    }}
  ],
  slideNumber: { x: 12.5, y: 7.0, fontSize: 10, color: 'FFFFFF' }
});

const slide = pptx.addSlide({ masterName: 'MASTER_TITLE' });
```

## 텍스트

### 기본 텍스트

```javascript
slide.addText('제목 텍스트', {
  x: 1, y: 1, w: 10, h: 1,
  fontSize: 24,
  fontFace: 'Arial',
  color: '363636',
  bold: false,
  italic: false,
  underline: false,
  strike: false,
  align: 'left',
  valign: 'top',
  rotate: 0,
  isTextBox: true
});
```

주요 옵션:

| 속성 | 의미 |
|---|---|
| `x`, `y` | inch 단위 위치 |
| `w`, `h` | 크기. 숫자는 inch, 문자열은 percentage |
| `fontSize` | point 단위 폰트 크기 |
| `fontFace` | 폰트명 |
| `color` | `#` 없는 hex 색상 |
| `bold`, `italic`, `underline`, `strike` | 글자 스타일 |
| `align`, `valign` | 가로/세로 정렬 |
| `fill`, `line` | 배경과 테두리 |
| `shadow`, `glow` | 효과 |
| `margin` | text margin |
| `paraSpaceBefore`, `paraSpaceAfter` | 문단 앞/뒤 여백 |
| `lineSpacing`, `charSpacing` | 줄 간격과 자간 |
| `rectRadius` | 둥근 모서리 |
| `transparency` | 투명도 0-100 |
| `hyperlink` | `{ url: 'https://...', tooltip: 'Click' }` |

### Rich Text

```javascript
slide.addText([
  { text: '제목: ', options: { bold: true, fontSize: 28, color: '003366' } },
  { text: '부제목', options: { fontSize: 20, color: '666666' } },
  { text: '\n\n', options: { fontSize: 10 } },
  { text: '핵심 항목 1', options: { bullet: true, fontSize: 16 } },
  { text: '핵심 항목 2', options: { bullet: true, fontSize: 16 } },
  { text: '번호 항목', options: { bullet: { type: 'number' }, fontSize: 16 } }
], { x: 1, y: 1, w: 10, h: 5 });
```

### Bullet

```javascript
slide.addText([
  { text: '항목 A', options: { bullet: true } },
  { text: '항목 B', options: { bullet: true } },
  { text: '항목 C', options: { bullet: true } }
], { x: 1, y: 1, w: 5, h: 3, fontSize: 16 });

slide.addText([
  { text: '1단계', options: { bullet: { type: 'number' } } },
  { text: '2단계', options: { bullet: { type: 'number' } } }
], { x: 1, y: 1, w: 5, h: 2, fontSize: 16 });
```

## 도형

주요 shape type:

```javascript
pptx.ShapeType.rect
pptx.ShapeType.roundRect
pptx.ShapeType.ellipse
pptx.ShapeType.triangle
pptx.ShapeType.line
pptx.ShapeType.rightArrow
pptx.ShapeType.leftArrow
pptx.ShapeType.upArrow
pptx.ShapeType.downArrow
pptx.ShapeType.star5
pptx.ShapeType.diamond
pptx.ShapeType.hexagon
```

사용 예:

```javascript
slide.addShape(pptx.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 2.5,
  fill: { color: '003366' }
});

slide.addShape(pptx.ShapeType.ellipse, {
  x: 5, y: 3, w: 3, h: 3,
  fill: { color: 'FF6600', transparency: 30 },
  line: { color: 'FF6600', width: 2 }
});

slide.addText('바로 시작하기', {
  shape: pptx.ShapeType.roundRect,
  x: 4, y: 5, w: 4, h: 0.8,
  fill: { color: '0066CC' },
  color: 'FFFFFF',
  fontSize: 16,
  bold: true,
  align: 'center',
  valign: 'middle',
  rectRadius: 0.2
});
```

선 dash type:

```text
solid, dash, dashDot, lgDash, lgDashDot, lgDashDotDot, sysDash, sysDot
```

## 이미지

```javascript
slide.addImage({
  path: 'https://example.com/photo.jpg',
  x: 1, y: 1, w: 4, h: 3
});

slide.addImage({
  data: 'data:image/png;base64,iVBOR...',
  x: 1, y: 1, w: 4, h: 3
});

slide.addImage({
  path: 'https://example.com/logo.png',
  x: 0.5, y: 0.5, w: 2, h: 1,
  hyperlink: { url: 'https://example.com' }
});

slide.addImage({
  path: 'image.jpg',
  x: 1, y: 1, w: 4, h: 3,
  sizing: { type: 'cover', w: 4, h: 3 }
});
```

`sizing.type`은 `cover`, `contain`, `crop`을 사용할 수 있다.

## 차트

Chart type:

```javascript
pptx.ChartType.bar
pptx.ChartType.bar3d
pptx.ChartType.line
pptx.ChartType.pie
pptx.ChartType.pie3d
pptx.ChartType.doughnut
pptx.ChartType.area
pptx.ChartType.scatter
pptx.ChartType.bubble
pptx.ChartType.radar
```

Bar chart:

```javascript
slide.addChart(pptx.ChartType.bar, [
  { name: 'Series A', labels: ['Q1','Q2','Q3','Q4'], values: [100,200,300,400] },
  { name: 'Series B', labels: ['Q1','Q2','Q3','Q4'], values: [150,250,350,450] }
], {
  x: 1, y: 1.5, w: 10, h: 5,
  showTitle: true,
  title: '분기별 매출',
  showLegend: true,
  legendPos: 'b',
  showValue: true,
  chartColors: ['4472C4', 'ED7D31'],
  barDir: 'col',
  barGrouping: 'clustered'
});
```

Pie / doughnut:

```javascript
slide.addChart(pptx.ChartType.pie, [
  { name: 'Share', labels: ['A','B','C','D'], values: [40,30,20,10] }
], {
  x: 2, y: 1.5, w: 8, h: 5,
  showPercent: true,
  showLegend: true,
  legendPos: 'b',
  chartColors: ['4472C4', 'ED7D31', 'A5A5A5', 'FFC000'],
  dataLabelPosition: 'outEnd',
  showTitle: true,
  title: '시장 점유율'
});

slide.addChart(pptx.ChartType.doughnut, [/* ... */], {
  holeSize: 50
});
```

Line chart:

```javascript
slide.addChart(pptx.ChartType.line, [
  { name: '2024', labels: ['Jan','Feb','Mar','Apr','May','Jun'], values: [10,15,12,18,22,25] },
  { name: '2025', labels: ['Jan','Feb','Mar','Apr','May','Jun'], values: [12,18,16,22,28,32] }
], {
  x: 1, y: 1.5, w: 10, h: 5,
  lineSize: 3,
  lineSmooth: true,
  lineDataSymbol: 'circle',
  chartColors: ['0088CC', 'FF6600'],
  showLegend: true,
  showValue: false
});
```

## 표

기본 표:

```javascript
const rows = [
  ['항목', '값', '비고'],
  ['A', '1.2M', '+15%'],
  ['B', '800K', '-3%']
];

slide.addTable(rows, {
  x: 1, y: 1.5, w: 10,
  colW: [3, 3.5, 3.5],
  rowH: [0.5, 0.4, 0.4],
  fontSize: 12,
  border: { type: 'solid', pt: 1, color: 'CCCCCC' },
  align: 'left',
  valign: 'middle'
});
```

Cell별 스타일:

```javascript
const headerStyle = { bold: true, fill: { color: '003366' }, color: 'FFFFFF', fontSize: 13 };
const cellStyle = { fontSize: 11, color: '333333' };

const rows = [
  [
    { text: '제품', options: headerStyle },
    { text: '매출', options: headerStyle },
    { text: '성장률', options: headerStyle }
  ],
  [
    { text: 'Product A', options: cellStyle },
    { text: '$1.2M', options: { ...cellStyle, align: 'right' } },
    { text: '+15%', options: { ...cellStyle, align: 'right', color: '00AA00' } }
  ]
];
```

병합 cell:

```javascript
[
  [{ text: '통합 헤더', options: { colspan: 3, bold: true, align: 'center' } }],
  ['A열', 'B열', 'C열']
]
```

긴 표 auto-paging:

```javascript
slide.addTable(rows, {
  x: 0.5, y: 1.5, w: 9,
  autoPage: true,
  autoPageRepeatHeader: true,
  autoPageHeaderRows: 1
});
```

## 미디어

```javascript
slide.addMedia({
  type: 'online',
  link: 'https://www.youtube.com/embed/VIDEO_ID',
  x: 1, y: 1, w: 8, h: 4.5
});
```

## 내보내기

```javascript
pptx.writeFile({ fileName: 'Presentation.pptx' });

const base64 = await pptx.write({ outputType: 'base64' });
const blob = await pptx.write({ outputType: 'blob' });
const buffer = await pptx.write({ outputType: 'arraybuffer' });
const stream = await pptx.stream();
```

## 색상 규칙

PptxGenJS는 `#` 없는 6자리 hex를 사용한다.

- `003366`: dark blue
- `FFFFFF`: white
- `FF6600`: orange
- `00AA00`: green
- `333333`: dark gray

## 자주 쓰는 디자인 패턴

### 전체 폭 header bar

```javascript
slide.addShape(pptx.ShapeType.rect, {
  x: 0, y: 0, w: '100%', h: 1.5,
  fill: { color: '003366' }
});
slide.addText('섹션 제목', {
  x: 0.5, y: 0.25, w: 12, h: 1,
  fontSize: 32, color: 'FFFFFF', bold: true
});
```

### 2열 레이아웃

```javascript
slide.addText([...], { x: 0.5, y: 1.5, w: 6, h: 5 });
slide.addImage({ path: 'image.jpg', x: 7, y: 1.5, w: 5.5, h: 5 });
```

### Accent line

```javascript
slide.addShape(pptx.ShapeType.rect, {
  x: 1, y: 2.5, w: 2, h: 0.06,
  fill: { color: 'FF6600' }
});
```

### Card element

```javascript
slide.addShape(pptx.ShapeType.roundRect, {
  x: 1, y: 2, w: 3.5, h: 4,
  fill: { color: 'F8F9FA' },
  shadow: { type: 'outer', blur: 10, offset: 3, color: '000000', opacity: 0.15 },
  rectRadius: 0.1
});
slide.addText('카드 제목', { x: 1.3, y: 2.3, w: 3, h: 0.5, fontSize: 18, bold: true });
slide.addText('설명 텍스트', { x: 1.3, y: 3, w: 3, h: 2, fontSize: 12 });
```
