'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
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
  AlertCircle,
  Clock,
  Stethoscope,
  BarChart3,
  Info,
  ChevronRight,
  Ruler,
} from 'lucide-react';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  label?: string;
  area_pixels?: number;
  area_mm2?: number;
}

interface TopPrediction {
  class_id: number;
  class_name: string;
  probability: number;
}

interface DetailedAnalysisResult {
  status?: string;
  has_anomaly: boolean;
  anomaly_class: string;
  anomaly_name?: string;
  confidence: number;
  severity?: string;
  urgency?: string;
  description?: string;
  recommendations?: string[];
  bounding_boxes: BoundingBox[];
  attention_regions?: any[];
  measurements: {
    num_regions?: number;
    total_area_pixels?: number;
    total_area_mm2?: number;
    max_area_mm2?: number;
    min_area_mm2?: number;
    avg_area_mm2?: number;
    segmented_area_mm2?: number;
    segmentation_ratio?: number;
    pixel_spacing_mm?: number[];
  };
  visualizations?: {
    original?: string;
    annotated?: string;
    heatmap?: string;
    segmentation?: string;
    zoomed_regions?: string[];
  };
  top_predictions?: TopPrediction[];
  model_info?: {
    type?: string;
    device?: string;
    version?: string;
  };
  processing_time_ms?: number;
}

interface DetailedAnalysisViewerProps {
  result: DetailedAnalysisResult;
  onReanalyze?: () => void;
  imageUrl?: string;
}

// Severity color mapping
const SEVERITY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  none: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/30' },
  low: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
  moderate: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  high: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
  critical: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
};

// Urgency icons
const URGENCY_INFO: Record<string, { icon: any; label: string; color: string }> = {
  routine: { icon: Clock, label: 'Routine', color: 'text-green-400' },
  'semi-urgent': { icon: AlertCircle, label: 'Semi-urgent', color: 'text-yellow-400' },
  urgent: { icon: AlertTriangle, label: 'Urgent', color: 'text-orange-400' },
  immediate: { icon: AlertTriangle, label: 'Immédiat', color: 'text-red-400' },
};

