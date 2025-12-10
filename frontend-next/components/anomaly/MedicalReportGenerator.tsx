'use client';

import React, { useState } from 'react';
import { FileText, Download, Send, User, Calendar, Activity } from 'lucide-react';

interface MedicalReportGeneratorProps {
  result: any;
  originalFile: File | null;
}

export default function MedicalReportGenerator({ result, originalFile }: MedicalReportGeneratorProps) {
  const [report, setReport] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    id: '',
    age: '',
    studyDescription: ''
  });
  
  const handleGenerateReport = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/v1/anomaly/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_id: result.image_id,
          patient_name: patientInfo.name || undefined,
          patient_id: patientInfo.id || undefined,
          patient_age: patientInfo.age ? parseInt(patientInfo.age) : undefined,
          study_description: patientInfo.studyDescription || undefined
        })
      });
      
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Erreur lors de la génération du rapport');
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleDownloadReport = () => {
    if (!report) return;
    
    const reportText = `
RAPPORT MÉDICAL D'ANALYSE D'IMAGERIE
${'='.repeat(60)}

INFORMATIONS PATIENT:
  Nom: ${report.patient_info?.name || 'N/A'}
  ID: ${report.patient_info?.id || 'N/A'}
  Âge: ${report.patient_info?.age || 'N/A'} ans
  Examen: ${report.patient_info?.study_description || 'N/A'}
  
Date du rapport: ${new Date(report.report_date).toLocaleString('fr-FR')}
Image ID: ${report.image_id}

${'='.repeat(60)}

RÉSUMÉ:
${report.summary}

${'='.repeat(60)}

OBSERVATIONS DÉTAILLÉES:
${report.findings.map((f: string, i: number) => `${i + 1}. ${f}`).join('\n')}

${'='.repeat(60)}

MESURES:
${report.measurements}

${'='.repeat(60)}

ÉVALUATION:
  Type d'anomalie: ${report.anomaly_type}
  Niveau de confiance IA: ${(report.confidence * 100).toFixed(1)}%
  Sévérité: ${report.severity}

${'='.repeat(60)}

RECOMMANDATIONS:
${report.recommendations.map((r: string, i: number) => `${i + 1}. ${r}`).join('\n')}

${'='.repeat(60)}

Ce rapport a été généré automatiquement par IA et doit être validé
par un médecin qualifié. Il ne remplace pas un diagnostic médical.

Système: IRMSIA Medical AI Platform
Version: 1.0
`;
    
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `rapport_medical_${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'GRAVE': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'MODÉRÉE': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'LÉGÈRE': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'NORMAL': return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Form pour info patient */}
      {!report && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-cyan-400" />
            Informations Patient (Optionnel)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Nom du patient</label>
              <input
                type="text"
                value={patientInfo.name}
                onChange={(e) => setPatientInfo({ ...patientInfo, name: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                placeholder="Ex: Jean Dupont"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">ID Patient</label>
              <input
                type="text"
                value={patientInfo.id}
                onChange={(e) => setPatientInfo({ ...patientInfo, id: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                placeholder="Ex: P12345"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Âge</label>
              <input
                type="number"
                value={patientInfo.age}
                onChange={(e) => setPatientInfo({ ...patientInfo, age: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                placeholder="Ex: 45"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Type d'examen</label>
              <input
                type="text"
                value={patientInfo.studyDescription}
                onChange={(e) => setPatientInfo({ ...patientInfo, studyDescription: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                placeholder="Ex: IRM cérébrale"
              />
            </div>
          </div>
          
          <button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="mt-6 w-full flex items-center justify-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors font-semibold"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Génération en cours...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5" />
                Générer le Rapport Médical
              </>
            )}
          </button>
        </div>
      )}
      
      {/* Rapport généré */}
      {report && (
        <div className="space-y-4">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg p-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold mb-2">Rapport Médical</h3>
                <div className="text-sm text-gray-400 space-y-1">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {new Date(report.report_date).toLocaleString('fr-FR')}
                  </div>
                  {report.patient_info?.name && (
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      {report.patient_info.name}
                    </div>
                  )}
                </div>
              </div>
              
              <button
                onClick={handleDownloadReport}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors"
              >
                <Download className="w-4 h-4" />
                Télécharger
              </button>
            </div>
          </div>
          
          {/* Sévérité */}
          <div className={`rounded-lg p-4 border ${getSeverityColor(report.severity)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                <span className="font-semibold">Sévérité:</span>
              </div>
              <span className="text-xl font-bold">{report.severity}</span>
            </div>
          </div>
          
          {/* Résumé */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h4 className="font-semibold mb-3 text-lg">Résumé</h4>
            <p className="text-gray-300">{report.summary}</p>
          </div>
          
          {/* Observations */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h4 className="font-semibold mb-3 text-lg">Observations Détaillées</h4>
            <ul className="space-y-2">
              {report.findings.map((finding: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-gray-300">
                  <span className="text-cyan-400 font-medium">{idx + 1}.</span>
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Mesures */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h4 className="font-semibold mb-3 text-lg">Mesures</h4>
            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
              {report.measurements}
            </pre>
          </div>
          
          {/* Recommandations */}
          <div className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-lg p-6">
            <h4 className="font-semibold mb-3 text-lg flex items-center gap-2">
              <Send className="w-5 h-5 text-yellow-400" />
              Recommandations
            </h4>
            <ul className="space-y-2">
              {report.recommendations.map((rec: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-gray-300">
                  <span className="text-yellow-400 font-medium">{idx + 1}.</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Disclaimer */}
          <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-4 text-sm text-gray-400">
            <p className="font-semibold mb-2">⚠️ Avertissement Important:</p>
            <p>
              Ce rapport a été généré automatiquement par intelligence artificielle.
              Il doit être validé par un médecin qualifié et ne remplace en aucun cas
              un diagnostic médical professionnel. En cas de doute, consultez un spécialiste.
            </p>
          </div>
          
          <button
            onClick={() => setReport(null)}
            className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            Générer un nouveau rapport
          </button>
        </div>
      )}
    </div>
  );
}


