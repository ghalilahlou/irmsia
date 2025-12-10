'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Ruler, 
  Layers, 
  MapPin, 
  TrendingUp, 
  Activity,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  label?: string;
}

interface Measurement {
  total_area_mm2?: number;
  num_regions?: number;
  max_area_mm2?: number;
  min_area_mm2?: number;
  perimeter_mm?: number;
  average_confidence?: number;
}

interface AnalysisSegmentsProps {
  boundingBoxes?: BoundingBox[];
  measurements?: Measurement;
  segmentationMask?: any;
  visualization?: any;
  anomalyClass?: string;
  confidence?: number;
}

export function AnalysisSegments({
  boundingBoxes = [],
  measurements,
  segmentationMask,
  visualization,
  anomalyClass,
  confidence,
}: AnalysisSegmentsProps) {
  const hasData = boundingBoxes.length > 0 || measurements || segmentationMask || visualization;

  if (!hasData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Segments de Segmentation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            Aucun segment détecté pour cette analyse.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {/* Bounding Boxes */}
      {boundingBoxes.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <MapPin className="h-4 w-4 text-blue-400" />
              Régions Détectées ({boundingBoxes.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {boundingBoxes.map((box, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border bg-card/50 p-2 text-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">
                        Région #{idx + 1}
                      </span>
                      {box.confidence && (
                        <Badge variant="secondary" className="text-xs">
                          {(box.confidence * 100).toFixed(1)}%
                        </Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-1 text-muted-foreground">
                      <div>
                        <span className="text-[10px]">Position:</span>
                        <p className="font-mono text-[10px]">
                          ({Math.round(box.x)}, {Math.round(box.y)})
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px]">Taille:</span>
                        <p className="font-mono text-[10px]">
                          {Math.round(box.width)} × {Math.round(box.height)} px
                        </p>
                      </div>
                    </div>
                    {box.label && (
                      <div className="mt-1 pt-1 border-t">
                        <Badge variant="outline" className="text-[10px]">
                          {box.label}
                        </Badge>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Measurements */}
      {measurements && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Ruler className="h-4 w-4 text-green-400" />
              Mesures Détaillées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {/* Surface totale */}
              {measurements.total_area_mm2 !== undefined && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2">
                    <Activity className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">Surface totale</span>
                  </div>
                  <span className="text-xs font-mono font-semibold">
                    {measurements.total_area_mm2.toFixed(2)} mm²
                  </span>
                </div>
              )}

              {/* Nombre de régions */}
              {measurements.num_regions !== undefined && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2">
                    <Layers className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">Nombre de régions</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {measurements.num_regions}
                  </Badge>
                </div>
              )}

              {/* Surface max/min */}
              {(measurements.max_area_mm2 !== undefined || measurements.min_area_mm2 !== undefined) && (
                <div className="grid grid-cols-2 gap-2">
                  {measurements.max_area_mm2 !== undefined && (
                    <div className="p-2 rounded-lg bg-muted/30">
                      <span className="text-[10px] text-muted-foreground block mb-1">
                        Surface max
                      </span>
                      <span className="text-xs font-mono font-semibold">
                        {measurements.max_area_mm2.toFixed(2)} mm²
                      </span>
                    </div>
                  )}
                  {measurements.min_area_mm2 !== undefined && (
                    <div className="p-2 rounded-lg bg-muted/30">
                      <span className="text-[10px] text-muted-foreground block mb-1">
                        Surface min
                      </span>
                      <span className="text-xs font-mono font-semibold">
                        {measurements.min_area_mm2.toFixed(2)} mm²
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Périmètre */}
              {measurements.perimeter_mm !== undefined && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">Périmètre</span>
                  </div>
                  <span className="text-xs font-mono font-semibold">
                    {measurements.perimeter_mm.toFixed(2)} mm
                  </span>
                </div>
              )}

              {/* Confiance moyenne */}
              {measurements.average_confidence !== undefined && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">Confiance moyenne</span>
                  </div>
                  <Badge 
                    variant={measurements.average_confidence > 0.7 ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {(measurements.average_confidence * 100).toFixed(1)}%
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Segmentation Info */}
      {(segmentationMask || visualization) && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Layers className="h-4 w-4 text-purple-400" />
              Masques de Segmentation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-xs">
              {segmentationMask && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-muted-foreground">Masque de segmentation</span>
                  <Badge variant="outline" className="text-xs">
                    Disponible
                  </Badge>
                </div>
              )}
              {visualization && (
                <div className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                  <span className="text-muted-foreground">Visualisation (GradCAM)</span>
                  <Badge variant="outline" className="text-xs">
                    Disponible
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Anomaly Summary */}
      {anomalyClass && (
        <Card className="border-orange-500/30 bg-orange-500/5">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-400" />
              Classification
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Type d'anomalie</span>
                <Badge variant="destructive" className="text-xs capitalize">
                  {anomalyClass}
                </Badge>
              </div>
              {confidence !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Niveau de confiance</span>
                  <span className="text-xs font-semibold">
                    {(confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

