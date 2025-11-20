'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DicomUploader } from '@/components/DicomUploader';
import { DicomList } from '@/components/DicomList';
import { ImageList } from '@/components/ImageList';
import { AnalyzeButton } from '@/components/AnalyzeButton';
import { Button } from '@/components/ui/button';
import { Download, RefreshCw } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { medicalAPI } from '@/lib/api';
import { useToast } from '@/components/ToastProvider';
import { Navbar } from '@/components/Navbar';
import { auth } from '@/lib/auth';

export default function MedicalPage() {
  const router = useRouter();
  const [selectedImage, setSelectedImage] = useState<string | undefined>();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const authenticated = auth.isAuthenticated();
      setIsAuthenticated(authenticated);
      if (!authenticated) {
        router.push('/login');
      }
    };
    checkAuth();
  }, [router]);

  const importMutation = useMutation({
    mutationFn: () => medicalAPI.importTciaDicoms(),
    onSuccess: (data) => {
      showToast(`${data.files?.length || 0} fichiers téléchargés depuis TCIA`, 'success');
      // Refresh lists
      queryClient.invalidateQueries({ queryKey: ['png-files'] });
      queryClient.invalidateQueries({ queryKey: ['dicom-files'] });
      // Auto-refresh after a short delay to show new files
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['dicom-files'] });
      }, 500);
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Erreur lors de l\'import', 'error');
    },
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['png-files'] });
    queryClient.invalidateQueries({ queryKey: ['dicom-files'] });
    showToast('Liste des images mise à jour', 'success');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analyse d&apos;Imagerie Médicale</h1>
          <p className="text-muted-foreground mt-2">
            Upload DICOM, conversion PNG, et analyse LLM
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>
          <Button
            variant="outline"
            onClick={() => importMutation.mutate()}
            disabled={importMutation.isPending}
          >
            <Download className="h-4 w-4 mr-2" />
            Importer depuis TCIA
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Upload & DICOM Files */}
        <div className="space-y-6">
          <DicomUploader />
          <DicomList />
        </div>

        {/* Middle Column: PNG Gallery */}
        <div>
          <ImageList
            onImageSelect={setSelectedImage}
            selectedImage={selectedImage}
          />
        </div>

        {/* Right Column: Analysis */}
        <div>
          {selectedImage && <AnalyzeButton filename={selectedImage} />}
        </div>
      </div>
      </div>
    </div>
  );
}

