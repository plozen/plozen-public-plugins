---
name: app-design-skill
description: 웹앱, 모바일 앱, 관리자 화면, 대시보드, 설정, 마이페이지, 로그인, 데이터 테이블, 모달, 사이드시트 등 사용자가 실제로 조작하는 앱 UI나 컴포넌트를 설계/생성할 때 사용한다.
---

# Aegis 앱 UI 디자인 스킬

## 목적

마케팅 랜딩페이지가 아니라 사용자가 반복적으로 사용하는 앱 화면을 만든다. 기본 출력은 React Native + Expo + NativeWind v4 기반 `.tsx` 컴포넌트다.

## 기본 설정

- `DENSITY`: 4. 넓고 여유로운 앱 UI를 기본으로 하되, 업무 도구는 더 촘촘하게 조정할 수 있다.
- `MOTION`: 3. 앱 UI는 화려한 모션보다 즉각적인 반응이 중요하다.
- `THEME`: dark. 요청이나 제품 맥락에 따라 light/system으로 조정한다.

## 고정 기술 스택

- Framework: React Native + Expo SDK 54
- Styling: NativeWind v4.1 `className` 방식
- Font: Pretendard. Inter, Roboto, Noto Sans KR 금지
- Icons: `@expo/vector-icons` 또는 `react-native-vector-icons`. Solar 계열을 우선한다.
- Charts: 필요할 때만 `react-native-chart-kit` 또는 `victory-native`
- Animation: 복잡한 전환에만 `react-native-reanimated`. 단순 상태 변화는 `useState` 우선
- Output: 실제 프로젝트에 붙여 넣을 수 있는 완전한 `.tsx`
- 이모지 금지. 필요한 표시는 아이콘으로 대체한다.

## React Native 태그 규칙

HTML 태그를 `.tsx`에 섞지 않는다.

| HTML 개념 | React Native |
|---|---|
| `div` | `View` |
| `p`, `span`, `h1`-`h6` | `Text` |
| `img` | `Image` |
| `button` | `Pressable` |
| `input` | `TextInput` |
| `ul`, `ol` | `FlatList` 또는 `View` + `map` |
| `a` | `Pressable` + `onPress` |
| `form` | `View` |

NativeWind v4에서 `backdrop-blur`, CSS filter, 브라우저식 box-shadow는 그대로 쓸 수 없다. 반투명 배경, RN shadow class, 또는 명시적 라이브러리로 대체한다.

## 레이아웃 패턴

### 사이드바

대시보드, 관리자 패널, 앱 메인에 사용한다.

- 사이드바: `View className="w-60 absolute left-0 top-0 h-full bg-zinc-900"`
- 메인: `View className="flex-1 ml-60"`
- 모바일: 사이드바 숨김 + 햄버거 메뉴 + 조건부 렌더링

### 센터 폼

로그인, 회원가입, 온보딩에 사용한다.

- 외곽: `View className="flex-1 items-center justify-center bg-zinc-950"`
- 카드: `View className="w-full max-w-md px-6"`

### 설정/마이페이지

좌측 메뉴와 우측 내용을 나누고, 모바일에서는 세로 stack으로 접는다.

## 컴포넌트 원칙

### 카드

- 기본: `View className="bg-zinc-900 border border-white/8 rounded-xl p-6"`
- 반투명: `View className="bg-white/5 border border-white/10 rounded-xl"`
- Double-Bezel: 외부 wrapper와 내부 content container를 분리한다.

### 통계 카드

- 아이콘, 제목, 수치, 변화율을 함께 둔다.
- 숫자는 47,200, 4.87처럼 실제처럼 보이게 쓴다.
- 증가/감소는 색으로 구분한다. 증가 `text-emerald-400`, 감소 `text-red-400`.

### 리스트/테이블

