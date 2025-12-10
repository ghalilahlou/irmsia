'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Brain,
  Loader2,
  AlertTriangle,
  CheckCircle,
  ZoomIn,
  Download,
  RefreshCw,
  Eye,
  Layers,
  Target,
  FileText,
  TrendingUp,
  Activity,
} from 'lucide-react';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  label?: string;
  area_pixels?: number;
}

interface AnalysisResult {
  status: string;
  has_anomaly: boolean;
  anomaly_class: string;
  confidence: number;
  bounding_boxes: BoundingBox[];
  measurements: {
    total_area_pixels?: number;
    num_regions?: number;
    total_area_mm2?: number;
    total_perimeter_mm?: number;
    anomaly_ratio?: number;
  };
  visualizations?: {
    original?: string;
    annotated?: string;
    heatmap?: string;
    segmentation?: string;
    zoomed_regions?: string[];
  };
  segmentation?: {
    regions: any[];
    measurements: any;
  };
  processing_time_ms: number;
}

interface AnalysisViewerProps {
  result: AnalysisResult;
  onReanalyze?: () => void;
}

export function AnalysisViewer({ result, onReanalyze }: AnalysisViewerProps) {
  const [selectedRegion, setSelectedRegion] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'original' | 'annotated' | 'heatmap' | 'segmentation'>('annotated');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Get current visualization
  const getCurrentVisualization = () => {
    if (!result.visualizations) return null;
    switch (viewMode) {
      case 'original':
        return result.visualizations.original;
      case 'annotated':
        return result.visualizations.annotated;
      case 'heatmap':
        return result.visualizations.heatmap;
      case 'segmentation':
        return result.visualizations.segmentation;
      default:
        return result.visualizations.annotated || result.visualizations.original;
    }
  };

  // Draw bounding boxes on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const visualization = getCurrentVisualization();
    if (!visualization) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // Draw selected region highlight
      if (selectedRegion !== null && result.bounding_boxes[selectedRegion]) {
        const box = result.bounding_boxes[selectedRegion];
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 3;
        ctx.strokeRect(box.x, box.y, box.width, box.height);
        
        // Draw selection indicator
        ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
        ctx.fillRect(box.x, box.y, box.width, box.height);
      }
    };
    img.src = `data:image/png;base64,${visualization}`;
  }, [result, viewMode, selectedRegion]);

  // Download report
  const downloadReport = () => {
    const reportText = generateTextReport(result);
    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-report-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card className={result.has_anomaly ? 'border-orange-500/50' : 'border-green-500/50'}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Brain className="h-5 w-5 text-purple-400" />
              Résultats de l'Analyse IA
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={result.has_anomaly ? 'destructive' : 'default'}>
                {result.has_anomaly ? (
                  <>
                    <AlertTriangle className="h-3 w-3 mr-1" />
                    Anomalie
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Normal
                  </>
                )}
              </Badge>
              <Badge variant="outline">
                {(result.confidence * 100).toFixed(1)}% confiance
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="rounded-lg bg-muted/50 p-3">
              <div className="text-muted-foreground text-xs mb-1">Classification</div>
              <div className="font-semibold capitalize">{result.anomaly_class}</div>
            </div>
            <div className="rounded-lg bg-muted/50 p-3">
              <div className="text-muted-foreground text-xs mb-1">Régions détectées</div>
              <div className="font-semibold">{result.bounding_boxes.length}</div>
            </div>
            <div className="rounded-lg bg-muted/50 p-3">
              <div className="text-muted-foreground text-xs mb-1">Temps de traitement</div>
              <div className="font-semibold">{result.processing_time_ms.toFixed(0)}ms</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Visualization Panel */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Visualisation
              </CardTitle>
              <div className="flex items-center gap-1">
                {result.visualizations?.original && (
                  <Button
                    variant={viewMode === 'original' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('original')}
                    className="h-7 text-xs"
                  >
                    Original
                  </Button>
                )}
                {result.visualizations?.annotated && (
                  <Button
                    variant={viewMode === 'annotated' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('annotated')}
                    className="h-7 text-xs"
                  >
                    Annoté
                  </Button>
                )}
                {result.visualizations?.heatmap && (
                  <Button
                    variant={viewMode === 'heatmap' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('heatmap')}
                    className="h-7 text-xs"
                  >
                    Heatmap
                  </Button>
                )}
                {result.visualizations?.segmentation && (
                  <Button
                    variant={viewMode === 'segmentation' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('segmentation')}
                    className="h-7 text-xs"
                  >
                    Segmentation
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-square bg-black rounded-lg overflow-hidden">
              {getCurrentVisualization() ? (
                <canvas
                  ref={canvasRef}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  Aucune visualisation disponible
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Details Panel */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Layers className="h-4 w-4" />
              Détails
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="regions" className="w-full">
              <TabsList className="grid w-full grid-cols-3 h-8">
                <TabsTrigger value="regions" className="text-xs">Régions</TabsTrigger>
                <TabsTrigger value="measures" className="text-xs">Mesures</TabsTrigger>
                <TabsTrigger value="zoom" className="text-xs">Zoom</TabsTrigger>
              </TabsList>

              <TabsContent value="regions" className="mt-3">
                <ScrollArea className="h-[300px]">
                  {result.bounding_boxes.length > 0 ? (
                    <div className="space-y-2">
                      {result.bounding_boxes.map((box, idx) => (
                        <div
                          key={idx}
                          onClick={() => setSelectedRegion(selectedRegion === idx ? null : idx)}
                          className={`
                            p-2 rounded-lg border cursor-pointer transition-colors
                            ${selectedRegion === idx 
                              ? 'border-green-500 bg-green-500/10' 
                              : 'border-border hover:bg-muted/50'}
                          `}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <Target className="h-3 w-3 text-muted-foreground" />
                              <span className="text-xs font-medium">
                                Région #{idx + 1}
                              </span>
                            </div>
                            {box.confidence && (
                              <Badge variant="secondary" className="text-[10px]">
                                {(box.confidence * 100).toFixed(1)}%
                              </Badge>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-1 text-[10px] text-muted-foreground">
                            <div>Position: ({box.x}, {box.y})</div>
                            <div>Taille: {box.width}×{box.height}</div>
                            {box.area_pixels && (
                              <div className="col-span-2">
                                Surface: {box.area_pixels.toLocaleString()} px²
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground text-sm py-8">
                      Aucune région détectée
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="measures" className="mt-3">
                <div className="space-y-3">
                  {result.measurements.total_area_mm2 !== undefined && (
                    <div className="flex items-center justify-between p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Activity className="h-3 w-3" />
                        Surface totale
                      </div>
                      <span className="text-xs font-mono font-semibold">
                        {result.measurements.total_area_mm2.toFixed(2)} mm²
                      </span>
                    </div>
                  )}
                  {result.measurements.total_area_pixels !== undefined && (
                    <div className="flex items-center justify-between p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Activity className="h-3 w-3" />
                        Surface (pixels)
                      </div>
                      <span className="text-xs font-mono font-semibold">
                        {result.measurements.total_area_pixels.toLocaleString()} px²
                      </span>
                    </div>
                  )}
                  {result.measurements.total_perimeter_mm !== undefined && (
                    <div className="flex items-center justify-between p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <TrendingUp className="h-3 w-3" />
                        Périmètre
                      </div>
                      <span className="text-xs font-mono font-semibold">
                        {result.measurements.total_perimeter_mm.toFixed(2)} mm
                      </span>
                    </div>
                  )}
                  {result.measurements.anomaly_ratio !== undefined && (
                    <div className="flex items-center justify-between p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <TrendingUp className="h-3 w-3" />
                        Ratio anomalie
                      </div>
                      <span className="text-xs font-mono font-semibold">
                        {(result.measurements.anomaly_ratio * 100).toFixed(2)}%
                      </span>
                    </div>
                  )}
                  {result.segmentation?.measurements && (
                    <>
                      <div className="border-t pt-2 mt-2">
                        <div className="text-xs text-muted-foreground mb-2">
                          Segmentation
                        </div>
                        {Object.entries(result.segmentation.measurements).map(([key, value]) => (
                          <div key={key} className="flex justify-between text-[10px] py-1">
                            <span className="text-muted-foreground capitalize">
                              {key.replace(/_/g, ' ')}
                            </span>
                            <span className="font-mono">
                              {typeof value === 'number' ? value.toFixed(2) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="zoom" className="mt-3">
                {result.visualizations?.zoomed_regions?.length ? (
                  <div className="grid grid-cols-1 gap-2">
                    {result.visualizations.zoomed_regions.map((region, idx) => (
                      <div key={idx} className="rounded-lg overflow-hidden border">
                        <img
                          src={`data:image/png;base64,${region}`}
                          alt={`Région ${idx + 1}`}
                          className="w-full h-auto"
                        />
                        <div className="px-2 py-1 bg-muted text-xs text-center">
                          Région #{idx + 1} (x2)
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground text-sm py-8">
                    Aucune vue agrandie
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-2">
        {onReanalyze && (
          <Button variant="outline" size="sm" onClick={onReanalyze}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Réanalyser
          </Button>
        )}
        <Button variant="outline" size="sm" onClick={downloadReport}>
          <Download className="h-4 w-4 mr-2" />
          Télécharger le rapport
        </Button>
      </div>
    </div>
  );
}

// Helper function to generate text report
function generateTextReport(result: AnalysisResult): string {
  const lines = [
    '=' .repeat(60),
    'RAPPORT D\'ANALYSE D\'IMAGERIE MÉDICALE',
    '=' .repeat(60),
    '',
    `Date: ${new Date().toLocaleString('fr-FR')}`,
    '',
    '-'.repeat(40),
    'SYNTHÈSE',
    '-'.repeat(40),
    `Statut: ${result.has_anomaly ? 'ANOMALIE DÉTECTÉE' : 'NORMAL'}`,
    `Classification: ${result.anomaly_class}`,
    `Confiance: ${(result.confidence * 100).toFixed(1)}%`,
    `Régions détectées: ${result.bounding_boxes.length}`,
    '',
    '-'.repeat(40),
    'MESURES',
    '-'.repeat(40),
  ];

  if (result.measurements.total_area_mm2) {
    lines.push(`Surface totale: ${result.measurements.total_area_mm2.toFixed(2)} mm²`);
  }
  if (result.measurements.total_area_pixels) {
    lines.push(`Surface (pixels): ${result.measurements.total_area_pixels} px²`);
  }
  if (result.measurements.num_regions) {
    lines.push(`Nombre de régions: ${result.measurements.num_regions}`);
  }

  if (result.bounding_boxes.length > 0) {
    lines.push('');
    lines.push('-'.repeat(40));
    lines.push('RÉGIONS DÉTECTÉES');
    lines.push('-'.repeat(40));
    
    result.bounding_boxes.forEach((box, idx) => {
      lines.push(`\nRégion #${idx + 1}:`);
      lines.push(`  Position: (${box.x}, ${box.y})`);
      lines.push(`  Dimensions: ${box.width} × ${box.height} pixels`);
      if (box.confidence) {
        lines.push(`  Confiance: ${(box.confidence * 100).toFixed(1)}%`);
      }
      if (box.area_pixels) {
        lines.push(`  Surface: ${box.area_pixels} px²`);
      }
    });
  }

  lines.push('');
  lines.push('=' .repeat(60));
  lines.push(`Temps de traitement: ${result.processing_time_ms.toFixed(0)}ms`);
  lines.push('Généré par IRMSIA Deep Learning Analysis System');
  lines.push('=' .repeat(60));

  return lines.join('\n');
}

export default AnalysisViewer;