export function DetailedAnalysisViewer({ result, onReanalyze, imageUrl }: DetailedAnalysisViewerProps) {
  const [selectedRegion, setSelectedRegion] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'annotated' | 'heatmap' | 'segmentation' | 'original'>('annotated');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const severity = result.severity || 'none';
  const urgency = result.urgency || 'routine';
  const severityColors = SEVERITY_COLORS[severity] || SEVERITY_COLORS.none;
  const urgencyInfo = URGENCY_INFO[urgency] || URGENCY_INFO.routine;
  const UrgencyIcon = urgencyInfo.icon;

  // Get current visualization
  const getCurrentVisualization = useCallback(() => {
    if (!result.visualizations) return null;
    switch (viewMode) {
      case 'original':
        return result.visualizations.original;
      case 'annotated':
        return result.visualizations.annotated || result.visualizations.original;
      case 'heatmap':
        return result.visualizations.heatmap;
      case 'segmentation':
        return result.visualizations.segmentation;
      default:
        return result.visualizations.annotated || result.visualizations.original;
    }
  }, [result.visualizations, viewMode]);

  // Draw on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const visualization = getCurrentVisualization();
    if (!visualization) {
      // Use imageUrl as fallback
      if (imageUrl) {
        const img = new Image();
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.drawImage(img, 0, 0);
          drawOverlays(ctx, canvas.width, canvas.height);
        };
        img.src = imageUrl;
      }
      return;
    }

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      drawOverlays(ctx, canvas.width, canvas.height);
    };
    img.src = `data:image/png;base64,${visualization}`;
  }, [result, viewMode, selectedRegion, getCurrentVisualization, imageUrl]);

  const drawOverlays = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    // Draw bounding boxes
    result.bounding_boxes.forEach((box, idx) => {
      const isSelected = selectedRegion === idx;
      const color = isSelected ? '#00FF00' : '#FF6B6B';
      
      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeRect(box.x, box.y, box.width, box.height);

      if (isSelected) {
        ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
        ctx.fillRect(box.x, box.y, box.width, box.height);
      }

      // Label
      if (box.label) {
        ctx.font = '12px sans-serif';
        ctx.fillStyle = color;
        const label = `${box.label} ${box.confidence ? `(${(box.confidence * 100).toFixed(0)}%)` : ''}`;
        ctx.fillText(label, box.x, box.y - 5);
      }
    });
  };

  // Download report
  const downloadReport = () => {
    const reportText = generateDetailedReport(result);
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rapport-analyse-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Header Card - Summary */}
      <Card className={`border ${severityColors.border}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Brain className="h-5 w-5 text-purple-400" />
              Analyse IA - {result.anomaly_name || result.anomaly_class}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={result.has_anomaly ? 'destructive' : 'default'} className="text-xs">
                {result.has_anomaly ? 'Anomalie' : 'Normal'}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {(result.confidence * 100).toFixed(1)}%
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Severity and Urgency */}
          <div className="grid grid-cols-2 gap-4">
            <div className={`rounded-lg ${severityColors.bg} p-3`}>
              <div className="text-xs text-muted-foreground mb-1">Sévérité</div>
              <div className={`font-semibold capitalize ${severityColors.text}`}>
                {severity === 'none' ? 'Aucune' : severity}
              </div>
            </div>
            <div className="rounded-lg bg-muted/50 p-3">
              <div className="text-xs text-muted-foreground mb-1">Urgence</div>
              <div className={`font-semibold flex items-center gap-1 ${urgencyInfo.color}`}>
                <UrgencyIcon className="h-4 w-4" />
                {urgencyInfo.label}
              </div>
            </div>
          </div>

          {/* Description */}
          {result.description && (
            <div className="rounded-lg border p-3">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">{result.description}</p>
              </div>
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="rounded bg-muted/30 p-2">
              <div className="text-lg font-bold">{result.bounding_boxes.length}</div>
              <div className="text-[10px] text-muted-foreground">Régions</div>
            </div>
            <div className="rounded bg-muted/30 p-2">
              <div className="text-lg font-bold">
                {result.measurements.total_area_mm2 
                  ? result.measurements.total_area_mm2.toFixed(1) 
                  : result.measurements.total_area_pixels || 0}
              </div>
              <div className="text-[10px] text-muted-foreground">
                {result.measurements.total_area_mm2 ? 'mm²' : 'pixels'}
              </div>
            </div>
            <div className="rounded bg-muted/30 p-2">
              <div className="text-lg font-bold">
                {result.model_info?.type || 'DL'}
              </div>
              <div className="text-[10px] text-muted-foreground">Modèle</div>
            </div>
            <div className="rounded bg-muted/30 p-2">
              <div className="text-lg font-bold">
                {result.processing_time_ms ? `${result.processing_time_ms.toFixed(0)}` : '--'}
              </div>
              <div className="text-[10px] text-muted-foreground">ms</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content - Visualization + Details */}
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
                <Button
                  variant={viewMode === 'annotated' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('annotated')}
                  className="h-7 text-xs"
                >
                  Annoté
                </Button>
                {result.visualizations?.heatmap && (
                  <Button
                    variant={viewMode === 'heatmap' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('heatmap')}
                    className="h-7 text-xs"
                  >
                    GradCAM
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
              <canvas ref={canvasRef} className="w-full h-full object-contain" />
              {!getCurrentVisualization() && !imageUrl && (
                <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
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
              <Stethoscope className="h-4 w-4" />
              Détails Cliniques
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Tabs defaultValue="predictions" className="w-full">
              <TabsList className="grid w-full grid-cols-3 rounded-none h-9">
                <TabsTrigger value="predictions" className="text-xs">Diagnostic</TabsTrigger>
                <TabsTrigger value="regions" className="text-xs">Régions</TabsTrigger>
                <TabsTrigger value="measures" className="text-xs">Mesures</TabsTrigger>
              </TabsList>

              <TabsContent value="predictions" className="mt-0 p-3">
                <ScrollArea className="h-[300px]">
                  {/* Top Predictions */}
                  {result.top_predictions && result.top_predictions.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                        <BarChart3 className="h-3 w-3" />
                        Classifications
                      </h4>
                      <div className="space-y-2">
                        {result.top_predictions.map((pred, idx) => (
                          <div key={idx} className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${
                                idx === 0 ? 'bg-primary' : 'bg-muted'
                              }`} />
                              <span className="text-sm capitalize">{pred.class_name}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary transition-all"
                                  style={{ width: `${pred.probability * 100}%` }}
                                />
                              </div>
                              <span className="text-xs text-muted-foreground w-12 text-right">
                                {(pred.probability * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Separator className="my-3" />

                  {/* Recommendations */}
                  {result.recommendations && result.recommendations.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        Recommandations
                      </h4>
                      <ul className="space-y-2">
                        {result.recommendations.map((rec, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-xs">
                            <ChevronRight className="h-3 w-3 mt-0.5 text-primary flex-shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="regions" className="mt-0 p-3">
                <ScrollArea className="h-[300px]">
                  {result.bounding_boxes.length > 0 ? (
                    <div className="space-y-2">
                      {result.bounding_boxes.map((box, idx) => (
                        <div
                          key={idx}
                          onClick={() => setSelectedRegion(selectedRegion === idx ? null : idx)}
                          className={`
                            p-2 rounded-lg border cursor-pointer transition-all
                            ${selectedRegion === idx
                              ? 'border-green-500 bg-green-500/10'
                              : 'border-border hover:bg-muted/50'}
                          `}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <Target className="h-3 w-3 text-primary" />
                              <span className="text-xs font-medium">{box.label || `Région ${idx + 1}`}</span>
                            </div>
                            {box.confidence !== undefined && (
                              <Badge variant="secondary" className="text-[10px]">
                                {(box.confidence * 100).toFixed(0)}%
                              </Badge>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-1 text-[10px] text-muted-foreground">
                            <div>Position: ({box.x}, {box.y})</div>
                            <div>Taille: {box.width}×{box.height}</div>
                            {box.area_mm2 !== undefined && (
                              <div className="col-span-2">Surface: {box.area_mm2.toFixed(2)} mm²</div>
                            )}
                            {box.area_pixels !== undefined && !box.area_mm2 && (
                              <div className="col-span-2">Surface: {box.area_pixels.toLocaleString()} px</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                      <Target className="h-8 w-8 mb-2 opacity-50" />
                      <p className="text-sm">Aucune région détectée</p>
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="measures" className="mt-0 p-3">
                <ScrollArea className="h-[300px]">
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <MeasureItem
                        icon={Layers}
                        label="Régions"
                        value={result.measurements.num_regions || 0}
                      />
                      <MeasureItem
                        icon={Activity}
                        label="Surface totale"
                        value={result.measurements.total_area_mm2
                          ? `${result.measurements.total_area_mm2.toFixed(2)} mm²`
                          : result.measurements.total_area_pixels
                            ? `${result.measurements.total_area_pixels.toLocaleString()} px`
                            : 'N/A'}
                      />
                    </div>
                    
                    {result.measurements.max_area_mm2 !== undefined && (
                      <div className="grid grid-cols-2 gap-2">
                        <MeasureItem
                          icon={TrendingUp}
                          label="Surface max"
                          value={`${result.measurements.max_area_mm2.toFixed(2)} mm²`}
                        />
                        <MeasureItem
                          icon={TrendingUp}
                          label="Surface min"
                          value={`${result.measurements.min_area_mm2?.toFixed(2) || 0} mm²`}
                        />
                      </div>
                    )}

                    {result.measurements.avg_area_mm2 !== undefined && (
                      <MeasureItem
                        icon={Ruler}
                        label="Surface moyenne"
                        value={`${result.measurements.avg_area_mm2.toFixed(2)} mm²`}
                        fullWidth
                      />
                    )}

                    {result.measurements.segmentation_ratio !== undefined && (
                      <MeasureItem
                        icon={Layers}
                        label="Ratio segmentation"
                        value={`${(result.measurements.segmentation_ratio * 100).toFixed(2)}%`}
                        fullWidth
                      />
                    )}

                    {result.measurements.pixel_spacing_mm && (
                      <MeasureItem
                        icon={Ruler}
                        label="Espacement pixels"
                        value={`${result.measurements.pixel_spacing_mm[0].toFixed(3)} × ${result.measurements.pixel_spacing_mm[1].toFixed(3)} mm`}
                        fullWidth
                      />
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Zoomed Regions */}
      {result.visualizations?.zoomed_regions && result.visualizations.zoomed_regions.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <ZoomIn className="h-4 w-4" />
              Régions Agrandies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {result.visualizations.zoomed_regions.map((region, idx) => (
                <div key={idx} className="rounded-lg overflow-hidden border bg-black">
                  <img
                    src={`data:image/png;base64,${region}`}
                    alt={`Région ${idx + 1}`}
                    className="w-full h-32 object-contain"
                  />
                  <div className="px-2 py-1 bg-muted text-[10px] text-center">
                    Région {idx + 1} (×2)
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center justify-end gap-2">
        {onReanalyze && (
          <Button variant="outline" size="sm" onClick={onReanalyze}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Réanalyser
          </Button>
        )}
        <Button variant="default" size="sm" onClick={downloadReport}>
          <Download className="h-4 w-4 mr-2" />
          Télécharger le rapport
        </Button>
      </div>
    </div>
  );
}

// Helper component for measurements
function MeasureItem({
  icon: Icon,
  label,
  value,
  fullWidth = false,
}: {
  icon: any;
  label: string;
  value: string | number;
  fullWidth?: boolean;
}) {
  return (
    <div className={`flex items-center justify-between p-2 rounded bg-muted/30 ${fullWidth ? 'col-span-2' : ''}`}>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <span className="text-xs font-mono font-semibold">{value}</span>
    </div>
  );
}

// Generate detailed text report
function generateDetailedReport(result: DetailedAnalysisResult): string {
  const lines = [
    '═'.repeat(70),
    '              RAPPORT D\'ANALYSE D\'IMAGERIE MÉDICALE',
    '                    Système IRMSIA Deep Learning',
    '═'.repeat(70),
    '',
    `Date du rapport: ${new Date().toLocaleString('fr-FR')}`,
    `Modèle utilisé: ${result.model_info?.type || 'Non spécifié'}`,
    `Version: ${result.model_info?.version || '2.0.0'}`,
    '',
    '─'.repeat(70),
    '                         SYNTHÈSE DIAGNOSTIQUE',
    '─'.repeat(70),
    '',
    `Diagnostic principal: ${result.anomaly_name || result.anomaly_class}`,
    `Statut: ${result.has_anomaly ? 'ANOMALIE DÉTECTÉE' : 'NORMAL'}`,
    `Niveau de confiance: ${(result.confidence * 100).toFixed(1)}%`,
    `Sévérité: ${result.severity?.toUpperCase() || 'NON ÉVALUÉE'}`,
    `Urgence: ${result.urgency?.toUpperCase() || 'NON ÉVALUÉE'}`,
    '',
  ];

  if (result.description) {
    lines.push('Description clinique:');
    lines.push(`  ${result.description}`);
    lines.push('');
  }

  // Top predictions
  if (result.top_predictions && result.top_predictions.length > 0) {
    lines.push('─'.repeat(70));
    lines.push('                      CLASSIFICATIONS DIFFÉRENTIELLES');
    lines.push('─'.repeat(70));
    lines.push('');
    
    result.top_predictions.forEach((pred, idx) => {
      const bar = '█'.repeat(Math.round(pred.probability * 20));
      lines.push(`  ${idx + 1}. ${pred.class_name.padEnd(20)} ${bar.padEnd(20)} ${(pred.probability * 100).toFixed(1)}%`);
    });
    lines.push('');
  }

  // Measurements
  lines.push('─'.repeat(70));
  lines.push('                           MESURES QUANTITATIVES');
  lines.push('─'.repeat(70));
  lines.push('');
  lines.push(`  Nombre de régions détectées: ${result.measurements.num_regions || 0}`);
  
  if (result.measurements.total_area_mm2) {
    lines.push(`  Surface totale: ${result.measurements.total_area_mm2.toFixed(2)} mm²`);
    if (result.measurements.max_area_mm2) {
      lines.push(`  Surface maximale: ${result.measurements.max_area_mm2.toFixed(2)} mm²`);
    }
    if (result.measurements.avg_area_mm2) {
      lines.push(`  Surface moyenne: ${result.measurements.avg_area_mm2.toFixed(2)} mm²`);
    }
  } else if (result.measurements.total_area_pixels) {
    lines.push(`  Surface totale: ${result.measurements.total_area_pixels} pixels`);
  }
  
  if (result.measurements.segmentation_ratio) {
    lines.push(`  Ratio de segmentation: ${(result.measurements.segmentation_ratio * 100).toFixed(2)}%`);
  }
  lines.push('');

  // Regions
  if (result.bounding_boxes.length > 0) {
    lines.push('─'.repeat(70));
    lines.push('                         RÉGIONS D\'INTÉRÊT');
    lines.push('─'.repeat(70));
    lines.push('');
    
    result.bounding_boxes.forEach((box, idx) => {
      lines.push(`  Région ${idx + 1}: ${box.label || ''}`);
      lines.push(`    Position: (${box.x}, ${box.y})`);
      lines.push(`    Dimensions: ${box.width} × ${box.height} pixels`);
      if (box.confidence) {
        lines.push(`    Confiance: ${(box.confidence * 100).toFixed(1)}%`);
      }
      if (box.area_mm2) {
        lines.push(`    Surface: ${box.area_mm2.toFixed(2)} mm²`);
      }
      lines.push('');
    });
  }

  // Recommendations
  if (result.recommendations && result.recommendations.length > 0) {
    lines.push('─'.repeat(70));
    lines.push('                    RECOMMANDATIONS CLINIQUES');
    lines.push('─'.repeat(70));
    lines.push('');
    
    result.recommendations.forEach((rec, idx) => {
      lines.push(`  ${idx + 1}. ${rec}`);
    });
    lines.push('');
  }

  // Footer
  lines.push('═'.repeat(70));
  lines.push('                    AVERTISSEMENT MÉDICO-LÉGAL');
  lines.push('─'.repeat(70));
  lines.push('');
  lines.push('  Ce rapport est généré automatiquement par un système d\'intelligence');
  lines.push('  artificielle et ne constitue pas un diagnostic médical définitif.');
  lines.push('  Une corrélation clinique par un professionnel de santé qualifié');
  lines.push('  est indispensable avant toute décision thérapeutique.');
  lines.push('');
  lines.push(`  Temps de traitement: ${result.processing_time_ms?.toFixed(0) || 'N/A'} ms`);
  lines.push('═'.repeat(70));

  return lines.join('\n');
}

export default DetailedAnalysisViewer;

