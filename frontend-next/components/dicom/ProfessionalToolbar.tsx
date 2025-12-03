'use client';

import { Button } from '@/components/ui/button';
import {
  ZoomIn,
  Move,
  SlidersHorizontal,
  ArrowUpDown,
  Ruler,
  Triangle,
  Square,
  Circle,
  Pipette,
  FlipHorizontal,
  FlipVertical,
  RotateCw,
  RefreshCw,
  Download,
  ImageIcon,
  Layers,
} from 'lucide-react';
import type { ViewerTool } from '@/lib/dicom/types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { WindowLevelPreset } from '@/lib/dicom/presets';

type ProfessionalToolbarProps = {
  activeTool: ViewerTool;
  onSelectTool: (tool: ViewerTool) => void;
  onInvert: () => void;
  onFlipHorizontal: () => void;
  onFlipVertical: () => void;
  onRotate: () => void;
  onReset: () => void;
  onFit: () => void;
  onExport: () => void;
  onPresetSelect?: (preset: WindowLevelPreset) => void;
  windowLevelPresets?: WindowLevelPreset[];
  disabled?: boolean;
  showOverlay?: boolean;
  onToggleOverlay?: () => void;
};

export function ProfessionalToolbar({
  activeTool,
  onSelectTool,
  onInvert,
  onFlipHorizontal,
  onFlipVertical,
  onRotate,
  onReset,
  onFit,
  onExport,
  onPresetSelect,
  windowLevelPresets = [],
  disabled = false,
  showOverlay = true,
  onToggleOverlay,
}: ProfessionalToolbarProps) {
  const navigationTools: Array<{ tool: ViewerTool; icon: any; label: string; shortcut: string }> = [
    { tool: 'zoom', icon: ZoomIn, label: 'Zoom', shortcut: 'Z' },
    { tool: 'pan', icon: Move, label: 'Pan', shortcut: 'P' },
    { tool: 'wl', icon: SlidersHorizontal, label: 'Window/Level', shortcut: 'W' },
    { tool: 'scroll', icon: ArrowUpDown, label: 'Scroll', shortcut: 'S' },
  ];

  const measurementTools: Array<{ tool: ViewerTool; icon: any; label: string; shortcut: string }> = [
    { tool: 'length', icon: Ruler, label: 'Length', shortcut: 'L' },
    { tool: 'angle', icon: Triangle, label: 'Angle', shortcut: 'A' },
    { tool: 'rectangleROI', icon: Square, label: 'Rectangle ROI', shortcut: 'R' },
    { tool: 'ellipticalROI', icon: Circle, label: 'Ellipse ROI', shortcut: 'E' },
    { tool: 'probe', icon: Pipette, label: 'Probe', shortcut: 'B' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-card p-2 shadow-sm">
      {/* Navigation Tools */}
      <div className="flex items-center gap-1 border-r pr-2">
        {navigationTools.map(({ tool, icon: Icon, label, shortcut }) => (
          <Button
            key={tool}
            variant={activeTool === tool ? 'default' : 'ghost'}
            size="sm"
            onClick={() => onSelectTool(tool)}
            disabled={disabled}
            title={`${label} (${shortcut})`}
            className="h-8 w-8 p-0"
          >
            <Icon className="h-4 w-4" />
          </Button>
        ))}
      </div>

      {/* Measurement Tools */}
      <div className="flex items-center gap-1 border-r pr-2">
        {measurementTools.map(({ tool, icon: Icon, label, shortcut }) => (
          <Button
            key={tool}
            variant={activeTool === tool ? 'default' : 'ghost'}
            size="sm"
            onClick={() => onSelectTool(tool)}
            disabled={disabled}
            title={`${label} (${shortcut})`}
            className="h-8 w-8 p-0"
          >
            <Icon className="h-4 w-4" />
          </Button>
        ))}
      </div>

      {/* Transform Tools */}
      <div className="flex items-center gap-1 border-r pr-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onInvert}
          disabled={disabled}
          title="Invert (I)"
          className="h-8 w-8 p-0"
        >
          <ImageIcon className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onFlipHorizontal}
          disabled={disabled}
          title="Flip Horizontal (H)"
          className="h-8 w-8 p-0"
        >
          <FlipHorizontal className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onFlipVertical}
          disabled={disabled}
          title="Flip Vertical (V)"
          className="h-8 w-8 p-0"
        >
          <FlipVertical className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onRotate}
          disabled={disabled}
          title="Rotate 90° (Ctrl+R)"
          className="h-8 w-8 p-0"
        >
          <RotateCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Window/Level Presets */}
      {windowLevelPresets.length > 0 && onPresetSelect && (
        <div className="flex items-center gap-1 border-r pr-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                disabled={disabled}
                className="h-8 text-xs"
              >
                <SlidersHorizontal className="mr-1 h-3 w-3" />
                Presets
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Window/Level Presets</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {windowLevelPresets.map((preset, index) => (
                <DropdownMenuItem
                  key={index}
                  onClick={() => onPresetSelect(preset)}
                >
                  <span className="font-medium">{preset.name}</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {preset.windowWidth}/{preset.windowCenter}
                  </span>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}

      {/* Utility Tools */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          onClick={onFit}
          disabled={disabled}
          title="Fit to Window (F)"
          className="h-8 w-8 p-0"
        >
          <Layers className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onReset}
          disabled={disabled}
          title="Reset (Esc)"
          className="h-8 w-8 p-0"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
        {onToggleOverlay && (
          <Button
            variant={showOverlay ? 'default' : 'ghost'}
            size="sm"
            onClick={onToggleOverlay}
            disabled={disabled}
            title="Toggle Overlay (O)"
            className="h-8 text-xs"
          >
            Overlay
          </Button>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={onExport}
          disabled={disabled}
          title="Export PNG (Ctrl+S)"
          className="h-8 text-xs"
        >
          <Download className="mr-1 h-3 w-3" />
          Export
        </Button>
      </div>
    </div>
  );
}

