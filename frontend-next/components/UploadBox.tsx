'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

type UploadBoxProps = {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
};

export const UploadBox = ({ onFilesSelected, disabled }: UploadBoxProps) => {
  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (!acceptedFiles.length) return;
      onFilesSelected(acceptedFiles);
    },
    [onFilesSelected],
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop: handleDrop,
    multiple: true,
    disabled,
    noClick: true,
    accept: {
      'application/dicom': ['.dcm'],
      'application/dicom+zip': ['.zip'],
      'application/octet-stream': ['.dcm'],
    },
  });

  return (
    <div
      {...getRootProps()}
      className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
        isDragActive ? 'border-primary bg-primary/10' : 'border-border bg-muted/40'
      } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
    >
      <input {...getInputProps()} />
      <p className="text-lg font-semibold text-foreground">
        Glissez-déposez vos fichiers DICOM
      </p>
      <p className="mt-2 text-sm text-muted-foreground">
        Les fichiers restent localement.<br />Sélection multiple et multi-frame pris en charge.
      </p>
      <button
        type="button"
        onClick={open}
        disabled={disabled}
        className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow hover:bg-primary/90 disabled:cursor-not-allowed disabled:bg-muted"
      >
        Parcourir les fichiers
      </button>
    </div>
  );
};

export default UploadBox;

