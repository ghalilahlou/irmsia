'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import UploadBox from '@/components/UploadBox';
import { ProfessionalToolbar } from '@/components/dicom/ProfessionalToolbar';
import { LayoutSelector } from '@/components/dicom/LayoutSelector';
import { loadDicomStudy } from '@/lib/dicom/studyLoader';
import { getPresetsForModality } from '@/lib/dicom/presets';
import type {
  DicomStudy,
  ViewerTool,
  ViewportLayout,
  DicomMetadata,
  WindowLevelPreset,
} from '@/lib/dicom/types';
import type { ViewportHandle } from '@/components/dicom/ProfessionalViewport';

const ProfessionalViewport = dynamic(
  () => import('@/components/dicom/ProfessionalViewport'),
  { ssr: false },
);

export default function ProfessionalViewerPage() {
  const viewportRefs = useRef<Array<ViewportHandle | null>>([null, null, null, null]);
  
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
    setStatus('Parsing DICOM files…');
    try {
      const loadedStudy = await loadDicomStudy(files);
      if (!loadedStudy || loadedStudy.series.length === 0) {
        setStatus('No DICOM series found');
        return;
      }
      setStudy(loadedStudy);
      setStatus(
        `Loaded: ${loadedStudy.series.length} series, ${loadedStudy.series.reduce((sum, s) => sum + s.instances.length, 0)} images`,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load DICOM';
      setStatus(message);
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
      if (ref) ref.applyPreset(preset);
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
            viewportRefs.current[0]?.fitToWindow();
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
            viewportRefs.current[0]?.rotate(90);
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
          <ProfessionalToolbar
            activeTool={activeTool}
            onSelectTool={setActiveTool}
            onInvert={() => viewportRefs.current[0]?.invert()}
            onFlipHorizontal={() => viewportRefs.current[0]?.flipHorizontal()}
            onFlipVertical={() => viewportRefs.current[0]?.flipVertical()}
            onRotate={() => viewportRefs.current[0]?.rotate(90)}
            onReset={() => viewportRefs.current[0]?.reset()}
            onFit={() => viewportRefs.current[0]?.fitToWindow()}
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
            const imageIds = series.instances.map((inst) => inst.imageId);
            
            const metadata: DicomMetadata = {
              studyDescription: study.studyDescription,
              seriesDescription: series.seriesDescription,
              seriesNumber: series.seriesNumber.toString(),
              instanceNumber: series.instances[0]?.instanceNumber.toString(),
              modality: series.modality,
              patientName: study.patientName,
              patientID: study.patientID,
              studyDate: study.studyDate,
            };

            return (
              <ProfessionalViewport
                key={index}
                ref={(el) => {
                  viewportRefs.current[index] = el;
                }}
                imageIds={imageIds}
                currentIndex={viewportStates[index].imageIndex}
                metadata={metadata}
                activeTool={activeTool}
                showOverlay={showOverlay}
                onIndexChange={(newIndex) => {
                  setViewportStates((prev) => {
                    const newStates = [...prev];
                    newStates[index] = { ...newStates[index], imageIndex: newIndex };
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

