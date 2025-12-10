'use client';

import React from 'react';
import { Ruler, MapPin, Circle } from 'lucide-react';

interface MeasurementToolsProps {
  result: any;
  viewerRef: any;
}

export default function MeasurementTools({ result, viewerRef }: MeasurementToolsProps) {
  if (!result?.measurements) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Ruler className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>Aucune mesure disponible</p>
      </div>
    );
  }
  
  const { measurements, bounding_boxes } = result;
  
  return (
    <div className="space-y-6">
      {/* Résumé global */}
      <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Ruler className="w-6 h-6 text-cyan-400" />
          Mesures Globales
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-cyan-400">
              {measurements.num_regions || 0}
            </div>
            <div className="text-sm text-gray-400 mt-1">Régions Détectées</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-cyan-400">
              {measurements.total_area_mm2?.toFixed(1) || 0}
            </div>
            <div className="text-sm text-gray-400 mt-1">Surface Totale (mm²)</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-cyan-400">
              {measurements.image_size?.width || 0}×{measurements.image_size?.height || 0}
            </div>
            <div className="text-sm text-gray-400 mt-1">Résolution (px)</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-cyan-400">
              {measurements.pixel_to_mm_ratio?.toFixed(2) || 0}
            </div>
            <div className="text-sm text-gray-400 mt-1">Ratio px/mm</div>
          </div>
        </div>
      </div>
      
      {/* Mesures par région */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Mesures Détaillées par Région</h3>
        
        <div className="space-y-3">
          {bounding_boxes?.map((bbox: any, idx: number) => (
            <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-cyan-500/20 border border-cyan-500/30 rounded-full flex items-center justify-center text-cyan-400 font-semibold text-sm">
                    {bbox.id}
                  </div>
                  <h4 className="font-semibold">Région #{bbox.id}</h4>
                </div>
                
                <div className="text-right">
                  <div className="text-lg font-bold text-cyan-400">
                    {bbox.area_mm2?.toFixed(2)} mm²
                  </div>
                  <div className="text-xs text-gray-400">Surface</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Largeur</div>
                  <div className="font-semibold">{bbox.width_mm?.toFixed(2)} mm</div>
                  <div className="text-xs text-gray-500">{bbox.width} px</div>
                </div>
                
                <div>
                  <div className="text-gray-400 mb-1">Hauteur</div>
                  <div className="font-semibold">{bbox.height_mm?.toFixed(2)} mm</div>
                  <div className="text-xs text-gray-500">{bbox.height} px</div>
                </div>
                
                <div>
                  <div className="text-gray-400 mb-1">Périmètre</div>
                  <div className="font-semibold">{bbox.perimeter_mm?.toFixed(2)} mm</div>
                  <div className="text-xs text-gray-500">{bbox.perimeter_pixels?.toFixed(0)} px</div>
                </div>
                
                <div>
                  <div className="text-gray-400 mb-1">Position</div>
                  <div className="font-semibold">({bbox.x}, {bbox.y})</div>
                  <div className="text-xs text-gray-500">pixels</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Légende */}
      <div className="bg-gray-800/30 rounded-lg p-4 text-sm text-gray-400">
        <h4 className="font-semibold mb-2 text-white">💡 Notes:</h4>
        <ul className="space-y-1 list-disc list-inside">
          <li>Les mesures sont calculées automatiquement à partir de la segmentation</li>
          <li>Le ratio pixel/mm est estimé (peut nécessiter calibration DICOM)</li>
          <li>Surface = aire de la région segmentée</li>
          <li>Périmètre = contour de la région</li>
        </ul>
      </div>
    </div>
  );
}


