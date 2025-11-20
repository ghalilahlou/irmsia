'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { dicomAPI } from '@/lib/api';
import { auth } from '@/lib/auth';
import { Navbar } from '@/components/Navbar';
import { Dropzone } from '@/components/Dropzone';
import { DicomPreview } from '@/components/DicomPreview';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Loader2 } from 'lucide-react';
import { formatFileSize } from '@/lib/utils';

export default function UploadPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  useEffect(() => {
    if (!auth.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const uploadMutation = useMutation({
    mutationFn: (file: File) => dicomAPI.upload(file),
    onSuccess: (data) => {
      setUploadResult(data);
    },
    onError: (error: any) => {
      console.error('Upload error:', error);
      alert(error.response?.data?.detail || 'Upload failed');
    },
  });

  const handleFileAccepted = (file: File) => {
    setSelectedFile(file);
    setUploadResult(null);
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleViewAnalysis = () => {
    if (uploadResult?.image_id) {
      router.push(`/analysis/${uploadResult.image_id}`);
    }
  };

  if (!auth.isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Upload DICOM</h1>
          <p className="text-muted-foreground">
            Upload a DICOM file for AI analysis
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>File Upload</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Dropzone onFileAccepted={handleFileAccepted} />
              {selectedFile && (
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              <Button
                onClick={handleUpload}
                disabled={!selectedFile || uploadMutation.isPending}
                className="w-full"
              >
                {uploadMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload & Process
                  </>
                )}
              </Button>
              {uploadResult && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm font-medium text-green-800 mb-2">
                    Upload successful!
                  </p>
                  <p className="text-xs text-green-700 mb-4">
                    Image ID: {uploadResult.image_id}
                  </p>
                  <Button
                    onClick={handleViewAnalysis}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    View Analysis
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {uploadResult?.png_url && (
            <DicomPreview
              imageUrl={uploadResult.png_url}
              metadata={uploadResult.metadata}
            />
          )}
        </div>
      </div>
    </div>
  );
}

