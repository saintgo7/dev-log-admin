'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { GitCommit } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import type { RecentActivity as RecentActivityType } from '@/types';
import { COMMIT_TYPE_COLORS, CommitType } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface RecentActivityProps {
  activities: RecentActivityType[];
  loading?: boolean;
}

export function RecentActivity({ activities, loading = false }: RecentActivityProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-8 w-8 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest commits across all projects</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: index * 0.03 }}
              >
                <Link
                  href={`/projects/${activity.project_slug}`}
                  className="flex gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <GitCommit className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge
                        variant="outline"
                        className={`text-xs ${
                          COMMIT_TYPE_COLORS[activity.type as CommitType] ||
                          COMMIT_TYPE_COLORS.other
                        }`}
                      >
                        {activity.type}
                      </Badge>
                      <span className="text-xs text-muted-foreground truncate">
                        {activity.project_name}
                      </span>
                    </div>
                    <p className="text-sm font-medium line-clamp-1">{activity.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(activity.date), { addSuffix: true })}
                    </p>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
