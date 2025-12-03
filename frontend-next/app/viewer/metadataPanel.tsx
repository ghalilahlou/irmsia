'use client';

import type { DicomMetadata } from '@/lib/dicomLoader';

type MetadataPanelProps = {
  metadata: DicomMetadata;
};

const fields: { label: string; key: keyof DicomMetadata }[] = [
  { label: 'Study Description', key: 'studyDescription' },
  { label: 'Series Description', key: 'seriesDescription' },
  { label: 'Series Number', key: 'seriesNumber' },
  { label: 'Instance Number', key: 'instanceNumber' },
  { label: 'Modality', key: 'modality' },
  { label: 'Pixel Spacing', key: 'pixelSpacing' },
  { label: 'Slice Thickness', key: 'sliceThickness' },
];

const maskedPhi = [
  { label: 'Patient Name', value: 'REDACTED' },
  { label: 'Patient ID', value: 'REDACTED' },
  { label: 'Birth Date', value: 'REDACTED' },
];

export const MetadataPanel = ({ metadata }: MetadataPanelProps) => (
  <aside className="flex h-full flex-col gap-4 rounded-2xl border bg-card/80 p-4 shadow">
    <div>
      <h3 className="text-lg font-semibold">Series Metadata</h3>
      <p className="text-sm text-muted-foreground">
        Résumé minimal de l&apos;étude en respectant la confidentialité.
      </p>
    </div>
    <dl className="space-y-3 text-sm">
      {fields.map(({ label, key }) => (
        <div key={key} className="rounded-lg bg-muted/60 px-3 py-2">
          <dt className="text-xs uppercase tracking-wide text-muted-foreground">
            {label}
          </dt>
          <dd className="font-medium text-foreground">
            {metadata[key] ?? 'Non disponible'}
          </dd>
        </div>
      ))}
    </dl>
    <div className="pt-2">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        PHI Masked
      </h4>
      <dl className="mt-3 space-y-2 text-sm">
        {maskedPhi.map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between">
            <dt className="text-muted-foreground">{label}</dt>
            <dd className="font-semibold text-orange-600">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  </aside>
);

export default MetadataPanel;

