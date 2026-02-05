'use client';

import * as React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  GitCommit,
  ExternalLink,
  Terminal,
  Calendar,
  FileCode,
  Clock,
  Plus,
  Minus,
  Search,
  Filter,
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { DashboardLayout } from '@/components/dashboard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useProject, useProjectCommits } from '@/hooks/use-projects';
import { projectsApi } from '@/lib/api';
import { COMMIT_TYPE_COLORS, CommitType } from '@/types';
import { COMMIT_TYPE_LABELS } from '@/lib/constants';

export default function ProjectDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const { project, loading: projectLoading } = useProject(slug);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedTypes, setSelectedTypes] = React.useState<string[]>([]);

  const { data: commitsData, loading: commitsLoading } = useProjectCommits({
    slug,
    limit: 100,
    search: searchQuery || undefined,
    type: selectedTypes.length === 1 ? selectedTypes[0] : undefined,
  });

  const handleOpenHtml = async () => {
    try {
      await projectsApi.openHtml(slug);
    } catch (error) {
      console.error('Failed to open HTML:', error);
    }
  };

  const handleOpenTerminal = async () => {
    try {
      await projectsApi.openTerminal(slug);
    } catch (error) {
      console.error('Failed to open terminal:', error);
    }
  };

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  // Filter commits by selected types
  const filteredCommits = React.useMemo(() => {
    if (!commitsData?.commits) return [];
    if (selectedTypes.length === 0) return commitsData.commits;
    return commitsData.commits.filter((commit) => selectedTypes.includes(commit.type));
  }, [commitsData?.commits, selectedTypes]);

  if (projectLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-6 w-96" />
          <div className="grid gap-4 md:grid-cols-3">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!project) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-lg font-medium">Project not found</p>
          <Link href="/projects">
            <Button variant="link">Back to Projects</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Back Button */}
        <Link
          href="/projects"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Projects
        </Link>

        {/* Project Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
            {project.description && (
              <p className="text-muted-foreground max-w-2xl">{project.description}</p>
            )}
            {project.tech_stack && project.tech_stack.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2">
                {project.tech_stack.map((tech) => (
                  <Badge key={tech} variant="secondary">
                    {tech}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            {project.html_url && (
              <Button variant="outline" onClick={handleOpenHtml}>
                <ExternalLink className="h-4 w-4 mr-2" />
                Open HTML
              </Button>
            )}
            <Button variant="outline" onClick={handleOpenTerminal}>
              <Terminal className="h-4 w-4 mr-2" />
              Terminal
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Commits</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <GitCommit className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-bold">{project.total_commits}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Last Synced</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-muted-foreground" />
                <span className="text-lg font-medium">
                  {project.last_synced_at
                    ? formatDistanceToNow(new Date(project.last_synced_at), {
                        addSuffix: true,
                      })
                    : 'Never'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Commit Types</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1">
                {project.type_stats &&
                  Object.entries(project.type_stats)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 4)
                    .map(([type, count]) => (
                      <Badge
                        key={type}
                        variant="outline"
                        className={COMMIT_TYPE_COLORS[type as CommitType] || COMMIT_TYPE_COLORS.other}
                      >
                        {type}: {count}
                      </Badge>
                    ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Commits Section */}
        <Card>
          <CardHeader>
            <CardTitle>Commits</CardTitle>
            <CardDescription>
              {commitsData?.total ?? 0} commits in this project
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Filters */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search commits..."
                  className="pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="gap-2">
                    <Filter className="h-4 w-4" />
                    Type
                    {selectedTypes.length > 0 && (
                      <span className="ml-1 rounded-full bg-primary px-1.5 py-0.5 text-xs text-primary-foreground">
                        {selectedTypes.length}
                      </span>
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  {Object.entries(COMMIT_TYPE_LABELS).map(([type, label]) => (
                    <DropdownMenuCheckboxItem
                      key={type}
                      checked={selectedTypes.includes(type)}
                      onCheckedChange={() => toggleType(type)}
                    >
                      {label}
                    </DropdownMenuCheckboxItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Commits List */}
            <ScrollArea className="h-[500px]">
              {commitsLoading ? (
                <div className="space-y-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="flex gap-4 p-4 border rounded-lg">
                      <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-5 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-2 pr-4">
                  {filteredCommits.map((commit, index) => (
                    <motion.div
                      key={commit.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2, delay: index * 0.02 }}
                      className="flex gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        <GitCommit className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge
                            variant="outline"
                            className={
                              COMMIT_TYPE_COLORS[commit.type as CommitType] ||
                              COMMIT_TYPE_COLORS.other
                            }
                          >
                            {commit.type}
                          </Badge>
                          <span className="text-xs text-muted-foreground font-mono">
                            #{commit.log_number}
                          </span>
                        </div>
                        <p className="font-medium line-clamp-2">{commit.title}</p>
                        <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {format(new Date(commit.date), 'MMM d, yyyy HH:mm')}
                          </span>
                          <span className="flex items-center gap-1">
                            <FileCode className="h-3 w-3" />
                            {commit.files_changed} file{commit.files_changed !== 1 ? 's' : ''}
                          </span>
                          <span className="flex items-center gap-1 text-emerald-500">
                            <Plus className="h-3 w-3" />
                            {commit.lines_added}
                          </span>
                          <span className="flex items-center gap-1 text-red-500">
                            <Minus className="h-3 w-3" />
                            {commit.lines_deleted}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Empty State */}
              {!commitsLoading && filteredCommits.length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <p className="text-muted-foreground">No commits found</p>
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
