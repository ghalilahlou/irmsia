'use client';

import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { formatDate } from '@/lib/utils';
import { Search } from 'lucide-react';
import { useState, useMemo } from 'react';

interface AccessLog {
  image_id: string;
  user_id: string;
  action: string;
  timestamp: string;
  ip_address?: string;
}

interface BlockchainLogTableProps {
  logs: AccessLog[];
}

export function BlockchainLogTable({ logs }: BlockchainLogTableProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = useMemo(() => {
    if (!searchTerm) return logs;
    const term = searchTerm.toLowerCase();
    return logs.filter(
      (log) =>
        log.image_id.toLowerCase().includes(term) ||
        log.user_id.toLowerCase().includes(term) ||
        log.action.toLowerCase().includes(term)
    );
  }, [logs, searchTerm]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Access Audit Logs</CardTitle>
        <div className="relative mt-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Timestamp</th>
                <th className="text-left p-2">Image ID</th>
                <th className="text-left p-2">User</th>
                <th className="text-left p-2">Action</th>
                <th className="text-left p-2">IP Address</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center p-8 text-muted-foreground">
                    No logs found
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log, index) => (
                  <tr key={index} className="border-b hover:bg-muted/50">
                    <td className="p-2">{formatDate(log.timestamp)}</td>
                    <td className="p-2 font-mono text-xs">{log.image_id}</td>
                    <td className="p-2">{log.user_id}</td>
                    <td className="p-2">
                      <span className="px-2 py-1 bg-primary/10 text-primary rounded text-xs">
                        {log.action}
                      </span>
                    </td>
                    <td className="p-2 text-muted-foreground">
                      {log.ip_address || 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

