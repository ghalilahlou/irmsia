'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from './ui/button';
import { auth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { LogOut, Activity, Upload, FileText, Shield } from 'lucide-react';

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const isAuthenticated = auth.isAuthenticated();

  const handleLogout = () => {
    auth.removeToken();
    router.push('/login');
  };

  if (!isAuthenticated || pathname === '/login') {
    return null;
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: Activity },
    { href: '/medical', label: 'Analyse Médicale', icon: Upload },
    { href: '/logs', label: 'Audit Logs', icon: Shield },
  ];

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/dashboard" className="mr-6 flex items-center space-x-2">
            <Activity className="h-6 w-6" />
            <span className="font-bold">IRMSIA</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center space-x-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-1 text-sm font-medium transition-colors hover:text-foreground/80 ${
                  isActive
                    ? 'text-foreground'
                    : 'text-foreground/60'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </nav>
  );
}

