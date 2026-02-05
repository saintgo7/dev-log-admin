'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { GitCommit, ExternalLink, Terminal, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import type { Project } from '@/types';
import { projectsApi } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface ProjectCardProps {
  project: Project;
  index?: number;
}

export function ProjectCard({ project, index = 0 }: ProjectCardProps) {
  const [isHovered, setIsHovered] = React.useState(false);

  const handleOpenHtml = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await projectsApi.openHtml(project.slug);
    } catch (error) {
      console.error('Failed to open HTML:', error);
    }
  };

  const handleOpenTerminal = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await projectsApi.openTerminal(project.slug);
    } catch (error) {
      console.error('Failed to open terminal:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Link href={`/projects/${project.slug}`}>
        <Card className="h-full transition-all duration-200 hover:shadow-lg hover:border-primary/50 cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <CardTitle className="text-lg line-clamp-1">{project.name}</CardTitle>
                <CardDescription className="line-clamp-2 min-h-[2.5rem]">
                  {project.description || 'No description'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Tech Stack */}
            {project.tech_stack && project.tech_stack.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {project.tech_stack.slice(0, 4).map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
                {project.tech_stack.length > 4 && (
                  <Badge variant="outline" className="text-xs">
                    +{project.tech_stack.length - 4}
                  </Badge>
                )}
              </div>
            )}

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-1">
                      <GitCommit className="h-4 w-4" />
                      <span>{project.total_commits}</span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>Total commits</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {project.last_synced_at && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span className="text-xs">
                          {formatDistanceToNow(new Date(project.last_synced_at), {
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>Last synced</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
            </div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              className="flex gap-2 pt-2"
            >
              {project.html_url && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={handleOpenHtml}
                >
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Open HTML
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={handleOpenTerminal}
              >
                <Terminal className="h-4 w-4 mr-1" />
                Terminal
              </Button>
            </motion.div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}

// Loading Skeleton
export function ProjectCardSkeleton() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-full mt-2" />
        <Skeleton className="h-4 w-2/3" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-1">
          <Skeleton className="h-5 w-14" />
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-12" />
        </div>
        <div className="flex gap-4">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

// Project Grid
interface ProjectGridProps {
  children: React.ReactNode;
  className?: string;
}

export function ProjectGrid({ children, className }: ProjectGridProps) {
  return (
    <div
      className={`grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 ${className || ''}`}
    >
      {children}
    </div>
  );
}
