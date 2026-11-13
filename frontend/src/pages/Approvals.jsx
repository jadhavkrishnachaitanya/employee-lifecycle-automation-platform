import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { ShieldCheck, Check, X, Clock, AlertCircle } from 'lucide-react';

export function Approvals() {
  const [approvals, setApprovals] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    loadApprovals();
  }, [statusFilter]);

  async function loadApprovals() {
    setLoading(true);
    try {
      const res = await api.getApprovals(statusFilter);
      setApprovals(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleDecision = async (requestId, decision) => {
    setFeedback(null);
    try {
      await api.approveAccessRequest(requestId, decision, `Decision recorded via UI: ${decision}`);
      setFeedback({ type: 'success', text: `Access request ${requestId} was successfully ${decision.toLowerCase()}!` });
      loadApprovals();
    } catch (err) {
      setFeedback({ type: 'error', text: `Failed to record decision: ${err.message}` });
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Filters and counts */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Approval Filter:</span>
          <div className="flex items-center bg-white p-1 rounded-lg border border-slate-200 text-xs shadow-2xs">
            {['', 'PENDING', 'APPROVED', 'REJECTED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-md font-medium transition ${
                  statusFilter === st
                    ? 'bg-indigo-600 text-white shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {st === '' ? 'All Requests' : st}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{approvals.length}</span> approval workflows
        </div>
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

      {/* Approvals Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Approval ID</th>
                <th className="px-6 py-3.5">Access Request ID</th>
                <th className="px-6 py-3.5">Designated Approver</th>
                <th className="px-6 py-3.5">Role Matrix</th>
                <th className="px-6 py-3.5">Decision Timestamp</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    Loading approvals queue...
                  </td>
                </tr>
              ) : approvals.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    No approval records matching filter criteria.
                  </td>
                </tr>
              ) : (
                approvals.map((appr) => {
                  const isPending = appr.status === 'PENDING';
                  return (
                    <tr key={appr.approval_id} className="hover:bg-slate-50/75 transition">
                      <td className="px-6 py-4 font-mono font-bold text-xs text-slate-900">{appr.approval_id}</td>
                      <td className="px-6 py-4 font-mono text-xs text-indigo-600 font-medium">
                        {appr.request_id}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-700">{appr.approver_id}</td>
                      <td className="px-6 py-4">
                        <Badge variant="MANAGER" size="sm">
                          {appr.approver_role}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-500">
                        {appr.decided_at ? appr.decided_at.split('T')[0] : 'Pending Action'}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={appr.status}>{appr.status}</Badge>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {isPending ? (
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleDecision(appr.request_id, 'APPROVED')}
                              className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold flex items-center gap-1 transition shadow-2xs"
                            >
                              <Check className="w-3 h-3" />
                              <span>Approve</span>
                            </button>
                            <button
                              onClick={() => handleDecision(appr.request_id, 'REJECTED')}
                              className="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold flex items-center gap-1 transition shadow-2xs"
                            >
                              <X className="w-3 h-3" />
                              <span>Reject</span>
                            </button>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 italic">Decided</span>
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
    </div>
  );
}
