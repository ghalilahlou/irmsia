'use client';

import { useRef, useState, useCallback, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import UploadBox from '@/components/UploadBox';
import { UnifiedToolbar } from '@/components/dicom/UnifiedToolbar';
import MetadataPanel from './metadataPanel';
import { loadDicomFiles } from '@/lib/dicom/unifiedLoader';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Brain,
  AlertTriangle,
  CheckCircle,
  Eye,
  EyeOff,
  Layers,
  Info,
  Target,
} from 'lucide-react';
import type { DicomMetadata, ViewerTool } from '@/lib/dicom/types';
import type { UnifiedViewerHandle, AnomalyResult } from '@/components/dicom/UnifiedDicomViewer';

// Dynamic import with stable loading component
const UnifiedDicomViewer = dynamic(
  () => import('@/components/dicom/UnifiedDicomViewer'),
  { ssr: false }
) as typeof import('@/components/dicom/UnifiedDicomViewer').default;

// Spinner component - stable, no conditional rendering issues
function Spinner({ size = 'sm', className = '' }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClass = size === 'sm' ? 'h-3 w-3' : size === 'md' ? 'h-4 w-4' : 'h-5 w-5';
  return (
    <div className={`${sizeClass} ${className} animate-spin rounded-full border-2 border-current border-t-transparent`} />
  );
}

// Fonction utilitaire pour convertir data URL en File (CSP-safe)
function dataUrlToFile(dataUrl: string, filename: string): File {
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
}

