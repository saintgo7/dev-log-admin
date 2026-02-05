'use client';

import * as React from 'react';
import { statsApi } from '@/lib/api';
import type { OverviewStats, TimelineStats } from '@/types';

interface UseOverviewStatsReturn {
  stats: OverviewStats | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useOverviewStats(): UseOverviewStatsReturn {
  const [stats, setStats] = React.useState<OverviewStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchStats = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await statsApi.overview();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch stats'));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
}

interface UseTimelineStatsReturn {
  timeline: TimelineStats | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useTimelineStats(days: number = 30): UseTimelineStatsReturn {
  const [timeline, setTimeline] = React.useState<TimelineStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchTimeline = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await statsApi.timeline(days);
      setTimeline(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch timeline'));
    } finally {
      setLoading(false);
    }
  }, [days]);

  React.useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  return {
    timeline,
    loading,
    error,
    refetch: fetchTimeline,
  };
}
