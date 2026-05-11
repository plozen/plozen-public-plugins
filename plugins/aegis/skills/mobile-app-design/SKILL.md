---
name: mobile-app-design
description: React Native, Expo, NativeWind 기반 모바일 앱 화면이나 컴포넌트를 설계/생성할 때 사용한다. 로그인, 온보딩, 탭 화면, 설정, 마이페이지, 폼, 리스트, 모달 등 모바일 앱 UI 산출물에 사용하며 웹앱은 web-app-design, 랜딩페이지는 landing-page-design을 사용한다.
---

# Aegis 모바일 앱 디자인 스킬

## 역할

사용자가 반복적으로 조작하는 모바일 앱 화면을 만든다. 기본 출력은 React Native + Expo + NativeWind 기반 `.tsx` 컴포넌트다.

## 연결 스킬

- `design-quality`: 색상, 타이포그래피, 밀도, 카드, 모션, 한국어 문구를 프리미엄 기준으로 점검할 때 함께 사용한다.
- `web-app-design`: React/Next/Tailwind 기반 웹앱 UI는 이 스킬로 넘긴다.
- `landing-page-design`: 마케팅 랜딩페이지는 이 스킬로 넘긴다.

## 프로젝트 디자인 원본

프로젝트 저장소 안에서 작업 중이면 `DESIGN.md`를 디자인 원본으로 사용한다.

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
- Output: 실제 프로젝트에 붙여 넣을 수 있는 완전한 `.tsx`
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

## 검증

1. Expo Web 실행: `npx expo start --web`
2. 모바일 폭, pressed/focused/loading/error/empty 상태를 확인한다.
3. 로그인 없는 화면은 빠른 브라우저 검증, 로그인 필요한 화면은 세션 있는 Playwright 검증을 사용한다.
4. 디자인 변경 폭이 크면 `design-quality` 기준으로 독립 점검한다.
