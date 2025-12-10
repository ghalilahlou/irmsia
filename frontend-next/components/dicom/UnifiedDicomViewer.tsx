/**
 * Composant Viewer DICOM unifie
 * Compatible avec cornerstone-tools v4
 * Utilise un wrapper DOM isole pour eviter les conflits React/Cornerstone
 */

'use client';

import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  memo,
  useLayoutEffect,
} from 'react';
import {
  getCornerstoneBundle,
  initCornerstone,
  setupElementTools,
  setToolActive,
  setToolPassive,
} from '@/lib/cornerstone';
import { DicomOverlay } from './DicomOverlay';
import { AnomalyOverlay } from './AnomalyOverlay';
import type { ViewerTool, DicomMetadata, WindowLevelPreset } from '@/lib/dicom/types';

export type UnifiedViewerMode = 'simple' | 'professional';

export interface AnomalyResult {
  has_anomaly: boolean;
  anomaly_class?: string;
  confidence?: number;
  bounding_boxes?: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    confidence?: number;
    label?: string;
  }>;
  segmentation_mask?: number[][];
  visualization?: string;
  measurements?: Record<string, number>;
}

type UnifiedDicomViewerProps = {
  imageIds: string[];
  currentIndex?: number;
  metadata?: DicomMetadata;
  activeTool?: ViewerTool;
  mode?: UnifiedViewerMode;
  showOverlay?: boolean;
  showAnomalyOverlay?: boolean;
  anomalyResult?: AnomalyResult | null;
  onIndexChange?: (index: number) => void;
  onError?: (message: string) => void;
  onReady?: () => void;
};

export type UnifiedViewerHandle = {
  nextImage: () => void;
  previousImage: () => void;
  setImageIndex: (index: number) => void;
  applyPreset?: (preset: WindowLevelPreset) => void;
  invert: () => void;
  flipHorizontal: () => void;
  flipVertical: () => void;
  rotate?: (degrees: number) => void;
  reset: () => void;
  fitToWindow?: () => void;
  exportPng: () => Promise<string | null>;
  getViewportStats?: () => any;
};

// Generate unique ID for each viewer instance
let viewerInstanceId = 0;

