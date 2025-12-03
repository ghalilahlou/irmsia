'use client';

import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import { getCornerstoneBundle, initCornerstone } from '@/lib/cornerstone';
import type { ViewerTool } from '@/components/Toolbar';

type DicomViewerProps = {
  imageIds: string[];
  activeTool: ViewerTool;
  onError?: (message: string) => void;
};

export type ViewerHandle = {
  invert: () => void;
  flipHorizontal: () => void;
  flipVertical: () => void;
  resetViewport: () => void;
  exportPng: () => Promise<string | null>;
};

let toolsRegistered = false;

const registerTools = () => {
  const { cornerstoneTools } = getCornerstoneBundle();
  if (toolsRegistered) return;

  cornerstoneTools.addTool(cornerstoneTools.ZoomTool);
  cornerstoneTools.addTool(cornerstoneTools.PanTool);
  cornerstoneTools.addTool(cornerstoneTools.WwwcTool);
  cornerstoneTools.addTool(cornerstoneTools.StackScrollMouseWheelTool);

  toolsRegistered = true;
};

export const DicomViewer = forwardRef<ViewerHandle, DicomViewerProps>(
  ({ imageIds, activeTool, onError }, ref) => {
    const elementRef = useRef<HTMLDivElement>(null);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
      initCornerstone();
      registerTools();
    }, []);

    useLayoutEffect(() => {
      if (!imageIds.length || !elementRef.current) return undefined;

      const { cornerstone, cornerstoneTools } = getCornerstoneBundle();
      const element = elementRef.current;
      let mounted = true;
      let isEnabled = false;

      try {
        cornerstone.enable(element);
        isEnabled = true;
      } catch {
        // already enabled
        isEnabled = true;
      }

      const stack = {
        imageIds,
        currentImageIdIndex: 0,
      };

      cornerstoneTools.clearToolState(element, 'stack');
      cornerstoneTools.addStackStateManager(element, ['stack']);
      cornerstoneTools.addToolState(element, 'stack', stack);

      const load = async () => {
        try {
          console.log('[DICOM Viewer] Starting load for imageId:', imageIds[0]);
          
          const image = await cornerstone.loadAndCacheImage(imageIds[0]);
          console.log('[DICOM Viewer] Image loaded successfully:', {
            width: image.width,
            height: image.height,
            color: image.color,
            windowWidth: image.windowWidth,
            windowCenter: image.windowCenter,
            minPixelValue: image.minPixelValue,
            maxPixelValue: image.maxPixelValue,
            slope: image.slope,
            intercept: image.intercept,
            photometricInterpretation: (image as any).photometricInterpretation,
            pixelDataLength: (image as any).data?.length || 'unknown',
          });
          
          if (!mounted) return;
          
          // Check if we have valid pixel data
          const pixelData = image.getPixelData();
          console.log('[DICOM Viewer] Pixel data check:', {
            hasPixelData: !!pixelData,
            pixelDataLength: pixelData?.length,
            firstPixels: pixelData ? Array.from(pixelData.slice(0, 10)) : [],
          });
          
          cornerstone.displayImage(element, image);
          console.log('[DICOM Viewer] Image displayed on canvas');
          
          // Force initial viewport - handle MONOCHROME1 (inverted)
          const viewport = cornerstone.getViewport(element);
          console.log('[DICOM Viewer] Initial viewport:', viewport);
          
          const photometric = (image as any).photometricInterpretation;
          const needsInvert = photometric === 'MONOCHROME1';
          
          const newViewport = {
            ...viewport,
            voi: {
              windowWidth: viewport.voi?.windowWidth || image.windowWidth || 256,
              windowCenter: viewport.voi?.windowCenter || image.windowCenter || 128,
            },
            invert: needsInvert,
          };
          console.log('[DICOM Viewer] Setting viewport:', newViewport, needsInvert ? '(inverted for MONOCHROME1)' : '');
          cornerstone.setViewport(element, newViewport);
          
          cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
          cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
          cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 2 });
          console.log('[DICOM Viewer] ✅ Ready! Tools activated');
          setIsReady(true);
        } catch (error) {
          if (!mounted) return;
          const message =
            error instanceof Error ? error.message : 'Unable to load DICOM image';
          onError?.(message);
          console.error('[DICOM Viewer] ❌ Load error:', error);
          console.error('[DICOM Viewer] Error stack:', error instanceof Error ? error.stack : 'no stack');
        }
      };

      load();

      return () => {
        mounted = false;
        setIsReady(false);
        
        // Minimal cleanup: just clear tool state
        // Don't call cornerstone.disable() to avoid React DOM conflicts
        if (isEnabled && element) {
          try {
            cornerstoneTools.clearToolState(element, 'stack');
            console.log('[DICOM Viewer] Cleanup completed');
          } catch (error) {
            // Silently ignore cleanup errors
            console.warn('[DICOM Viewer] Cleanup warning (safe to ignore):', error);
          }
        }
      };
    }, [imageIds, onError]);

    useEffect(() => {
      if (!elementRef.current || !isReady) return;

      const { cornerstoneTools } = getCornerstoneBundle();

      switch (activeTool) {
        case 'zoom':
          cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 1 });
          break;
        case 'pan':
          cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
          break;
        case 'wl':
          cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 });
          break;
        case 'scroll':
          cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
          break;
        default:
          break;
      }
    }, [activeTool, isReady]);

    useImperativeHandle(
      ref,
      () => ({
        invert: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            if (!viewport) return;
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              invert: !viewport.invert,
            });
          } catch (error) {
            console.warn('[DICOM Viewer] Invert failed:', error);
          }
        },
        flipHorizontal: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            if (!viewport) return;
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              hflip: !viewport.hflip,
            });
          } catch (error) {
            console.warn('[DICOM Viewer] Flip H failed:', error);
          }
        },
        flipVertical: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            if (!viewport) return;
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              vflip: !viewport.vflip,
            });
          } catch (error) {
            console.warn('[DICOM Viewer] Flip V failed:', error);
          }
        },
        resetViewport: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            cornerstone.reset(elementRef.current);
          } catch (error) {
            console.warn('[DICOM Viewer] Reset failed:', error);
          }
        },
        exportPng: async () => {
          if (!elementRef.current || !isReady) return null;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const enabledElement = cornerstone.getEnabledElement(elementRef.current);
            const canvas = enabledElement?.canvas as HTMLCanvasElement | undefined;
            if (!canvas) return null;
            const base64 = canvas.toDataURL('image/png');
            const response = await fetch('/api/convert', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ dataUrl: base64 }),
            });
            if (!response.ok) {
              onError?.('PNG export failed');
              return null;
            }
            const data = await response.json();
            return (data?.dataUrl as string) ?? base64;
          } catch (error) {
            console.error('[DICOM Viewer] Export failed:', error);
            onError?.('Export PNG failed');
            return null;
          }
        },
      }),
      [isReady, onError],
    );

    return (
      <div className="flex h-[520px] w-full flex-col overflow-hidden rounded-2xl border bg-black shadow-inner">
        <div ref={elementRef} className="relative flex-1">
          {!imageIds.length && (
            <div className="flex h-full w-full items-center justify-center text-sm text-muted-foreground">
              Importez des fichiers DICOM pour commencer la visualisation.
            </div>
          )}
        </div>
        <div className="border-t bg-zinc-900 px-4 py-2 text-xs text-zinc-200">
          {imageIds.length
            ? `${imageIds.length} frame${imageIds.length > 1 ? 's' : ''} chargée(s)`
            : 'Aucune étude chargée'}
        </div>
      </div>
    );
  },
);

DicomViewer.displayName = 'DicomViewer';

export default DicomViewer;