export default function ViewerPage() {
  const viewerRef = useRef<UnifiedViewerHandle>(null);
  const [imageIds, setImageIds] = useState<string[]>([]);
  const [metadata, setMetadata] = useState<DicomMetadata>({});
  const [activeTool, setActiveTool] = useState<ViewerTool>('pan');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [viewerReady, setViewerReady] = useState(false);

  // États pour l'analyse Deep Learning
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnomalyResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [showAnomalyOverlay, setShowAnomalyOverlay] = useState(true);

  // Stable key for viewer - only changes when imageIds actually change content
  const viewerKey = useMemo(() => {
    if (imageIds.length === 0) return 'empty';
    return imageIds[0].slice(0, 50); // Use first 50 chars to avoid too long keys
  }, [imageIds]);

  // Reset l'analyse quand une nouvelle image est chargée
  useEffect(() => {
    if (imageIds.length === 0) {
      setAnalysisResult(null);
      setAnalysisError(null);
      setViewerReady(false);
    }
  }, [imageIds]);

  const handleFiles = useCallback(async (files: File[]) => {
    setLoading(true);
    setStatus('Analyse des fichiers DICOM…');
    setAnalysisResult(null);
    setAnalysisError(null);
    setViewerReady(false);

    try {
      const stack = await loadDicomFiles(files, { format: 'stack' });
      if (!stack || !('imageIds' in stack) || !stack.imageIds.length) {
        setStatus('Aucune image DICOM exploitable détectée.');
        setImageIds([]);
        setMetadata({});
        return;
      }
      setImageIds(stack.imageIds);
      setMetadata(stack.metadata);
      setStatus(
        `${stack.imageIds.length} frame${stack.imageIds.length > 1 ? 's' : ''} chargée(s). Prêt pour l'analyse.`,
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Impossible de charger les fichiers.';
      setStatus(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExport = useCallback(async () => {
    if (!viewerRef.current) return;
    const png = await viewerRef.current.exportPng();
    if (!png) return;
    const link = document.createElement('a');
    link.href = png;
    link.download = `dicom-frame-${Date.now()}.png`;
    link.click();
  }, []);

  const handleViewerReady = useCallback(() => {
    setViewerReady(true);
  }, []);

  // Fonction d'analyse Deep Learning
  const handleAnalyze = useCallback(async () => {
    if (!viewerRef.current || !viewerReady) {
      setAnalysisError('Le viewer n\'est pas prêt. Veuillez attendre le chargement complet.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      // Exporter l'image actuelle du viewer
      const pngDataUrl = await viewerRef.current.exportPng();
      if (!pngDataUrl) {
        throw new Error('Impossible d\'exporter l\'image pour l\'analyse.');
      }

      // Convertir en File
      const imageFile = dataUrlToFile(pngDataUrl, `dicom-analysis-${Date.now()}.png`);

      // Appel API pour l'analyse
      const formData = new FormData();
      formData.append('file', imageFile);

      // Try the anomaly detection endpoint first
      let response = await fetch('/api/v1/anomaly/detect', {
        method: 'POST',
        body: formData,
      });

      // Fallback to other endpoints if needed
      if (!response.ok) {
        const formData2 = new FormData();
        formData2.append('file', imageFile);
        
        response = await fetch('/api/v1/analysis/detect', {
          method: 'POST',
          body: formData2,
        });
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur serveur (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      setAnalysisResult(result);
      setStatus(
        result.has_anomaly
          ? `⚠️ Anomalie détectée: ${result.anomaly_class || 'Type inconnu'} (${((result.confidence || 0) * 100).toFixed(1)}%)`
          : '✅ Aucune anomalie détectée',
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erreur lors de l\'analyse';
      setAnalysisError(message);
      setStatus(`❌ Erreur d'analyse: ${message}`);
    } finally {
      setIsAnalyzing(false);
    }
  }, [viewerReady]);

  const handleResetAnalysis = useCallback(() => {
    setAnalysisResult(null);
    setAnalysisError(null);
    setStatus(imageIds.length > 0 ? 'Prêt pour l\'analyse.' : null);
  }, [imageIds.length]);

  const viewerDisabled = !imageIds.length || loading;
  const canAnalyze = imageIds.length > 0 && viewerReady && !isAnalyzing;

  // Button text based on state - computed once
  const analyzeButtonContent = useMemo(() => {
    if (isAnalyzing) {
      return (
        <span className="inline-flex items-center">
          <Spinner size="md" className="mr-2" />
          Analyse en cours...
        </span>
      );
    }
    if (analysisResult) {
      return (
        <span className="inline-flex items-center">
          <Brain className="mr-2 h-4 w-4" />
          Réanalyser l'image
        </span>
      );
    }
    return (
      <span className="inline-flex items-center">
        <Brain className="mr-2 h-4 w-4" />
        Lancer l'analyse IA
      </span>
    );
  }, [isAnalyzing, analysisResult]);

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">DICOM Viewer avec Analyse IA</h1>
        <p className="text-sm text-muted-foreground">
          Chargez une image DICOM, utilisez les outils de visualisation, et lancez l'analyse Deep Learning pour détecter les anomalies.
        </p>
      </div>

      {/* Upload */}
      <UploadBox onFilesSelected={handleFiles} disabled={loading} />

      {/* Toolbar */}
      <UnifiedToolbar
        mode="simple"
        activeTool={activeTool}
        onSelectTool={setActiveTool}
        onInvert={() => viewerRef.current?.invert()}
        onFlipHorizontal={() => viewerRef.current?.flipHorizontal()}
        onFlipVertical={() => viewerRef.current?.flipVertical()}
        onReset={() => viewerRef.current?.reset()}
        onExport={handleExport}
        disabled={viewerDisabled}
      />

      {/* Status */}
      {status && (
        <div className="rounded-lg border border-dashed bg-muted/40 px-4 py-2 text-sm">
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <Spinner size="sm" />
              Traitement en cours…
            </span>
          ) : (
            status
          )}
        </div>
      )}

      {/* Main Content */}
      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        {/* Viewer - completely isolated section */}
        <div className="relative min-h-[500px]">
          {imageIds.length === 0 ? (
            <div className="flex h-[500px] items-center justify-center rounded-lg border bg-black text-muted-foreground">
              Aucune image DICOM chargée
            </div>
          ) : (
            <UnifiedDicomViewer
              key={viewerKey}
              ref={viewerRef}
              imageIds={imageIds}
              metadata={metadata}
              activeTool={activeTool}
              mode="simple"
              showAnomalyOverlay={showAnomalyOverlay}
              anomalyResult={analysisResult}
              onError={(message) => setStatus(`❌ ${message}`)}
              onReady={handleViewerReady}
            />
          )}

          {/* Overlay control - only show when we have results */}
          {analysisResult?.has_anomaly && (
            <div className="absolute bottom-2 left-2 z-10">
              <Button
                variant={showAnomalyOverlay ? 'default' : 'outline'}
                size="sm"
                onClick={() => setShowAnomalyOverlay(!showAnomalyOverlay)}
                className="gap-2"
              >
                {showAnomalyOverlay ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                {showAnomalyOverlay ? 'Masquer overlay' : 'Afficher overlay'}
              </Button>
            </div>
          )}
        </div>

        {/* Side panel */}
        <div className="flex flex-col gap-4">
          {/* Analysis button */}
          <Card className="border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-transparent">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Brain className="h-5 w-5 text-purple-400" />
                Analyse Deep Learning
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {!imageIds.length ? (
                <p className="text-sm text-muted-foreground">
                  Chargez une image DICOM pour activer l'analyse IA.
                </p>
              ) : !viewerReady ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Spinner size="md" />
                  Initialisation du viewer...
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs text-muted-foreground">
                    Analysez l'image DICOM avec notre algorithme de deep learning pour détecter automatiquement les anomalies médicales.
                  </p>
                  <Button
                    onClick={handleAnalyze}
                    disabled={!canAnalyze}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                    size="lg"
                  >
                    {analyzeButtonContent}
                  </Button>
                </div>
              )}

              {/* Error display */}
              {analysisError && (
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-400">
                  {analysisError}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Analysis results */}
          {analysisResult && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-base">
                  <span className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Résultats
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleResetAnalysis}
                    className="h-7 text-xs"
                  >
                    Effacer
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="summary" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 h-8 text-xs">
                    <TabsTrigger value="summary">Résumé</TabsTrigger>
                    <TabsTrigger value="zones">Zones</TabsTrigger>
                    <TabsTrigger value="details">Détails</TabsTrigger>
                  </TabsList>

                  <TabsContent value="summary" className="space-y-3 mt-3">
                    <div
                      className={`rounded-lg border p-3 ${
                        analysisResult.has_anomaly
                          ? 'border-orange-500/30 bg-orange-500/10'
                          : 'border-green-500/30 bg-green-500/10'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {analysisResult.has_anomaly ? (
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
                              Aucune anomalie
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {analysisResult.has_anomaly && (
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="rounded-lg border bg-card p-2">
                          <span className="text-muted-foreground block">Type</span>
                          <p className="font-medium capitalize">
                            {analysisResult.anomaly_class || 'Non classifié'}
                          </p>
                        </div>
                        <div className="rounded-lg border bg-card p-2">
                          <span className="text-muted-foreground block">Confiance</span>
                          <p className="font-medium">
                            {analysisResult.confidence
                              ? `${(analysisResult.confidence * 100).toFixed(1)}%`
                              : 'N/A'}
                          </p>
                        </div>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="zones" className="mt-3">
                    {analysisResult.bounding_boxes && analysisResult.bounding_boxes.length > 0 ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Layers className="h-3 w-3" />
                          {analysisResult.bounding_boxes.length} zone(s) détectée(s)
                        </div>
                        <div className="max-h-[200px] overflow-y-auto space-y-2">
                          {analysisResult.bounding_boxes.map((box, idx) => (
                            <div
                              key={idx}
                              className="rounded-lg border bg-muted/30 p-2 text-xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-medium">
                                  Zone {idx + 1}
                                  {box.label && ` - ${box.label}`}
                                </span>
                                {box.confidence && (
                                  <span className="text-muted-foreground">
                                    {(box.confidence * 100).toFixed(0)}%
                                  </span>
                                )}
                              </div>
                              <p className="text-[10px] text-muted-foreground mt-1 font-mono">
                                Position: ({Math.round(box.x)}, {Math.round(box.y)}) |
                                Taille: {Math.round(box.width)}×{Math.round(box.height)}px
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center py-6 text-xs text-muted-foreground">
                        <Info className="h-8 w-8 mb-2 opacity-50" />
                        <p>Aucune zone spécifique détectée</p>
                        {analysisResult.has_anomaly && (
                          <p className="text-[10px] mt-1">
                            L'anomalie a été détectée de manière globale
                          </p>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="details" className="mt-3">
                    <div className="space-y-3 text-xs">
                      {analysisResult.measurements && Object.keys(analysisResult.measurements).length > 0 && (
                        <div className="rounded-lg border bg-card p-2">
                          <h4 className="font-semibold mb-2">Mesures</h4>
                          <div className="space-y-1">
                            {Object.entries(analysisResult.measurements).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground capitalize">
                                  {key.replace(/_/g, ' ')}:
                                </span>
                                <span className="font-mono">
                                  {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="rounded-lg border bg-card p-2">
                        <h4 className="font-semibold mb-2">Informations techniques</h4>
                        <div className="space-y-1 text-[10px]">
                          <p>
                            <span className="text-muted-foreground">Segmentation: </span>
                            {analysisResult.segmentation_mask ? 'Disponible' : 'Non disponible'}
                          </p>
                          <p>
                            <span className="text-muted-foreground">Heatmap: </span>
                            {analysisResult.visualization ? 'Disponible' : 'Non disponible'}
                          </p>
                          <p>
                            <span className="text-muted-foreground">Bounding boxes: </span>
                            {analysisResult.bounding_boxes?.length || 0}
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* DICOM Metadata */}
          <MetadataPanel metadata={metadata} />
        </div>
      </div>
    </div>
  );
}
