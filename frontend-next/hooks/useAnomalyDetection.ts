import { useState, useCallback } from 'react';

interface AnomalyDetectionResult {
  has_anomaly: boolean;
  anomaly_class: string;
  confidence: number;
  bounding_boxes?: any[];
  segmentation_mask?: any;
  visualization?: any;
  measurements?: any;
  image_id?: string;
  filename?: string;
  timestamp?: string;
}

interface UseAnomalyDetectionReturn {
  isAnalyzing: boolean;
  error: string | null;
  result: AnomalyDetectionResult | null;
  analyzeImage: (file: File) => Promise<void>;
  reset: () => void;
}

export function useAnomalyDetection(): UseAnomalyDetectionReturn {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnomalyDetectionResult | null>(null);

  const analyzeImage = useCallback(async (file: File) => {
    setError(null);
    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('return_visualization', 'true');
      formData.append('return_segmentation', 'true');
      
      const response = await fetch('/api/v1/anomaly/detect', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText || response.statusText}`);
      }
      
      const data = await response.json();
      setResult(data);
      
      if (data.has_anomaly) {
        console.log(`⚠️ Anomalie détectée: ${data.anomaly_class} (${(data.confidence * 100).toFixed(1)}%)`);
      } else {
        console.log('✅ Aucune anomalie détectée');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur inconnue lors de l\'analyse';
      console.error('Erreur lors de l\'analyse:', err);
      setError(errorMessage);
      setResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setIsAnalyzing(false);
  }, []);

  return {
    isAnalyzing,
    error,
    result,
    analyzeImage,
    reset,
  };
}

