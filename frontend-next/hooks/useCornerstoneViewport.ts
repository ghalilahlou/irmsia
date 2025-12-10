/**
 * Hook unifié pour gérer la logique Cornerstone commune
 * Extrait la logique partagée entre DicomViewer et ProfessionalViewport
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { getCornerstoneBundle, initCornerstone } from '@/lib/cornerstone';

type UseCornerstoneViewportOptions = {
  imageIds: string[];
  currentIndex?: number;
  onError?: (message: string) => void;
  onImageChange?: (index: number) => void;
  enableTools?: string[]; // Liste des outils à activer
};

type CornerstoneViewportState = {
  isReady: boolean;
  currentImageIndex: number;
  viewportState: any;
};

let globalToolsRegistered = false;

const registerGlobalTools = (tools: string[] = []) => {
  try {
    const { cornerstoneTools } = getCornerstoneBundle();
    if (globalToolsRegistered) return;

    const toolMap: Record<string, any> = {
      Zoom: cornerstoneTools.ZoomTool,
      Pan: cornerstoneTools.PanTool,
      Wwwc: cornerstoneTools.WwwcTool,
      StackScrollMouseWheel: cornerstoneTools.StackScrollMouseWheelTool,
      Length: cornerstoneTools.LengthTool,
      Angle: cornerstoneTools.AngleTool,
      RectangleRoi: cornerstoneTools.RectangleRoiTool,
      EllipticalRoi: cornerstoneTools.EllipticalRoiTool,
      Probe: cornerstoneTools.ProbeTool,
    };

    // Enregistrer uniquement les outils demandés
    const toolsToRegister = tools.length > 0 ? tools : ['Zoom', 'Pan', 'Wwwc', 'StackScrollMouseWheel'];
    
    toolsToRegister.forEach((toolName) => {
      const tool = toolMap[toolName];
      if (tool) {
        try {
          cornerstoneTools.addTool(tool);
        } catch (error) {
          console.warn(`[Cornerstone Viewport] Failed to add ${toolName}:`, error);
        }
      }
    });

    globalToolsRegistered = true;
  } catch (error) {
    console.error('[Cornerstone Viewport] Error registering tools:', error);
  }
};

export function useCornerstoneViewport({
  imageIds,
  currentIndex = 0,
  onError,
  onImageChange,
  enableTools = ['Zoom', 'Pan', 'Wwwc', 'StackScrollMouseWheel'],
}: UseCornerstoneViewportOptions) {
  const elementRef = useRef<HTMLDivElement | null>(null);
  const [state, setState] = useState<CornerstoneViewportState>({
    isReady: false,
    currentImageIndex: currentIndex,
    viewportState: null,
  });

  // Initialiser Cornerstone une seule fois
  useEffect(() => {
    initCornerstone();
    registerGlobalTools(enableTools);
  }, [enableTools]);

  const loadImage = useCallback(async (element: HTMLDivElement, imageId: string, index: number) => {
    try {
      if (!element.isConnected) {
        console.warn('[Cornerstone Viewport] Element not connected');
        return;
      }

      const { cornerstone, cornerstoneTools } = getCornerstoneBundle();

      // Vérifier et activer l'élément
      let isEnabled = false;
      try {
        const existingEnabled = cornerstone.getEnabledElement(element);
        if (existingEnabled) {
          isEnabled = true;
        } else {
          cornerstone.enable(element);
          isEnabled = true;
        }
      } catch (error) {
        console.warn('[Cornerstone Viewport] Enable error:', error);
        try {
          cornerstone.enable(element);
          isEnabled = true;
        } catch {
          isEnabled = false;
        }
      }

      if (!isEnabled) {
        throw new Error('Failed to enable Cornerstone element');
      }

      // Configurer le stack
      const stack = {
        imageIds,
        currentImageIdIndex: index,
      };

      try {
        cornerstoneTools.clearToolState(element, 'stack');
        cornerstoneTools.addStackStateManager(element, ['stack']);
        cornerstoneTools.addToolState(element, 'stack', stack);
      } catch (error) {
        console.warn('[Cornerstone Viewport] Tool state setup error:', error);
      }

      // Charger l'image
      const image = await cornerstone.loadAndCacheImage(imageId);

      if (!element.isConnected) {
        return;
      }

      cornerstone.displayImage(element, image);

      // Configurer le viewport
      const viewport = cornerstone.getViewport(element);
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

      cornerstone.setViewport(element, newViewport);
      setState((prev) => ({
        ...prev,
        isReady: true,
        viewportState: newViewport,
      }));

      // Activer les outils par défaut
      try {
        cornerstoneTools.setToolActive('StackScrollMouseWheel', {});
        cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 });
        cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 2 });
      } catch (error) {
        console.warn('[Cornerstone Viewport] Tool activation warning:', error);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to load DICOM image';
      onError?.(message);
      console.error('[Cornerstone Viewport] Load error:', error);
    }
  }, [imageIds, onError]);

  const setImageIndex = useCallback((index: number) => {
    if (index < 0 || index >= imageIds.length) {
      console.warn('[Cornerstone Viewport] Invalid image index:', index);
      return;
    }

    const imageId = imageIds[index];
    if (!imageId || !elementRef.current) {
      return;
    }

    setState((prev) => ({ ...prev, currentImageIndex: index }));
    loadImage(elementRef.current, imageId, index);
    onImageChange?.(index);
  }, [imageIds, loadImage, onImageChange]);

  const getViewport = useCallback(() => {
    if (!elementRef.current || !state.isReady) return null;
    try {
      const { cornerstone } = getCornerstoneBundle();
      return cornerstone.getViewport(elementRef.current);
    } catch {
      return null;
    }
  }, [state.isReady]);

  const updateViewport = useCallback((updates: any) => {
    if (!elementRef.current || !state.isReady) return;
    try {
      const { cornerstone } = getCornerstoneBundle();
      const currentViewport = cornerstone.getViewport(elementRef.current);
      cornerstone.setViewport(elementRef.current, { ...currentViewport, ...updates });
      setState((prev) => ({
        ...prev,
        viewportState: { ...currentViewport, ...updates },
      }));
    } catch (error) {
      console.warn('[Cornerstone Viewport] Update viewport failed:', error);
    }
  }, [state.isReady]);

  const cleanup = useCallback(() => {
    if (!elementRef.current) return;

    const element = elementRef.current;
    try {
      const { cornerstone, cornerstoneTools } = getCornerstoneBundle();
      
      if (element.isConnected) {
        try {
          const enabledElement = cornerstone.getEnabledElement(element);
          if (enabledElement) {
            cornerstoneTools.clearToolState(element, 'stack');
          }
        } catch (error) {
          // Ignorer les erreurs de nettoyage
        }
      }
    } catch (error) {
      // Ignorer silencieusement
    }
  }, []);

  return {
    elementRef,
    state,
    loadImage,
    setImageIndex,
    getViewport,
    updateViewport,
    cleanup,
  };
}

