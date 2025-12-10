/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export for lightweight frontend
  output: 'standalone',
  
  // Disable SSR where not needed
  reactStrictMode: true,
  
  // Allow cross-origin requests from network IPs (for development)
  allowedDevOrigins: ['10.40.38.181', '10.5.0.2', 'localhost', '127.0.0.1'],

  // Webpack config for Cornerstone workers
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Make sure cornerstone wado loader workers are available
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
      };
    }
    
    // Désactiver le cache webpack pour éviter les erreurs de mémoire
    config.cache = false;
    
    return config;
  },
  
  // API proxy - routes /api/* to backend
  // This allows the frontend to work with both localhost and network IP access
  // In Docker, use http://backend:8000 for internal communication
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 
                   (process.env.NODE_ENV === 'production' ? 'http://backend:8000' : 'http://localhost:8000');
    return [
      {
        source: '/api/:path*',
        // Keep /api in the destination since backend routes are at /api/v1/*
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  
  // Images configuration - allow images from API
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/api/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/api/**',
      },
      {
        protocol: 'http',
        hostname: '10.5.0.2',
        port: '8000',
        pathname: '/api/**',
      },
    ],
    unoptimized: true, // Disable optimization for API images
  },
  
  // Security headers
  async headers() {
    // Get API URL from environment or default to localhost:8000
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            // Allow connections to backend API (localhost and network IP)
            // Support both localhost and network IP access (10.5.0.2, etc.)
            // data: and blob: are required for Cornerstone web workers WASM loading
            value: `default-src 'self'; connect-src 'self' data: blob: ${apiUrl} http://localhost:8000 http://10.5.0.2:8000 http://127.0.0.1:8000 ws://localhost:* ws://10.5.0.2:*; script-src 'self' 'unsafe-eval' 'unsafe-inline' blob:; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: ${apiUrl} http://localhost:8000 http://10.5.0.2:8000 http://127.0.0.1:8000; font-src 'self' data:; worker-src 'self' blob:;`,
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

