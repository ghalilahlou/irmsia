'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileImage, Search, Loader2 } from 'lucide-react';
import axios from 'axios';

interface DicomInspectorProps {
  filename: string;
}

export function DicomInspector({ filename }: DicomInspectorProps) {
  const [isInspecting, setIsInspecting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dicom-info', filename],
    queryFn: async () => {
      const apiUrl = typeof window !== 'undefined' ? '/api/v1' : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/debug/dicom/${filename}/info`);
      return response.data;
    },
    enabled: isInspecting,
  });

  const handleInspect = useMemo(() => {
    return () => {
      setIsInspecting(true);
      refetch();
    };
  }, [refetch]);

  // Structure stable - toujours retourner un conteneur
  const content = useMemo(() => {
    if (!isInspecting) {
      return (
        <Button
          variant="outline"
          size="sm"
          onClick={handleInspect}
          className="w-full"
        >
          <Search className="h-4 w-4 mr-2" />
          Inspecter le DICOM
        </Button>
      );
    }

    if (isLoading) {
      return (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              Inspection DICOM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      );
    }

    if (error) {
      return (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileImage className="h-5 w-5" />
              Inspection DICOM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-destructive">
              Erreur lors de l'inspection: {error instanceof Error ? error.message : 'Erreur inconnue'}
            </p>
          </CardContent>
        </Card>
      );
    }

    const metadata = data?.metadata || {};
    const pixelStats = data?.pixel_stats || {};

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Inspection: {filename}
          </CardTitle>
          <CardDescription>
            Métadonnées et statistiques des pixels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Métadonnées</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">Modality:</span>
                <p className="font-medium">{metadata.modality || 'N/A'}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Taille:</span>
                <p className="font-medium">{metadata.rows}x{metadata.columns}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Bits:</span>
                <p className="font-medium">{metadata.bits_stored}/{metadata.bits_allocated}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Taille fichier:</span>
                <p className="font-medium">{(data?.file_size || 0) / 1024} KB</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Statistiques des Pixels</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Shape:</span>
                <span className="font-medium">{JSON.stringify(pixelStats.shape)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type:</span>
                <span className="font-medium">{pixelStats.dtype}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Min:</span>
                <span className="font-medium">{pixelStats.min}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Max:</span>
                <span className="font-medium">{pixelStats.max}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Moyenne:</span>
                <span className="font-medium">{pixelStats.mean?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Écart-type:</span>
                <span className="font-medium">{pixelStats.std?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Valeurs uniques:</span>
                <span className="font-medium">{pixelStats.unique_values_count} / {pixelStats.shape?.[0] * pixelStats.shape?.[1]}</span>
              </div>
              {pixelStats.is_likely_noise !== undefined && (
                <div className={`p-2 rounded ${pixelStats.is_likely_noise ? 'bg-yellow-100 dark:bg-yellow-900' : pixelStats.is_uniform ? 'bg-blue-100 dark:bg-blue-900' : 'bg-green-100 dark:bg-green-900'}`}>
                  <span className="font-semibold">
                    {pixelStats.is_likely_noise 
                      ? '⚠️ Probablement du bruit aléatoire' 
                      : pixelStats.is_uniform
                      ? 'ℹ️ Image uniforme (peu de variation)'
                      : '✅ Pattern structuré détecté'}
                  </span>
                  <div className="text-xs text-muted-foreground mt-1 space-y-1">
                    <p>Ratio valeurs uniques: {(pixelStats.unique_ratio * 100).toFixed(1)}%</p>
                    {pixelStats.std_ratio !== undefined && (
                      <p>Ratio écart-type: {(pixelStats.std_ratio * 100).toFixed(1)}%</p>
                    )}
                    {pixelStats.value_range !== undefined && (
                      <p>Plage de valeurs: {pixelStats.value_range.toFixed(0)}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }, [isInspecting, isLoading, error, data, filename, handleInspect]);

  return <div className="w-full">{content}</div>;
}
