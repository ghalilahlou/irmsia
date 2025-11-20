'use client';

// Component to debug API connection
export function DebugAPI() {
  const testConnection = async () => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      // Test health endpoint
      const healthResponse = await fetch(`${API_URL}/health`);
      const healthData = await healthResponse.json();
      console.log('Health check:', healthData);
      
      // Test login endpoint
      const formData = new URLSearchParams();
      formData.append('username', 'admin');
      formData.append('password', 'admin123');
      
      const loginResponse = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });
      
      const loginData = await loginResponse.json();
      console.log('Login test:', loginData);
      
      alert(`Health: ${healthResponse.ok ? 'OK' : 'FAIL'}\nLogin: ${loginResponse.ok ? 'OK' : 'FAIL'}\nCheck console for details`);
    } catch (error) {
      console.error('Debug error:', error);
      alert('Erreur de connexion. Vérifiez la console.');
    }
  };

  return (
    <button
      onClick={testConnection}
      className="fixed bottom-4 left-4 bg-gray-500 text-white px-4 py-2 rounded text-sm"
    >
      Debug API
    </button>
  );
}


