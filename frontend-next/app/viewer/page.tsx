'use client';

import { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import UploadBox from '@/components/UploadBox';
import { Toolbar, type ViewerTool } from '@/components/Toolbar';
import MetadataPanel from './metadataPanel';
import { DicomCodecTest } from './DicomCodecTest';
import {
  loadDicomFiles,
  type DicomMetadata,
} from '@/lib/dicomLoader';
import type { ViewerHandle } from './dicomViewer';

const DicomViewer = dynamic(() => import('./dicomViewer'), {
  ssr: false,
}) as typeof import('./dicomViewer').default;

export default function ViewerPage() {
  const viewerRef = useRef<ViewerHandle>(null);
  const [imageIds, setImageIds] = useState<string[]>([]);
  const [metadata, setMetadata] = useState<DicomMetadata>({});
  const [activeTool, setActiveTool] = useState<ViewerTool>('pan');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFiles = async (files: File[]) => {
    setLoading(true);
    setStatus('Analyse des fichiers DICOM…');
    try {
      const stack = await loadDicomFiles(files);
      if (!stack.imageIds.length) {
        setStatus('Aucune image DICOM exploitable détectée.');
        setImageIds([]);
        setMetadata({});
        return;
      }
      setImageIds(stack.imageIds);
      setMetadata(stack.metadata);
      setStatus(
        `${stack.imageIds.length} frame${stack.imageIds.length > 1 ? 's' : ''} chargée(s).`,
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Impossible de charger les fichiers.';
      setStatus(message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!viewerRef.current) return;
    const png = await viewerRef.current.exportPng();
    if (!png) return;
    const link = document.createElement('a');
    link.href = png;
    link.download = `dicom-frame-${Date.now()}.png`;
    link.click();
  };

  const viewerDisabled = !imageIds.length || loading;

  return (
    <div className="flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">DICOM Viewer</h1>
        <p className="text-muted-foreground">
          Téléchargez une étude DICOM, parcourez les frames, ajustez Window/Level et exportez une vue PNG.
        </p>
      </div>

      <UploadBox onFilesSelected={handleFiles} disabled={loading} />

      <Toolbar
        activeTool={activeTool}
        onSelectTool={setActiveTool}
        onInvert={() => viewerRef.current?.invert()}
        onFlipHorizontal={() => viewerRef.current?.flipHorizontal()}
        onFlipVertical={() => viewerRef.current?.flipVertical()}
        onReset={() => viewerRef.current?.resetViewport()}
        onExport={handleExport}
        disabled={viewerDisabled}
      />

      {status && (
        <div className="rounded-lg border border-dashed bg-muted/40 px-4 py-2 text-sm text-muted-foreground">
          {loading ? 'Traitement en cours… ' : null}
          {status}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[3fr_1fr]">
        <DicomViewer
          ref={viewerRef}
          imageIds={imageIds}
          activeTool={activeTool}
          onError={(message) => setStatus(message)}
        />
        <div className="flex flex-col gap-4">
          <MetadataPanel metadata={metadata} />
          <DicomCodecTest />
        </div>
      </div>
    </div>
  );
}

