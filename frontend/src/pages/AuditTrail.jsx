import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { History, Search, Filter, ShieldCheck, Eye, X } from 'lucide-react';

export function AuditTrail() {
  const [events, setEvents] = useState([]);
  const [entityFilter, setEntityFilter] = useState('');
  const [actorFilter, setActorFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    loadEvents();
  }, [entityFilter, actorFilter]);

  async function loadEvents() {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (entityFilter) params.entity_type = entityFilter;
      if (actorFilter) params.actor = actorFilter;
      const res = await api.getAuditEvents(params);
      setEvents(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700"
          >
            <option value="">All Entity Types</option>
            <option value="Employee">Employee</option>
            <option value="TaskInstance">Task Instance</option>
            <option value="OnboardingCase">Onboarding Case</option>
            <option value="AccessGrant">Access Grant</option>
            <option value="AccessRequest">Access Request</option>
            <option value="Asset">Asset</option>
            <option value="AssetAssignment">Asset Assignment</option>
          </select>

          <input
            type="text"
            placeholder="Filter by Actor (e.g. HR_ADMIN, IT_ADMIN)..."
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-800 focus:outline-none"
          />
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{events.length}</span> immutable audit records
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Audit ID</th>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5">Entity Type & ID</th>
                <th className="px-6 py-3.5">Action Executed</th>
                <th className="px-6 py-3.5">Authorized Actor</th>
                <th className="px-6 py-3.5">Business Reason</th>
                <th className="px-6 py-3.5 text-right">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    Loading audit ledger...
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    No audit records matching filter.
                  </td>
                </tr>
              ) : (
                events.map((evt) => (
                  <tr key={evt.audit_id} className="hover:bg-slate-50/75 transition">
                    <td className="px-6 py-4 font-mono font-bold text-xs text-slate-900">{evt.audit_id}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-500">
                      {evt.timestamp ? evt.timestamp.replace('T', ' ').slice(0, 19) : ''}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-xs text-slate-800">{evt.entity_type}</div>
                      <div className="text-[11px] font-mono text-indigo-600 mt-0.5">{evt.entity_id}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs font-semibold text-slate-700">
                      {evt.action}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-xs text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                        {evt.actor}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-600 truncate max-w-xs">{evt.reason || '-'}</td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedEvent(evt)}
                        className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        Inspect Diff
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspect Event Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Audit Snapshot: {selectedEvent.audit_id}
                </h3>
                <span className="text-[11px] text-slate-500">
                  {selectedEvent.action} on {selectedEvent.entity_type} ({selectedEvent.entity_id})
                </span>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-semibold text-slate-700 block mb-1">Old State</span>
                <div className="bg-slate-900 text-slate-200 p-3 rounded font-mono text-[11px] max-h-36 overflow-auto">
                  <pre>{selectedEvent.old_state_json ? JSON.stringify(JSON.parse(selectedEvent.old_state_json), null, 2) : 'null'}</pre>
                </div>
              </div>
              <div>
                <span className="font-semibold text-slate-700 block mb-1">New State</span>
                <div className="bg-slate-900 text-emerald-400 p-3 rounded font-mono text-[11px] max-h-36 overflow-auto">
                  <pre>{selectedEvent.new_state_json ? JSON.stringify(JSON.parse(selectedEvent.new_state_json), null, 2) : 'null'}</pre>
                </div>
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                onClick={() => setSelectedEvent(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
