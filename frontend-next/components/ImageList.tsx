'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { medicalAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Image as ImageIcon, Loader2, RefreshCw, Maximize2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/components/ToastProvider';
import { ImageModal } from './ImageModal';

interface ImageListProps {
  onImageSelect?: (filename: string) => void;
  selectedImage?: string;
}

export function ImageList({ onImageSelect, selectedImage }: ImageListProps) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [modalImage, setModalImage] = useState<string | null>(null);
  const [deletingFile, setDeletingFile] = useState<string | null>(null);
  
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['png-files'],
    queryFn: () => medicalAPI.listPngFiles(),
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });

  const deleteMutation = useMutation({
    mutationFn: (filename: string) => medicalAPI.deletePngFile(filename),
    onSuccess: (data, filename) => {
      showToast(`Image ${filename} supprimée avec succès`, 'success');
      queryClient.invalidateQueries({ queryKey: ['png-files'] });
      setDeletingFile(null);
      // Si l'image supprimée était sélectionnée, désélectionner
      if (selectedImage === filename) {
        onImageSelect?.(undefined as any);
      }
    },
    onError: (error: any, filename) => {
      showToast(`Erreur lors de la suppression de ${filename}: ${error.response?.data?.detail || error.message}`, 'error');
      setDeletingFile(null);
    },
  });

  const handleRefresh = () => {
    refetch();
    showToast('Liste des images actualisée', 'success');
  };

  const handleImageClick = (filename: string, e: React.MouseEvent) => {
    // Double click to open modal
    if (e.detail === 2) {
      setModalImage(filename);
    } else {
      // Single click to select
      onImageSelect?.(filename);
    }
  };

  const handleViewFullscreen = (filename: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setModalImage(filename);
  };

  const handleDelete = (filename: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'image "${filename}" ?`)) {
      setDeletingFile(filename);
      deleteMutation.mutate(filename);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5" />
            Galerie PNG
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
            <ImageIcon className="h-5 w-5" />
            Galerie PNG
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive">
            Erreur lors du chargement des images
          </p>
        </CardContent>
      </Card>
    );
  }

  const images = data?.files || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-5 w-5" />
              Galerie PNG ({images.length})
            </CardTitle>
            <CardDescription>
              Images converties depuis DICOM
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {images.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <ImageIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Aucune image disponible</p>
            <p className="text-sm">Upload un fichier DICOM pour commencer</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map((image: any) => (
              <div
                key={image.filename}
                className={`relative aspect-square rounded-lg overflow-hidden border-2 cursor-pointer transition-all group ${
                  selectedImage === image.filename
                    ? 'border-primary ring-2 ring-primary'
                    : 'border-border hover:border-primary/50'
                }`}
                onClick={(e) => handleImageClick(image.filename, e)}
              >
                <img
                  src={`/api/v1/medical/png/${image.filename}`}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-2 truncate">
                  {image.filename}
                </div>
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                  <Button
                    size="sm"
                    variant="secondary"
                    className="h-8 w-8 p-0"
                    onClick={(e) => handleViewFullscreen(image.filename, e)}
                    title="Voir en grand (double-clic)"
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    className="h-8 w-8 p-0"
                    onClick={(e) => handleDelete(image.filename, e)}
                    disabled={deletingFile === image.filename}
                    title="Supprimer l'image"
                  >
                    {deletingFile === image.filename ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
      {modalImage && (
        <ImageModal
          filename={modalImage}
          isOpen={!!modalImage}
          onClose={() => setModalImage(null)}
        />
      )}
    </Card>
  );
}

