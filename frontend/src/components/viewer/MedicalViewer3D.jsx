import React, { useEffect, useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Eye, 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Pan,
  Layers,
  Settings,
  Download,
  Camera
} from 'lucide-react';

// Import VTK.js
import '@kitware/vtk.js/Rendering/Profiles/Volume';
import vtkFullScreenRenderWindow from '@kitware/vtk.js/Rendering/Misc/FullScreenRenderWindow';
import vtkVolume from '@kitware/vtk.js/Rendering/Core/Volume';
import vtkVolumeMapper from '@kitware/vtk.js/Rendering/Core/VolumeMapper';
import vtkImageData from '@kitware/vtk.js/Common/DataModel/ImageData';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import vtkColorTransferFunction from '@kitware/vtk.js/Rendering/Core/ColorTransferFunction';
import vtkPiecewiseFunction from '@kitware/vtk.js/Common/DataModel/PiecewiseFunction';
import vtkImageSlice from '@kitware/vtk.js/Rendering/Core/ImageSlice';
import vtkImageMapper from '@kitware/vtk.js/Rendering/Core/ImageMapper';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkOutlineFilter from '@kitware/vtk.js/Filters/General/OutlineFilter';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkCubeSource from '@kitware/vtk.js/Filters/Sources/CubeSource';

