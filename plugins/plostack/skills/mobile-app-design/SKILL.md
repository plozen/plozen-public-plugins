---
name: mobile-app-design
description: React Native, Expo, NativeWind 기반 모바일 앱 화면이나 컴포넌트를 설계/생성할 때 사용한다. 로그인, 온보딩, 탭 화면, 설정, 마이페이지, 폼, 리스트, 모달 등 모바일 앱 UI 산출물에 사용하며 웹앱은 web-app-design, 랜딩페이지는 landing-page-design을 사용한다.
---

# Plostack 모바일 앱 디자인 스킬

## 역할

사용자가 반복적으로 조작하는 모바일 앱 화면을 만든다. 기본 출력은 React Native + Expo + NativeWind 기반 `.tsx` 컴포넌트다.

## 연결 스킬

- `design-quality`: 색상, 타이포그래피, 밀도, 카드, 모션, 한국어 문구를 프리미엄 기준으로 점검할 때 함께 사용한다.
- `web-app-design`: React/Next/Tailwind 기반 웹앱 UI는 이 스킬로 넘긴다.
- `landing-page-design`: 마케팅 랜딩페이지는 이 스킬로 넘긴다.

## 프로젝트 디자인 원본

프로젝트 저장소 안에서 작업 중이면 `DESIGN.md`를 디자인 원본으로 사용한다. 새 모바일 앱/주요 화면/포트폴리오용 앱 화면은 실제 앱 구현 전에 `design-gate-hook-harness`를 적용해 `Marketing Brief -> DESIGN.md -> pub mock -> screenshots -> design review -> implementation handoff` 흐름을 통과시킨다. 퍼블리싱/mock 원본은 `design-lab/pub/`, 캡처 산출물은 `design-lab/screenshots/`, 구현 handoff는 필요 시 `design-lab/handoff.md`에 둔다.

`design-lab/pub/`는 개발자가 바로 열어 구조/토큰/상태를 확인하는 raw publishing/artboard 원본이다. 디바이스 프레임, 손에 든 폰 합성, 배경 장식, 크몽 썸네일용 composite는 넣지 않는다. 썸네일이나 포트폴리오 이미지 합성이 필요하면 `kmong-thumbnail/`, `design-lab/composite/`처럼 별도 목적 폴더/페이지로 분리하고, `pub` 원본을 감싸서 덮어쓰지 않는다.

- 기존 `DESIGN.md` 또는 `design.md`가 있으면 먼저 읽고 모바일 앱 UI 규칙을 맞춘다.
- 둘 다 없고 새 앱 화면/컴포넌트 세트를 프로젝트에 추가한다면 `DESIGN.md`를 만든다.
- 새 `DESIGN.md`에는 모바일 화면 밀도, 색상, 타이포, spacing, 컴포넌트 상태, 접근성, 금지 패턴, 검증 기준을 기록한다.
- `DesignSystem.tsx`를 만들거나 바꾸면 `DESIGN.md`와 서로 어긋나지 않게 갱신한다.

## 고정 스택

- Framework: React Native + Expo SDK 54
- Styling: NativeWind v4.1 `className` 방식
- Font: Pretendard. Inter, Roboto, Noto Sans KR 금지
- Icons: `@expo/vector-icons` 또는 `react-native-vector-icons`. Solar 계열을 우선한다.
- Charts: 필요할 때만 `react-native-chart-kit` 또는 `victory-native`
- Animation: 복잡한 전환에만 `react-native-reanimated`. 단순 상태 변화는 `useState` 우선
- Output: 실제 프로젝트에 붙여 넣을 수 있는 완전한 `.tsx`. 단, design gate 단계의 브라우저 확인용 mock은 `design-lab/pub/`에 두고 캡처는 `design-lab/screenshots/`에 저장한다. `design-lab/pub/` 출력은 요청 폭의 순수 모바일 화면 원본이어야 하며 디바이스 목업으로 감싸지 않는다. 단일 repo/단일 포트폴리오 작업에서는 `design-lab/pub/<project-slug>/` 중첩을 기본값으로 쓰지 않는다.
- 이모지 금지. 필요한 표시는 아이콘으로 대체한다.

## React Native 규칙

HTML 태그를 `.tsx`에 섞지 않는다.

- `div` -> `View`
- `p`, `span`, `h1`-`h6` -> `Text`
- `img` -> `Image`
- `button` -> `Pressable`
- `input` -> `TextInput`
- `ul`, `ol` -> `FlatList` 또는 `View` + `map`
- `a` -> `Pressable` + `onPress`
- `form` -> `View`

NativeWind에서 `backdrop-blur`, CSS filter, 브라우저식 box-shadow는 그대로 쓸 수 없다. 반투명 배경, RN shadow class, 또는 명시적 라이브러리로 대체한다.

## UI 기준

