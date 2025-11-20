import React, { useState } from 'react';
import { 
  Cog6ToothIcon,
  UserIcon,
  ShieldCheckIcon,
  BellIcon,
  ComputerDesktopIcon,
  DocumentTextIcon,
  DatabaseIcon,
  ServerIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      language: 'fr',
      theme: 'light',
      timezone: 'Europe/Paris',
      dateFormat: 'DD/MM/YYYY',
    },
    notifications: {
      email: true,
      push: true,
      analysisComplete: true,
      reportReady: true,
      systemAlerts: false,
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 30,
      passwordExpiry: 90,
      loginAttempts: 5,
    },
    performance: {
      autoSave: true,
      cacheSize: 100,
      maxUploadSize: 100,
      enableGPU: true,
    },
    display: {
      showGrid: true,
      showAxes: true,
      defaultOpacity: 0.8,
      defaultColorMap: 'grayscale',
    },
  });

  const tabs = [
    { id: 'general', name: 'Général', icon: Cog6ToothIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Sécurité', icon: ShieldCheckIcon },
    { id: 'performance', name: 'Performance', icon: ComputerDesktopIcon },
    { id: 'display', name: 'Affichage', icon: DocumentTextIcon },
  ];

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const handleSaveSettings = () => {
    // Implementation for saving settings
    console.log('Saving settings:', settings);
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="form-label">Langue</label>
        <select
          value={settings.general.language}
          onChange={(e) => handleSettingChange('general', 'language', e.target.value)}
          className="form-input"
        >
          <option value="fr">Français</option>
          <option value="en">English</option>
          <option value="es">Español</option>
        </select>
      </div>

      <div>
        <label className="form-label">Thème</label>
        <select
          value={settings.general.theme}
          onChange={(e) => handleSettingChange('general', 'theme', e.target.value)}
          className="form-input"
        >
          <option value="light">Clair</option>
          <option value="dark">Sombre</option>
          <option value="auto">Automatique</option>
        </select>
      </div>

      <div>
        <label className="form-label">Fuseau horaire</label>
        <select
          value={settings.general.timezone}
          onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
          className="form-input"
        >
          <option value="Europe/Paris">Europe/Paris</option>
          <option value="UTC">UTC</option>
          <option value="America/New_York">America/New_York</option>
        </select>
      </div>

      <div>
        <label className="form-label">Format de date</label>
        <select
          value={settings.general.dateFormat}
          onChange={(e) => handleSettingChange('general', 'dateFormat', e.target.value)}
          className="form-input"
        >
          <option value="DD/MM/YYYY">DD/MM/YYYY</option>
          <option value="MM/DD/YYYY">MM/DD/YYYY</option>
          <option value="YYYY-MM-DD">YYYY-MM-DD</option>
        </select>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Types de notifications</h4>
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={settings.notifications.email}
              onChange={(e) => handleSettingChange('notifications', 'email', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Notifications par email</span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={settings.notifications.push}
              onChange={(e) => handleSettingChange('notifications', 'push', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Notifications push</span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={settings.notifications.analysisComplete}
              onChange={(e) => handleSettingChange('notifications', 'analysisComplete', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Analyse terminée</span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={settings.notifications.reportReady}
              onChange={(e) => handleSettingChange('notifications', 'reportReady', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Rapport prêt</span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={settings.notifications.systemAlerts}
              onChange={(e) => handleSettingChange('notifications', 'systemAlerts', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Alertes système</span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.security.twoFactorAuth}
            onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Authentification à deux facteurs</span>
        </label>
      </div>

      <div>
        <label className="form-label">Délai d'expiration de session (minutes)</label>
        <input
          type="number"
          value={settings.security.sessionTimeout}
          onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
          className="form-input"
          min="5"
          max="480"
        />
      </div>

      <div>
        <label className="form-label">Expiration du mot de passe (jours)</label>
        <input
          type="number"
          value={settings.security.passwordExpiry}
          onChange={(e) => handleSettingChange('security', 'passwordExpiry', parseInt(e.target.value))}
          className="form-input"
          min="30"
          max="365"
        />
      </div>

      <div>
        <label className="form-label">Tentatives de connexion maximales</label>
        <input
          type="number"
          value={settings.security.loginAttempts}
          onChange={(e) => handleSettingChange('security', 'loginAttempts', parseInt(e.target.value))}
          className="form-input"
          min="3"
          max="10"
        />
      </div>
    </div>
  );

  const renderPerformanceSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.performance.autoSave}
            onChange={(e) => handleSettingChange('performance', 'autoSave', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Sauvegarde automatique</span>
        </label>
      </div>

      <div>
        <label className="form-label">Taille du cache (MB)</label>
        <input
          type="number"
          value={settings.performance.cacheSize}
          onChange={(e) => handleSettingChange('performance', 'cacheSize', parseInt(e.target.value))}
          className="form-input"
          min="50"
          max="1000"
        />
      </div>

      <div>
        <label className="form-label">Taille maximale d'upload (MB)</label>
        <input
          type="number"
          value={settings.performance.maxUploadSize}
          onChange={(e) => handleSettingChange('performance', 'maxUploadSize', parseInt(e.target.value))}
          className="form-input"
          min="10"
          max="500"
        />
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.performance.enableGPU}
            onChange={(e) => handleSettingChange('performance', 'enableGPU', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Accélération GPU</span>
        </label>
      </div>
    </div>
  );

  const renderDisplaySettings = () => (
    <div className="space-y-6">
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.display.showGrid}
            onChange={(e) => handleSettingChange('display', 'showGrid', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Afficher la grille</span>
        </label>
      </div>

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={settings.display.showAxes}
            onChange={(e) => handleSettingChange('display', 'showAxes', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700">Afficher les axes</span>
        </label>
      </div>

      <div>
        <label className="form-label">Opacité par défaut</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={settings.display.defaultOpacity}
          onChange={(e) => handleSettingChange('display', 'defaultOpacity', parseFloat(e.target.value))}
          className="w-full"
        />
        <span className="text-xs text-gray-500">{Math.round(settings.display.defaultOpacity * 100)}%</span>
      </div>

      <div>
        <label className="form-label">Colormap par défaut</label>
        <select
          value={settings.display.defaultColorMap}
          onChange={(e) => handleSettingChange('display', 'defaultColorMap', e.target.value)}
          className="form-input"
        >
          <option value="grayscale">Grayscale</option>
          <option value="hot">Hot</option>
          <option value="cool">Cool</option>
          <option value="rainbow">Rainbow</option>
          <option value="jet">Jet</option>
        </select>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'security':
        return renderSecuritySettings();
      case 'performance':
        return renderPerformanceSettings();
      case 'display':
        return renderDisplaySettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Paramètres</h1>
        <p className="text-gray-600">Configurez votre application</p>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5 inline mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {renderTabContent()}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end space-x-3">
            <button className="btn-outline">
              Réinitialiser
            </button>
            <button
              onClick={handleSaveSettings}
              className="btn-primary"
            >
              Enregistrer
            </button>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="mt-8 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Informations système</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Application</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Version:</span>
                  <span>1.0.0</span>
                </div>
                <div className="flex justify-between">
                  <span>Build:</span>
                  <span>2024.01.15</span>
                </div>
                <div className="flex justify-between">
                  <span>Environnement:</span>
                  <span>Production</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Système</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Navigateur:</span>
                  <span>Chrome 120.0</span>
                </div>
                <div className="flex justify-between">
                  <span>Système:</span>
                  <span>Windows 11</span>
                </div>
                <div className="flex justify-between">
                  <span>Résolution:</span>
                  <span>1920×1080</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 