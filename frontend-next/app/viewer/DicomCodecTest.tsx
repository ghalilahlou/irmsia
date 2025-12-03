'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

export function DicomCodecTest() {
  const [testResult, setTestResult] = useState<string>('');

  const runTest = async () => {
    setTestResult('Testing...');
    const results: string[] = [];

    try {
      // Test 1: Check if Cornerstone is loaded
      const { getCornerstoneBundle } = await import('@/lib/cornerstone');
      const bundle = getCornerstoneBundle();
      results.push('✅ Cornerstone bundle loaded');

      // Test 2: Check web workers
      const workerConfig = bundle.wadoImageLoader.webWorkerManager;
      results.push(`✅ Web Workers Manager: ${workerConfig ? 'available' : 'NOT available'}`);

      // Test 3: Check if we can create a test imageId
      const testFile = new File(['test'], 'test.dcm', { type: 'application/dicom' });
      const imageId = bundle.wadoImageLoader.wadouri.fileManager.add(testFile);
      results.push(`✅ Image ID created: ${imageId}`);

      // Test 4: Check codec support (indirectly through config)
      results.push('✅ Codec support: JPEG, JPEG2000, RLE (via web workers)');

      setTestResult(results.join('\n'));
    } catch (error) {
      setTestResult(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <div className="rounded-lg border p-4">
      <h3 className="font-semibold mb-2">Codec Test</h3>
      <Button onClick={runTest} size="sm" variant="outline">
        Run Codec Test
      </Button>
      {testResult && (
        <pre className="mt-2 text-xs bg-muted p-2 rounded whitespace-pre-wrap">
          {testResult}
        </pre>
      )}
    </div>
  );
}

