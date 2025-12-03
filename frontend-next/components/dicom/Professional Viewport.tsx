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
import { DicomOverlay } from './DicomOverlay';
import type { ViewerTool, DicomMetadata, WindowLevelPreset } from '@/lib/dicom/types';

type ProfessionalViewportProps = {
  imageIds: string[];
  currentIndex?: number;
  metadata: DicomMetadata;
  activeTool?: ViewerTool;
  showOverlay?: boolean;
  onIndexChange?: (index: number) => void;
  onError?: (message: string) => void;
};

export type ViewportHandle = {
  nextImage: () => void;
  previousImage: () => void;
  setImageIndex: (index: number) => void;
  applyPreset: (preset: WindowLevelPreset) => void;
  invert: () => void;
  flipHorizontal: () => void;
  flipVertical: () => void;
  rotate: (degrees: number) => void;
  reset: () => void;
  fitToWindow: () => void;
  exportPng: () => Promise<string | null>;
  getViewportStats: () => any;
};

let toolsRegistered = false;

const registerTools = () => {
  const { cornerstoneTools } = getCornerstoneBundle();
  if (toolsRegistered) return;

  // Navigation tools
  cornerstoneTools.addTool(cornerstoneTools.ZoomTool);
  cornerstoneTools.addTool(cornerstoneTools.PanTool);
  cornerstoneTools.addTool(cornerstoneTools.WwwcTool);
  cornerstoneTools.addTool(cornerstoneTools.StackScrollMouseWheelTool);

  // Measurement tools
  cornerstoneTools.addTool(cornerstoneTools.LengthTool);
  cornerstoneTools.addTool(cornerstoneTools.AngleTool);
  cornerstoneTools.addTool(cornerstoneTools.RectangleRoiTool);
  cornerstoneTools.addTool(cornerstoneTools.EllipticalRoiTool);
  cornerstoneTools.addTool(cornerstoneTools.ProbeTool);

  toolsRegistered = true;
};

