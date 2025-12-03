'use client';

import type { DicomMetadata } from '@/lib/dicom/types';

type DicomOverlayProps = {
  metadata: DicomMetadata;
  currentIndex: number;
  totalImages: number;
  windowWidth?: number;
  windowCenter?: number;
  zoom?: number;
};

export function DicomOverlay({
  metadata,
  currentIndex,
  totalImages,
  windowWidth,
  windowCenter,
  zoom,
}: DicomOverlayProps) {
  const formatPatientInfo = (name?: string, id?: string) => {
    if (!name && !id) return 'N/A';
    const safeName = name?.replace(/\^/g, ' ') || 'REDACTED';
    const safeID = id || 'REDACTED';
    return `${safeName} [${safeID}]`;
  };

  return (
    <div className="pointer-events-none absolute inset-0 text-xs text-white">
      {/* Top Left */}
      <div className="absolute left-2 top-2 space-y-0.5 text-shadow">
        <div className="font-semibold">
          {formatPatientInfo(metadata.patientName, metadata.patientID)}
        </div>
        <div>{metadata.studyDescription || 'No Study Description'}</div>
        <div>{metadata.studyDate || 'Unknown Date'}</div>
        <div className="text-cyan-300">
          {metadata.modality || 'OT'}
        </div>
      </div>

      {/* Top Right */}
      <div className="absolute right-2 top-2 space-y-0.5 text-right text-shadow">
        <div>Series: {metadata.seriesNumber || 'N/A'}</div>
        <div>{metadata.seriesDescription || 'No Series Description'}</div>
        <div>
          Image: {currentIndex + 1}/{totalImages}
        </div>
      </div>

      {/* Bottom Left */}
      <div className="absolute bottom-2 left-2 space-y-0.5 text-shadow">
        {metadata.pixelSpacing && (
          <div>Spacing: {metadata.pixelSpacing}</div>
        )}
        {metadata.sliceThickness && (
          <div>Thickness: {metadata.sliceThickness}</div>
        )}
        {metadata.sliceLocation && (
          <div>Location: {metadata.sliceLocation}</div>
        )}
        {metadata.imagePositionPatient && (
          <div className="text-xs text-gray-400">
            Pos: {metadata.imagePositionPatient}
          </div>
        )}
      </div>

      {/* Bottom Right */}
      <div className="absolute bottom-2 right-2 space-y-0.5 text-right text-shadow">
        {windowWidth !== undefined && windowCenter !== undefined && (
          <div>
            W/L: {Math.round(windowWidth)} / {Math.round(windowCenter)}
          </div>
        )}
        {zoom !== undefined && (
          <div>Zoom: {(zoom * 100).toFixed(0)}%</div>
        )}
        {metadata.rows && metadata.columns && (
          <div>
            {metadata.rows} × {metadata.columns}
          </div>
        )}
      </div>
    </div>
  );
}

