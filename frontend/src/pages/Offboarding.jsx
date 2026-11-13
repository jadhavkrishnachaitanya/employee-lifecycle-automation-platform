import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { UserX, ShieldAlert, CheckCircle2, AlertOctagon, Plus, X } from 'lucide-react';

export function Offboarding() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    employee_id: 'EMP-000001',
    reason: 'RESIGNATION',
    termination_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadOffboarding();
  }, []);

  async function loadOffboarding() {
    setLoading(true);
    try {
      const res = await api.getOffboardingCases();
      setCases(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleRevoke = async (offboardingId) => {
    setFeedback(null);
    try {
      await api.revokeOffboardingAccess(offboardingId);
      setFeedback({
        type: 'success',
        text: `Success: All active entitlements for case ${offboardingId} were permanently revoked and audit logged.`,
      });
      loadOffboarding();
    } catch (err) {
      setFeedback({ type: 'error', text: `Revocation failed: ${err.message}` });
    }
  };

  const handleInitiateSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    try {
      await api.initiateOffboarding({
        ...form,
        termination_date: new Date(form.termination_date).toISOString(),
      });
      setShowModal(false);
      setFeedback({ type: 'success', text: `Offboarding initiated for ${form.employee_id}.` });
      loadOffboarding();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top action header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">Offboarding & Zero-Trust Access Revocation</h2>
          <p className="text-xs text-slate-500">
            Enforces complete separation of credentials, reconciliation of physical hardware, and exit auditability.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          <span>Initiate Offboarding</span>
        </button>
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
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{feedback.text}</span>
        </div>
      )}

      {/* Offboarding Cases Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Case ID</th>
                <th className="px-6 py-3.5">Employee ID</th>
                <th className="px-6 py-3.5">Exit Reason</th>
                <th className="px-6 py-3.5">Effective Exit Date</th>
                <th className="px-6 py-3.5">Revocation Status</th>
                <th className="px-6 py-3.5">Asset Recovery</th>
                <th className="px-6 py-3.5">Workflow Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-slate-400">
                    Loading exit workflows...
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-slate-400">
                    No active offboarding cases.
                  </td>
                </tr>
              ) : (
                cases.map((off) => {
                  const hasOpenAccess = off.access_revocation_status === 'PENDING';
                  return (
                    <tr key={off.offboarding_id} className="hover:bg-slate-50/75 transition">
                      <td className="px-6 py-4 font-mono font-bold text-xs text-slate-900">{off.offboarding_id}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">{off.employee_id}</td>
                      <td className="px-6 py-4 text-xs font-medium text-slate-800">{off.reason}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">
                        {off.termination_date?.split('T')[0]}
                      </td>
                      <td className="px-6 py-4">
                        {hasOpenAccess ? (
                          <Badge variant="danger" size="sm">
                            Access Retained (Anomaly #5)
                          </Badge>
                        ) : (
                          <Badge variant="success" size="sm">
                            All Revoked
                          </Badge>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant="default" size="sm">
                          {off.asset_recovery_status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={off.status}>{off.status}</Badge>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {hasOpenAccess ? (
                          <button
                            onClick={() => handleRevoke(off.offboarding_id)}
                            className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold shadow-2xs transition"
                          >
                            Revoke All Credentials
                          </button>
                        ) : (
                          <span className="text-xs text-slate-400 italic">Reconciled</span>
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

      {/* Initiate Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-sm font-bold text-slate-900">Initiate Employee Termination</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleInitiateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-medium mb-1">Employee ID</label>
                <input
                  type="text"
                  required
                  value={form.employee_id}
                  onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono"
                  placeholder="EMP-000001"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Separation Reason</label>
                <select
                  value={form.reason}
                  onChange={(e) => setForm({ ...form, reason: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                >
                  <option value="RESIGNATION">Voluntary Resignation</option>
                  <option value="TERMINATION">Involuntary Termination</option>
                  <option value="CONTRACT_END">Contract Expiration</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Effective Separation Date</label>
                <input
                  type="date"
                  required
                  value={form.termination_date}
                  onChange={(e) => setForm({ ...form, termination_date: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-medium shadow-xs"
                >
                  Execute Termination
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
