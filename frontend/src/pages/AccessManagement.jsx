import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { KeyRound, Plus, ShieldCheck, Check, AlertTriangle, X } from 'lucide-react';

export function AccessManagement() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  // New Request Modal
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    employee_id: 'EMP-000001',
    system_name: 'GITHUB',
    access_level: 'WRITE',
    justification: 'Need repository commit access for engineering roadmap',
  });

  useEffect(() => {
    loadRequests();
  }, []);

  async function loadRequests() {
    setLoading(true);
    try {
      const res = await api.getAccessRequests({ limit: 100 });
      setRequests(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleProvision = async (requestId) => {
    setFeedback(null);
    try {
      const grant = await api.provisionAccessRequest(requestId);
      setFeedback({
        type: 'success',
        text: `Success: System access grant ${grant.grant_id} provisioned at level ${grant.access_level}!`,
      });
      loadRequests();
    } catch (err) {
      setFeedback({ type: 'error', text: `Provisioning Blocked: ${err.message}` });
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    try {
      await api.createAccessRequest(form);
      setShowModal(false);
      setFeedback({ type: 'success', text: 'New access request submitted and pending approval.' });
      loadRequests();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Banner and Actions */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">Enterprise Entitlements & Access Grants</h2>
          <p className="text-xs text-slate-500">
            Strict two-phase commit: Requests must receive affirmative approval before provisioning active credentials.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          <span>Request Entitlement</span>
        </button>
      </div>

      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs font-medium ${
            feedback.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {feedback.text}
        </div>
      )}

      {/* Access Requests Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Request ID</th>
                <th className="px-6 py-3.5">Employee ID</th>
                <th className="px-6 py-3.5">Target System</th>
                <th className="px-6 py-3.5">Access Level</th>
                <th className="px-6 py-3.5">Request Status</th>
                <th className="px-6 py-3.5">Active Grant ID</th>
                <th className="px-6 py-3.5 text-right">Provision Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    Loading access requests...
                  </td>
                </tr>
              ) : requests.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    No access requests registered.
                  </td>
                </tr>
              ) : (
                requests.map((req) => {
                  const grant = req.grants && req.grants[0];
                  const canProvision = req.status === 'APPROVED';

                  return (
                    <tr key={req.request_id} className="hover:bg-slate-50/75 transition">
                      <td className="px-6 py-4 font-mono font-bold text-xs text-slate-900">{req.request_id}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">{req.employee_id}</td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-xs text-slate-800">{req.system_name}</span>
                        <div className="text-[11px] text-slate-400 truncate max-w-xs">{req.justification}</div>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-700">{req.access_level}</td>
                      <td className="px-6 py-4">
                        <Badge variant={req.status}>{req.status}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        {grant ? (
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-xs text-emerald-700 font-semibold">{grant.grant_id}</span>
                            <Badge variant={grant.status} size="sm">
                              {grant.status}
                            </Badge>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 italic">None</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {canProvision ? (
                          <button
                            onClick={() => handleProvision(req.request_id)}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold transition shadow-2xs"
                          >
                            Provision Access
                          </button>
                        ) : req.status === 'REQUESTED' ? (
                          <span className="text-xs text-amber-600 font-medium">Pending Approval</span>
                        ) : req.status === 'PROVISIONED' ? (
                          <span className="text-xs text-emerald-600 font-medium">Provisioned</span>
                        ) : (
                          <span className="text-xs text-slate-400 italic">{req.status}</span>
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

      {/* New Request Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-base font-bold text-slate-900">Submit Entitlement Request</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-medium mb-1">Employee ID</label>
                <input
                  type="text"
                  required
                  value={form.employee_id}
                  onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-medium mb-1">System Name</label>
                  <select
                    value={form.system_name}
                    onChange={(e) => setForm({ ...form, system_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                  >
                    <option value="EMAIL_SLACK">EMAIL_SLACK</option>
                    <option value="GITHUB">GITHUB</option>
                    <option value="AWS_CLOUD">AWS_CLOUD</option>
                    <option value="JIRA_CONFLUENCE">JIRA_CONFLUENCE</option>
                    <option value="ERP_FINANCE">ERP_FINANCE</option>
                    <option value="HRIS">HRIS</option>
                    <option value="VPN_INTERNAL">VPN_INTERNAL</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Access Level</label>
                  <select
                    value={form.access_level}
                    onChange={(e) => setForm({ ...form, access_level: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                  >
                    <option value="READ">READ</option>
                    <option value="WRITE">WRITE</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Business Justification</label>
                <textarea
                  required
                  rows="3"
                  value={form.justification}
                  onChange={(e) => setForm({ ...form, justification: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium shadow-xs"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
