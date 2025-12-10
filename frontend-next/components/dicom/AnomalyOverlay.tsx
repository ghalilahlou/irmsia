'use client';

import { useMemo } from 'react';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  label?: string;
}

export interface AnomalyResult {
  has_anomaly: boolean;
  anomaly_class?: string;
  confidence?: number;
  bounding_boxes?: BoundingBox[];
  segmentation_mask?: number[][];
  visualization?: string; // Base64 heatmap
  measurements?: {
    area_pixels?: number;
    area_mm2?: number;
    perimeter_pixels?: number;
    perimeter_mm?: number;
  };
}

interface AnomalyOverlayProps {
  analysisResult: AnomalyResult | null;
  imageWidth: number;
  imageHeight: number;
  showBoundingBoxes?: boolean;
  showHeatmap?: boolean;
  showLabels?: boolean;
  opacity?: number;
}

// Couleurs par classe d'anomalie
const ANOMALY_COLORS: Record<string, string> = {
  tumor: '#ef4444',
  nodule: '#f97316',
  mass: '#eab308',
  calcification: '#22c55e',
  opacity: '#3b82f6',
  consolidation: '#8b5cf6',
  pneumonia: '#ec4899',
  fracture: '#14b8a6',
  hemorrhage: '#dc2626',
  unknown: '#6b7280',
  default: '#f59e0b',
};

export function AnomalyOverlay({
  analysisResult,
  imageWidth,
  imageHeight,
  showBoundingBoxes = true,
  showHeatmap = true,
  showLabels = true,
  opacity = 0.6,
}: AnomalyOverlayProps) {
  const anomalyColor = useMemo(() => {
    if (!analysisResult?.anomaly_class) return ANOMALY_COLORS.default;
    const classLower = analysisResult.anomaly_class.toLowerCase();
    return ANOMALY_COLORS[classLower] || ANOMALY_COLORS.default;
  }, [analysisResult?.anomaly_class]);

  if (!analysisResult || !analysisResult.has_anomaly) {
    return null;
  }

  return (
    <div
      className="absolute inset-0 pointer-events-none"
      style={{ width: imageWidth, height: imageHeight }}
    >
      {/* Heatmap/Visualization overlay */}
      {showHeatmap && analysisResult.visualization && (
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url(data:image/png;base64,${analysisResult.visualization})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: opacity * 0.5,
            mixBlendMode: 'screen',
          }}
        />
      )}

      {/* Segmentation mask overlay */}
      {analysisResult.segmentation_mask && analysisResult.segmentation_mask.length > 0 && (
        <SegmentationMaskOverlay
          mask={analysisResult.segmentation_mask}
          width={imageWidth}
          height={imageHeight}
          color={anomalyColor}
          opacity={opacity * 0.4}
        />
      )}

      {/* Bounding boxes */}
      {showBoundingBoxes && analysisResult.bounding_boxes?.map((box, index) => (
        <BoundingBoxOverlay
          key={index}
          box={box}
          index={index}
          color={anomalyColor}
          showLabel={showLabels}
          anomalyClass={analysisResult.anomaly_class}
        />
      ))}

      {/* Legend */}
      {showLabels && analysisResult.has_anomaly && (
        <div className="absolute top-2 left-2 bg-black/70 rounded-lg p-2 text-xs text-white">
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: anomalyColor }}
            />
            <span className="capitalize font-medium">
              {analysisResult.anomaly_class || 'Anomalie'}
            </span>
            {analysisResult.confidence && (
              <span className="text-white/70">
                ({(analysisResult.confidence * 100).toFixed(1)}%)
              </span>
            )}
          </div>
          {analysisResult.measurements && (
            <div className="mt-1 text-[10px] text-white/60">
              {analysisResult.measurements.area_mm2 && (
                <span>Surface: {analysisResult.measurements.area_mm2.toFixed(1)} mm²</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Composant pour afficher une bounding box
function BoundingBoxOverlay({
  box,
  index,
  color,
  showLabel,
  anomalyClass,
}: {
  box: BoundingBox;
  index: number;
  color: string;
  showLabel: boolean;
  anomalyClass?: string;
}) {
  return (
    <div
      className="absolute border-2 rounded"
      style={{
        left: box.x,
        top: box.y,
        width: box.width,
        height: box.height,
        borderColor: color,
        boxShadow: `0 0 8px ${color}50`,
      }}
    >
      {/* Corner markers */}
      <div className="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2" style={{ borderColor: color }} />
      <div className="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2" style={{ borderColor: color }} />
      <div className="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2" style={{ borderColor: color }} />
      <div className="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2" style={{ borderColor: color }} />

      {/* Label */}
      {showLabel && (
        <div
          className="absolute -top-6 left-0 px-1.5 py-0.5 rounded text-[10px] font-medium text-white whitespace-nowrap"
          style={{ backgroundColor: color }}
        >
          {box.label || anomalyClass || `R${index + 1}`}
          {box.confidence && ` ${(box.confidence * 100).toFixed(0)}%`}
        </div>
      )}

      {/* Size indicator */}
      <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[9px] text-white/80 whitespace-nowrap bg-black/50 px-1 rounded">
        {Math.round(box.width)}×{Math.round(box.height)}px
      </div>
    </div>
  );
}

// Composant pour afficher le masque de segmentation
function SegmentationMaskOverlay({
  mask,
  width,
  height,
  color,
  opacity,
}: {
  mask: number[][];
  width: number;
  height: number;
  color: string;
  opacity: number;
}) {
  const canvasDataUrl = useMemo(() => {
    if (!mask || mask.length === 0) return null;

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Parse color to RGB
    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result
        ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16),
          }
        : { r: 255, g: 165, b: 0 };
    };

    const rgb = hexToRgb(color);
    const maskHeight = mask.length;
    const maskWidth = mask[0]?.length || 0;

    if (maskWidth === 0 || maskHeight === 0) return null;

    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const maskY = Math.floor((y / height) * maskHeight);
        const maskX = Math.floor((x / width) * maskWidth);
        const maskValue = mask[maskY]?.[maskX] || 0;

        const idx = (y * width + x) * 4;
        if (maskValue > 0.5) {
          data[idx] = rgb.r;
          data[idx + 1] = rgb.g;
          data[idx + 2] = rgb.b;
          data[idx + 3] = Math.round(maskValue * 255 * opacity);
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);
    return canvas.toDataURL();
  }, [mask, width, height, color, opacity]);

  if (!canvasDataUrl) return null;

  return (
    <img
      src={canvasDataUrl}
      alt="Segmentation mask"
      className="absolute inset-0 w-full h-full"
      style={{ mixBlendMode: 'screen' }}
    />
  );
}

export default AnomalyOverlay;

