'use client';

import React, { useEffect, useRef } from 'react';
import { Layers, Eye, EyeOff } from 'lucide-react';

interface SegmentationPanelProps {
  result: any;
  originalFile: File | null;
}

export default function SegmentationPanel({ result, originalFile }: SegmentationPanelProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [showOverlay, setShowOverlay] = React.useState(true);
  const [opacity, setOpacity] = React.useState(0.5);
  
  useEffect(() => {
    if (!result?.segmentation_mask || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const mask = result.segmentation_mask;
    canvas.width = mask[0].length;
    canvas.height = mask.length;
    
    const imageData = ctx.createImageData(canvas.width, canvas.height);
    
    for (let y = 0; y < canvas.height; y++) {
      for (let x = 0; x < canvas.width; x++) {
        const idx = (y * canvas.width + x) * 4;
        const value = mask[y][x];
        
        if (value > 0) {
          imageData.data[idx] = 0;       // R
          imageData.data[idx + 1] = 255; // G (cyan)
          imageData.data[idx + 2] = 255; // B
          imageData.data[idx + 3] = showOverlay ? opacity * 255 : 0; // A
        } else {
          imageData.data[idx] = 0;
          imageData.data[idx + 1] = 0;
          imageData.data[idx + 2] = 0;
          imageData.data[idx + 3] = 0;
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0);
  }, [result, showOverlay, opacity]);
  
  if (!result?.segmentation_mask) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Layers className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>Aucune segmentation disponible</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between bg-gray-800/50 rounded-lg p-3">
        <h3 className="font-semibold flex items-center gap-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          Segmentation des Anomalies
        </h3>
        
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="range"
              min="0"
              max="100"
              value={opacity * 100}
              onChange={(e) => setOpacity(Number(e.target.value) / 100)}
              className="w-24"
            />
            Opacité: {(opacity * 100).toFixed(0)}%
          </label>
          
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
          >
            {showOverlay ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            {showOverlay ? 'Masquer' : 'Afficher'}
          </button>
        </div>
      </div>
      
      <div className="bg-black rounded-lg p-4">
        <canvas ref={canvasRef} className="max-w-full h-auto mx-auto" />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {result.bounding_boxes?.map((bbox: any, idx: number) => (
          <div key={idx} className="bg-gray-800/30 rounded-lg p-3">
            <h4 className="font-semibold text-sm mb-2">Région #{bbox.id}</h4>
            <div className="text-xs space-y-1 text-gray-300">
              <div>Surface: {bbox.area_mm2?.toFixed(2)} mm²</div>
              <div>Dimensions: {bbox.width_mm?.toFixed(1)} × {bbox.height_mm?.toFixed(1)} mm</div>
              <div>Périmètre: {bbox.perimeter_mm?.toFixed(1)} mm</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


