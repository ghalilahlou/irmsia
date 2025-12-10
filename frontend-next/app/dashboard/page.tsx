'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { healthAPI } from '@/lib/api';
import { auth } from '@/lib/auth';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Server, Shield, Zap } from 'lucide-react';
import { BackendStatus } from '@/components/BackendStatus';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    if (!auth.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const { data: health, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: (query) => {
      // Ne pas refetch automatiquement si le backend n'est pas disponible
      const data = query.state.data as any;
      if (data?.error || data?.status === 'unavailable') {
        return false; // Désactiver le refetch automatique
      }
      return 30000; // Every 30 seconds si disponible
    },
    retry: 1, // Réessayer seulement 1 fois
    retryDelay: 2000, // Attendre 2 secondes avant de réessayer
    staleTime: 10000, // Considérer les données comme fraîches pendant 10 secondes
  });

  if (!auth.isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to IRMSIA Medical AI Platform
          </p>
        </div>

        {/* Backend Status Banner */}
        <BackendStatus />

        {/* Health Status */}
        {health && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
            <Card className={health.error ? 'border-red-500' : ''}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Status</CardTitle>
                <Activity className={`h-4 w-4 ${health.error ? 'text-red-500' : 'text-muted-foreground'}`} />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  health.error || health.status === 'unavailable' 
                    ? 'text-red-600' 
                    : 'text-green-600'
                }`}>
                  {health.status === 'unavailable' ? 'Indisponible' : health.status}
                </div>
                <p className="text-xs text-muted-foreground">
                  Service: {health.service}
                </p>
                {health.error && (
                  <p className="text-xs text-red-500 mt-1">
                    {health.message}
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Version</CardTitle>
                <Server className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{health.version}</div>
                <p className="text-xs text-muted-foreground">API Version</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">AI Provider</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {health.components?.ai || 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">AI Service</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Blockchain</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {health.components?.blockchain || 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">Blockchain Status</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <a
                href="/medical"
                className="p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <h3 className="font-semibold mb-2">Analyse Médicale</h3>
                <p className="text-sm text-muted-foreground">
                  Upload DICOM, conversion PNG, et analyse LLM
                </p>
              </a>
              <a
                href="/logs"
                className="p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <h3 className="font-semibold mb-2">View Audit Logs</h3>
                <p className="text-sm text-muted-foreground">
                  Review blockchain access logs
                </p>
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

