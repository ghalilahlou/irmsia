'use client';

import { useState, useEffect } from 'react';
import { X, ZoomIn, ZoomOut, RotateCw, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { medicalAPI } from '@/lib/api';

interface ImageModalProps {
  filename: string;
  isOpen: boolean;
  onClose: () => void;
}

export function ImageModal({ filename, isOpen, onClose }: ImageModalProps) {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (isOpen) {
      // Reset on open
      setZoom(100);
      setRotation(0);
      setPosition({ x: 0, y: 0 });
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 25, 300));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 25, 50));
  };

  const handleReset = () => {
    setZoom(100);
    setRotation(0);
    setPosition({ x: 0, y: 0 });
  };

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const handleDownload = () => {
    const imageUrl = medicalAPI.getPngFileUrl(filename);
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 100) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y,
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoom > 100) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  if (!isOpen) return null;

  const imageUrl = medicalAPI.getPngFileUrl(filename);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full h-full flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-black/50 backdrop-blur-sm">
          <div className="flex items-center gap-2 text-white">
            <h2 className="text-lg font-semibold truncate max-w-md">{filename}</h2>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDownload}
              className="text-white hover:bg-white/20"
            >
              <Download className="h-4 w-4 mr-2" />
              Télécharger
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-white hover:bg-white/20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Image Container */}
        <div
          className="flex-1 flex items-center justify-center overflow-hidden p-4"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <div
            className="relative transition-transform duration-200"
            style={{
              transform: `translate(${position.x}px, ${position.y}px) rotate(${rotation}deg) scale(${zoom / 100})`,
              transformOrigin: 'center center',
              maxWidth: '90vw',
              maxHeight: '90vh',
            }}
          >
            <img
              src={imageUrl}
              alt={filename}
              className="max-w-full max-h-full object-contain"
              style={{ width: 'auto', height: 'auto' }}
            />
          </div>
        </div>

        {/* Controls */}
        <div className="absolute bottom-0 left-0 right-0 z-10 flex items-center justify-center gap-2 p-4 bg-black/50 backdrop-blur-sm">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomOut}
            disabled={zoom <= 50}
            className="text-white hover:bg-white/20"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-white text-sm min-w-[60px] text-center">
            {zoom}%
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleZoomIn}
            disabled={zoom >= 300}
            className="text-white hover:bg-white/20"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <div className="w-px h-6 bg-white/30 mx-2" />
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRotate}
            className="text-white hover:bg-white/20"
          >
            <RotateCw className="h-4 w-4" />
          </Button>
          <div className="w-px h-6 bg-white/30 mx-2" />
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="text-white hover:bg-white/20"
          >
            Réinitialiser
          </Button>
        </div>
      </div>
    </div>
  );
}

