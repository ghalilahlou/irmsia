'use client';

import clsx from 'clsx';
import {
  Crosshair,
  FlipHorizontal,
  FlipVertical,
  ImageIcon,
  MousePointer,
  RefreshCcw,
  ScrollText,
  ZoomIn,
} from 'lucide-react';

export type ViewerTool = 'zoom' | 'pan' | 'wl' | 'scroll';

type ToolbarProps = {
  activeTool: ViewerTool;
  onSelectTool: (tool: ViewerTool) => void;
  onInvert: () => void;
  onFlipHorizontal: () => void;
  onFlipVertical: () => void;
  onReset: () => void;
  onExport: () => void;
  disabled?: boolean;
};

const toolButtons: {
  key: ViewerTool;
  label: string;
  Icon: typeof ZoomIn;
}[] = [
  { key: 'zoom', label: 'Zoom', Icon: ZoomIn },
  { key: 'pan', label: 'Pan', Icon: MousePointer },
  { key: 'wl', label: 'Window/Level', Icon: Crosshair },
  { key: 'scroll', label: 'Scroll', Icon: ScrollText },
];

const actionButtons = [
  { key: 'invert', label: 'Invert', Icon: ImageIcon },
  { key: 'flipH', label: 'Flip H', Icon: FlipHorizontal },
  { key: 'flipV', label: 'Flip V', Icon: FlipVertical },
  { key: 'reset', label: 'Reset', Icon: RefreshCcw },
] as const;

export const Toolbar = ({
  activeTool,
  onSelectTool,
  onInvert,
  onFlipHorizontal,
  onFlipVertical,
  onReset,
  onExport,
  disabled,
}: ToolbarProps) => (
  <div className="flex w-full flex-wrap gap-3 rounded-2xl border bg-card/80 p-4 shadow">
    <div className="flex flex-wrap gap-2">
      {toolButtons.map(({ key, label, Icon }) => (
        <button
          key={key}
          type="button"
          disabled={disabled}
          onClick={() => onSelectTool(key)}
          className={clsx(
            'flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition',
            activeTool === key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-border bg-muted text-foreground hover:bg-muted/70',
            disabled && 'cursor-not-allowed opacity-50',
          )}
        >
          <Icon className="h-4 w-4" />
          {label}
        </button>
      ))}
    </div>
    <div className="ml-auto flex flex-wrap gap-2">
      {actionButtons.map(({ key, label, Icon }) => {
        const handlerMap: Record<string, () => void> = {
          invert: onInvert,
          flipH: onFlipHorizontal,
          flipV: onFlipVertical,
          reset: onReset,
        };
        return (
          <button
            key={key}
            type="button"
            disabled={disabled && key !== 'reset'}
            onClick={() => handlerMap[key]?.()}
            className={clsx(
              'flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition',
              'border-border bg-muted text-foreground hover:bg-muted/70',
              disabled && key !== 'reset' && 'cursor-not-allowed opacity-50',
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        );
      })}
      <button
        type="button"
        disabled={disabled}
        onClick={onExport}
        className="flex items-center gap-2 rounded-lg border border-emerald-500 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-600 hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <ImageIcon className="h-4 w-4" />
        Export PNG
      </button>
    </div>
  </div>
);

export default Toolbar;

