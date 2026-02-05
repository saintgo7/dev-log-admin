'use client';

import * as React from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts';
import { DashboardLayout, CommitChart } from '@/components/dashboard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useOverviewStats, useTimelineStats } from '@/hooks/use-stats';
import { COMMIT_TYPE_LABELS } from '@/lib/constants';

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
  'hsl(142 76% 36%)',
  'hsl(346 84% 61%)',
  'hsl(47 96% 53%)',
];

export default function AnalyticsPage() {
  const { stats, loading: statsLoading } = useOverviewStats();
  const { timeline, loading: timelineLoading } = useTimelineStats(30);

  // Transform data for charts
  const chartData = React.useMemo(() => {
    if (!timeline?.timeline) return [];
    return [...timeline.timeline]
      .sort((a, b) => new Date(a.day).getTime() - new Date(b.day).getTime())
      .map((item) => ({
        date: item.day,
        commits: item.count,
      }));
  }, [timeline]);

  const commitsByTypeData = React.useMemo(() => {
    if (!stats?.commits_by_type) return [];
    return Object.entries(stats.commits_by_type)
      .map(([type, count]) => ({
        name: COMMIT_TYPE_LABELS[type] || type,
        value: count,
        type,
      }))
      .sort((a, b) => b.value - a.value);
  }, [stats]);

  const projectsData = React.useMemo(() => {
    if (!stats?.commits_by_project) return [];
    return stats.commits_by_project
      .sort((a, b) => b.commit_count - a.commit_count)
      .slice(0, 10);
  }, [stats]);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Detailed insights into your development activity.
          </p>
        </div>

        {/* Time-based Activity */}
        <CommitChart
          data={chartData}
          loading={timelineLoading}
          title="Commit Timeline"
          description="Your commit activity over the last 30 days"
        />

        {/* Charts Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Commits by Type */}
          <Card>
            <CardHeader>
              <CardTitle>Commits by Type</CardTitle>
              <CardDescription>Distribution of commit types</CardDescription>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-[300px] w-full" />
              ) : (
                <Tabs defaultValue="pie" className="space-y-4">
                  <TabsList>
                    <TabsTrigger value="pie">Pie</TabsTrigger>
                    <TabsTrigger value="bar">Bar</TabsTrigger>
                  </TabsList>
                  <TabsContent value="pie">
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={commitsByTypeData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) =>
                              `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                            }
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {commitsByTypeData.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <Tooltip
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                return (
                                  <div className="rounded-lg border bg-background p-2 shadow-sm">
                                    <p className="font-medium">{payload[0].name}</p>
                                    <p className="text-sm text-muted-foreground">
                                      {payload[0].value} commits
                                    </p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </TabsContent>
                  <TabsContent value="bar">
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={commitsByTypeData} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis type="number" className="text-xs text-muted-foreground" />
                          <YAxis
                            type="category"
                            dataKey="name"
                            width={80}
                            className="text-xs text-muted-foreground"
                          />
                          <Tooltip
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                return (
                                  <div className="rounded-lg border bg-background p-2 shadow-sm">
                                    <p className="font-medium">{payload[0].payload.name}</p>
                                    <p className="text-sm text-muted-foreground">
                                      {payload[0].value} commits
                                    </p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Bar dataKey="value" fill="hsl(var(--chart-1))" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </TabsContent>
                </Tabs>
              )}
            </CardContent>
          </Card>

          {/* Commits by Project */}
          <Card>
            <CardHeader>
              <CardTitle>Commits by Project</CardTitle>
              <CardDescription>Top projects by commit count</CardDescription>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-[300px] w-full" />
              ) : (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={projectsData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis
                        dataKey="name"
                        tickLine={false}
                        axisLine={false}
                        tickMargin={8}
                        className="text-xs text-muted-foreground"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis
                        tickLine={false}
                        axisLine={false}
                        tickMargin={8}
                        className="text-xs text-muted-foreground"
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            return (
                              <div className="rounded-lg border bg-background p-2 shadow-sm">
                                <p className="font-medium">{payload[0].payload.name}</p>
                                <p className="text-sm text-muted-foreground">
                                  {payload[0].value} commits
                                </p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar
                        dataKey="commit_count"
                        fill="hsl(var(--chart-2))"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Summary Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Summary Statistics</CardTitle>
            <CardDescription>Quick overview of your development metrics</CardDescription>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="grid gap-4 md:grid-cols-3">
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
                <Skeleton className="h-20" />
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">Total Projects</p>
                  <p className="text-3xl font-bold">{stats?.total_projects ?? 0}</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">Total Commits</p>
                  <p className="text-3xl font-bold">{stats?.total_commits ?? 0}</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-sm text-muted-foreground">Commit Types</p>
                  <p className="text-3xl font-bold">
                    {Object.keys(stats?.commits_by_type ?? {}).length}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
