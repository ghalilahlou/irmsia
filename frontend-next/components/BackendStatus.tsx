'use client';

import React from 'react';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { healthAPI } from '@/lib/api';

export function BackendStatus() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: (query) => {
      const data = query.state.data as any;
      if (data?.error || data?.status === 'unavailable') {
        return 10000; // Vérifier toutes les 10 secondes si indisponible
      }
      return 30000; // Toutes les 30 secondes si disponible
    },
    retry: false,
    staleTime: 5000,
  });

  if (isLoading) {
    return null; // Ne rien afficher pendant le chargement initial
  }

  if (!health || health.error || health.status === 'unavailable') {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-4">
        <div className="flex items-start gap-3">
          <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-red-400 mb-1">Backend non disponible</h3>
            <p className="text-sm text-red-300/80 mb-2">
              {health?.message || 'Le serveur backend n\'est pas accessible. Veuillez démarrer le serveur backend.'}
            </p>
            <div className="text-xs text-red-300/60 space-y-1">
              <p>Pour démarrer le backend :</p>
              <code className="block bg-red-900/20 px-2 py-1 rounded mt-1">
                cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
              </code>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 mb-4">
      <div className="flex items-center gap-2">
        <CheckCircle className="w-4 h-4 text-green-400" />
        <span className="text-sm text-green-400">
          Backend connecté ({health.service || 'API'})
        </span>
      </div>
    </div>
  );
}

