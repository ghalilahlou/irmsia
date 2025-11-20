import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  CloudArrowUpIcon, 
  DocumentIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ImageUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle accepted files
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      preview: URL.createObjectURL(file)
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(({ file, errors }) => {
        errors.forEach(error => {
          toast.error(`${file.name}: ${error.message}`);
        });
      });
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.dcm', '.nii', '.nii.gz', '.mha', '.mhd'],
      'application/dicom': ['.dcm'],
      'application/octet-stream': ['.nii', '.nii.gz', '.mha', '.mhd']
    },
    multiple: true,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const removeFile = (id) => {
    setUploadedFiles(prev => {
      const fileToRemove = prev.find(f => f.id === id);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prev.filter(f => f.id !== id);
    });
  };

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Aucun fichier à uploader');
      return;
    }

    setUploading(true);

    // Simulate upload progress
    for (let i = 0; i < uploadedFiles.length; i++) {
      const file = uploadedFiles[i];
      if (file.status === 'pending') {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === file.id 
              ? { ...f, status: 'uploading' }
              : f
          )
        );

        // Simulate progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === file.id 
                ? { ...f, progress }
                : f
            )
          );
        }

        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === file.id 
              ? { ...f, status: 'completed' }
              : f
          )
        );
      }
    }

    setUploading(false);
    toast.success(`${uploadedFiles.length} fichier(s) uploadé(s) avec succès`);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.includes('dicom') || type.includes('dcm')) {
      return '🏥';
    } else if (type.includes('nii')) {
      return '🧠';
    } else if (type.includes('image')) {
      return '🖼️';
    }
    return '📄';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'uploading':
        return <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Upload d'images</h1>
        <p className="text-gray-600">Téléchargez vos images médicales pour analyse</p>
      </div>

      {/* Upload Zone */}
      <div className="mb-8">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-lg font-medium text-gray-900">
            {isDragActive ? 'Déposez les fichiers ici' : 'Glissez-déposez vos fichiers ici'}
          </p>
          <p className="mt-2 text-sm text-gray-500">
            ou cliquez pour sélectionner des fichiers
          </p>
          <p className="mt-1 text-xs text-gray-400">
            Formats supportés: DICOM, NIfTI, MHA/MHD, PNG, JPG (max 100MB)
          </p>
        </div>
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Fichiers sélectionnés ({uploadedFiles.length})
            </h3>
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Upload en cours...' : 'Uploader tous les fichiers'}
            </button>
          </div>

          <div className="space-y-4">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="bg-white border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <span className="text-2xl">{getFileIcon(file.type)}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(file.status)}
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                {file.status === 'uploading' && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {file.progress}% terminé
                    </p>
                  </div>
                )}

                {/* Preview */}
                {file.preview && file.type.includes('image') && (
                  <div className="mt-3">
                    <img
                      src={file.preview}
                      alt={file.name}
                      className="w-20 h-20 object-cover rounded border"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Guidelines */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-4">
          Conseils pour l'upload
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Formats supportés:</h4>
            <ul className="space-y-1">
              <li>• DICOM (.dcm) - Images médicales standard</li>
              <li>• NIfTI (.nii, .nii.gz) - Volumes 3D</li>
              <li>• MHA/MHD (.mha, .mhd) - Métadonnées</li>
              <li>• Images standard (PNG, JPG, BMP)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Limitations:</h4>
            <ul className="space-y-1">
              <li>• Taille maximale: 100MB par fichier</li>
              <li>• Formats non supportés: ZIP, RAR</li>
              <li>• Images corrompues seront rejetées</li>
              <li>• Métadonnées DICOM requises</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageUpload; 