'use client';

/**
 * Anomaly Detection Page - Optimisé
 * Interface complète pour détection d'anomalies, segmentation, mesures et rapport médical
 */

import React, { useState, useRef, useMemo, Suspense, lazy } from 'react';
import { Upload, AlertCircle, CheckCircle, FileText, Ruler, Target, Activity } from 'lucide-react';
import ImageUploader from '@/components/anomaly/ImageUploader';
import ProgressBar from '@/components/anomaly/ProgressBar';
import { useAnomalyDetection } from '@/hooks/useAnomalyDetection';

// Lazy loading des composants lourds pour améliorer les performances initiales
const AdvancedAnomalyViewer = lazy(() => import('@/components/anomaly/AdvancedAnomalyViewer'));
const SegmentationPanel = lazy(() => import('@/components/anomaly/SegmentationPanel'));
const MeasurementTools = lazy(() => import('@/components/anomaly/MeasurementTools'));
const MedicalReportGenerator = lazy(() => import('@/components/anomaly/MedicalReportGenerator'));

// Composant de chargement
const LoadingFallback = () => (
  <div className="flex items-center justify-center h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
  </div>
);

export default function AnomalyDetectionPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedTab, setSelectedTab] = useState<'viewer' | 'segmentation' | 'measurements' | 'report'>('viewer');
  const viewerRef = useRef<any>(null);
  
  // Utiliser le hook personnalisé pour la logique métier
  const { isAnalyzing, error, result, analyzeImage, reset } = useAnomalyDetection();

  // Handler optimisé avec useCallback implicite dans le hook
  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    await analyzeImage(file);
  };

  // Mémoriser les tabs pour éviter les re-créations
  const tabs = useMemo(() => [
    { id: 'viewer' as const, label: 'Visualisation', icon: Target },
    { id: 'segmentation' as const, label: 'Segmentation', icon: Activity },
    { id: 'measurements' as const, label: 'Mesures', icon: Ruler },
    { id: 'report' as const, label: 'Rapport', icon: FileText },
  ], []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
          <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Détection d'Anomalies Médicales
          </h1>
          <p className="text-gray-400">
            Analysez vos images médicales avec IA avancée, segmentation automatique et rapport médical
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne gauche: Upload */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-cyan-400" />
              Upload Image
            </h2>
            
            <ImageUploader
              onFileSelect={handleFileUpload}
              isAnalyzing={isAnalyzing}
            />
            
            {/* Status avec Progress Bar */}
            {isAnalyzing && (
              <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg space-y-3">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                  <span className="text-sm text-blue-400 font-medium">Analyse en cours...</span>
                </div>
                <ProgressBar 
                  progress={50} 
                  label="Traitement de l'image"
                  showPercentage={true}
                />
                <p className="text-xs text-gray-400 mt-2">
                  L'analyse peut prendre quelques secondes selon la taille de l'image...
                </p>
              </div>
            )}
            
            {error && (
              <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <span className="text-sm text-red-400">{error}</span>
                </div>
              </div>
            )}
            
            {result && !isAnalyzing && (
              <div className="mt-4 space-y-4">
                {/* Résultat */}
                <div className={`p-4 rounded-lg border ${
                  result.has_anomaly 
                    ? 'bg-red-500/10 border-red-500/30' 
                    : 'bg-green-500/10 border-green-500/30'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    {result.has_anomaly ? (
                      <AlertCircle className="w-5 h-5 text-red-400" />
                    ) : (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                    <span className="font-semibold">
                      {result.has_anomaly ? 'Anomalie Détectée' : 'Normal'}
                    </span>
                  </div>
                  
                  {result.has_anomaly && (
                    <div className="text-sm space-y-1">
                      <div>
                        <span className="text-gray-400">Type: </span>
                        <span className="text-white font-medium capitalize">
                          {result.anomaly_class}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Confiance: </span>
                        <span className="text-white font-medium">
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      {result.measurements && (
                        <div>
                          <span className="text-gray-400">Régions: </span>
                          <span className="text-white font-medium">
                            {result.measurements.num_regions}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Détails */}
                {result.measurements && (
                  <div className="p-4 bg-gray-700/30 rounded-lg">
                    <h3 className="text-sm font-semibold mb-2">Mesures</h3>
                    <div className="text-xs space-y-1 text-gray-300">
                      <div>Surface totale: {result.measurements.total_area_mm2?.toFixed(1) || 0} mm²</div>
                      <div>Nombre de régions: {result.measurements.num_regions || 0}</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Colonne droite: Visualisation et analyse */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-gray-700 bg-gray-800/30">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedTab(tab.id)}
                    className={`flex-1 px-4 py-3 flex items-center justify-center gap-2 transition-colors ${
                      selectedTab === tab.id
                        ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-400'
                        : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
                    }`}
                    disabled={!result}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Content */}
            <div className="p-6">
              {!result ? (
                <div className="flex flex-col items-center justify-center h-96 text-gray-500">
                  <Upload className="w-16 h-16 mb-4 opacity-50" />
                  <p className="text-lg">Uploadez une image pour commencer l'analyse</p>
                  <p className="text-sm mt-2">Formats supportés: DICOM, PNG, TIFF, JPG</p>
                </div>
              ) : (
                <Suspense fallback={<LoadingFallback />}>
                  {selectedTab === 'viewer' && (
                    <AdvancedAnomalyViewer
                      ref={viewerRef}
                      result={result}
                      originalFile={uploadedFile}
                    />
                  )}
                  
                  {selectedTab === 'segmentation' && (
                    <SegmentationPanel
                      result={result}
                      originalFile={uploadedFile}
                    />
                  )}
                  
                  {selectedTab === 'measurements' && (
                    <MeasurementTools
                      result={result}
                      viewerRef={viewerRef}
                    />
                  )}
                  
                  {selectedTab === 'report' && (
                    <MedicalReportGenerator
                      result={result}
                      originalFile={uploadedFile}
                    />
                  )}
                </Suspense>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