export const ProfessionalViewport = forwardRef<ViewportHandle, ProfessionalViewportProps>(
  (
    {
      imageIds,
      currentIndex = 0,
      metadata,
      activeTool = 'pan',
      showOverlay = true,
      onIndexChange,
      onError,
    },
    ref,
  ) => {
    const elementRef = useRef<HTMLDivElement>(null);
    const [isReady, setIsReady] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(currentIndex);
    const [viewportState, setViewportState] = useState<any>(null);

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
        isEnabled = true;
      }

      const stack = {
        imageIds,
        currentImageIdIndex: currentImageIndex,
      };

      cornerstoneTools.clearToolState(element, 'stack');
      cornerstoneTools.addStackStateManager(element, ['stack']);
      cornerstoneTools.addToolState(element, 'stack', stack);

      const load = async () => {
        try {
          console.log('[Professional Viewport] Loading image:', imageIds[currentImageIndex]);

          const image = await cornerstone.loadAndCacheImage(imageIds[currentImageIndex]);

          if (!mounted) return;

          cornerstone.displayImage(element, image);

          // Set viewport
          const viewport = cornerstone.getViewport(element);
          const photometric = (image as any).photometricInterpretation;
          const needsInvert = photometric === 'MONOCHROME1';

          const newViewport = {
            ...viewport,
            voi: {
              windowWidth:
                viewport.voi?.windowWidth ||
                image.windowWidth ||
                metadata.windowWidth ||
                256,
              windowCenter:
                viewport.voi?.windowCenter ||
                image.windowCenter ||
                metadata.windowCenter ||
                128,
            },
            invert: needsInvert,
          };

          cornerstone.setViewport(element, newViewport);
          setViewportState(newViewport);

          // Activate default tools
          cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
          cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
          cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 2 });

          console.log('[Professional Viewport] ✅ Ready!');
          setIsReady(true);
        } catch (error) {
          if (!mounted) return;
          const message =
            error instanceof Error ? error.message : 'Unable to load DICOM image';
          onError?.(message);
          console.error('[Professional Viewport] Load error:', error);
        }
      };

      load();

      // Stack scroll event listener
      const handleNewImage = (event: any) => {
        const newIndex = event.detail.newImageIdIndex;
        setCurrentImageIndex(newIndex);
        onIndexChange?.(newIndex);

        // Update viewport state
        try {
          const viewport = cornerstone.getViewport(element);
          setViewportState(viewport);
        } catch {
          // Ignore
        }
      };

      element.addEventListener('cornerstonenewimage', handleNewImage);

      // Viewport updated listener
      const handleViewportUpdated = () => {
        try {
          const viewport = cornerstone.getViewport(element);
          setViewportState(viewport);
        } catch {
          // Ignore
        }
      };

      element.addEventListener('cornerstoneimagerendered', handleViewportUpdated);

      return () => {
        mounted = false;
        setIsReady(false);

        element.removeEventListener('cornerstonenewimage', handleNewImage);
        element.removeEventListener('cornerstoneimagerendered', handleViewportUpdated);

        if (isEnabled && element) {
          try {
            cornerstoneTools.clearToolState(element, 'stack');
            const enabledElement = cornerstone.getEnabledElement(element);
            const canvas = enabledElement?.canvas;
            cornerstone.disable(element);
            if (canvas && canvas.parentNode === element) {
              element.removeChild(canvas);
            }
          } catch (error) {
            console.warn('[Professional Viewport] Cleanup warning:', error);
          }
        }
      };
    }, [imageIds, currentImageIndex, metadata, onError, onIndexChange]);

    // Handle tool changes
    useEffect(() => {
      if (!elementRef.current || !isReady) return;

      const { cornerstoneTools } = getCornerstoneBundle();

      // Deactivate all tools first
      cornerstoneTools.setToolPassive('Zoom');
      cornerstoneTools.setToolPassive('Pan');
      cornerstoneTools.setToolPassive('Wwwc');
      cornerstoneTools.setToolPassive('Length');
      cornerstoneTools.setToolPassive('Angle');
      cornerstoneTools.setToolPassive('RectangleRoi');
      cornerstoneTools.setToolPassive('EllipticalRoi');
      cornerstoneTools.setToolPassive('Probe');

      // Always keep stack scroll active
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {});

      // Activate selected tool
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
        case 'length':
          cornerstoneTools.setToolActive('Length', { mouseButtonMask: 1 });
          break;
        case 'angle':
          cornerstoneTools.setToolActive('Angle', { mouseButtonMask: 1 });
          break;
        case 'rectangleROI':
          cornerstoneTools.setToolActive('RectangleRoi', { mouseButtonMask: 1 });
          break;
        case 'ellipticalROI':
          cornerstoneTools.setToolActive('EllipticalRoi', { mouseButtonMask: 1 });
          break;
        case 'probe':
          cornerstoneTools.setToolActive('Probe', { mouseButtonMask: 1 });
          break;
        default:
          break;
      }
    }, [activeTool, isReady]);

    useImperativeHandle(
      ref,
      () => ({
        nextImage: () => {
          if (currentImageIndex < imageIds.length - 1) {
            setCurrentImageIndex(currentImageIndex + 1);
          }
        },
        previousImage: () => {
          if (currentImageIndex > 0) {
            setCurrentImageIndex(currentImageIndex - 1);
          }
        },
        setImageIndex: (index: number) => {
          if (index >= 0 && index < imageIds.length) {
            setCurrentImageIndex(index);
          }
        },
        applyPreset: (preset: WindowLevelPreset) => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              voi: {
                windowWidth: preset.windowWidth,
                windowCenter: preset.windowCenter,
              },
            });
          } catch (error) {
            console.warn('[Professional Viewport] Apply preset failed:', error);
          }
        },
        invert: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              invert: !viewport.invert,
            });
          } catch (error) {
            console.warn('[Professional Viewport] Invert failed:', error);
          }
        },
        flipHorizontal: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              hflip: !viewport.hflip,
            });
          } catch (error) {
            console.warn('[Professional Viewport] Flip H failed:', error);
          }
        },
        flipVertical: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              vflip: !viewport.vflip,
            });
          } catch (error) {
            console.warn('[Professional Viewport] Flip V failed:', error);
          }
        },
        rotate: (degrees: number) => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(elementRef.current);
            const currentRotation = viewport.rotation || 0;
            cornerstone.setViewport(elementRef.current, {
              ...viewport,
              rotation: (currentRotation + degrees) % 360,
            });
          } catch (error) {
            console.warn('[Professional Viewport] Rotate failed:', error);
          }
        },
        reset: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            cornerstone.reset(elementRef.current);
          } catch (error) {
            console.warn('[Professional Viewport] Reset failed:', error);
          }
        },
        fitToWindow: () => {
          if (!elementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            cornerstone.fitToWindow(elementRef.current);
          } catch (error) {
            console.warn('[Professional Viewport] Fit failed:', error);
          }
        },
        exportPng: async () => {
          if (!elementRef.current || !isReady) return null;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const enabledElement = cornerstone.getEnabledElement(elementRef.current);
            const canvas = enabledElement?.canvas as HTMLCanvasElement | undefined;
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
          } catch (error) {
            console.error('[Professional Viewport] Export failed:', error);
            return null;
          }
        },
        getViewportStats: () => {
          if (!elementRef.current || !isReady) return null;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const enabledElement = cornerstone.getEnabledElement(elementRef.current);
            return {
              viewport: enabledElement.viewport,
              image: {
                width: enabledElement.image.width,
                height: enabledElement.image.height,
              },
            };
          } catch (error) {
            return null;
          }
        },
      }),
      [isReady, imageIds.length, currentImageIndex],
    );

    return (
      <div className="relative h-full w-full overflow-hidden rounded-lg border bg-black">
        <div ref={elementRef} className="h-full w-full" />
        {showOverlay && isReady && (
          <DicomOverlay
            metadata={metadata}
            currentIndex={currentImageIndex}
            totalImages={imageIds.length}
            windowWidth={viewportState?.voi?.windowWidth}
            windowCenter={viewportState?.voi?.windowCenter}
            zoom={viewportState?.scale}
          />
        )}
        {!imageIds.length && (
          <div className="flex h-full w-full items-center justify-center text-sm text-muted-foreground">
            No DICOM image loaded
          </div>
        )}
      </div>
    );
  },
);

ProfessionalViewport.displayName = 'ProfessionalViewport';

export default ProfessionalViewport;