- 모든 버튼은 default, pressed, disabled, loading 상태를 가진다.
- `TextInput`은 default, focused, error, disabled 상태를 구현한다.
- 리스트는 `FlatList` 또는 `ScrollView` + 반복 행 구조를 사용한다.
- 빈 상태는 아이콘, 짧은 안내 문구, 기본 액션을 포함한다.
- 통계는 실제처럼 보이는 숫자를 사용한다. 예: 47,200, 4.87, 98.7%.
- 업무 도구는 장식보다 스캔성, 반복 작업 속도, 정보 밀도를 우선한다.

## 모바일 화면 구조

- 기준 폭은 사용자 요청값을 따른다. 요청이 없으면 390px을 기본으로 보고, `Z Fold 5 folded`, `folded`, `344px` 요청이 있으면 344px 기준으로 설계/검증한다.
- bottom tab root 화면은 back button을 넣지 않는다. 탭 루트는 상단 title, 현재 위치 표시, primary action, bottom tab fixed/anchored 상태를 우선한다.
- task/detail/modal/secondary flow 화면은 back button이 필수다. back 위치는 좌상단 또는 safe-area header 안으로 통일하고, 닫기/저장/삭제 같은 보조 액션과 시각적으로 충돌시키지 않는다.
- bottom tab은 viewport 하단에 고정하거나 safe-area anchor로 유지한다. 스크롤 콘텐츠가 tab 아래로 가려지지 않게 하단 padding을 둔다.
- hero, status band, functional surface, list, detail section을 서로 다른 역할로 분리한다. 모든 정보를 같은 카드 컴포넌트로 감싸지 않는다.

## 카드 사용 기준

카드는 “하나의 독립된 데이터 묶음/결과/입력/선택지”를 담을 때만 쓴다. 시각적 여백을 만들기 위해 모든 section을 카드화하지 않는다.

- 카드가 맞는 경우: 신청 결과 요약, 개별 task, 장소/숙소/프로그램 항목, 사용자 입력 form group, 결제/견적 결과, 상태별 알림 묶음.
- 카드가 아닌 것이 맞는 경우: 앱 header, hero copy, section title, 설명 band, timeline/list container, sticky bottom action, navigation, 단순 라벨/메타 정보.
- 카드 유형은 2개 이상 섞는다. 예: outline card, filled surface, compact row, media tile, statistic chip, full-width functional surface.
- 카드 안의 카드, 같은 radius/그림자/테두리 반복, 동일한 3~5개 카드 grid/list만 이어지는 구조는 피한다.

## 기본 색상

- 앱 배경: `zinc-950`
- 사이드/탭 표면: `zinc-900`
- 카드: `zinc-800/50` 또는 `white/5`
- 입력창: `zinc-800`
- primary text: `zinc-50`
- secondary text: `zinc-400`
- accent: `emerald-500` 기본. 대안은 `blue-500`, `amber-500`, `violet-500` 중 하나만 사용
- border: `white/8` - `white/12`

accent는 버튼, 활성 메뉴, focus ring, chart primary에만 사용한다.

## DesignSystem.tsx

새 프로젝트나 컴포넌트 세트를 처음 설계할 때는 `DesignSystem.tsx`를 먼저 만든다.

- 개발 전용 화면으로 두고 필요하면 `__DEV__` 조건부로 노출한다.
- 실제 재사용 컴포넌트를 그대로 사용한다.
- 색상, 타이포, spacing, 버튼, 입력, 카드, badge, list, empty state, modal을 한 화면에서 확인한다.
- 컴포넌트를 우회한 하드코딩 스타일을 금지한다.

## 금지 패턴

- React Native 컴포넌트 안의 HTML 태그
- Inter, Roboto, Noto Sans KR
- John Doe, example@email.com, Lorem Ipsum
- 1,000, 10,000 같은 둥근 숫자
- hover 중심의 웹 전용 인터랙션
- 상태 없는 버튼/입력/모달
- 보라/파랑 AI gradient, neon glow, 순수 black
- `design-lab/pub/` 화면을 디바이스 mockup, 배경 합성, 썸네일 레이아웃으로 감싸기
- bottom tab root에 불필요한 back button을 넣거나, task/detail/modal flow에서 back button을 누락하기
- 모든 section/list/item을 같은 카드 UI로 처리하기

## 검증

1. Expo Web 실행: `npx expo start --web`
2. 모바일 폭은 요청값으로 확인한다. 요청이 없으면 390px, Z Fold 5 folded/344px 요청이면 344px screenshot을 기준으로 본다.
3. hero/header/status panel/list/bottom tab 간 overlap이 0px인지, 최소 좌우 여백이 16px 이상인지, text overflow가 없는지 확인한다.
4. bottom tab root는 back button 없음, task/detail/modal flow는 back button 있음, bottom tab은 fixed/anchored인지 확인한다.
5. pressed/focused/loading/error/empty 상태를 확인한다.
6. 로그인 없는 화면은 빠른 브라우저 검증, 로그인 필요한 화면은 세션 있는 Playwright 검증을 사용한다.
7. 디자인 변경 폭이 크면 `design-quality` 기준으로 독립 점검한다.
