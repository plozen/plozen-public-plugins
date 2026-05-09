---
name: full-output-skill
description: 랜딩페이지, HTML 산출물, 긴 코드 결과가 중간 생략/placeholder/스켈레톤으로 끝날 위험이 있거나 완성된 단일 파일 출력을 강제해야 할 때 사용한다.
---

# Aegis 완전 출력 강제 규칙

## 기본 원칙

랜딩페이지 생성은 production-critical 작업으로 본다. 일부만 출력한 결과는 실패한 결과다. 사용자가 랜딩페이지나 완전한 HTML 파일을 요청하면 모든 섹션, 애니메이션, 반응형 breakpoint, 실제 콘텐츠를 생략 없이 작성한다.

## 금지 출력 패턴

코드 블록 안에서 금지:

- `<!-- ... -->`
- `<!-- rest of sections -->`
- `<!-- similar to above -->`
- `<!-- add more sections as needed -->`
- `<!-- TODO -->`
- `// ...`
- 생략을 뜻하는 단독 `...`

설명 문장에서 금지:

- "계속하려면 알려주세요"
- "필요하면 더 추가할 수 있습니다"
- "간단히 hero만 보여드리겠습니다"
- "나머지도 같은 패턴입니다"
- "직접 커스터마이즈하세요"

구조적 shortcut 금지:

- 전체 페이지 요청에 hero만 출력
- 중간 섹션을 건너뛰고 첫/마지막 섹션만 출력
- 반복 섹션을 예시 하나와 설명으로 대체
- HTML을 써야 할 위치에 설명만 작성
- 완성 페이지 요청에 skeleton/wireframe만 제공

## 실행 절차

1. 범위 고정: 요청을 읽고 필요한 섹션/컴포넌트 수를 센다. 랜딩페이지의 최소 구성은 nav, hero, social proof, features, testimonials, CTA, footer다.
2. 완전 작성: 모든 섹션에 반응형 클래스, 모션, 실제 한국어 콘텐츠, 적절한 Iconify Solar 아이콘을 채운다.
3. 교차 점검: `<!DOCTYPE html>`부터 `</html>`까지 닫혔는지, 7개 이상 섹션이 실제 콘텐츠로 채워졌는지 확인한다.

## 출력이 길어질 때

토큰 한계가 가까워져도 남은 섹션을 압축하거나 footer로 건너뛰지 않는다. 완성된 `</section>` 같은 안전한 경계까지만 작성하고 아래 문구로 멈춘다.

```text
[일시 중단 - 전체 Y개 섹션 중 X개 완료. "계속"을 입력하면 다음 섹션 이름부터 이어서 작성합니다.]
```

사용자가 "계속"이라고 하면 다음 `<section>`부터 바로 이어 쓴다. 요약, 재출력, `<head>` 반복은 하지 않는다.

## 완성 기준

필수 요소:

- `<!DOCTYPE html>`과 `<html lang="ko">`
- meta tags, Tailwind CDN, Pretendard font, Iconify, `tailwind.config`
- Navigation
- Hero
- trust/social proof 요소 1개 이상
- features 3-5개 이상
- testimonials 또는 case studies
- primary CTA
- footer
- `IntersectionObserver` 기반 스크롤 애니메이션
- 완전한 `</html>` 종료 태그

품질 기준:

- 모든 섹션에 placeholder가 아닌 실제 한국어 콘텐츠가 있다.
- 모든 섹션에 `sm:`, `md:`, `lg:` 등 반응형 처리가 있다.
- 모든 인터랙티브 요소에 hover/active/focus 상태가 있다.
- 모든 이미지는 유효한 `src`, 한국어 `alt`, 필요한 `loading="lazy"`를 가진다.
- 모든 아이콘은 `<iconify-icon icon="solar:..."></iconify-icon>` 형식을 따른다.

## 최종 점검

- 금지 패턴이 결과물 안에 없는가?
- HTML이 처음부터 끝까지 실행 가능한 단일 파일인가?
- 요청된 모든 섹션이 생략 없이 채워졌는가?
- 코드 블록이 설명이 아니라 실제 실행 가능한 코드인가?
- 보이는 모든 문구가 자연스러운 한국어인가?
