import React, { useState } from 'react';
import { useAnalysis } from '../contexts/AnalysisContext';
import { 
  PlayIcon, 
  StopIcon, 
  EyeIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  FunnelIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Analysis = () => {
  const { 
    analyses, 
    loading, 
    startAnalysis, 
    cancelAnalysis, 
    setCurrentAnalysis,
    setFilters,
    clearFilters 
  } = useAnalysis();

  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleStartAnalysis = (analysisId) => {
    startAnalysis({ analysisId });
  };

  const handleCancelAnalysis = (analysisId) => {
    cancelAnalysis(analysisId);
  };

  const handleViewAnalysis = (analysis) => {
    setSelectedAnalysis(analysis);
    setCurrentAnalysis(analysis);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <XMarkIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'processing':
        return 'status-processing';
      case 'pending':
        return 'status-pending';
      case 'error':
        return 'status-error';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return 'status-pending';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'processing':
        return 'En cours';
      case 'pending':
        return 'En attente';
      case 'error':
        return 'Erreur';
      case 'cancelled':
        return 'Annulé';
      default:
        return 'Inconnu';
    }
  };

  const filteredAnalyses = analyses.filter(analysis => {
    const matchesSearch = analysis.patientName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         analysis.studyType?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         analysis.id?.toString().includes(searchTerm);
    
    return matchesSearch;
  });

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analyses</h1>
        <p className="text-gray-600">Gérez vos analyses médicales</p>
      </div>

      {/* Search and Filters */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Rechercher des analyses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-outline btn-sm"
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              Filtres
            </button>
            <button
              onClick={clearFilters}
              className="btn-outline btn-sm"
            >
              Réinitialiser
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="form-label">Statut</label>
                <select
                  onChange={(e) => setFilters({ status: e.target.value })}
                  className="form-input"
                >
                  <option value="all">Tous les statuts</option>
                  <option value="pending">En attente</option>
                  <option value="processing">En cours</option>
                  <option value="completed">Terminé</option>
                  <option value="error">Erreur</option>
                  <option value="cancelled">Annulé</option>
                </select>
              </div>
              <div>
                <label className="form-label">Type d'étude</label>
                <select
                  onChange={(e) => setFilters({ studyType: e.target.value })}
                  className="form-input"
                >
                  <option value="">Tous les types</option>
                  <option value="IRM">IRM</option>
                  <option value="CT">CT</option>
                  <option value="X-Ray">X-Ray</option>
                  <option value="Ultrasound">Échographie</option>
                </select>
              </div>
              <div>
                <label className="form-label">Date</label>
                <input
                  type="date"
                  onChange={(e) => setFilters({ date: e.target.value })}
                  className="form-input"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Analyses List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Analyses ({filteredAnalyses.length})
          </h3>
        </div>
        
        {loading ? (
          <div className="p-6 text-center">
            <div className="spinner-lg mx-auto"></div>
            <p className="mt-2 text-gray-500">Chargement des analyses...</p>
          </div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="p-6 text-center">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500">Aucune analyse trouvée</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredAnalyses.map((analysis) => (
              <div key={analysis.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(analysis.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {analysis.patientName || `Analyse ${analysis.id}`}
                      </p>
                      <p className="text-sm text-gray-500">
                        {analysis.studyType} - {analysis.modality}
                      </p>
                      <p className="text-xs text-gray-400">
                        Créé le {new Date(analysis.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`status-badge ${getStatusColor(analysis.status)}`}>
                      {getStatusText(analysis.status)}
                    </span>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleViewAnalysis(analysis)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Voir les détails"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      
                      {analysis.status === 'pending' && (
                        <button
                          onClick={() => handleStartAnalysis(analysis.id)}
                          className="p-1 text-green-400 hover:text-green-600"
                          title="Démarrer l'analyse"
                        >
                          <PlayIcon className="h-4 w-4" />
                        </button>
                      )}
                      
                      {analysis.status === 'processing' && (
                        <button
                          onClick={() => handleCancelAnalysis(analysis.id)}
                          className="p-1 text-red-400 hover:text-red-600"
                          title="Annuler l'analyse"
                        >
                          <StopIcon className="h-4 w-4" />
                        </button>
                      )}
                      
                      {analysis.status === 'completed' && (
                        <button
                          onClick={() => {/* Navigate to report */}}
                          className="p-1 text-blue-400 hover:text-blue-600"
                          title="Voir le rapport"
                        >
                          <DocumentTextIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Progress Bar for Processing */}
                {analysis.status === 'processing' && analysis.progress && (
                  <div className="mt-3">
                    <div className="progress">
                      <div
                        className="progress-primary"
                        style={{ width: `${analysis.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {analysis.progress}% terminé
                    </p>
                  </div>
                )}
                
                {/* Error Message */}
                {analysis.status === 'error' && analysis.error && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-800">
                      Erreur: {analysis.error}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Details Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="modal-header">
              <h3 className="text-lg font-medium text-gray-900">
                Détails de l'analyse
              </h3>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Patient</p>
                  <p className="text-sm text-gray-900">{selectedAnalysis.patientName}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Type d'étude</p>
                  <p className="text-sm text-gray-900">{selectedAnalysis.studyType}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Modalité</p>
                  <p className="text-sm text-gray-900">{selectedAnalysis.modality}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Statut</p>
                  <p className="text-sm text-gray-900">{getStatusText(selectedAnalysis.status)}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Date de création</p>
                  <p className="text-sm text-gray-900">
                    {new Date(selectedAnalysis.createdAt).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Modèle utilisé</p>
                  <p className="text-sm text-gray-900">{selectedAnalysis.modelName || 'N/A'}</p>
                </div>
              </div>
              
              {selectedAnalysis.metrics && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Métriques</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {selectedAnalysis.metrics.accuracy || 'N/A'}%
                      </p>
                      <p className="text-xs text-gray-500">Précision</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">
                        {selectedAnalysis.metrics.sensitivity || 'N/A'}%
                      </p>
                      <p className="text-xs text-gray-500">Sensibilité</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">
                        {selectedAnalysis.metrics.specificity || 'N/A'}%
                      </p>
                      <p className="text-xs text-gray-500">Spécificité</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="modal-footer">
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="btn-outline"
              >
                Fermer
              </button>
              {selectedAnalysis.status === 'completed' && (
                <button
                  onClick={() => {/* Navigate to viewer */}}
                  className="btn-primary"
                >
                  Voir en 3D
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analysis; 