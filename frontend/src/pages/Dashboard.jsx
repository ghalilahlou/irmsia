import React from 'react';
import { 
  ChartBarIcon, 
  DocumentTextIcon, 
  ClockIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const stats = [
    {
      name: 'Analyses en cours',
      value: '12',
      change: '+2',
      changeType: 'increase',
      icon: ClockIcon,
    },
    {
      name: 'Analyses terminées',
      value: '156',
      change: '+23',
      changeType: 'increase',
      icon: CheckCircleIcon,
    },
    {
      name: 'Rapports générés',
      value: '89',
      change: '+12',
      changeType: 'increase',
      icon: DocumentTextIcon,
    },
    {
      name: 'Images traitées',
      value: '1,234',
      change: '+156',
      changeType: 'increase',
      icon: ChartBarIcon,
    },
  ];

  const recentAnalyses = [
    {
      id: 1,
      patient: 'Jean Dupont',
      study: 'IRM Cérébrale',
      status: 'completed',
      date: '2024-01-15',
      time: '14:30',
    },
    {
      id: 2,
      patient: 'Marie Martin',
      study: 'CT Thorax',
      status: 'processing',
      date: '2024-01-15',
      time: '13:45',
    },
    {
      id: 3,
      patient: 'Pierre Durand',
      study: 'IRM Abdominale',
      status: 'pending',
      date: '2024-01-15',
      time: '12:20',
    },
  ];

  const alerts = [
    {
      id: 1,
      type: 'warning',
      message: 'Modèle IA nécessite une mise à jour',
      time: '2 heures ago',
    },
    {
      id: 2,
      type: 'info',
      message: 'Nouvelle fonctionnalité 3D disponible',
      time: '1 jour ago',
    },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
      default:
        return 'Inconnu';
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="text-gray-600">Vue d'ensemble de vos analyses médicales</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-8 w-8 text-gray-400" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
            <div className="mt-4">
              <span className={`text-sm font-medium ${
                stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.change}
              </span>
              <span className="text-sm text-gray-500 ml-1">vs hier</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Analyses */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Analyses récentes</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {recentAnalyses.map((analysis) => (
              <div key={analysis.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{analysis.patient}</p>
                    <p className="text-sm text-gray-500">{analysis.study}</p>
                    <p className="text-xs text-gray-400">{analysis.date} à {analysis.time}</p>
                  </div>
                  <div className="ml-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(analysis.status)}`}>
                      {getStatusText(analysis.status)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Alertes</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div key={alert.id} className="px-6 py-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    {alert.type === 'warning' ? (
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                    ) : (
                      <InformationCircleIcon className="h-5 w-5 text-blue-400" />
                    )}
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="text-sm text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Actions rapides</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <CloudArrowUpIcon className="h-5 w-5 mr-2" />
              Upload d'images
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <CubeIcon className="h-5 w-5 mr-2" />
              Visualisation 3D
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Générer rapport
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 