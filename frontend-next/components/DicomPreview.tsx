'use client';

import { Card, CardContent } from './ui/card';
import Image from 'next/image';

interface DicomPreviewProps {
  imageUrl: string;
  metadata?: {
    modality?: string;
    study_date?: string;
    series_description?: string;
    pixel_spacing?: number[];
    slice_thickness?: number;
  };
}

export function DicomPreview({ imageUrl, metadata }: DicomPreviewProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="relative w-full aspect-square bg-muted rounded-lg overflow-hidden">
            <Image
              src={imageUrl}
              alt="DICOM Preview"
              fill
              className="object-contain"
              unoptimized
            />
          </div>
          {metadata && (
            <div className="grid grid-cols-2 gap-4 text-sm">
              {metadata.modality && (
                <div>
                  <span className="text-muted-foreground">Modality:</span>
                  <p className="font-medium">{metadata.modality}</p>
                </div>
              )}
              {metadata.study_date && (
                <div>
                  <span className="text-muted-foreground">Study Date:</span>
                  <p className="font-medium">{metadata.study_date}</p>
                </div>
              )}
              {metadata.series_description && (
                <div className="col-span-2">
                  <span className="text-muted-foreground">Description:</span>
                  <p className="font-medium">{metadata.series_description}</p>
                </div>
              )}
              {metadata.pixel_spacing && (
                <div>
                  <span className="text-muted-foreground">Pixel Spacing:</span>
                  <p className="font-medium">
                    {metadata.pixel_spacing.join(' × ')} mm
                  </p>
                </div>
              )}
              {metadata.slice_thickness && (
                <div>
                  <span className="text-muted-foreground">Slice Thickness:</span>
                  <p className="font-medium">{metadata.slice_thickness} mm</p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

