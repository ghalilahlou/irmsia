'use client';

import React, { useState, useEffect, useRef, forwardRef, useImperativeHandle, useMemo, useCallback } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Download, Eye, EyeOff, Layers } from 'lucide-react';
import { processVisualizationArray, getPathologyColor, getPathologyTextColor } from '@/utils/imageProcessing';

interface AdvancedAnomalyViewerProps {
  result: any;
  originalFile: File | null;
}

const AdvancedAnomalyViewer = React.memo(forwardRef((props: AdvancedAnomalyViewerProps, ref) => {
  const { result, originalFile } = props;
  const [imageData, setImageData] = useState<string | null>(null);
  const [heatmapData, setHeatmapData] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatmapOpacity, setHeatmapOpacity] = useState(0.5);
  const [selectedBbox, setSelectedBbox] = useState<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const heatmapImageRef = useRef<HTMLImageElement | null>(null);
  
  // Expose methods to parent
  useImperativeHandle(ref, () => ({
    getCanvas: () => canvasRef.current,
    getCurrentZoom: () => zoom,
    getCurrentRotation: () => rotation,
  }), [zoom, rotation]);
  
  // Load base image - optimisé avec cleanup
  useEffect(() => {
    if (!originalFile) {
      setImageData(null);
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setImageData(e.target?.result as string);
    };
    reader.readAsDataURL(originalFile);
    
    return () => {
      reader.abort();
    };
  }, [originalFile]);
  
  // Load heatmap - optimisé avec useMemo pour le traitement
  useEffect(() => {
    if (!result?.visualization || !Array.isArray(result.visualization)) {
      setHeatmapData(null);
      return;
    }
    
    // Utiliser la fonction optimisée de traitement
    const processed = processVisualizationArray(result.visualization);
    setHeatmapData(processed);
  }, [result?.visualization]);
  
  // Mémoriser les bounding boxes pour éviter les recalculs
  const boundingBoxes = useMemo(() => {
    return result?.bounding_boxes || [];
  }, [result?.bounding_boxes]);
  
  // Draw to canvas with annotations - optimisé avec requestAnimationFrame
  useEffect(() => {
    if (!imageData || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d', { willReadFrequently: false });
    if (!ctx) return;
    
    let animationFrameId: number;
    let img: HTMLImageElement | null = null;
    
    const draw = () => {
      if (!img || !canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      // Set canvas size
      const maxWidth = 1200;
      const maxHeight = 800;
      const aspectRatio = img.width / img.height;
      
      let canvasWidth = Math.min(img.width, maxWidth);
      let canvasHeight = canvasWidth / aspectRatio;
      
      if (canvasHeight > maxHeight) {
        canvasHeight = maxHeight;
        canvasWidth = canvasHeight * aspectRatio;
      }
      
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      
      // Center and transform
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((rotation * Math.PI) / 180);
      ctx.scale(zoom, zoom);
      
      // Draw base image
      const drawWidth = img.width;
      const drawHeight = img.height;
      ctx.drawImage(img, -drawWidth / 2, -drawHeight / 2, drawWidth, drawHeight);
      
      // Draw heatmap overlay if enabled
      if (showHeatmap && heatmapImageRef.current) {
        ctx.globalAlpha = heatmapOpacity;
        ctx.drawImage(heatmapImageRef.current, -drawWidth / 2, -drawHeight / 2, drawWidth, drawHeight);
        ctx.globalAlpha = 1.0;
      }
      
      // Draw bounding boxes if available and enabled
      if (showAnnotations && boundingBoxes.length > 0) {
        const scale = drawWidth / (result.measurements?.image_size?.width || img.width);
        
        boundingBoxes.forEach((bbox: any, index: number) => {
          const x = (bbox.x * scale) - drawWidth / 2;
          const y = (bbox.y * scale) - drawHeight / 2;
          const w = bbox.width * scale;
          const h = bbox.height * scale;
          
          // Couleur selon pathologie
          const color = getPathologyColor(bbox.pathology || 'unknown');
          const label = bbox.pathology || `Anomalie #${bbox.id}`;
          
          // Highlight selected bbox
          const isSelected = selectedBbox === index;
          const lineWidth = isSelected ? 4 : 2;
          const alpha = isSelected ? 1.0 : 0.8;
          
          ctx.strokeStyle = color;
          ctx.fillStyle = color;
          ctx.globalAlpha = alpha;
          ctx.lineWidth = lineWidth / zoom;
          
          // Draw rectangle
          ctx.strokeRect(x, y, w, h);
          
          // Draw label background
          const fontSize = Math.max(12, 14 / zoom);
          ctx.font = `bold ${fontSize}px Arial`;
          const text = `${label} (${bbox.confidence ? (bbox.confidence * 100).toFixed(0) : 'N/A'}%)`;
          const textMetrics = ctx.measureText(text);
          const textWidth = textMetrics.width;
          const textHeight = fontSize;
          
          ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
          ctx.fillRect(x, y - textHeight - 4, textWidth + 8, textHeight + 4);
          
          // Draw label text
          ctx.fillStyle = color;
          ctx.fillText(text, x + 4, y - 4);
          
          // Draw measurements if available
          if (bbox.area_mm2) {
            const measureText = `${bbox.area_mm2.toFixed(1)} mm²`;
            const measureMetrics = ctx.measureText(measureText);
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.fillRect(x, y + h + 2, measureMetrics.width + 8, textHeight + 2);
            ctx.fillStyle = '#ffffff';
            ctx.fillText(measureText, x + 4, y + h + textHeight);
          }
          
          ctx.globalAlpha = 1.0;
        });
      }
      
      ctx.restore();
    };
    
    img = new Image();
    img.onload = () => {
      imageRef.current = img;
      animationFrameId = requestAnimationFrame(draw);
    };
    img.src = imageData;
    
    // Load heatmap image if available
    if (showHeatmap && heatmapData) {
      const heatmapImg = new Image();
      heatmapImg.onload = () => {
        heatmapImageRef.current = heatmapImg;
        animationFrameId = requestAnimationFrame(draw);
      };
      heatmapImg.src = heatmapData;
    }
    
    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      if (img) {
        img.onload = null;
      }
    };
  }, [imageData, zoom, rotation, showAnnotations, showHeatmap, heatmapOpacity, heatmapData, boundingBoxes, selectedBbox, result?.measurements]);
  
  // Handlers optimisés avec useCallback
  const handleZoomIn = useCallback(() => setZoom((z) => Math.min(z * 1.2, 5)), []);
  const handleZoomOut = useCallback(() => setZoom((z) => Math.max(z / 1.2, 0.1)), []);
  const handleRotate = useCallback(() => setRotation((r) => (r + 90) % 360), []);
  const handleReset = useCallback(() => {
    setZoom(1);
    setRotation(0);
    setSelectedBbox(null);
  }, []);
  
  const handleDownload = useCallback(() => {
    if (!canvasRef.current) return;
    const link = document.createElement('a');
    link.download = `anomaly_analysis_${Date.now()}.png`;
    link.href = canvasRef.current.toDataURL('image/png');
    link.click();
  }, []);
  
  const handleBboxClick = useCallback((index: number) => {
    setSelectedBbox(index);
    setShowAnnotations(true);
  }, []);
  
  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-gray-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Zoom avant"
            aria-label="Zoom avant"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Zoom arrière"
            aria-label="Zoom arrière"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleRotate}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Rotation"
            aria-label="Rotation"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="px-3 py-2 hover:bg-gray-700 rounded-lg transition-colors text-sm"
            title="Réinitialiser"
            aria-label="Réinitialiser"
          >
            Réinitialiser
          </button>
          
          <div className="h-6 w-px bg-gray-600 mx-2" />
          
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={showAnnotations}
              onChange={(e) => setShowAnnotations(e.target.checked)}
              className="rounded"
              aria-label="Afficher annotations"
            />
            {showAnnotations ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            <span>Annotations</span>
          </label>
          
          {heatmapData && (
            <>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={showHeatmap}
                  onChange={(e) => setShowHeatmap(e.target.checked)}
                  className="rounded"
                  aria-label="Afficher heatmap"
                />
                <Layers className="w-4 h-4" />
                <span>Heatmap</span>
              </label>
              
              {showHeatmap && (
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={heatmapOpacity}
                    onChange={(e) => setHeatmapOpacity(parseFloat(e.target.value))}
                    className="w-24"
                    aria-label="Opacité heatmap"
                  />
                  <span className="text-xs text-gray-400">
                    {Math.round(heatmapOpacity * 100)}%
                  </span>
                </div>
              )}
            </>
          )}
        </div>
        
        <button
          onClick={handleDownload}
          className="flex items-center gap-2 px-3 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors text-sm"
          aria-label="Télécharger l'image"
        >
          <Download className="w-4 h-4" />
          Télécharger
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Canvas */}
        <div className="lg:col-span-3">
          <div className="bg-black rounded-lg overflow-hidden flex items-center justify-center" style={{ minHeight: '600px' }}>
            <canvas
              ref={canvasRef}
              className="max-w-full h-auto"
              style={{ imageRendering: 'auto' }}
              aria-label="Visualisation des anomalies"
            />
          </div>
        </div>
        
        {/* Sidebar: Anomalies list */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 space-y-3">
            <h3 className="font-semibold text-sm mb-3">Anomalies détectées</h3>
            
            {boundingBoxes.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {boundingBoxes.map((bbox: any, index: number) => (
                  <div
                    key={`bbox-${bbox.id || index}`}
                    onClick={() => handleBboxClick(index)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedBbox === index
                        ? 'bg-cyan-500/20 border-cyan-500'
                        : 'bg-gray-700/30 border-gray-600 hover:bg-gray-700/50'
                    }`}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        handleBboxClick(index);
                      }
                    }}
                    aria-label={`Anomalie ${bbox.pathology || index}`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className={`font-medium text-sm ${getPathologyTextColor(bbox.pathology || 'unknown')}`}>
                        {bbox.pathology || `Anomalie #${bbox.id}`}
                      </span>
                      {bbox.confidence && (
                        <span className="text-xs text-gray-400">
                          {(bbox.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    
                    {bbox.area_mm2 && (
                      <div className="text-xs text-gray-400">
                        Surface: {bbox.area_mm2.toFixed(1)} mm²
                      </div>
                    )}
                    
                    {bbox.severity && (
                      <div className="text-xs mt-1">
                        <span className="text-gray-400">Sévérité: </span>
                        <span className="font-medium">{bbox.severity}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-400 text-center py-8">
                {result?.has_anomaly ? 'Aucune anomalie détectée' : 'Aucune annotation disponible'}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Info */}
      <div className="text-xs text-gray-400 bg-gray-800/30 rounded-lg p-3">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="font-medium">Zoom:</span> {(zoom * 100).toFixed(0)}%
          </div>
          <div>
            <span className="font-medium">Rotation:</span> {rotation}°
          </div>
          <div>
            <span className="font-medium">Annotations:</span> {showAnnotations ? 'Activées' : 'Désactivées'}
          </div>
          <div>
            <span className="font-medium">Heatmap:</span> {showHeatmap ? `${Math.round(heatmapOpacity * 100)}%` : 'Désactivée'}
          </div>
        </div>
      </div>
    </div>
  );
}), (prevProps, nextProps) => {
  // Comparaison personnalisée pour éviter les re-renders inutiles
  return (
    prevProps.result === nextProps.result &&
    prevProps.originalFile === nextProps.originalFile
  );
});

AdvancedAnomalyViewer.displayName = 'AdvancedAnomalyViewer';

export default AdvancedAnomalyViewer;
