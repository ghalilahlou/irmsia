import React, { useState, useEffect } from 'react';
import { useAnalysis } from '../contexts/AnalysisContext';
import MedicalViewer3D from '../components/viewer/MedicalViewer3D';
import { 
  CubeIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ArrowPathIcon,
  CameraIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const Viewer3D = () => {
  const { currentAnalysis } = useAnalysis();
  const [viewerConfig, setViewerConfig] = useState({
    showVolume: true,
    showSegmentation: true,
    showAnatomical: false,
    renderMode: 'volume', // 'volume', 'surface', 'mpr'
    windowLevel: { center: 0, width: 100 },
    opacity: 0.8,
    colorMap: 'grayscale',
  });

  const [viewerState, setViewerState] = useState({
    isLoaded: false,
    isLoading: false,
    error: null,
  });

  const [controls, setControls] = useState({
    rotation: { x: 0, y: 0, z: 0 },
    zoom: 1,
    pan: { x: 0, y: 0 },
  });

  // Mock data for demonstration
  const mockVolumeData = {
    dimensions: [256, 256, 128],
    spacing: [1, 1, 1],
    origin: [0, 0, 0],
    data: new Uint8Array(256 * 256 * 128).fill(128),
  };

  const mockSegmentationData = {
    labels: ['background', 'brain', 'tumor'],
    colors: [[0, 0, 0], [255, 255, 255], [255, 0, 0]],
    data: new Uint8Array(256 * 256 * 128).fill(0),
  };

  const handleViewerLoad = () => {
    setViewerState(prev => ({ ...prev, isLoaded: true, isLoading: false }));
  };

  const handleViewerError = (error) => {
    setViewerState(prev => ({ ...prev, error, isLoading: false }));
  };

  const handleConfigChange = (key, value) => {
    setViewerConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleControlChange = (key, value) => {
    setControls(prev => ({ ...prev, [key]: value }));
  };

  const resetView = () => {
    setControls({
      rotation: { x: 0, y: 0, z: 0 },
      zoom: 1,
      pan: { x: 0, y: 0 },
    });
  };

  const exportScene = (format) => {
    // Implementation for scene export
    console.log(`Exporting scene in ${format} format`);
  };

  const captureScreenshot = () => {
    // Implementation for screenshot capture
    console.log('Capturing screenshot');
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Visualisation 3D</h1>
            <p className="text-sm text-gray-600">
              {currentAnalysis ? `Analyse: ${currentAnalysis.patientName}` : 'Aucune analyse sélectionnée'}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={resetView}
              className="btn-outline btn-sm"
              title="Réinitialiser la vue"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </button>
            <button
              onClick={captureScreenshot}
              className="btn-outline btn-sm"
              title="Capturer une image"
            >
              <CameraIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => exportScene('png')}
              className="btn-outline btn-sm"
              title="Exporter la scène"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Sidebar Controls */}
        <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
          <div className="space-y-6">
            {/* Display Options */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Affichage</h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewerConfig.showVolume}
                    onChange={(e) => handleConfigChange('showVolume', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Volume</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewerConfig.showSegmentation}
                    onChange={(e) => handleConfigChange('showSegmentation', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Segmentation</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewerConfig.showAnatomical}
                    onChange={(e) => handleConfigChange('showAnatomical', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Modèle anatomique</span>
                </label>
              </div>
            </div>

            {/* Render Mode */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Mode de rendu</h3>
              <select
                value={viewerConfig.renderMode}
                onChange={(e) => handleConfigChange('renderMode', e.target.value)}
                className="form-input"
              >
                <option value="volume">Volume</option>
                <option value="surface">Surface</option>
                <option value="mpr">MPR</option>
              </select>
            </div>

            {/* Window/Level */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Fenêtre/Niveau</h3>
              <div className="space-y-2">
                <div>
                  <label className="text-xs text-gray-500">Centre</label>
                  <input
                    type="range"
                    min="0"
                    max="255"
                    value={viewerConfig.windowLevel.center}
                    onChange={(e) => handleConfigChange('windowLevel', {
                      ...viewerConfig.windowLevel,
                      center: parseInt(e.target.value)
                    })}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-500">{viewerConfig.windowLevel.center}</span>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Largeur</label>
                  <input
                    type="range"
                    min="1"
                    max="255"
                    value={viewerConfig.windowLevel.width}
                    onChange={(e) => handleConfigChange('windowLevel', {
                      ...viewerConfig.windowLevel,
                      width: parseInt(e.target.value)
                    })}
                    className="w-full"
                  />
                  <span className="text-xs text-gray-500">{viewerConfig.windowLevel.width}</span>
                </div>
              </div>
            </div>

            {/* Opacity */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Opacité</h3>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={viewerConfig.opacity}
                onChange={(e) => handleConfigChange('opacity', parseFloat(e.target.value))}
                className="w-full"
              />
              <span className="text-xs text-gray-500">{Math.round(viewerConfig.opacity * 100)}%</span>
            </div>

            {/* Color Map */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Colormap</h3>
              <select
                value={viewerConfig.colorMap}
                onChange={(e) => handleConfigChange('colorMap', e.target.value)}
                className="form-input"
              >
                <option value="grayscale">Grayscale</option>
                <option value="hot">Hot</option>
                <option value="cool">Cool</option>
                <option value="rainbow">Rainbow</option>
                <option value="jet">Jet</option>
              </select>
            </div>

            {/* Camera Controls */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Contrôles caméra</h3>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleControlChange('zoom', controls.zoom * 1.2)}
                  className="btn-outline btn-sm"
                  title="Zoom in"
                >
                  <ArrowsPointingInIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleControlChange('zoom', controls.zoom * 0.8)}
                  className="btn-outline btn-sm"
                  title="Zoom out"
                >
                  <ArrowsPointingOutIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 3D Viewer */}
        <div className="flex-1 relative">
          {viewerState.isLoading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="spinner-lg mx-auto"></div>
                <p className="text-white mt-2">Chargement du volume...</p>
              </div>
            </div>
          )}

          {viewerState.error && (
            <div className="absolute inset-0 bg-red-50 flex items-center justify-center z-10">
              <div className="text-center">
                <p className="text-red-600">Erreur de chargement: {viewerState.error}</p>
                <button
                  onClick={() => setViewerState(prev => ({ ...prev, error: null }))}
                  className="btn-primary mt-2"
                >
                  Réessayer
                </button>
              </div>
            </div>
          )}

          <div className="w-full h-full">
            <MedicalViewer3D
              volumeData={mockVolumeData}
              segmentationData={mockSegmentationData}
              config={viewerConfig}
              controls={controls}
              onLoad={handleViewerLoad}
              onError={handleViewerError}
            />
          </div>

          {/* Viewer Controls Overlay */}
          <div className="absolute top-4 right-4 bg-white bg-opacity-90 rounded-lg p-2 shadow-lg">
            <div className="flex flex-col space-y-2">
              <button
                onClick={() => handleConfigChange('showVolume', !viewerConfig.showVolume)}
                className={`p-2 rounded ${viewerConfig.showVolume ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:text-gray-900'}`}
                title="Afficher/Masquer le volume"
              >
                <CubeIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => handleConfigChange('showSegmentation', !viewerConfig.showSegmentation)}
                className={`p-2 rounded ${viewerConfig.showSegmentation ? 'bg-green-100 text-green-600' : 'text-gray-600 hover:text-gray-900'}`}
                title="Afficher/Masquer la segmentation"
              >
                <EyeIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Volume: {mockVolumeData.dimensions.join(' × ')}</span>
            <span>Segmentation: {mockSegmentationData.labels.length} labels</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>Zoom: {Math.round(controls.zoom * 100)}%</span>
            <span>FPS: 60</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Viewer3D; 