'use client';

import React, { useCallback, useState } from 'react';
import { Upload, File, X } from 'lucide-react';

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
  isAnalyzing: boolean;
}

export default function ImageUploader({ onFileSelect, isAnalyzing }: ImageUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);
  
  const handleFile = (file: File) => {
    // Vérifier extension
    const validExtensions = ['.dcm', '.dicom', '.png', '.jpg', '.jpeg', '.tif', '.tiff'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!validExtensions.includes(fileExt)) {
      alert(`Format non supporté. Extensions valides: ${validExtensions.join(', ')}`);
      return;
    }
    
    setSelectedFileName(file.name);
    onFileSelect(file);
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };
  
  const clearFile = () => {
    setSelectedFileName(null);
  };
  
  return (
    <div>
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? 'border-cyan-400 bg-cyan-400/10' 
            : 'border-gray-600 hover:border-gray-500'
        } ${isAnalyzing ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleChange}
          accept=".dcm,.dicom,.png,.jpg,.jpeg,.tif,.tiff"
          disabled={isAnalyzing}
        />
        
        {!selectedFileName ? (
          <>
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <label
              htmlFor="file-upload"
              className="cursor-pointer"
            >
              <span className="text-cyan-400 hover:text-cyan-300 font-medium">
                Cliquez pour uploader
              </span>
              <span className="text-gray-400"> ou glissez-déposez</span>
            </label>
            <p className="text-sm text-gray-500 mt-2">
              DICOM, PNG, TIFF, JPG (max. 50MB)
            </p>
          </>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <File className="w-8 h-8 text-cyan-400" />
              <div className="text-left">
                <p className="text-sm font-medium text-white">{selectedFileName}</p>
                <p className="text-xs text-gray-400">Prêt pour l'analyse</p>
              </div>
            </div>
            {!isAnalyzing && (
              <button
                onClick={clearFile}
                className="p-2 hover:bg-gray-700 rounded-full transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            )}
          </div>
        )}
      </div>
      
      <div className="mt-4 text-xs text-gray-500">
        <p className="mb-1">Formats supportés:</p>
        <ul className="list-disc list-inside space-y-0.5 ml-2">
          <li>DICOM (.dcm, .dicom) - Images médicales standard</li>
          <li>TIFF (.tif, .tiff) - Images haute résolution</li>
          <li>PNG, JPG - Images standard</li>
        </ul>
      </div>
    </div>
  );
}


