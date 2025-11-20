import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Layout Components
import Layout from './components/layout/Layout';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

// Page Components
import Dashboard from './pages/Dashboard';
import ImageUpload from './pages/ImageUpload';
import Analysis from './pages/Analysis';
import Viewer3D from './pages/Viewer3D';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { AnalysisProvider } from './contexts/AnalysisContext';
import { ViewerProvider } from './contexts/ViewerContext';

// Styles
import './styles/globals.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AnalysisProvider>
          <ViewerProvider>
            <Router>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/upload" element={<ImageUpload />} />
                  <Route path="/analysis" element={<Analysis />} />
                  <Route path="/viewer" element={<Viewer3D />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                }}
              />
            </Router>
          </ViewerProvider>
        </AnalysisProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App; 