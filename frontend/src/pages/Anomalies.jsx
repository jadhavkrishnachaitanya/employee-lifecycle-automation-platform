import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import {
  AlertOctagon,
  ShieldAlert,
  Search,
  Filter,
  Eye,
  CheckCircle2,
  RefreshCw,
  X,
  FileCode,
} from 'lucide-react';

const SEVEN_RULES = [
  { id: 'RULE-TASK-001', name: 'Task Completed Before Prerequisite', category: 'TASK_COMPLETED_BEFORE_PREREQUISITE', sev: 'HIGH' },
  { id: 'RULE-ORG-002', name: 'Missing Direct Manager', category: 'MISSING_MANAGER', sev: 'HIGH' },
  { id: 'RULE-AST-003', name: 'Asset Double Assignment (Overlap)', category: 'ASSET_DOUBLE_ASSIGNMENT', sev: 'HIGH' },
  { id: 'RULE-ONB-004', name: 'Started Before Background Check', category: 'STARTED_BEFORE_BACKGROUND_CHECK', sev: 'CRITICAL' },
  { id: 'RULE-ACC-005', name: 'Terminated User Retains Active Access', category: 'TERMINATED_EMPLOYEE_ACTIVE_ACCESS', sev: 'CRITICAL' },
  { id: 'RULE-TASK-006', name: 'Overdue Incomplete Tasks (SLA Breach)', category: 'OVERDUE_INCOMPLETE_TASK', sev: 'MEDIUM' },
  { id: 'RULE-ONB-007', name: 'Mid-Process Department Transfer', category: 'DEPARTMENT_CHANGE_MID_PROCESS', sev: 'MEDIUM' },
];

export function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [scanResult, setScanResult] = useState(null);

  useEffect(() => {
    loadAnomalies();
  }, [severityFilter, typeFilter]);

  async function loadAnomalies() {
    setLoading(true);
    try {
      const params = {};
      if (severityFilter) params.severity = severityFilter;
      if (typeFilter) params.issue_type = typeFilter;
      const res = await api.getAnomalies(params);
      setAnomalies(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleRunScan = async () => {
    setIsScanning(true);
    setScanResult(null);
    try {
      const res = await api.getValidation();
      setScanResult(res);
      loadAnomalies();
    } catch (err) {
      alert(`Validation Scan Error: ${err.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Overview Cards for the 7 Rules */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="danger" size="sm">Ground Truth Evaluator</Badge>
              <span className="text-xs text-slate-500 font-medium">Independent Rule Engine</span>
            </div>
            <h2 className="text-base font-bold text-slate-900">Seven Required Anomaly Categories</h2>
            <p className="text-xs text-slate-500">
              Deterministic anomalies injected into database and audited without ground-truth leakage.
            </p>
          </div>

          <button
            onClick={handleRunScan}
            disabled={isScanning}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-xs transition disabled:opacity-50 shrink-0"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>{isScanning ? 'Scanning Live Records...' : 'Run Independent Validator'}</span>
          </button>
        </div>

        {/* 7 Anomaly Category Pills */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5 pt-2">
          {SEVEN_RULES.map((r, idx) => {
            const count = anomalies.filter((a) => a.issue_type === r.category).length;
            const isSelected = typeFilter === r.category;
            return (
              <div
                key={r.id}
                onClick={() => setTypeFilter(isSelected ? '' : r.category)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition flex flex-col justify-between ${
                  isSelected
                    ? 'bg-indigo-50/70 border-indigo-400 ring-1 ring-indigo-400'
                    : 'bg-slate-50/50 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-mono text-[10px] text-slate-400">#{idx + 1} • {r.id}</span>
                  <Badge variant={r.sev} size="sm">
                    {r.sev}
                  </Badge>
                </div>
                <div className="font-semibold text-slate-800 leading-tight">{r.name}</div>
                <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
                  <span>Detected Records:</span>
                  <span className="font-mono font-bold text-indigo-700">{count}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Scan Results banner */}
      {scanResult && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-900 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
          <div>
            <div className="font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Independent Validation Complete ({scanResult.reference_date.split(' ')[0]})</span>
            </div>
            <div className="mt-1 text-emerald-700">
              Evaluated {scanResult.total_rules_evaluated} rules across {scanResult.total_records_checked} entities. Total anomalies confirmed: <span className="font-bold">{scanResult.total_anomalies_detected}</span>.
            </div>
          </div>
          {scanResult.evaluation_metrics && (
            <div className="flex items-center gap-3 font-mono text-xs font-semibold bg-emerald-100/60 px-3 py-1.5 rounded-lg border border-emerald-200 shrink-0">
              <span>Precision: {(scanResult.evaluation_metrics.precision * 100).toFixed(1)}%</span>
              <span>•</span>
              <span>Recall: {(scanResult.evaluation_metrics.recall * 100).toFixed(1)}%</span>
              <span>•</span>
              <span>F1: {(scanResult.evaluation_metrics.f1_score * 100).toFixed(1)}%</span>
            </div>
          )}
        </div>
      )}

      {/* Filter bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {typeFilter && (
            <button
              onClick={() => setTypeFilter('')}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium underline"
            >
              Clear Category Filter ({typeFilter})
            </button>
          )}
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{anomalies.length}</span> verified issues
        </div>
      </div>

      {/* Issues Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Issue ID</th>
                <th className="px-6 py-3.5">Rule ID</th>
                <th className="px-6 py-3.5">Entity Affected</th>
                <th className="px-6 py-3.5">Anomaly Category</th>
                <th className="px-6 py-3.5">Severity</th>
                <th className="px-6 py-3.5 text-right">Evidence Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    Scanning anomaly records...
                  </td>
                </tr>
              ) : anomalies.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    No anomalies matching filter.
                  </td>
                </tr>
              ) : (
                anomalies.map((iss) => (
                  <tr key={iss.issue_id} className="hover:bg-slate-50/75 transition">
                    <td className="px-6 py-4 font-mono font-bold text-xs text-slate-900">{iss.issue_id}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">{iss.rule_id}</td>
                    <td className="px-6 py-4 font-mono text-xs font-semibold text-indigo-600">
                      {iss.entity_id}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-xs text-slate-800">
                        {iss.issue_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={iss.severity}>{iss.severity}</Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedEvidence(iss)}
                        className="px-2.5 py-1 text-xs text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100/70 font-semibold rounded-md transition inline-flex items-center gap-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect Evidence</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Evidence Modal */}
      {selectedEvidence && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Evidence Payload: {selectedEvidence.issue_id}
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  {selectedEvidence.rule_id} • Entity {selectedEvidence.entity_id}
                </span>
              </div>
              <button
                onClick={() => setSelectedEvidence(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 font-mono text-xs text-emerald-400 overflow-x-auto max-h-72">
              <pre>{JSON.stringify(JSON.parse(selectedEvidence.evidence_json), null, 2)}</pre>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                onClick={() => setSelectedEvidence(null)}
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
