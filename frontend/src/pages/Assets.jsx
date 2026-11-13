import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { Laptop, AlertTriangle, Check, RefreshCw, X, ShieldAlert } from 'lucide-react';

export function Assets() {
  const [assets, setAssets] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  // Assign Modal
  const [assignModalAsset, setAssignModalAsset] = useState(null);
  const [assignEmpId, setAssignEmpId] = useState('EMP-000001');

  useEffect(() => {
    loadAssets();
  }, [categoryFilter, statusFilter]);

  async function loadAssets() {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (categoryFilter) params.category = categoryFilter;
      if (statusFilter) params.status = statusFilter;
      const res = await api.getAssets(params);
      setAssets(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    try {
      await api.assignAsset(assignModalAsset.asset_id, assignEmpId);
      setFeedback({
        type: 'success',
        text: `Asset ${assignModalAsset.asset_tag} successfully assigned to ${assignEmpId}.`,
      });
      setAssignModalAsset(null);
      loadAssets();
    } catch (err) {
      setFeedback({
        type: 'error',
        text: `Assignment Blocked by Policy: ${err.message}`,
      });
    }
  };

  const handleRecover = async (assetId) => {
    setFeedback(null);
    try {
      await api.recoverAsset(assetId, 'Recovered via Facilities Portal');
      setFeedback({ type: 'success', text: `Asset ${assetId} recovered and marked AVAILABLE.` });
      loadAssets();
    } catch (err) {
      setFeedback({ type: 'error', text: `Recovery error: ${err.message}` });
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header filters */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700"
          >
            <option value="">All Categories (Laptop, Monitor, etc.)</option>
            <option value="LAPTOP">Laptops</option>
            <option value="MONITOR">Monitors</option>
            <option value="SECURITY_KEY">Security Keys (FIPS)</option>
            <option value="MOBILE_PHONE">Mobile Phones</option>
            <option value="HEADSET">Headsets</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">Available</option>
            <option value="ASSIGNED">Assigned</option>
          </select>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{assets.length}</span> devices (600 Total Fleet)
        </div>
      </div>

      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs font-medium flex items-center gap-2 ${
            feedback.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {feedback.type === 'success' ? (
            <Check className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{feedback.text}</span>
        </div>
      )}

      {/* Assets Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Asset Tag & ID</th>
                <th className="px-6 py-3.5">Hardware Model</th>
                <th className="px-6 py-3.5">Category</th>
                <th className="px-6 py-3.5">Serial Number</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    Scanning hardware inventory...
                  </td>
                </tr>
              ) : assets.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    No hardware assets found matching criteria.
                  </td>
                </tr>
              ) : (
                assets.map((asset) => {
                  const isAssigned = asset.status === 'ASSIGNED';
                  return (
                    <tr key={asset.asset_id} className="hover:bg-slate-50/75 transition">
                      <td className="px-6 py-4">
                        <div className="font-bold text-xs font-mono text-slate-900">{asset.asset_tag}</div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5">{asset.asset_id}</div>
                      </td>
                      <td className="px-6 py-4 font-medium text-xs text-slate-800">{asset.model}</td>
                      <td className="px-6 py-4">
                        <Badge variant="FACILITIES" size="sm">
                          {asset.category}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-500">{asset.serial_number}</td>
                      <td className="px-6 py-4">
                        <Badge variant={isAssigned ? 'primary' : 'success'}>{asset.status}</Badge>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {isAssigned ? (
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => {
                                setAssignModalAsset(asset);
                                setAssignEmpId('EMP-000002');
                              }}
                              className="px-2.5 py-1 text-slate-500 hover:text-amber-700 hover:bg-amber-50 rounded text-xs transition"
                              title="Attempting assignment on an already-assigned device tests the double assignment guard!"
                            >
                              Test Overlap
                            </button>
                            <button
                              onClick={() => handleRecover(asset.asset_id)}
                              className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded text-xs transition"
                            >
                              Recover
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => {
                              setAssignModalAsset(asset);
                              setAssignEmpId('EMP-000001');
                            }}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded text-xs shadow-2xs transition"
                          >
                            Assign Asset
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assign Modal */}
      {assignModalAsset && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-bold text-slate-900">
                Assign {assignModalAsset.asset_tag}
              </h3>
              <button onClick={() => setAssignModalAsset(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-medium mb-1">Target Employee ID</label>
                <input
                  type="text"
                  required
                  value={assignEmpId}
                  onChange={(e) => setAssignEmpId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono"
                  placeholder="EMP-000001"
                />
              </div>

              {assignModalAsset.status === 'ASSIGNED' && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-xs">
                  <span className="font-semibold block mb-0.5">Double-Assignment Guard:</span>
                  This device is currently assigned. Submitting will trigger the policy check to prevent overlapping active assignments.
                </div>
              )}

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setAssignModalAsset(null)}
                  className="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAssignSubmit}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium shadow-xs"
                >
                  Confirm Allocation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
