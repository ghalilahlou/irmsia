import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { api } from '../services/api';

const ViewerContext = createContext();

const initialState = {
  currentVolume: null,
  currentSegmentation: null,
  viewerConfig: {
    showVolume: true,
    showSegmentation: true,
    showAnatomical: false,
    renderMode: 'volume',
    windowLevel: { center: 0, width: 100 },
    opacity: 0.8,
    colorMap: 'grayscale',
  },
  controls: {
    rotation: { x: 0, y: 0, z: 0 },
    zoom: 1,
    pan: { x: 0, y: 0 },
  },
  loading: false,
  error: null,
  isLoaded: false,
};

const viewerReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_VOLUME':
      return { ...state, currentVolume: action.payload };
    case 'SET_SEGMENTATION':
      return { ...state, currentSegmentation: action.payload };
    case 'UPDATE_CONFIG':
      return {
        ...state,
        viewerConfig: { ...state.viewerConfig, ...action.payload },
      };
    case 'UPDATE_CONTROLS':
      return {
        ...state,
        controls: { ...state.controls, ...action.payload },
      };
    case 'SET_LOADED':
      return { ...state, isLoaded: action.payload };
    case 'RESET_VIEW':
      return {
        ...state,
        controls: {
          rotation: { x: 0, y: 0, z: 0 },
          zoom: 1,
          pan: { x: 0, y: 0 },
        },
      };
    case 'CLEAR_DATA':
      return {
        ...state,
        currentVolume: null,
        currentSegmentation: null,
        isLoaded: false,
      };
    default:
      return state;
  }
};

export const ViewerProvider = ({ children }) => {
  const [state, dispatch] = useReducer(viewerReducer, initialState);

  const loadVolumeData = async (analysisId) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const response = await api.getVolumeData(analysisId);
      dispatch({ type: 'SET_VOLUME', payload: response.data });
      dispatch({ type: 'SET_LOADED', payload: true });
    } catch (error) {
      dispatch({
        type: 'SET_ERROR',
        payload: 'Erreur lors du chargement du volume',
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const loadSegmentationData = async (analysisId) => {
    try {
      const response = await api.getSegmentationData(analysisId);
      dispatch({ type: 'SET_SEGMENTATION', payload: response.data });
    } catch (error) {
      console.error('Error loading segmentation:', error);
    }
  };

  const updateConfig = (config) => {
    dispatch({ type: 'UPDATE_CONFIG', payload: config });
  };

  const updateControls = (controls) => {
    dispatch({ type: 'UPDATE_CONTROLS', payload: controls });
  };

  const resetView = () => {
    dispatch({ type: 'RESET_VIEW' });
  };

  const clearData = () => {
    dispatch({ type: 'CLEAR_DATA' });
  };

  const exportScene = async (analysisId, format) => {
    try {
      const response = await api.exportScene(analysisId, format);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Erreur lors de l\'export' };
    }
  };

  const captureScreenshot = () => {
    // Implementation for screenshot capture
    return new Promise((resolve) => {
      // Simulate screenshot capture
      setTimeout(() => {
        resolve({ success: true, data: 'screenshot.png' });
      }, 1000);
    });
  };

  const value = {
    ...state,
    loadVolumeData,
    loadSegmentationData,
    updateConfig,
    updateControls,
    resetView,
    clearData,
    exportScene,
    captureScreenshot,
  };

  return (
    <ViewerContext.Provider value={value}>
      {children}
    </ViewerContext.Provider>
  );
};

export const useViewer = () => {
  const context = useContext(ViewerContext);
  if (!context) {
    throw new Error('useViewer must be used within a ViewerProvider');
  }
  return context;
}; 