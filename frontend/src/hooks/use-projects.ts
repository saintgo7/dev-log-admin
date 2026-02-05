'use client';

import * as React from 'react';
import { projectsApi } from '@/lib/api';
import type { Project, CommitsResponse } from '@/types';

interface UseProjectsReturn {
  projects: Project[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useProjects(): UseProjectsReturn {
  const [projects, setProjects] = React.useState<Project[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchProjects = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsApi.list();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch projects'));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
  };
}

interface UseProjectReturn {
  project: Project | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useProject(slug: string): UseProjectReturn {
  const [project, setProject] = React.useState<Project | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchProject = React.useCallback(async () => {
    if (!slug) return;

    try {
      setLoading(true);
      setError(null);
      const data = await projectsApi.get(slug);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch project'));
    } finally {
      setLoading(false);
    }
  }, [slug]);

  React.useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  return {
    project,
    loading,
    error,
    refetch: fetchProject,
  };
}

interface UseProjectCommitsParams {
  slug: string;
  limit?: number;
  offset?: number;
  type?: string;
  search?: string;
}

interface UseProjectCommitsReturn {
  data: CommitsResponse | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useProjectCommits({
  slug,
  limit = 50,
  offset = 0,
  type,
  search,
}: UseProjectCommitsParams): UseProjectCommitsReturn {
  const [data, setData] = React.useState<CommitsResponse | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchCommits = React.useCallback(async () => {
    if (!slug) return;

    try {
      setLoading(true);
      setError(null);
      const response = await projectsApi.getCommits(slug, { limit, offset, type, search });
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch commits'));
    } finally {
      setLoading(false);
    }
  }, [slug, limit, offset, type, search]);

  React.useEffect(() => {
    fetchCommits();
  }, [fetchCommits]);

  return {
    data,
    loading,
    error,
    refetch: fetchCommits,
  };
}
