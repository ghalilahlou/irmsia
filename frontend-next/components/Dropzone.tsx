'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DropzoneProps {
  onFileAccepted: (file: File) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  className?: string;
}

export function Dropzone({
  onFileAccepted,
  accept = { 'application/dicom': ['.dcm'], 'application/octet-stream': ['.dcm'] },
  maxSize = 50 * 1024 * 1024, // 50MB
  className,
}: DropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0]);
      }
    },
    [onFileAccepted]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } =
    useDropzone({
      onDrop,
      accept,
      maxSize,
      multiple: false,
    });

  return (
    <div className={cn('w-full', className)}>
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50',
          fileRejections.length > 0 && 'border-destructive'
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          {isDragActive ? (
            <Upload className="h-12 w-12 text-primary" />
          ) : (
            <File className="h-12 w-12 text-muted-foreground" />
          )}
          <div className="space-y-2">
            <p className="text-sm font-medium">
              {isDragActive
                ? 'Drop the DICOM file here'
                : 'Drag & drop a DICOM file here, or click to select'}
            </p>
            <p className="text-xs text-muted-foreground">
              DICOM files only (.dcm) • Max 50MB
            </p>
          </div>
        </div>
      </div>
      {fileRejections.length > 0 && (
        <div className="mt-2 text-sm text-destructive">
          {fileRejections[0].errors[0]?.message || 'File rejected'}
        </div>
      )}
    </div>
  );
}

