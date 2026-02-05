// API Response Types for Dev Log Admin

export interface Project {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  repository_url: string | null;
  tech_stack: string[];
  html_url: string | null;
  total_commits: number;
  last_synced_at: string | null;
  created_at?: string;
  updated_at?: string;
  type_stats?: Record<string, number>;
}

export interface Commit {
  id: number;
  log_number: number;
  commit_hash: string;
  type: string;
  title: string;
  author_name: string;
  author_email?: string;
  date: string;
  files_changed: number;
  lines_added: number;
  lines_deleted: number;
  full_content?: string;
  project_slug?: string;
  project_name?: string;
}

export interface CommitsResponse {
  total: number;
  limit: number;
  offset: number;
  commits: Commit[];
}

export interface SearchResult {
  total: number;
  limit: number;
  offset: number;
  query: string;
  results: Commit[];
}

export interface OverviewStats {
  total_projects: number;
  total_commits: number;
  commits_by_type: Record<string, number>;
  recent_activity: RecentActivity[];
  commits_by_project: ProjectStats[];
}

export interface RecentActivity {
  id: number;
  log_number: number;
  title: string;
  type: string;
  date: string;
  project_slug: string;
  project_name: string;
}

export interface ProjectStats {
  name: string;
  slug: string;
  commit_count: number;
}

export interface TimelineStats {
  days: number;
  timeline: TimelineDay[];
}

export interface TimelineDay {
  day: string;
  count: number;
  types: string;
}

// Commit Types for badges
export type CommitType =
  | 'feat'
  | 'fix'
  | 'docs'
  | 'style'
  | 'refactor'
  | 'test'
  | 'chore'
  | 'perf'
  | 'build'
  | 'ci'
  | 'revert'
  | 'other';

export const COMMIT_TYPE_COLORS: Record<CommitType, string> = {
  feat: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
  fix: 'bg-red-500/10 text-red-500 border-red-500/20',
  docs: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  style: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  refactor: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  test: 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
  chore: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
  perf: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  build: 'bg-indigo-500/10 text-indigo-500 border-indigo-500/20',
  ci: 'bg-pink-500/10 text-pink-500 border-pink-500/20',
  revert: 'bg-rose-500/10 text-rose-500 border-rose-500/20',
  other: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
};
