'use client';

import { Button } from '@/components/ui/button';
import { Square, Columns, Grid2X2 } from 'lucide-react';
import type { ViewportLayout } from '@/lib/dicom/types';

type LayoutSelectorProps = {
  currentLayout: ViewportLayout;
  onLayoutChange: (layout: ViewportLayout) => void;
  disabled?: boolean;
};

const layouts: Array<{ layout: ViewportLayout; icon: any; label: string }> = [
  { layout: '1x1', icon: Square, label: '1×1' },
  { layout: '1x2', icon: Columns, label: '1×2' },
  { layout: '2x2', icon: Grid2X2, label: '2×2' },
];

export function LayoutSelector({
  currentLayout,
  onLayoutChange,
  disabled = false,
}: LayoutSelectorProps) {
  return (
    <div className="flex items-center gap-1 rounded-lg border bg-card p-1 shadow-sm">
      <span className="px-2 text-xs font-medium text-muted-foreground">Layout:</span>
      {layouts.map(({ layout, icon: Icon, label }) => (
        <Button
          key={layout}
          variant={currentLayout === layout ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onLayoutChange(layout)}
          disabled={disabled}
          title={`${label} Layout`}
          className="h-7 w-12 p-0 text-xs"
        >
          <Icon className="mr-1 h-3 w-3" />
          {label}
        </Button>
      ))}
    </div>
  );
}

