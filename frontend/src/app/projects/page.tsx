'use client';

import * as React from 'react';
import { Search, Filter } from 'lucide-react';
import {
  DashboardLayout,
  ProjectCard,
  ProjectCardSkeleton,
  ProjectGrid,
} from '@/components/dashboard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useProjects } from '@/hooks/use-projects';

export default function ProjectsPage() {
  const { projects, loading } = useProjects();
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedTechStack, setSelectedTechStack] = React.useState<string[]>([]);

  // Get unique tech stacks
  const allTechStacks = React.useMemo(() => {
    const stacks = new Set<string>();
    projects.forEach((project) => {
      project.tech_stack?.forEach((tech) => stacks.add(tech));
    });
    return Array.from(stacks).sort();
  }, [projects]);

  // Filter projects
  const filteredProjects = React.useMemo(() => {
    return projects.filter((project) => {
      const matchesSearch =
        searchQuery === '' ||
        project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesTechStack =
        selectedTechStack.length === 0 ||
        selectedTechStack.some((tech) => project.tech_stack?.includes(tech));

      return matchesSearch && matchesTechStack;
    });
  }, [projects, searchQuery, selectedTechStack]);

  const toggleTechStack = (tech: string) => {
    setSelectedTechStack((prev) =>
      prev.includes(tech) ? prev.filter((t) => t !== tech) : [...prev, tech]
    );
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground">
            Browse and manage your development projects.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search projects..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Filter className="h-4 w-4" />
                Tech Stack
                {selectedTechStack.length > 0 && (
                  <span className="ml-1 rounded-full bg-primary px-1.5 py-0.5 text-xs text-primary-foreground">
                    {selectedTechStack.length}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 max-h-64 overflow-auto">
              {allTechStacks.map((tech) => (
                <DropdownMenuCheckboxItem
                  key={tech}
                  checked={selectedTechStack.includes(tech)}
                  onCheckedChange={() => toggleTechStack(tech)}
                >
                  {tech}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Results count */}
        <p className="text-sm text-muted-foreground">
          Showing {filteredProjects.length} of {projects.length} project
          {projects.length !== 1 ? 's' : ''}
        </p>

        {/* Projects Grid */}
        <ProjectGrid>
          {loading
            ? Array.from({ length: 8 }).map((_, i) => <ProjectCardSkeleton key={i} />)
            : filteredProjects.map((project, index) => (
                <ProjectCard key={project.id} project={project} index={index} />
              ))}
        </ProjectGrid>

        {/* Empty State */}
        {!loading && filteredProjects.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-lg font-medium">No projects found</p>
            <p className="text-muted-foreground">
              {searchQuery || selectedTechStack.length > 0
                ? 'Try adjusting your filters'
                : 'Add your first project to get started'}
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