const UnifiedDicomViewerInner = forwardRef<UnifiedViewerHandle, UnifiedDicomViewerProps>(
  (
    {
      imageIds,
      currentIndex = 0,
      metadata = {},
      activeTool = 'pan',
      mode = 'simple',
      showOverlay = false,
      showAnomalyOverlay = false,
      anomalyResult = null,
      onIndexChange,
      onError,
      onReady,
    },
    ref,
  ) => {
    // Use a stable ID for this viewer instance
    const instanceIdRef = useRef<number>(++viewerInstanceId);

    // Container ref - this is what React manages
    const containerRef = useRef<HTMLDivElement>(null);

    // Cornerstone element ref - this is created manually, outside React's control
    const cornerstoneElementRef = useRef<HTMLDivElement | null>(null);

    // State
    const [isReady, setIsReady] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(currentIndex);
    const [viewportState, setViewportState] = useState<any>(null);

    // Refs for tracking component state
    const isEnabledRef = useRef(false);
    const mountedRef = useRef(true);
    const initializingRef = useRef(false);
    const cleanedUpRef = useRef(false);

    // Initialize Cornerstone once on mount
    useEffect(() => {
      initCornerstone();
    }, []);

    // Sync external currentIndex prop
    useEffect(() => {
      if (currentIndex !== currentImageIndex && Number.isFinite(currentIndex)) {
        setCurrentImageIndex(currentIndex);
      }
    }, [currentIndex]);

    // Main setup/cleanup effect
    useLayoutEffect(() => {
      if (!containerRef.current) return;
      if (initializingRef.current) return;

      const container = containerRef.current;
      mountedRef.current = true;
      cleanedUpRef.current = false;
      initializingRef.current = true;

      // Create a new Cornerstone element
      const createCornerstoneElement = () => {
        // Remove any existing element first
        if (cornerstoneElementRef.current && container.contains(cornerstoneElementRef.current)) {
          try {
            container.removeChild(cornerstoneElementRef.current);
          } catch {
            // Element may already be removed
          }
        }

        const element = document.createElement('div');
        element.id = `cornerstone-viewport-${instanceIdRef.current}-${Date.now()}`;
        element.style.width = '100%';
        element.style.height = '100%';
        element.style.minHeight = '400px';
        element.style.position = 'relative';

        container.appendChild(element);
        cornerstoneElementRef.current = element;

        return element;
      };

      const element = createCornerstoneElement();

      if (!imageIds.length) {
        setIsReady(false);
        initializingRef.current = false;
        return;
      }

      const { cornerstone, cornerstoneTools } = getCornerstoneBundle();

      let validIndex = 0;
      if (Number.isFinite(currentImageIndex) && currentImageIndex >= 0) {
        validIndex = Math.min(Math.floor(currentImageIndex), imageIds.length - 1);
      }

      // Enable element for Cornerstone
      const enableElement = (): boolean => {
        if (cleanedUpRef.current) return false;

        try {
          // Check if already enabled
          try {
            cornerstone.getEnabledElement(element);
            isEnabledRef.current = true;
            return true;
          } catch {
            // Not enabled yet
          }

          cornerstone.enable(element);
          isEnabledRef.current = true;
          return true;
        } catch (error) {
          console.error('[Unified Viewer] Enable failed:', error);
          return false;
        }
      };

      if (!enableElement()) {
        initializingRef.current = false;
        return;
      }

      // Setup tools for this element AFTER enabling
      try {
        setupElementTools(element);
      } catch (e) {
        console.warn('[Unified Viewer] Tool setup warning:', e);
      }

      // Setup stack for cornerstoneTools
      try {
        const stack = {
          imageIds,
          currentImageIdIndex: validIndex,
        };

        cornerstoneTools.clearToolState(element, 'stack');
        cornerstoneTools.addStackStateManager(element, ['stack']);
        cornerstoneTools.addToolState(element, 'stack', stack);
      } catch (error) {
        console.warn('[Unified Viewer] Stack setup error:', error);
      }

      // Load and display image with retry logic
      const loadImage = async (retryCount = 0) => {
        const MAX_RETRIES = 2;
        const RETRY_DELAY = 500; // ms

        if (cleanedUpRef.current || !mountedRef.current) return;

        try {
          const imageId = imageIds[validIndex];
          if (!imageId) {
            onError?.('No image ID');
            initializingRef.current = false;
            return;
          }

          console.log('[Unified Viewer] Loading image:', imageId.slice(0, 50) + '...', retryCount > 0 ? `(retry ${retryCount})` : '');

          // Double-check element is still enabled
          if (!isEnabledRef.current) {
            console.warn('[Unified Viewer] Element not enabled, skipping load');
            initializingRef.current = false;
            return;
          }

          let image;
          try {
            image = await cornerstone.loadAndCacheImage(imageId);
          } catch (loadError: unknown) {
            // Check if this is an empty error (web worker issue)
            const isEmptyError = !loadError || 
              (typeof loadError === 'object' && Object.keys(loadError as object).length === 0);
            
            // Retry for empty errors or web worker issues
            if (retryCount < MAX_RETRIES && (isEmptyError || String(loadError).includes('worker'))) {
              console.warn(`[Unified Viewer] Image load failed with empty/worker error, retrying in ${RETRY_DELAY}ms...`);
              await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
              if (!mountedRef.current || cleanedUpRef.current) return;
              return loadImage(retryCount + 1);
            }

            // Log detailed error info
            console.error('[Unified Viewer] Image load failed:', {
              error: loadError,
              errorType: typeof loadError,
              errorString: String(loadError),
              imageId: imageId.slice(0, 100),
              retries: retryCount,
            });
            
            // Extract meaningful message
            let errorMessage = 'Failed to load DICOM image';
            if (loadError instanceof Error) {
              errorMessage = loadError.message;
            } else if (typeof loadError === 'object' && loadError !== null) {
              const errObj = loadError as Record<string, unknown>;
              errorMessage = errObj.error as string || errObj.message as string || 'Unknown load error';
            }
            
            if (!mountedRef.current || cleanedUpRef.current) return;
            onError?.(errorMessage);
            initializingRef.current = false;
            return;
          }

          if (cleanedUpRef.current || !mountedRef.current) return;

          // Verify element is still enabled before displaying
          try {
            cornerstone.getEnabledElement(element);
          } catch {
            console.warn('[Unified Viewer] Element disabled during load');
            initializingRef.current = false;
            return;
          }

          cornerstone.displayImage(element, image);

          const viewport = cornerstone.getViewport(element);
          const photometric = (image as any).photometricInterpretation;
          const needsInvert = photometric === 'MONOCHROME1';

          const newViewport = {
            ...viewport,
            voi: {
              windowWidth:
                viewport.voi?.windowWidth || image.windowWidth || metadata.windowWidth || 256,
              windowCenter:
                viewport.voi?.windowCenter || image.windowCenter || metadata.windowCenter || 128,
            },
            invert: needsInvert,
          };

          cornerstone.setViewport(element, newViewport);

          if (mountedRef.current && !cleanedUpRef.current) {
            setViewportState(newViewport);
            setIsReady(true);
            onReady?.();
            console.log('[Unified Viewer] Image loaded and displayed successfully');
          }
        } catch (error: unknown) {
          if (!mountedRef.current || cleanedUpRef.current) return;
          console.error('[Unified Viewer] Unexpected error:', error);
          const message = error instanceof Error ? error.message : 'Unexpected error loading image';
          onError?.(message);
        } finally {
          initializingRef.current = false;
        }
      };

      loadImage();

      // Event handler for image changes
      const handleNewImage = (event: any) => {
        if (cleanedUpRef.current || !mountedRef.current) return;

        try {
          const newIndex = event?.detail?.newImageIdIndex;
          if (Number.isFinite(newIndex)) {
            setCurrentImageIndex(newIndex);
            onIndexChange?.(newIndex);
          }
          const vp = cornerstone.getViewport(element);
          setViewportState(vp);
        } catch {
          // Ignore
        }
      };

      element.addEventListener('cornerstonenewimage', handleNewImage);

      // Cleanup function
      return () => {
        cleanedUpRef.current = true;
        mountedRef.current = false;
        initializingRef.current = false;

        try {
          element.removeEventListener('cornerstonenewimage', handleNewImage);
        } catch {
          // Ignore
        }

        if (isEnabledRef.current) {
          try {
            cornerstoneTools.clearToolState(element, 'stack');
          } catch {
            // Ignore
          }

          try {
            cornerstone.disable(element);
          } catch {
            // Ignore
          }
        }

        try {
          if (container.contains(element)) {
            container.removeChild(element);
          }
        } catch {
          // Ignore
        }

        cornerstoneElementRef.current = null;
        isEnabledRef.current = false;
        setIsReady(false);
      };
    }, [imageIds, metadata, onError, onIndexChange, onReady]);

    // Effect to handle image index changes
    useEffect(() => {
      if (!isReady || !cornerstoneElementRef.current || !imageIds.length) return;
      if (cleanedUpRef.current) return;

      const element = cornerstoneElementRef.current;
      const validIndex = Math.max(0, Math.min(currentImageIndex, imageIds.length - 1));
      const imageId = imageIds[validIndex];
      if (!imageId) return;

      const { cornerstone } = getCornerstoneBundle();

      // Verify element is enabled
      try {
        cornerstone.getEnabledElement(element);
      } catch {
        return;
      }

      cornerstone
        .loadAndCacheImage(imageId)
        .then((image) => {
          if (!mountedRef.current || cleanedUpRef.current) return;
          if (!cornerstoneElementRef.current) return;
          
          // Verify element is still enabled before display
          try {
            cornerstone.getEnabledElement(element);
            cornerstone.displayImage(element, image);
          } catch {
            // Element was disabled, ignore
          }
        })
        .catch((err: unknown) => {
          if (!mountedRef.current || cleanedUpRef.current) return;
          console.warn('[Unified Viewer] Failed to load image at index:', validIndex, {
            error: err,
            errorType: typeof err,
          });
        });
    }, [currentImageIndex, isReady, imageIds]);

    // Effect to handle tool changes
    useEffect(() => {
      if (!isReady || !cornerstoneElementRef.current) return;
      if (cleanedUpRef.current) return;

      const element = cornerstoneElementRef.current;

      // Tool name mapping
      const toolMap: Record<ViewerTool, string> = {
        zoom: 'Zoom',
        pan: 'Pan',
        wl: 'Wwwc',
        length: 'Length',
        angle: 'Angle',
        rectangleROI: 'RectangleRoi',
        ellipticalROI: 'EllipticalRoi',
        probe: 'Probe',
        scroll: 'StackScrollMouseWheel',
      };

      // Deactivate all tools first
      ['Zoom', 'Pan', 'Wwwc', 'Length', 'Angle', 'RectangleRoi', 'EllipticalRoi', 'Probe'].forEach(
        (tool) => {
          try {
            setToolPassive(element, tool);
          } catch {
            // Ignore
          }
        },
      );

      // Keep scroll active (no mouse button)
      try {
        setToolActive(element, 'StackScrollMouseWheel', {});
      } catch {
        // Ignore
      }

      // Activate selected tool
      const toolName = toolMap[activeTool];
      if (toolName) {
        try {
          setToolActive(element, toolName, { mouseButtonMask: 1 });
        } catch {
          // Ignore
        }
      }
    }, [activeTool, isReady]);

    // Imperative handle for parent components
    useImperativeHandle(
      ref,
      () => ({
        nextImage: () => {
          if (currentImageIndex < imageIds.length - 1) {
            setCurrentImageIndex((prev) => prev + 1);
          }
        },
        previousImage: () => {
          if (currentImageIndex > 0) {
            setCurrentImageIndex((prev) => prev - 1);
          }
        },
        setImageIndex: (index: number) => {
          if (index >= 0 && index < imageIds.length) {
            setCurrentImageIndex(index);
          }
        },
        applyPreset:
          mode === 'professional'
            ? (preset: WindowLevelPreset) => {
                if (!cornerstoneElementRef.current || !isReady) return;
                try {
                  const { cornerstone } = getCornerstoneBundle();
                  const viewport = cornerstone.getViewport(cornerstoneElementRef.current);
                  cornerstone.setViewport(cornerstoneElementRef.current, {
                    ...viewport,
                    voi: { windowWidth: preset.windowWidth, windowCenter: preset.windowCenter },
                  });
                } catch (e) {
                  console.warn('[Unified Viewer] applyPreset failed:', e);
                }
              }
            : undefined,
        invert: () => {
          if (!cornerstoneElementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(cornerstoneElementRef.current);
            cornerstone.setViewport(cornerstoneElementRef.current, {
              ...viewport,
              invert: !viewport.invert,
            });
          } catch (e) {
            console.warn('[Unified Viewer] invert failed:', e);
          }
        },
        flipHorizontal: () => {
          if (!cornerstoneElementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(cornerstoneElementRef.current);
            cornerstone.setViewport(cornerstoneElementRef.current, {
              ...viewport,
              hflip: !viewport.hflip,
            });
          } catch (e) {
            console.warn('[Unified Viewer] flipH failed:', e);
          }
        },
        flipVertical: () => {
          if (!cornerstoneElementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const viewport = cornerstone.getViewport(cornerstoneElementRef.current);
            cornerstone.setViewport(cornerstoneElementRef.current, {
              ...viewport,
              vflip: !viewport.vflip,
            });
          } catch (e) {
            console.warn('[Unified Viewer] flipV failed:', e);
          }
        },
        rotate:
          mode === 'professional'
            ? (degrees: number) => {
                if (!cornerstoneElementRef.current || !isReady) return;
                try {
                  const { cornerstone } = getCornerstoneBundle();
                  const viewport = cornerstone.getViewport(cornerstoneElementRef.current);
                  cornerstone.setViewport(cornerstoneElementRef.current, {
                    ...viewport,
                    rotation: ((viewport.rotation || 0) + degrees) % 360,
                  });
                } catch (e) {
                  console.warn('[Unified Viewer] rotate failed:', e);
                }
              }
            : undefined,
        reset: () => {
          if (!cornerstoneElementRef.current || !isReady) return;
          try {
            const { cornerstone } = getCornerstoneBundle();
            cornerstone.reset(cornerstoneElementRef.current);
          } catch (e) {
            console.warn('[Unified Viewer] reset failed:', e);
          }
        },
        fitToWindow:
          mode === 'professional'
            ? () => {
                if (!cornerstoneElementRef.current || !isReady) return;
                try {
                  const { cornerstone } = getCornerstoneBundle();
                  cornerstone.fitToWindow(cornerstoneElementRef.current);
                } catch (e) {
                  console.warn('[Unified Viewer] fitToWindow failed:', e);
                }
              }
            : undefined,
        exportPng: async () => {
          if (!cornerstoneElementRef.current || !isReady) return null;
          try {
            const { cornerstone } = getCornerstoneBundle();
            const enabledElement = cornerstone.getEnabledElement(cornerstoneElementRef.current);
            const canvas = enabledElement?.canvas as HTMLCanvasElement | undefined;
            return canvas?.toDataURL('image/png') || null;
          } catch (e) {
            console.error('[Unified Viewer] exportPng failed:', e);
            return null;
          }
        },
        getViewportStats:
          mode === 'professional'
            ? () => {
                if (!cornerstoneElementRef.current || !isReady) return null;
                try {
                  const { cornerstone } = getCornerstoneBundle();
                  const ee = cornerstone.getEnabledElement(cornerstoneElementRef.current);
                  return {
                    viewport: ee.viewport,
                    image: { width: ee.image.width, height: ee.image.height },
                  };
                } catch {
                  return null;
                }
              }
            : undefined,
      }),
      [isReady, imageIds.length, currentImageIndex, mode],
    );

    return (
      <div className="relative h-full w-full overflow-hidden rounded-lg border bg-black">
        {/* Container for Cornerstone */}
        <div
          ref={containerRef}
          className="h-full w-full"
          style={{ minHeight: '400px' }}
          suppressHydrationWarning
        />

        {/* Overlays */}
        {showOverlay && isReady && metadata && (
          <DicomOverlay
            metadata={metadata}
            currentIndex={currentImageIndex}
            totalImages={imageIds.length}
            windowWidth={viewportState?.voi?.windowWidth}
            windowCenter={viewportState?.voi?.windowCenter}
            zoom={viewportState?.scale}
          />
        )}

        {showAnomalyOverlay && isReady && anomalyResult && anomalyResult.has_anomaly && (
          <AnomalyOverlay
            analysisResult={anomalyResult}
            imageWidth={containerRef.current?.clientWidth || 512}
            imageHeight={containerRef.current?.clientHeight || 512}
            showBoundingBoxes={true}
            showHeatmap={true}
            showLabels={true}
            opacity={0.6}
          />
        )}

        {/* Empty state */}
        {!imageIds.length && (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground pointer-events-none">
            No DICOM image loaded
          </div>
        )}

        {/* Loading state */}
        {imageIds.length > 0 && !isReady && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              Loading...
            </div>
          </div>
        )}
      </div>
    );
  },
);

UnifiedDicomViewerInner.displayName = 'UnifiedDicomViewerInner';

export const UnifiedDicomViewer = memo(UnifiedDicomViewerInner, (prevProps, nextProps) => {
  return (
    prevProps.imageIds === nextProps.imageIds &&
    prevProps.currentIndex === nextProps.currentIndex &&
    prevProps.activeTool === nextProps.activeTool &&
    prevProps.showOverlay === nextProps.showOverlay &&
    prevProps.showAnomalyOverlay === nextProps.showAnomalyOverlay &&
    prevProps.anomalyResult === nextProps.anomalyResult &&
    prevProps.mode === nextProps.mode
  );
});

export default UnifiedDicomViewer;
