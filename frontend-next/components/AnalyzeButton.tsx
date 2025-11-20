'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { medicalAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, Loader2, FileText } from 'lucide-react';
import { useToast } from '@/components/ToastProvider';

interface AnalyzeButtonProps {
  filename: string;
}

export function AnalyzeButton({ filename }: AnalyzeButtonProps) {
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const { showToast } = useToast();

  const analyzeMutation = useMutation({
    mutationFn: async (filename: string) => {
      return medicalAPI.analyzeImage(filename);
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      showToast('L\'analyse LLM a été effectuée avec succès', 'success');
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Erreur lors de l\'analyse', 'error');
    },
  });

  const handleAnalyze = () => {
    if (!filename) {
      showToast('Veuillez sélectionner une image', 'error');
      return;
    }
    analyzeMutation.mutate(filename);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          Analyse LLM
        </CardTitle>
        <CardDescription>
          Analysez l'image sélectionnée avec l'IA
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button
          onClick={handleAnalyze}
          disabled={analyzeMutation.isPending || !filename}
          className="w-full"
        >
          {analyzeMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Analyse en cours...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Analyser avec IA
            </>
          )}
        </Button>

        {analysisResult && (
          <div className="mt-4 p-4 bg-muted rounded-lg space-y-3">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="font-semibold">Résultats de l'analyse</span>
            </div>
            
            {analysisResult.analysis && (
              <>
                {analysisResult.analysis.findings && (
                  <div>
                    <h4 className="font-medium mb-2">Findings:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {analysisResult.analysis.findings.map((finding: string, idx: number) => (
                        <li key={idx}>{finding}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {analysisResult.analysis.risk_score !== undefined && (
                  <div>
                    <h4 className="font-medium mb-1">Score de risque:</h4>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-background rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ width: `${analysisResult.analysis.risk_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">
                        {analysisResult.analysis.risk_score}/100
                      </span>
                    </div>
                  </div>
                )}

                {analysisResult.analysis.diagnosis_suggestion && (
                  <div>
                    <h4 className="font-medium mb-1">Suggestion de diagnostic:</h4>
                    <p className="text-sm">{analysisResult.analysis.diagnosis_suggestion}</p>
                  </div>
                )}

                {analysisResult.analysis.recommendations && (
                  <div>
                    <h4 className="font-medium mb-2">Recommandations:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {analysisResult.analysis.recommendations.map((rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {analysisResult.message && (
              <div className="text-sm text-muted-foreground italic">
                {analysisResult.message}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

