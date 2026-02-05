// Application Constants

export const APP_NAME = 'Dev Log Admin';
export const APP_DESCRIPTION = 'Development Log Management Dashboard';

// Navigation Items
export const NAV_ITEMS = [
  {
    title: 'Home',
    href: '/',
    icon: 'Home',
  },
  {
    title: 'Projects',
    href: '/projects',
    icon: 'FolderGit2',
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: 'BarChart3',
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: 'Settings',
  },
] as const;

// Commit Type Labels
export const COMMIT_TYPE_LABELS: Record<string, string> = {
  feat: 'Feature',
  fix: 'Bug Fix',
  docs: 'Documentation',
  style: 'Style',
  refactor: 'Refactor',
  test: 'Test',
  chore: 'Chore',
  perf: 'Performance',
  build: 'Build',
  ci: 'CI/CD',
  revert: 'Revert',
  other: 'Other',
};

// Chart Colors
export const CHART_COLORS = {
  primary: 'hsl(var(--chart-1))',
  secondary: 'hsl(var(--chart-2))',
  tertiary: 'hsl(var(--chart-3))',
  quaternary: 'hsl(var(--chart-4))',
  quinary: 'hsl(var(--chart-5))',
};

// Breakpoints (matches Tailwind defaults)
export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

// API Configuration
export const API_CONFIG = {
  defaultLimit: 50,
  maxLimit: 100,
  defaultTimelineDays: 30,
};
