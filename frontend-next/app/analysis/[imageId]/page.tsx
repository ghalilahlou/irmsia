'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { dicomAPI, aiAPI } from '@/lib/api';
import { auth } from '@/lib/auth';
import { Navbar } from '@/components/Navbar';
import { DicomPreview } from '@/components/DicomPreview';
import { AnalysisCard } from '@/components/AnalysisCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, RefreshCw } from 'lucide-react';

export default function AnalysisPage() {
  const router = useRouter();
  const params = useParams();
  const imageId = params.imageId as string;
  const [analysisData, setAnalysisData] = useState<any>(null);

  useEffect(() => {
    if (!auth.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const { data: metadata, isLoading: metadataLoading } = useQuery({
    queryKey: ['dicom-metadata', imageId],
    queryFn: () => dicomAPI.getMetadata(imageId),
    enabled: !!imageId,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => aiAPI.analyze(imageId),
    onSuccess: (data) => {
      setAnalysisData(data);
    },
    onError: (error: any) => {
      console.error('Analysis error:', error);
      alert(error.response?.data?.detail || 'Analysis failed');
    },
  });

  const handleAnalyze = () => {
    analyzeMutation.mutate();
  };

  if (!auth.isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">AI Analysis</h1>
            <p className="text-muted-foreground">Image ID: {imageId}</p>
          </div>
          <Button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending}
          >
            {analyzeMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Run Analysis
              </>
            )}
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            {metadataLoading ? (
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-center">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            ) : (
              <DicomPreview
                imageUrl={metadata?.png_url || ''}
                metadata={metadata}
              />
            )}
          </div>

          <div>
            {analysisData ? (
              <AnalysisCard analysis={analysisData} />
            ) : (
              <Card>
                <CardContent className="p-6">
                  <div className="text-center text-muted-foreground">
                    <p>Click "Run Analysis" to analyze this image</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

