'use client';

import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { AlertCircle, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDate } from '@/lib/utils';

interface Finding {
  description: string;
  location?: string;
  severity: 'normal' | 'mild' | 'moderate' | 'severe';
}

interface AnalysisCardProps {
  analysis: {
    image_id: string;
    findings: Finding[];
    risk_score: number;
    suggested_diagnosis: string;
    confidence: number;
    ai_model: string;
    processing_time: number;
    timestamp: string;
    recommendations: string[];
  };
}

const severityConfig = {
  normal: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50' },
  mild: { icon: Info, color: 'text-blue-600', bg: 'bg-blue-50' },
  moderate: { icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50' },
  severe: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
};

export function AnalysisCard({ analysis }: AnalysisCardProps) {
  const riskColor =
    analysis.risk_score < 30
      ? 'text-green-600'
      : analysis.risk_score < 70
      ? 'text-yellow-600'
      : 'text-red-600';

  return (
    <div className="space-y-6">
      {/* Risk Score */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Risk Score</p>
              <p className={cn('text-4xl font-bold', riskColor)}>
                {analysis.risk_score}
              </p>
              <p className="text-xs text-muted-foreground mt-1">out of 100</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Confidence</p>
              <p className="text-2xl font-semibold">
                {(analysis.confidence * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Model: {analysis.ai_model}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Suggested Diagnosis */}
      <Card>
        <CardHeader>
          <CardTitle>Suggested Diagnosis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg">{analysis.suggested_diagnosis}</p>
          <p className="text-xs text-muted-foreground mt-2">
            Analyzed on {formatDate(analysis.timestamp)}
          </p>
        </CardContent>
      </Card>

      {/* Findings */}
      <Card>
        <CardHeader>
          <CardTitle>Findings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analysis.findings.map((finding, index) => {
              const config = severityConfig[finding.severity];
              const Icon = config.icon;
              return (
                <div
                  key={index}
                  className={cn(
                    'flex items-start space-x-3 p-3 rounded-lg',
                    config.bg
                  )}
                >
                  <Icon className={cn('h-5 w-5 mt-0.5', config.color)} />
                  <div className="flex-1">
                    <p className="font-medium">{finding.description}</p>
                    {finding.location && (
                      <p className="text-sm text-muted-foreground">
                        Location: {finding.location}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      Severity: {finding.severity}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {analysis.recommendations.map((rec, index) => (
                <li key={index} className="text-sm">
                  {rec}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