- `FlatList` 또는 `ScrollView` + 반복 행 구조를 사용한다.
- hover 대신 `Pressable`의 pressed 상태로 피드백을 준다.
- header는 작은 uppercase label 또는 muted text로 처리한다.

### 폼

- `TextInput`에는 default, focused, error, disabled 상태를 구현한다.
- focus는 `onFocus`/`onBlur`와 `useState`로 border 색을 바꾼다.
- error는 빨간 border와 짧은 메시지를 함께 제공한다.

### 버튼

- 모든 버튼은 default, pressed, disabled, loading 상태를 가진다.
- loading에는 `ActivityIndicator`를 사용한다.
- `Pressable`의 `active:opacity-80` 또는 scale 피드백을 둔다.

```tsx
<Pressable
  onPress={handlePress}
  disabled={isLoading}
  className="bg-emerald-500 rounded-xl px-6 py-3 items-center active:opacity-80"
>
  {isLoading
    ? <ActivityIndicator color="white" size="small" />
    : <Text className="text-white font-semibold">저장</Text>
  }
</Pressable>
```

### 빈 상태

데이터가 없을 때는 아이콘, 짧은 안내 문구, 기본 액션을 제공한다. 예: "아직 데이터가 없어요. 첫 번째 항목을 추가해보세요."

## 색상 시스템

```text
앱 배경: zinc-950
사이드바: zinc-900
카드: zinc-800/50 또는 white/5
입력창: zinc-800

primary text: zinc-50
secondary text: zinc-400
muted text: zinc-600

accent: emerald-500 기본
대안: blue-500, amber-500, violet-500 중 하나만
border: white/8 - white/12
```

accent는 버튼, 활성 메뉴, focus ring, chart primary에만 사용한다.

## 금지 패턴

- 모든 카드가 같은 크기인 단조로운 grid
- 보라/파랑 AI gradient, neon glow, 순수 black
- Inter, Roboto, Noto Sans KR
- John Doe, example@email.com, Lorem Ipsum
- 1,000, 10,000 같은 둥근 숫자
- hover/focus/disabled/loading 상태 없는 인터랙션
- React Native 컴포넌트 안의 `div`, `p`, `button` 같은 HTML 태그

## 한국어 기준

- 버튼은 짧게: "저장", "취소", "삭제", "확인"
- 안내 문구는 자연스럽게: "변경 사항은 자동으로 저장됩니다"
- 이름 예시: 하윤서, 박도현, 이서진, 김하늘
- 이메일 예시: `hayun@example.com`

## DesignSystem.tsx

새 프로젝트나 컴포넌트 세트를 처음 설계할 때는 `DesignSystem.tsx`를 먼저 만든다. 화면 하나에서 색상, 타이포, spacing, 버튼, 입력, 카드, badge, list, empty state, modal을 확인하게 한다.

규칙:

- 개발 전용 화면으로 둔다. 필요하면 `__DEV__` 조건부로 노출한다.
- 실제 재사용 컴포넌트를 그대로 사용한다.
- 컴포넌트를 우회한 하드코딩 스타일을 금지한다.
- Expo Web으로 실행하고 브라우저 스크린샷으로 검증한다.

## 검증

1. Expo Web 실행: `npx expo start --web`
2. 로그인 없는 화면은 빠른 브라우저 검증, 로그인 필요한 화면은 세션 있는 Playwright 검증
3. 스크린샷, 모바일 폭, pressed/focused/loading/empty 상태를 확인
4. 디자인 변경은 design-reviewer 또는 동등한 독립 검토에 넘긴다.

## 출력 기준

- 생략 없는 완전한 `.tsx`
- 자리표시 문구만 있는 화면 금지
- import 구문 전부 포함
- 모든 인터랙티브 요소 상태 구현
- 새 컴포넌트 세트의 첫 출력물은 `DesignSystem.tsx`
- 길어지면 완성된 컴포넌트 경계에서 멈추고 이어쓰기 위치를 명확히 남긴다.
