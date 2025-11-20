'use client';

import { memo, useCallback } from 'react';
import { FileImage, Loader2, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DicomFileItemProps {
  filename: string;
  size: number;
  isConverting: boolean;
  onConvert: (filename: string) => void;
}

export const DicomFileItem = memo(function DicomFileItem({
  filename,
  size,
  isConverting,
  onConvert,
}: DicomFileItemProps) {
  const fileSize = size || 0;
  const sizeDisplay = fileSize > 0 
    ? `${(fileSize / 1024 / 1024).toFixed(2)} MB` 
    : '0,00 Mo';

  const handleClick = useCallback(() => {
    if (!isConverting) {
      onConvert(filename);
    }
  }, [isConverting, onConvert, filename]);

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <FileImage className="h-5 w-5 text-muted-foreground flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{filename}</p>
          <p className="text-xs text-muted-foreground">
            {sizeDisplay}
          </p>
        </div>
      </div>
      <Button
        size="sm"
        variant="outline"
        onClick={handleClick}
        disabled={isConverting}
        className="ml-2 flex-shrink-0"
      >
        {isConverting ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Conversion...
          </>
        ) : (
          <>
            <ImageIcon className="h-4 w-4 mr-2" />
            Convertir
          </>
        )}
      </Button>
    </div>
  );
}, (prevProps, nextProps) => {
  // Comparaison personnalisée pour éviter les re-renders inutiles
  return (
    prevProps.filename === nextProps.filename &&
    prevProps.size === nextProps.size &&
    prevProps.isConverting === nextProps.isConverting &&
    prevProps.onConvert === nextProps.onConvert
  );
});

