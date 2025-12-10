'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import UploadBox from '@/components/UploadBox';
import { UnifiedToolbar } from '@/components/dicom/UnifiedToolbar';
import { LayoutSelector } from '@/components/dicom/LayoutSelector';
import { loadDicomFiles } from '@/lib/dicom/unifiedLoader';
import { getPresetsForModality } from '@/lib/dicom/presets';
import type {
  DicomStudy,
  ViewerTool,
  ViewportLayout,
  DicomMetadata,
} from '@/lib/dicom/types';
import type { WindowLevelPreset } from '@/lib/dicom/presets';
import type { UnifiedViewerHandle } from '@/components/dicom/UnifiedDicomViewer';

const UnifiedDicomViewer = dynamic(
  () => import('@/components/dicom/UnifiedDicomViewer'),
  { ssr: false },
);

export default function ProfessionalViewerPage() {
  const viewportRefs = useRef<Array<UnifiedViewerHandle | null>>([null, null, null, null]);
  
  const [study, setStudy] = useState<DicomStudy | null>(null);
  const [activeTool, setActiveTool] = useState<ViewerTool>('pan');
  const [layout, setLayout] = useState<ViewportLayout>('1x1');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [showOverlay, setShowOverlay] = useState(true);
  
  // Viewport states for multi-layout
  const [viewportStates, setViewportStates] = useState<Array<{
    seriesIndex: number;
    imageIndex: number;
  }>>([
    { seriesIndex: 0, imageIndex: 0 },
    { seriesIndex: 0, imageIndex: 0 },
    { seriesIndex: 0, imageIndex: 0 },
    { seriesIndex: 0, imageIndex: 0 },
  ]);

  const handleFilesSelected = async (files: File[]) => {
    setLoading(true);
    setStatus('Analyse des fichiers DICOM…');
    setStudy(null); // Réinitialiser l'étude précédente
    
    try {
      const loadedStudy = await loadDicomFiles(files, { format: 'study' }) as DicomStudy | null;
      if (!loadedStudy || loadedStudy.series.length === 0) {
        setStatus('Aucune série DICOM trouvée');
        setLoading(false);
        return;
      }
      
      // Vérifier que toutes les séries ont des instances valides
      const validSeries = loadedStudy.series.filter(
        (s) => s.instances && s.instances.length > 0 && s.instances.some((inst) => inst.imageId)
      );
      
      if (validSeries.length === 0) {
        setStatus('Aucune image DICOM valide trouvée dans les fichiers');
        setLoading(false);
        return;
      }
      
      // Mettre à jour l'étude avec seulement les séries valides
      const updatedStudy = {
        ...loadedStudy,
        series: validSeries,
      };
      
      setStudy(updatedStudy);
      
      // Réinitialiser les états des viewports
      setViewportStates(
        Array.from({ length: 4 }, () => ({
          seriesIndex: 0,
          imageIndex: 0,
        }))
      );
      
      const totalImages = validSeries.reduce((sum, s) => sum + s.instances.length, 0);
      setStatus(
        `Chargé: ${validSeries.length} série(s), ${totalImages} image(s)`,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Échec du chargement DICOM';
      setStatus(`Erreur: ${message}`);
      console.error('[Professional Viewer] Load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    const viewport = viewportRefs.current[0];
    if (!viewport) return;

    const png = await viewport.exportPng();
    if (!png) return;

    const link = document.createElement('a');
    link.href = png;
    link.download = `dicom-export-${Date.now()}.png`;
    link.click();
  };

  const handlePresetSelect = (preset: WindowLevelPreset) => {
    viewportRefs.current.forEach((ref) => {
      if (ref && ref.applyPreset) ref.applyPreset(preset);
    });
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (loading || !study) return;

      // Tool shortcuts
      if (!e.ctrlKey && !e.altKey && !e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'z':
            setActiveTool('zoom');
            break;
          case 'p':
            setActiveTool('pan');
            break;
          case 'w':
            setActiveTool('wl');
            break;
          case 's':
            setActiveTool('scroll');
            break;
          case 'l':
            setActiveTool('length');
            break;
          case 'a':
            setActiveTool('angle');
            break;
          case 'r':
            setActiveTool('rectangleROI');
            break;
          case 'e':
            setActiveTool('ellipticalROI');
            break;
          case 'b':
            setActiveTool('probe');
            break;
          case 'i':
            viewportRefs.current[0]?.invert();
            break;
          case 'h':
            viewportRefs.current[0]?.flipHorizontal();
            break;
          case 'v':
            viewportRefs.current[0]?.flipVertical();
            break;
          case 'f':
            viewportRefs.current[0]?.fitToWindow?.();
            break;
          case 'o':
            setShowOverlay(!showOverlay);
            break;
          case 'escape':
            viewportRefs.current[0]?.reset();
            break;
          default:
            break;
        }
      }

      // Ctrl shortcuts
      if (e.ctrlKey) {
        switch (e.key.toLowerCase()) {
          case 'r':
            e.preventDefault();
            viewportRefs.current[0]?.rotate?.(90);
            break;
          case 's':
            e.preventDefault();
            handleExport();
            break;
          default:
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, study, showOverlay]);

  const getViewportCount = (currentLayout: ViewportLayout): number => {
    switch (currentLayout) {
      case '1x1':
        return 1;
      case '1x2':
        return 2;
      case '2x2':
        return 4;
      default:
        return 1;
    }
  };

  const getLayoutClass = (currentLayout: ViewportLayout): string => {
    switch (currentLayout) {
      case '1x1':
        return 'grid-cols-1 grid-rows-1';
      case '1x2':
        return 'grid-cols-2 grid-rows-1';
      case '2x2':
        return 'grid-cols-2 grid-rows-2';
      default:
        return 'grid-cols-1 grid-rows-1';
    }
  };

  const viewportCount = getViewportCount(layout);
  const disabled = !study || loading;
  const presets = study?.series[0]?.modality
    ? getPresetsForModality(study.series[0].modality)
    : [];

  return (
    <div className="flex h-screen flex-col gap-4 p-4">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Professional DICOM Viewer</h1>
        <p className="text-muted-foreground">
          Advanced medical imaging viewer with multi-series support, measurement tools, and
          professional features
        </p>
      </div>

      {/* Upload */}
      {!study && (
        <UploadBox onFilesSelected={handleFilesSelected} disabled={loading} />
      )}

      {/* Status */}
      {status && (
        <div className="rounded-lg border border-dashed bg-muted/40 px-4 py-2 text-sm text-muted-foreground">
          {loading && 'Loading… '}
          {status}
        </div>
      )}

      {/* Toolbar & Layout */}
      {study && (
        <div className="flex flex-wrap items-center gap-2">
          <UnifiedToolbar
            mode="professional"
            activeTool={activeTool}
            onSelectTool={setActiveTool}
            onInvert={() => viewportRefs.current[0]?.invert()}
            onFlipHorizontal={() => viewportRefs.current[0]?.flipHorizontal()}
            onFlipVertical={() => viewportRefs.current[0]?.flipVertical()}
            onRotate={() => viewportRefs.current[0]?.rotate?.(90)}
            onReset={() => viewportRefs.current[0]?.reset()}
            onFit={() => viewportRefs.current[0]?.fitToWindow?.()}
            onExport={handleExport}
            onPresetSelect={handlePresetSelect}
            windowLevelPresets={presets}
            disabled={disabled}
            showOverlay={showOverlay}
            onToggleOverlay={() => setShowOverlay(!showOverlay)}
          />
          <LayoutSelector
            currentLayout={layout}
            onLayoutChange={setLayout}
            disabled={disabled}
          />
        </div>
      )}

      {/* Viewports Grid */}
      {study && (
        <div className={`grid flex-1 gap-2 ${getLayoutClass(layout)}`}>
          {Array.from({ length: viewportCount }).map((_, index) => {
            const seriesIndex = Math.min(viewportStates[index].seriesIndex, study.series.length - 1);
            const series = study.series[seriesIndex];
            
            // Vérifier que la série existe et a des instances
            if (!series || !series.instances || series.instances.length === 0) {
              return (
                <div key={index} className="flex items-center justify-center rounded-lg border bg-muted/40 text-sm text-muted-foreground">
                  No images in series {seriesIndex + 1}
                </div>
              );
            }
            
            const imageIds = series.instances
              .map((inst) => inst.imageId)
              .filter((id): id is string => !!id); // Filtrer les IDs undefined/null
            
            // Vérifier qu'il y a des imageIds valides
            if (imageIds.length === 0) {
              return (
                <div key={index} className="flex items-center justify-center rounded-lg border bg-muted/40 text-sm text-muted-foreground">
                  No valid image IDs in series {seriesIndex + 1}
                </div>
              );
            }
            
            // S'assurer que l'index est valide
            const validImageIndex = Math.max(0, Math.min(viewportStates[index].imageIndex, imageIds.length - 1));
            
            const metadata: DicomMetadata = {
              studyDescription: study.studyDescription,
              seriesDescription: series.seriesDescription,
              seriesNumber: series.seriesNumber.toString(),
              instanceNumber: series.instances[validImageIndex]?.instanceNumber?.toString() || '1',
              modality: series.modality,
              patientName: study.patientName,
              patientID: study.patientID,
              studyDate: study.studyDate,
            };

            return (
              <UnifiedDicomViewer
                key={`viewport-${index}-${seriesIndex}-${validImageIndex}`}
                ref={(el) => {
                  viewportRefs.current[index] = el;
                }}
                imageIds={imageIds}
                currentIndex={validImageIndex}
                metadata={metadata}
                activeTool={activeTool}
                mode="professional"
                showOverlay={showOverlay}
                onIndexChange={(newIndex) => {
                  setViewportStates((prev) => {
                    const newStates = [...prev];
                    newStates[index] = { ...newStates[index], imageIndex: Math.max(0, Math.min(newIndex, imageIds.length - 1)) };
                    return newStates;
                  });
                }}
                onError={(message) => setStatus(message)}
              />
            );
          })}
        </div>
      )}

      {/* Study Info */}
      {study && (
        <div className="rounded-lg border bg-card p-3 text-xs">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <span className="font-semibold">Patient:</span>{' '}
              {study.patientName || 'REDACTED'}
            </div>
            <div>
              <span className="font-semibold">Study:</span> {study.studyDescription || 'N/A'}
            </div>
            <div>
              <span className="font-semibold">Date:</span> {study.studyDate || 'N/A'}
            </div>
            <div>
              <span className="font-semibold">Series:</span> {study.series.length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

