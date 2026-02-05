# Phase 1: UI/UX Redesign

## 🎯 목표

현대적이고 프로페셔널한 SaaS UI로 전환

## 📋 Task List

### 1. Next.js 14 Setup (1-2시간)
```bash
feature/phase1-nextjs-setup
```
- [ ] Next.js 14 + TypeScript 초기화
- [ ] App Router 구조 설정
- [ ] 기본 레이아웃 구성
- [ ] 기존 FastAPI와 연동 확인

### 2. Tailwind CSS + shadcn/ui (2-3시간)
```bash
feature/phase1-tailwind-config
```
- [ ] Tailwind CSS 설치 및 설정
- [ ] shadcn/ui 설치
- [ ] 디자인 토큰 설정 (colors, spacing)
- [ ] 기본 컴포넌트 추가 (Button, Card, Input)

### 3. Sidebar Layout (3-4시간)
```bash
feature/phase1-sidebar-layout
```
- [ ] Sidebar 네비게이션 컴포넌트
- [ ] Topbar (유저 메뉴, 검색)
- [ ] Main content area
- [ ] Responsive 처리

### 4. Dark Mode (2-3시간)
```bash
feature/phase1-dark-mode
```
- [ ] next-themes 설정
- [ ] Light/Dark 토글
- [ ] 색상 시스템 정의
- [ ] localStorage 저장

### 5. Dashboard Redesign (4-5시간)
```bash
feature/phase1-dashboard
```
- [ ] Stats cards 리디자인
- [ ] Chart 업그레이드 (Recharts)
- [ ] Project grid 개선
- [ ] Loading states, Empty states

### 6. Project Detail Page (3-4시간)
```bash
feature/phase1-project-detail
```
- [ ] 프로젝트 헤더
- [ ] Commit timeline
- [ ] Stats visualization
- [ ] File changes view

### 7. Responsive Design (2-3시간)
```bash
feature/phase1-responsive
```
- [ ] Mobile: 햄버거 메뉴
- [ ] Tablet: 사이드바 접기/펴기
- [ ] Desktop: 고정 사이드바
- [ ] 모든 페이지 테스트

### 8. Animations (1-2시간)
```bash
feature/phase1-animations
```
- [ ] Framer Motion 설치
- [ ] 페이지 전환 애니메이션
- [ ] 로딩 애니메이션
- [ ] Hover effects

## 🎨 Design System

### Colors

```typescript
// tailwind.config.ts
colors: {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    900: '#1e3a8a',
  },
  // ... 전체 팔레트
}
```

### Components

- Button (primary, secondary, ghost, danger)
- Card (default, bordered, hoverable)
- Input (text, search, password)
- Badge (default, success, warning, error)
- Avatar (user, team)
- Dropdown
- Modal/Dialog
- Toast/Alert

### Layout

```
┌────────────────────────────────────┐
│ Sidebar  │ Main Content            │
│ (240px)  │                         │
│          │  Topbar                 │
│  Nav     │  ─────────────────────  │
│  Items   │                         │
│          │  Stats Cards            │
│          │  ┌────┐ ┌────┐ ┌────┐  │
│          │  │ 📊 │ │ 📈 │ │ 🎯 │  │
│          │  └────┘ └────┘ └────┘  │
│          │                         │
│          │  Chart Area             │
│          │  ┌──────────────────┐   │
│          │  │                  │   │
│          │  └──────────────────┘   │
│          │                         │
│          │  Project Grid           │
└────────────────────────────────────┘
```

## 🚀 Getting Started

### 1. Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/phase1-nextjs-setup
```

### 2. Initialize Next.js

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install
```

### 3. Install Dependencies

```bash
# shadcn/ui
npx shadcn-ui@latest init

# Icons
npm install lucide-react

# Charts
npm install recharts

# Dark mode
npm install next-themes

# Animations
npm install framer-motion

# Date formatting
npm install date-fns
```

### 4. Project Structure

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── signup/
│   ├── (dashboard)/
│   │   ├── layout.tsx         # Sidebar layout
│   │   ├── page.tsx           # Dashboard
│   │   ├── projects/
│   │   │   ├── page.tsx       # Project list
│   │   │   └── [slug]/
│   │   │       └── page.tsx   # Project detail
│   │   ├── analytics/
│   │   └── settings/
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Landing
├── components/
│   ├── ui/                    # shadcn components
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── topbar.tsx
│   │   ├── stats-card.tsx
│   │   └── commit-chart.tsx
│   └── projects/
│       ├── project-card.tsx
│       └── commit-list.tsx
├── lib/
│   ├── api.ts                 # API client
│   ├── utils.ts
│   └── constants.ts
├── hooks/
│   ├── use-projects.ts
│   └── use-commits.ts
├── types/
│   └── index.ts
└── styles/
    └── globals.css
```

## 📊 Progress Tracking

| Task | Branch | Status | Assignee |
|------|--------|--------|----------|
| Next.js Setup | `feature/phase1-nextjs-setup` | ⬜ Todo | - |
| Tailwind Config | `feature/phase1-tailwind-config` | ⬜ Todo | - |
| Sidebar Layout | `feature/phase1-sidebar-layout` | ⬜ Todo | - |
| Dark Mode | `feature/phase1-dark-mode` | ⬜ Todo | - |
| Dashboard | `feature/phase1-dashboard` | ⬜ Todo | - |
| Project Detail | `feature/phase1-project-detail` | ⬜ Todo | - |
| Responsive | `feature/phase1-responsive` | ⬜ Todo | - |
| Animations | `feature/phase1-animations` | ⬜ Todo | - |

## 🎯 Definition of Done

### Per Task
- [ ] 코드가 로컬에서 정상 동작
- [ ] TypeScript 에러 없음
- [ ] ESLint 에러 없음
- [ ] 데스크탑/태블릿/모바일 테스트
- [ ] PR 생성 및 리뷰 완료
- [ ] develop에 머지

### Phase 1 Complete
- [ ] 모든 8개 태스크 완료
- [ ] 전체 UI가 새 디자인으로 전환
- [ ] 다크모드 정상 작동
- [ ] 반응형 완벽 지원
- [ ] 성능 최적화 (Lighthouse 90+)
- [ ] 문서 업데이트

## 📚 References

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)
- [Framer Motion](https://www.framer.com/motion/)

## 🚦 Start Now

```bash
cd ~/dev-log-admin
git checkout develop
git pull origin develop
git checkout -b feature/phase1-nextjs-setup
```

**Let's build! 🚀**
