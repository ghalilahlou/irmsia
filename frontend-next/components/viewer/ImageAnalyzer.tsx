'use client';

import { useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, Loader2, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useAnomalyDetection } from '@/hooks/useAnomalyDetection';
import { AnalysisSegments } from './AnalysisSegments';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface ImageAnalyzerProps {
  imageFile?: File | null;
  imageUrl?: string | null;
  onAnalysisComplete?: (result: any) => void;
}

export function ImageAnalyzer({ imageFile, imageUrl, onAnalysisComplete }: ImageAnalyzerProps) {
  const { isAnalyzing, error, result, analyzeImage, reset } = useAnomalyDetection();
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Réinitialiser l'état quand l'image change
  useEffect(() => {
    if (imageFile || imageUrl) {
      reset();
      setHasAnalyzed(false);
    }
  }, [imageFile, imageUrl, reset]);

  // Appeler onAnalysisComplete quand le résultat change
  useEffect(() => {
    if (result && onAnalysisComplete) {
      onAnalysisComplete(result);
    }
  }, [result, onAnalysisComplete]);

  const handleAnalyze = useCallback(async () => {
    let fileToAnalyze: File | null = null;

    if (imageFile) {
      fileToAnalyze = imageFile;
    } else if (imageUrl) {
      // Convert data URL to File without fetch (CSP-safe)
      try {
        const dataUrlToFile = (dataUrl: string, filename: string): File => {
          const arr = dataUrl.split(',');
          const mimeMatch = arr[0].match(/:(.*?);/);
          const mime = mimeMatch ? mimeMatch[1] : 'image/png';
          const bstr = atob(arr[1]);
          let n = bstr.length;
          const u8arr = new Uint8Array(n);
          while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
          }
          return new File([u8arr], filename, { type: mime });
        };
        fileToAnalyze = dataUrlToFile(imageUrl, 'dicom-image.png');
      } catch (err) {
        console.error('Error converting image URL:', err);
        return;
      }
    }

    if (!fileToAnalyze) {
      console.error('No image file or URL available for analysis');
      return;
    }

    try {
      await analyzeImage(fileToAnalyze);
      setHasAnalyzed(true);
    } catch (err) {
      console.error('Error during analysis:', err);
    }
  }, [imageFile, imageUrl, analyzeImage]);

  const handleReset = useCallback(() => {
    reset();
    setHasAnalyzed(false);
  }, [reset]);

  const hasImage = imageFile || imageUrl;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Brain className="h-5 w-5 text-purple-400" />
          Analyse IA Deep Learning
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!hasImage && (
          <p className="text-sm text-muted-foreground">
            Chargez une image DICOM pour activer l'analyse IA
          </p>
        )}

        {hasImage && !hasAnalyzed && !result && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Analysez l'image DICOM actuelle avec l'algorithme de deep learning pour détecter les anomalies médicales.
            </p>
            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !hasImage}
              className="w-full"
              variant="default"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-4 w-4" />
                  Analyser l'image avec IA
                </>
              )}
            </Button>
          </div>
        )}

        {isAnalyzing && (
          <div className="flex items-center gap-2 text-sm text-blue-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Analyse en cours avec l'algorithme de deep learning...</span>
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3">
            <div className="flex items-start gap-2">
              <XCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-400">Erreur d'analyse</p>
                <p className="text-xs text-red-300/80 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {result && (
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-3 h-8 text-xs">
              <TabsTrigger value="summary">Résumé</TabsTrigger>
              <TabsTrigger value="segments">Segments</TabsTrigger>
              <TabsTrigger value="details">Détails</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="space-y-3 mt-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Résultat de l'analyse</span>
                <Button
                  onClick={handleReset}
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                >
                  Réanalyser
                </Button>
              </div>

              {/* Statut de détection */}
              <div className={`rounded-lg border p-3 ${
                result.has_anomaly 
                  ? 'border-orange-500/30 bg-orange-500/10' 
                  : 'border-green-500/30 bg-green-500/10'
              }`}>
                <div className="flex items-center gap-2">
                  {result.has_anomaly ? (
                    <>
                      <AlertTriangle className="h-4 w-4 text-orange-400" />
                      <span className="text-sm font-medium text-orange-400">
                        Anomalie détectée
                      </span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      <span className="text-sm font-medium text-green-400">
                        Aucune anomalie détectée
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Informations rapides */}
              {result.has_anomaly && (
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg border bg-card p-2">
                    <span className="text-muted-foreground block mb-1">Type</span>
                    <p className="font-medium capitalize">{result.anomaly_class || 'Inconnu'}</p>
                  </div>
                  <div className="rounded-lg border bg-card p-2">
                    <span className="text-muted-foreground block mb-1">Confiance</span>
                    <p className="font-medium">
                      {result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                  </div>
                </div>
              )}

              {/* Recommandations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 p-3">
                  <p className="text-xs font-medium text-blue-400 mb-2">Recommandations:</p>
                  <ul className="space-y-1 text-xs text-blue-300/80">
                    {result.recommendations.slice(0, 3).map((rec: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Lien vers la page d'analyse complète */}
              {result.has_anomaly && (
                <Button
                  onClick={() => {
                    window.location.href = '/anomaly-detection';
                  }}
                  variant="outline"
                  className="w-full text-xs"
                  size="sm"
                >
                  Voir l'analyse détaillée
                </Button>
              )}
            </TabsContent>

            <TabsContent value="segments" className="mt-3">
              <AnalysisSegments
                boundingBoxes={result.bounding_boxes}
                measurements={result.measurements}
                segmentationMask={result.segmentation_mask}
                visualization={result.visualization}
                anomalyClass={result.anomaly_class}
                confidence={result.confidence}
              />
            </TabsContent>

            <TabsContent value="details" className="mt-3 space-y-3">
              <div className="space-y-2 rounded-lg border bg-card p-3 text-xs">
                <h4 className="font-semibold mb-2">Informations complètes</h4>
                
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-muted-foreground">Image ID:</span>
                    <p className="font-mono text-[10px] break-all">{result.image_id || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Modèle utilisé:</span>
                    <p className="text-[10px]">{result.model_used || 'N/A'}</p>
                  </div>
                </div>

                {result.bounding_boxes && result.bounding_boxes.length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <span className="text-muted-foreground block mb-2">
                      Régions détectées: {result.bounding_boxes.length}
                    </span>
                    <div className="space-y-1 max-h-[150px] overflow-y-auto">
                      {result.bounding_boxes.map((box: any, idx: number) => (
                        <div key={idx} className="text-[10px] p-1 rounded bg-muted/30">
                          <span className="font-mono">
                            R{idx + 1}: ({Math.round(box.x)}, {Math.round(box.y)}) 
                            {Math.round(box.width)}×{Math.round(box.height)}px
                            {box.confidence && ` - ${(box.confidence * 100).toFixed(1)}%`}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.measurements && (
                  <div className="mt-3 pt-3 border-t">
                    <h5 className="font-semibold mb-2 text-xs">Mesures complètes</h5>
                    <div className="space-y-1 text-[10px]">
                      {Object.entries(result.measurements).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-muted-foreground capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="font-mono">
                            {typeof value === 'number' 
                              ? value.toFixed(2) 
                              : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}

