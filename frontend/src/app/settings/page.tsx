'use client';

import * as React from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon, Monitor, Check } from 'lucide-react';
import { DashboardLayout } from '@/components/dashboard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

const themes = [
  { name: 'Light', value: 'light', icon: Sun },
  { name: 'Dark', value: 'dark', icon: Moon },
  { name: 'System', value: 'system', icon: Monitor },
] as const;

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your application preferences.
          </p>
        </div>

        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              Customize the look and feel of the application.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Theme Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Theme</label>
              <p className="text-sm text-muted-foreground">
                Select your preferred color scheme.
              </p>
              <div className="flex gap-4 pt-2">
                {themes.map((t) => (
                  <Button
                    key={t.value}
                    variant="outline"
                    className={cn(
                      'flex flex-col gap-2 h-auto py-4 px-6',
                      mounted && theme === t.value && 'border-primary bg-primary/5'
                    )}
                    onClick={() => setTheme(t.value)}
                  >
                    <t.icon className="h-5 w-5" />
                    <span>{t.name}</span>
                    {mounted && theme === t.value && (
                      <Check className="h-4 w-4 text-primary absolute top-2 right-2" />
                    )}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card>
          <CardHeader>
            <CardTitle>API Configuration</CardTitle>
            <CardDescription>
              Configure the backend API connection.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">API URL</label>
              <p className="text-sm text-muted-foreground">
                The backend API endpoint for data fetching.
              </p>
              <div className="flex items-center gap-2">
                <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm">
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'}
                </code>
                <span className="text-xs text-emerald-500 flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  Connected
                </span>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <label className="text-sm font-medium">Environment</label>
              <div className="flex items-center gap-2">
                <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm">
                  {process.env.NODE_ENV}
                </code>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* About */}
        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
            <CardDescription>
              Application information.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <p className="text-sm font-medium">Application</p>
                <p className="text-sm text-muted-foreground">Dev Log Admin</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium">Version</p>
                <p className="text-sm text-muted-foreground">2.0.0 (Next.js)</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium">Frontend</p>
                <p className="text-sm text-muted-foreground">
                  Next.js 16 + TypeScript + Tailwind CSS
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium">Backend</p>
                <p className="text-sm text-muted-foreground">FastAPI + SQLite</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
