'use client';

import * as React from 'react';
import { FolderGit2, GitCommit, Activity, TrendingUp } from 'lucide-react';
import {
  DashboardLayout,
  StatsCard,
  StatsCards,
  CommitChart,
  ProjectCard,
  ProjectCardSkeleton,
  ProjectGrid,
  RecentActivity,
} from '@/components/dashboard';
import { useProjects } from '@/hooks/use-projects';
import { useOverviewStats, useTimelineStats } from '@/hooks/use-stats';

export default function DashboardPage() {
  const { projects, loading: projectsLoading } = useProjects();
  const { stats, loading: statsLoading } = useOverviewStats();
  const { timeline, loading: timelineLoading } = useTimelineStats(30);

  // Transform timeline data for chart
  const chartData = React.useMemo(() => {
    if (!timeline?.timeline) return [];

    // Sort by date ascending and fill in missing days
    const sortedTimeline = [...timeline.timeline].sort(
      (a, b) => new Date(a.day).getTime() - new Date(b.day).getTime()
    );

    return sortedTimeline.map((item) => ({
      date: item.day,
      commits: item.count,
    }));
  }, [timeline]);

  // Calculate trend (compare last 7 days with previous 7 days)
  const commitTrend = React.useMemo(() => {
    if (!timeline?.timeline || timeline.timeline.length < 14) return null;

    const sorted = [...timeline.timeline].sort(
      (a, b) => new Date(b.day).getTime() - new Date(a.day).getTime()
    );

    const last7Days = sorted.slice(0, 7).reduce((sum, d) => sum + d.count, 0);
    const prev7Days = sorted.slice(7, 14).reduce((sum, d) => sum + d.count, 0);

    if (prev7Days === 0) return null;

    const percentChange = Math.round(((last7Days - prev7Days) / prev7Days) * 100);
    return {
      value: percentChange,
      label: 'from last week',
    };
  }, [timeline]);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to Dev Log Admin. Monitor your development activity.
          </p>
        </div>

        {/* Stats Cards */}
        <StatsCards>
          <StatsCard
            title="Total Projects"
            value={stats?.total_projects ?? 0}
            icon={FolderGit2}
            loading={statsLoading}
          />
          <StatsCard
            title="Total Commits"
            value={stats?.total_commits ?? 0}
            icon={GitCommit}
            trend={commitTrend ?? undefined}
            loading={statsLoading}
          />
          <StatsCard
            title="Features"
            value={stats?.commits_by_type?.feat ?? 0}
            icon={TrendingUp}
            description="Total feature commits"
            loading={statsLoading}
          />
          <StatsCard
            title="Bug Fixes"
            value={stats?.commits_by_type?.fix ?? 0}
            icon={Activity}
            description="Total bug fix commits"
            loading={statsLoading}
          />
        </StatsCards>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Chart - Takes 2 columns on large screens */}
          <div className="lg:col-span-2">
            <CommitChart
              data={chartData}
              loading={timelineLoading}
              title="Commit Activity"
              description="Commits over the last 30 days"
            />
          </div>

          {/* Recent Activity - Takes 1 column */}
          <div className="lg:col-span-1">
            <RecentActivity
              activities={stats?.recent_activity ?? []}
              loading={statsLoading}
            />
          </div>
        </div>

        {/* Projects Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold tracking-tight">Projects</h2>
            <p className="text-sm text-muted-foreground">
              {projects.length} project{projects.length !== 1 ? 's' : ''} registered
            </p>
          </div>

          <ProjectGrid>
            {projectsLoading
              ? Array.from({ length: 4 }).map((_, i) => <ProjectCardSkeleton key={i} />)
              : projects.map((project, index) => (
                  <ProjectCard key={project.id} project={project} index={index} />
                ))}
          </ProjectGrid>
        </div>
      </div>
    </DashboardLayout>
  );
}
