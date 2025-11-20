'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback, useState } from 'react';
import { medicalAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileImage, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ToastProvider';
import { DicomFileItem } from './DicomFileItem';
import { DicomInspector } from './DicomInspector';

interface DicomListProps {
  onConvert?: (filename: string) => void;
}

export function DicomList({ onConvert }: DicomListProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [convertingFile, setConvertingFile] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['dicom-files'],
    queryFn: () => medicalAPI.listDicomFiles(),
  });

  const convertMutation = useMutation({
    mutationFn: async (filename: string) => {
      setConvertingFile(filename);
      return medicalAPI.convertDicomFile(filename);
    },
    onSuccess: (data, filename) => {
      showToast(`Fichier ${filename} converti avec succès: ${data.png_filename}`, 'success');
      setConvertingFile(null);
      queryClient.invalidateQueries({ queryKey: ['png-files'] });
      queryClient.invalidateQueries({ queryKey: ['dicom-files'] });
    },
    onError: (error: any, filename) => {
      showToast(`Erreur lors de la conversion de ${filename}: ${error.response?.data?.detail || error.message}`, 'error');
      setConvertingFile(null);
    },
  });

  const handleConvert = useCallback((filename: string) => {
    if (onConvert) {
      onConvert(filename);
    } else {
      convertMutation.mutate(filename);
    }
  }, [onConvert, convertMutation]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Fichiers DICOM
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
            Fichiers DICOM
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">
            Erreur lors du chargement des fichiers DICOM
          </p>
        </CardContent>
      </Card>
    );
  }

  const dicomFiles = data?.files || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileImage className="h-5 w-5" />
          Fichiers DICOM ({dicomFiles.length})
        </CardTitle>
        <CardDescription>
          Fichiers DICOM disponibles pour conversion
        </CardDescription>
      </CardHeader>
      <CardContent>
        {dicomFiles.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FileImage className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Aucun fichier DICOM disponible</p>
            <p className="text-sm">Importez des fichiers depuis TCIA pour commencer</p>
          </div>
        ) : (
          <div className="space-y-3">
            {dicomFiles.map((file: any) => {
              const isConverting = convertingFile === file.filename;
              
              return (
                <div key={`dicom-wrapper-${file.filename}`} className="space-y-2">
                  <DicomFileItem
                    filename={file.filename}
                    size={file.size || 0}
                    isConverting={isConverting}
                    onConvert={handleConvert}
                  />
                  <div key={`inspector-${file.filename}`}>
                    <DicomInspector filename={file.filename} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