const MedicalViewer3D = ({ 
  volumeData, 
  annotations = [], 
  onSliceChange,
  onVolumeLoaded,
  className = "" 
}) => {
  const containerRef = useRef(null);
  const renderWindowRef = useRef(null);
  const volumeRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState('volume'); // volume, mpr, surface
  const [opacity, setOpacity] = useState(0.8);
  const [windowLevel, setWindowLevel] = useState({ window: 2000, level: 1000 });
  const [camera, setCamera] = useState({ position: [0, 0, 1], focalPoint: [0, 0, 0] });

  // Initialisation du renderer VTK
  const initializeVTK = useCallback(() => {
    if (!containerRef.current) return;

    try {
      // Créer le render window
      const fullScreenRenderer = vtkFullScreenRenderWindow.newInstance({
        container: containerRef.current,
        background: [0.1, 0.1, 0.1]
      });

      const renderWindow = fullScreenRenderer.getRenderWindow();
      const renderer = fullScreenRenderer.getRenderer();
      
      renderWindowRef.current = renderWindow;
      
      // Configuration de la caméra
      const camera = renderer.getActiveCamera();
      camera.setPosition(0, 0, 1);
      camera.setFocalPoint(0, 0, 0);
      camera.setViewUp(0, 1, 0);
      
      renderWindow.render();
      
      setIsLoading(false);
      
    } catch (error) {
      console.error('Erreur lors de l\'initialisation VTK:', error);
      setIsLoading(false);
    }
  }, []);

  // Chargement du volume
  const loadVolume = useCallback(async (data) => {
    if (!renderWindowRef.current || !data) return;

    try {
      setIsLoading(true);
      
      const renderWindow = renderWindowRef.current;
      const renderer = renderWindow.getRenderer();
      
      // Nettoyer les acteurs existants
      renderer.removeAllViewProps();
      
      if (viewMode === 'volume') {
        await loadVolumeRendering(data, renderer);
      } else if (viewMode === 'mpr') {
        await loadMPRView(data, renderer);
      } else if (viewMode === 'surface') {
        await loadSurfaceRendering(data, renderer);
      }
      
      // Ajouter les annotations
      if (annotations.length > 0) {
        loadAnnotations(annotations, renderer);
      }
      
      // Ajouter l'outline
      addOutline(data, renderer);
      
      renderWindow.render();
      setIsLoading(false);
      
      if (onVolumeLoaded) {
        onVolumeLoaded(data);
      }
      
    } catch (error) {
      console.error('Erreur lors du chargement du volume:', error);
      setIsLoading(false);
    }
  }, [viewMode, annotations, onVolumeLoaded]);

  // Chargement du volume rendering
  const loadVolumeRendering = async (data, renderer) => {
    const volume = vtkVolume.newInstance();
    const mapper = vtkVolumeMapper.newInstance();
    
    // Créer l'image data
    const imageData = vtkImageData.newInstance();
    imageData.setDimensions(data.dimensions);
    imageData.setOrigin(data.origin);
    imageData.setSpacing(data.spacing);
    
    const dataArray = vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: data.pixelData
    });
    imageData.getPointData().setScalars(dataArray);
    
    mapper.setInputData(imageData);
    volume.setMapper(mapper);
    
    // Configuration du transfert de couleur
    const colorFunction = vtkColorTransferFunction.newInstance();
    colorFunction.addRGBPoint(0, 0.0, 0.0, 0.0);
    colorFunction.addRGBPoint(500, 0.2, 0.2, 0.2);
    colorFunction.addRGBPoint(1000, 0.4, 0.4, 0.4);
    colorFunction.addRGBPoint(1500, 0.6, 0.6, 0.6);
    colorFunction.addRGBPoint(2000, 1.0, 1.0, 1.0);
    
    const opacityFunction = vtkPiecewiseFunction.newInstance();
    opacityFunction.addPoint(0, 0.0);
    opacityFunction.addPoint(500, 0.1);
    opacityFunction.addPoint(1000, 0.3);
    opacityFunction.addPoint(1500, 0.6);
    opacityFunction.addPoint(2000, opacity);
    
    volume.getProperty().setRGBTransferFunction(0, colorFunction);
    volume.getProperty().setScalarOpacity(0, opacityFunction);
    volume.getProperty().setInterpolationTypeToLinear();
    volume.getProperty().setShade(true);
    volume.getProperty().setAmbient(0.4);
    volume.getProperty().setDiffuse(0.6);
    volume.getProperty().setSpecular(0.2);
    
    renderer.addVolume(volume);
    volumeRef.current = volume;
  };

  // Chargement de la vue MPR
  const loadMPRView = async (data, renderer) => {
    const imageData = vtkImageData.newInstance();
    imageData.setDimensions(data.dimensions);
    imageData.setOrigin(data.origin);
    imageData.setSpacing(data.spacing);
    
    const dataArray = vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: data.pixelData
    });
    imageData.getPointData().setScalars(dataArray);
    
    // Créer les vues axial, sagittal, coronal
    const views = [
      { name: 'axial', sliceMode: 2 },
      { name: 'sagittal', sliceMode: 0 },
      { name: 'coronal', sliceMode: 1 }
    ];
    
    views.forEach((view, index) => {
      const mapper = vtkImageMapper.newInstance();
      mapper.setInputData(imageData);
      mapper.setSlicingMode(view.sliceMode);
      mapper.setSlice(Math.floor(data.dimensions[view.sliceMode] / 2));
      
      const actor = vtkActor.newInstance();
      actor.setMapper(mapper);
      
      // Positionner les vues
      const offset = index * 0.3;
      actor.setPosition(offset, 0, 0);
      
      renderer.addActor(actor);
    });
  };

  // Chargement du surface rendering
  const loadSurfaceRendering = async (data, renderer) => {
    // Implémentation du surface rendering
    // Utiliser vtkMarchingCubes ou vtkContourFilter
    console.log('Surface rendering à implémenter');
  };

  // Chargement des annotations
  const loadAnnotations = (annotations, renderer) => {
    annotations.forEach(annotation => {
      if (annotation.type === 'boundingBox') {
        // Créer un cube pour représenter la bounding box
        const cubeSource = vtkCubeSource.newInstance({
          xLength: annotation.size[0],
          yLength: annotation.size[1],
          zLength: annotation.size[2]
        });
        
        const mapper = vtkMapper.newInstance();
        mapper.setInputConnection(cubeSource.getOutputPort());
        
        const actor = vtkActor.newInstance();
        actor.setMapper(mapper);
        actor.setPosition(annotation.position);
        
        // Couleur selon le type d'anomalie
        const colors = {
          'tumor': [1, 0, 0],      // Rouge
          'stroke': [0, 1, 0],     // Vert
          'aneurysm': [0, 0, 1],   // Bleu
          'lesion': [1, 1, 0]      // Jaune
        };
        
        actor.getProperty().setColor(colors[annotation.label] || [1, 1, 1]);
        actor.getProperty().setOpacity(0.7);
        
        renderer.addActor(actor);
      }
    });
  };

  // Ajout de l'outline
  const addOutline = (data, renderer) => {
    const imageData = vtkImageData.newInstance();
    imageData.setDimensions(data.dimensions);
    imageData.setOrigin(data.origin);
    imageData.setSpacing(data.spacing);
    
    const outlineFilter = vtkOutlineFilter.newInstance();
    outlineFilter.setInputData(imageData);
    
    const mapper = vtkMapper.newInstance();
    mapper.setInputConnection(outlineFilter.getOutputPort());
    
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(1, 1, 1);
    actor.getProperty().setLineWidth(2);
    
    renderer.addActor(actor);
  };

  // Gestionnaires d'événements
  const handleZoomIn = () => {
    if (renderWindowRef.current) {
      const camera = renderWindowRef.current.getRenderer().getActiveCamera();
      camera.zoom(1.2);
      renderWindowRef.current.render();
    }
  };

  const handleZoomOut = () => {
    if (renderWindowRef.current) {
      const camera = renderWindowRef.current.getRenderer().getActiveCamera();
      camera.zoom(0.8);
      renderWindowRef.current.render();
    }
  };

  const handleReset = () => {
    if (renderWindowRef.current) {
      const camera = renderWindowRef.current.getRenderer().getActiveCamera();
      camera.setPosition(0, 0, 1);
      camera.setFocalPoint(0, 0, 0);
      camera.setViewUp(0, 1, 0);
      renderWindowRef.current.render();
    }
  };

  const handleOpacityChange = (newOpacity) => {
    setOpacity(newOpacity);
    if (volumeRef.current) {
      const opacityFunction = vtkPiecewiseFunction.newInstance();
      opacityFunction.addPoint(0, 0.0);
      opacityFunction.addPoint(500, 0.1);
      opacityFunction.addPoint(1000, 0.3);
      opacityFunction.addPoint(1500, 0.6);
      opacityFunction.addPoint(2000, newOpacity);
      
      volumeRef.current.getProperty().setScalarOpacity(0, opacityFunction);
      renderWindowRef.current.render();
    }
  };

  const handleWindowLevelChange = (window, level) => {
    setWindowLevel({ window, level });
    // Mettre à jour le transfert de couleur
    if (volumeRef.current) {
      const colorFunction = vtkColorTransferFunction.newInstance();
      const minValue = level - window / 2;
      const maxValue = level + window / 2;
      
      colorFunction.addRGBPoint(minValue, 0.0, 0.0, 0.0);
      colorFunction.addRGBPoint(maxValue, 1.0, 1.0, 1.0);
      
      volumeRef.current.getProperty().setRGBTransferFunction(0, colorFunction);
      renderWindowRef.current.render();
    }
  };

  // Effets
  useEffect(() => {
    initializeVTK();
  }, [initializeVTK]);

  useEffect(() => {
    if (volumeData) {
      loadVolume(volumeData);
    }
  }, [volumeData, loadVolume]);

  useEffect(() => {
    if (volumeData) {
      loadVolume(volumeData);
    }
  }, [viewMode, loadVolume]);

  return (
    <motion.div 
      className={`relative w-full h-full bg-gray-900 rounded-lg overflow-hidden ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Container VTK */}
      <div 
        ref={containerRef} 
        className="w-full h-full"
        style={{ minHeight: '500px' }}
      />
      
      {/* Loading Overlay */}
      {isLoading && (
        <motion.div 
          className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p>Chargement du volume...</p>
          </div>
        </motion.div>
      )}
      
      {/* Toolbar */}
      <div className="absolute top-4 left-4 z-20">
        <div className="bg-white bg-opacity-90 rounded-lg p-2 shadow-lg">
          <div className="flex flex-col space-y-2">
            {/* View Mode Buttons */}
            <div className="flex space-x-1">
              <button
                onClick={() => setViewMode('volume')}
                className={`p-2 rounded ${viewMode === 'volume' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="Volume Rendering"
              >
                <Brain size={16} />
              </button>
              <button
                onClick={() => setViewMode('mpr')}
                className={`p-2 rounded ${viewMode === 'mpr' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="Multiplanar Reconstruction"
              >
                <Layers size={16} />
              </button>
              <button
                onClick={() => setViewMode('surface')}
                className={`p-2 rounded ${viewMode === 'surface' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                title="Surface Rendering"
              >
                <Eye size={16} />
              </button>
            </div>
            
            {/* Camera Controls */}
            <div className="flex space-x-1">
              <button
                onClick={handleZoomIn}
                className="p-2 bg-gray-200 rounded hover:bg-gray-300"
                title="Zoom In"
              >
                <ZoomIn size={16} />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 bg-gray-200 rounded hover:bg-gray-300"
                title="Zoom Out"
              >
                <ZoomOut size={16} />
              </button>
              <button
                onClick={handleReset}
                className="p-2 bg-gray-200 rounded hover:bg-gray-300"
                title="Reset View"
              >
                <RotateCcw size={16} />
              </button>
            </div>
            
            {/* Opacity Control */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Opacity</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={opacity}
                onChange={(e) => handleOpacityChange(parseFloat(e.target.value))}
                className="w-16"
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Window/Level Control */}
      <div className="absolute top-4 right-4 z-20">
        <div className="bg-white bg-opacity-90 rounded-lg p-3 shadow-lg">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Window</span>
              <input
                type="range"
                min="100"
                max="4000"
                step="100"
                value={windowLevel.window}
                onChange={(e) => handleWindowLevelChange(parseInt(e.target.value), windowLevel.level)}
                className="w-20"
              />
              <span className="text-xs">{windowLevel.window}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-600">Level</span>
              <input
                type="range"
                min="0"
                max="3000"
                step="100"
                value={windowLevel.level}
                onChange={(e) => handleWindowLevelChange(windowLevel.window, parseInt(e.target.value))}
                className="w-20"
              />
              <span className="text-xs">{windowLevel.level}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="absolute bottom-4 right-4 z-20">
        <div className="flex space-x-2">
          <button
            className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 shadow-lg"
            title="Screenshot"
          >
            <Camera size={20} />
          </button>
          <button
            className="p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 shadow-lg"
            title="Export"
          >
            <Download size={20} />
          </button>
          <button
            className="p-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 shadow-lg"
            title="Settings"
          >
            <Settings size={20} />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default MedicalViewer3D; 