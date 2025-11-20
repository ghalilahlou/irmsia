import React, { useState } from 'react';
import { 
  DocumentTextIcon,
  DocumentArrowDownIcon,
  PlusIcon,
  EyeIcon,
  TrashIcon,
  CalendarIcon,
  UserIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const Reports = () => {
  const [reports, setReports] = useState([
    {
      id: 1,
      title: 'Rapport IRM Cérébrale - Jean Dupont',
      patientName: 'Jean Dupont',
      studyType: 'IRM Cérébrale',
      createdAt: '2024-01-15T14:30:00Z',
      status: 'completed',
      format: 'pdf',
      size: '2.3 MB',
      analysisId: 1,
    },
    {
      id: 2,
      title: 'Rapport CT Thorax - Marie Martin',
      patientName: 'Marie Martin',
      studyType: 'CT Thorax',
      createdAt: '2024-01-15T13:45:00Z',
      status: 'completed',
      format: 'pdf',
      size: '1.8 MB',
      analysisId: 2,
    },
    {
      id: 3,
      title: 'Rapport IRM Abdominale - Pierre Durand',
      patientName: 'Pierre Durand',
      studyType: 'IRM Abdominale',
      createdAt: '2024-01-15T12:20:00Z',
      status: 'generating',
      format: 'pdf',
      size: null,
      analysisId: 3,
    },
  ]);

  const [selectedReport, setSelectedReport] = useState(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);

  const handleGenerateReport = async (analysisId, options) => {
    setGeneratingReport(true);
    
    // Simulate report generation
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const newReport = {
      id: Date.now(),
      title: `Rapport - Analyse ${analysisId}`,
      patientName: 'Nouveau Patient',
      studyType: 'IRM',
      createdAt: new Date().toISOString(),
      status: 'completed',
      format: options.format || 'pdf',
      size: '2.1 MB',
      analysisId,
    };
    
    setReports(prev => [newReport, ...prev]);
    setGeneratingReport(false);
    setShowGenerateModal(false);
  };

  const handleDownloadReport = (report) => {
    // Implementation for report download
    console.log(`Downloading report ${report.id}`);
  };

  const handleDeleteReport = (reportId) => {
    setReports(prev => prev.filter(r => r.id !== reportId));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'generating':
        return 'status-processing';
      case 'error':
        return 'status-error';
      default:
        return 'status-pending';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'generating':
        return 'Génération en cours';
      case 'error':
        return 'Erreur';
      default:
        return 'En attente';
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Rapports</h1>
            <p className="text-gray-600">Gérez vos rapports d'analyse médicale</p>
          </div>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="btn-primary"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Générer un rapport
          </button>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Rapports ({reports.length})
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {reports.map((report) => (
            <div key={report.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {report.title}
                    </p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <UserIcon className="h-4 w-4 mr-1" />
                        {report.patientName}
                      </span>
                      <span className="flex items-center">
                        <ChartBarIcon className="h-4 w-4 mr-1" />
                        {report.studyType}
                      </span>
                      <span className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        {new Date(report.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`status-badge ${getStatusColor(report.status)}`}>
                    {getStatusText(report.status)}
                  </span>
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => setSelectedReport(report)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Voir les détails"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    
                    {report.status === 'completed' && (
                      <button
                        onClick={() => handleDownloadReport(report)}
                        className="p-1 text-blue-400 hover:text-blue-600"
                        title="Télécharger"
                      >
                        <DocumentArrowDownIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleDeleteReport(report.id)}
                      className="p-1 text-red-400 hover:text-red-600"
                      title="Supprimer"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Progress Bar for Generating */}
              {report.status === 'generating' && (
                <div className="mt-3">
                  <div className="progress">
                    <div className="progress-primary" style={{ width: '60%' }} />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Génération en cours...
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="modal-header">
              <h3 className="text-lg font-medium text-gray-900">
                Générer un rapport
              </h3>
              <button
                onClick={() => setShowGenerateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <TrashIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="space-y-4">
                <div>
                  <label className="form-label">Analyse</label>
                  <select className="form-input">
                    <option value="">Sélectionner une analyse</option>
                    <option value="1">IRM Cérébrale - Jean Dupont</option>
                    <option value="2">CT Thorax - Marie Martin</option>
                    <option value="3">IRM Abdominale - Pierre Durand</option>
                  </select>
                </div>
                
                <div>
                  <label className="form-label">Format</label>
                  <select className="form-input">
                    <option value="pdf">PDF</option>
                    <option value="html">HTML</option>
                    <option value="docx">DOCX</option>
                  </select>
                </div>
                
                <div>
                  <label className="form-label">Options</label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Inclure les images</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Inclure les métriques</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Inclure les recommandations</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button
                onClick={() => setShowGenerateModal(false)}
                className="btn-outline"
              >
                Annuler
              </button>
              <button
                onClick={() => handleGenerateReport(1, { format: 'pdf' })}
                disabled={generatingReport}
                className="btn-primary"
              >
                {generatingReport ? (
                  <>
                    <div className="spinner-sm mr-2" />
                    Génération...
                  </>
                ) : (
                  'Générer'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Details Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
            <div className="modal-header">
              <h3 className="text-lg font-medium text-gray-900">
                Détails du rapport
              </h3>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <TrashIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Titre</p>
                  <p className="text-sm text-gray-900">{selectedReport.title}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Patient</p>
                  <p className="text-sm text-gray-900">{selectedReport.patientName}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Type d'étude</p>
                  <p className="text-sm text-gray-900">{selectedReport.studyType}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Format</p>
                  <p className="text-sm text-gray-900">{selectedReport.format.toUpperCase()}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Taille</p>
                  <p className="text-sm text-gray-900">{selectedReport.size || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Date de création</p>
                  <p className="text-sm text-gray-900">
                    {new Date(selectedReport.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Contenu du rapport</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li>• Résumé de l'analyse</li>
                    <li>• Images médicales</li>
                    <li>• Métriques de performance</li>
                    <li>• Recommandations cliniques</li>
                    <li>• Annexes techniques</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button
                onClick={() => setSelectedReport(null)}
                className="btn-outline"
              >
                Fermer
              </button>
              {selectedReport.status === 'completed' && (
                <button
                  onClick={() => handleDownloadReport(selectedReport)}
                  className="btn-primary"
                >
                  Télécharger
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports; 