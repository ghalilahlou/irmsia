'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { medicalAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileImage, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ToastProvider';

export function DicomUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { showToast } = useToast();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      return medicalAPI.uploadDicom(file);
    },
    onSuccess: (data) => {
      showToast(`Fichier DICOM uploadé et converti: ${data.png_filename}`, 'success');
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('dicom-file') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Erreur lors de l\'upload', 'error');
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.dcm') && !file.name.toLowerCase().endsWith('.dicom')) {
        showToast('Le fichier doit être un DICOM (.dcm ou .dicom)', 'error');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) {
      showToast('Veuillez sélectionner un fichier', 'error');
      return;
    }
    uploadMutation.mutate(selectedFile);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileImage className="h-5 w-5" />
          Upload DICOM
        </CardTitle>
        <CardDescription>
          Téléversez un fichier DICOM pour le convertir en PNG
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <input
            id="dicom-file"
            type="file"
            accept=".dcm,.dicom"
            onChange={handleFileChange}
            className="hidden"
          />
          <label
            htmlFor="dicom-file"
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 cursor-pointer"
          >
            <Upload className="h-4 w-4 mr-2" />
            Choisir un fichier DICOM
          </label>
          {selectedFile && (
            <span className="text-sm text-muted-foreground">
              {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </span>
          )}
        </div>
        {selectedFile && (
          <Button
            onClick={handleUpload}
            disabled={uploadMutation.isPending}
            className="w-full"
          >
            {uploadMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Upload en cours...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Uploader et convertir
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

