---
name: web-app-design
description: React, Next.js, Tailwind CSS 기반 웹앱 UI를 설계/구현할 때 사용한다. 관리자, SaaS 대시보드, CRM, 설정, 마이페이지, 데이터 테이블, 폼, 필터, 모달, 사이드시트, 반복 업무 화면에 사용하며 랜딩페이지는 landing-page-design, React Native/Expo 앱은 mobile-app-design을 사용한다.
---

# Aegis 웹앱 디자인 스킬

## 역할

마케팅 랜딩페이지가 아니라 사용자가 반복적으로 조작하는 웹앱 화면을 만든다. SaaS, 관리자, CRM, 운영 도구는 조용하고 스캔하기 쉬운 실무형 UI를 우선한다.

## 연결 스킬

- `design-quality`: 완성 화면이 평범하거나 AI 템플릿처럼 보일 때 품질 게이트로 함께 사용한다.
- `landing-page-design`: 제품 소개, 캠페인, 사전예약 등 전환 중심 랜딩은 이 스킬로 넘긴다.
- `mobile-app-design`: React Native/Expo 기반 모바일 앱 UI는 이 스킬로 넘긴다.

## 프로젝트 디자인 원본

프로젝트 저장소 안에서 작업 중이면 `DESIGN.md`를 디자인 원본으로 사용한다.

- 기존 `DESIGN.md` 또는 `design.md`가 있으면 먼저 읽고 웹앱 UI 규칙을 맞춘다.
- 둘 다 없고 새 화면/컴포넌트/디자인 시스템 변경이 프로젝트에 남는다면 `DESIGN.md`를 만든다.
- 새 `DESIGN.md`에는 제품 톤, 폰트, 색상 토큰, spacing, 컴포넌트 상태, 레이아웃 원칙, 접근성, 금지 패턴, 검증 기준을 기록한다.
- UI 구현 중 새 규칙이 생기면 코드만 바꾸지 말고 `DESIGN.md`도 함께 갱신한다.

## 기본 스택

- Framework: 기존 프로젝트의 스택을 우선한다. 새 산출물은 React + Tailwind 또는 Next.js + Tailwind를 기본으로 한다.
- Font: Pretendard. Inter, Roboto, Noto Sans KR 금지
- Icons: 프로젝트에 아이콘 라이브러리가 있으면 그것을 사용한다. 없으면 `lucide-react` 또는 Iconify Solar를 사용하되 버튼에는 텍스트보다 아이콘을 우선한다.
- Charts: 기존 라이브러리를 우선하고, 없으면 Recharts 또는 Tremor 계열을 검토한다.
- Output: 기존 프로젝트에 바로 붙는 컴포넌트/페이지 파일. 단일 HTML 요청은 `landing-page-design` 또는 `full-output`을 우선한다.

## 레이아웃 기준

- 운영 도구는 hero나 마케팅식 큰 카드보다 정보 구조를 우선한다.
- 좌측 내비게이션, 상단 필터, 메인 테이블/리스트, 우측 상세 패널 패턴을 자연스럽게 조합한다.
- 모바일에서는 사이드바를 숨기고, 핵심 액션과 필터를 sheet 또는 segmented control로 접는다.
- 카드 안에 카드를 중첩하지 않는다. 반복 항목, 모달, 독립 도구에만 카드를 사용한다.
- 고정 포맷 UI에는 `grid`, `minmax`, `aspect-ratio`, `min/max`로 안정적인 크기를 준다.

## 컴포넌트 기준

- 버튼: default, hover, active, focus-visible, disabled, loading 상태를 구현한다.
- 입력: label, hint/error, focused, disabled 상태를 구현한다.
- 테이블: 정렬, 필터, empty, loading, pagination 또는 virtualized list를 고려한다.
- 모달/사이드시트: 닫기, overlay, focus trap, escape, 모바일 높이 제한을 고려한다.
- 토글/체크박스/세그먼트/슬라이더/메뉴 등 익숙한 컨트롤을 적절히 사용한다.
- 아이콘 버튼에는 tooltip 또는 `aria-label`을 둔다.

## 색상과 밀도

- 배경은 `zinc`, `slate`, `stone` 중 하나의 neutral family로 통일한다.
- accent는 하나만 정하고 버튼, 활성 상태, focus ring에 제한적으로 사용한다.
- 업무용 UI는 `text-sm`, `leading-5`, `gap-2/3/4`, `rounded-md/lg` 중심으로 밀도를 유지한다.
- 본문/라벨/도움말의 contrast를 명확히 분리한다.
- 보라/파랑 AI gradient, neon glow, 의미 없는 glassmorphism을 피한다.

## 한국어 UX 문구

- 버튼은 짧게 쓴다. 예: "저장", "취소", "삭제", "초대", "내보내기".
- 상태 문구는 원인과 다음 행동을 말한다.
- Empty state는 짧은 설명과 한 가지 기본 액션을 제공한다.
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘, 정민준.
- 둥근 placeholder 숫자와 Lorem Ipsum을 쓰지 않는다.

## 접근성과 검증

- 폼 컨트롤에는 label 또는 `aria-label`을 둔다.
- 키보드 포커스가 보이고, 모달/메뉴는 keyboard navigation이 가능해야 한다.
- 텍스트가 버튼/카드/테이블 셀 안에서 넘치지 않는지 확인한다.
- 데스크톱과 모바일 폭에서 nav, toolbar, table, modal이 겹치지 않는지 Playwright 스크린샷으로 검증한다.
- 색상/간격/모션 품질은 필요하면 `design-quality` 기준으로 독립 점검한다.
