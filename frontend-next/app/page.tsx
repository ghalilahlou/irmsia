'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/auth';

const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Si l'authentification est désactivée, aller directement au dashboard
    if (!AUTH_ENABLED) {
      router.push('/dashboard');
    } else if (auth.isAuthenticated()) {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return null;
}

