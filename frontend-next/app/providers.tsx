'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { ToastProvider } from '@/components/ToastProvider';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            refetchOnWindowFocus: false,
            retry: (failureCount, error: any) => {
              // Ne pas réessayer si le backend n'est pas disponible
              if (error?.code === 'ECONNREFUSED' || error?.code === 'ERR_NETWORK') {
                return false;
              }
              return failureCount < 1; // Réessayer seulement 1 fois pour les autres erreurs
            },
            retryDelay: 2000,
            onError: (error: any) => {
              // Logger les erreurs mais ne pas spammer la console
              if (error?.code !== 'ECONNREFUSED' && error?.code !== 'ERR_NETWORK') {
                console.error('Query error:', error);
              }
            },
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>{children}</ToastProvider>
    </QueryClientProvider>
  );
}

