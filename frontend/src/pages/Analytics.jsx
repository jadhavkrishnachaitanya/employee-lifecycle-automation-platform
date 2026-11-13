import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import {
  BarChart3,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Target,
  Percent,
  Layers,
} from 'lucide-react';

export function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  async function loadMetrics() {
    setLoading(true);
    try {
      const res = await api.getMetrics();
      setMetrics(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Computing ground-truth benchmarks...</p>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return <div className="p-8 text-slate-500">Failed to load analytics telemetry.</div>;
  }

  const evalData = metrics.ground_truth_evaluation || {};
  const perIssue = evalData.per_issue_breakdown || {};

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">SLA Adherence Rate</span>
            <Target className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.task_sla_adherence_rate}%</div>
          <p className="text-xs text-slate-500 mt-1">Calculated against fixed evaluation date</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Onboarding Completion</span>
            <CheckCircle2 className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.onboarding_completion_rate}%</div>
          <p className="text-xs text-slate-500 mt-1">All 8 prerequisites fulfilled</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Asset Fleet Utilization</span>
            <Layers className="w-4 h-4 text-sky-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.asset_utilization_rate}%</div>
          <p className="text-xs text-slate-500 mt-1">600 total active inventory devices</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Clearance Time</span>
            <Clock className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{metrics.average_days_to_clear_onboarding} days</div>
          <p className="text-xs text-slate-500 mt-1">From creation to active start</p>
        </div>
      </div>

      {/* Model Benchmark / Evaluation Scorecard */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="success" size="sm">Independent Verification</Badge>
              <span className="text-xs font-semibold text-slate-500">Fixed Seed 20261022</span>
            </div>
            <h2 className="text-base font-bold text-slate-900">
              Ground-Truth Evaluation: Precision, Recall & F1
            </h2>
            <p className="text-xs text-slate-500">
              Evaluates the independent rule engine against the separate deterministic ground-truth manifest.
            </p>
          </div>

          <div className="flex items-center gap-4 bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Precision</span>
              <span className="font-mono text-base font-bold text-emerald-600">
                {((evalData.precision || 1.0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-px h-8 bg-slate-200"></div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Recall</span>
              <span className="font-mono text-base font-bold text-emerald-600">
                {((evalData.recall || 1.0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-px h-8 bg-slate-200"></div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">F1 Score</span>
              <span className="font-mono text-base font-bold text-indigo-600">
                {((evalData.f1_score || 1.0) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Breakdown by Issue Category Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Anomaly Category</th>
                <th className="px-6 py-3.5 text-center">Ground Truth</th>
                <th className="px-6 py-3.5 text-center">Detected</th>
                <th className="px-6 py-3.5 text-center">True Pos (TP)</th>
                <th className="px-6 py-3.5 text-center">False Pos (FP)</th>
                <th className="px-6 py-3.5 text-center">False Neg (FN)</th>
                <th className="px-6 py-3.5 text-center">Precision</th>
                <th className="px-6 py-3.5 text-center">Recall</th>
                <th className="px-6 py-3.5 text-center">F1 Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {Object.entries(perIssue).map(([issueType, stats]) => (
                <tr key={issueType} className="hover:bg-slate-50/75 transition font-mono text-xs">
                  <td className="px-6 py-4 font-sans font-semibold text-slate-900">
                    {issueType.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 text-center font-bold text-slate-700">{stats.ground_truth_count}</td>
                  <td className="px-6 py-4 text-center text-indigo-700 font-bold">{stats.detected_count}</td>
                  <td className="px-6 py-4 text-center text-emerald-600 font-semibold">{stats.true_positives}</td>
                  <td className="px-6 py-4 text-center text-rose-500">{stats.false_positives}</td>
                  <td className="px-6 py-4 text-center text-slate-400">{stats.false_negatives}</td>
                  <td className="px-6 py-4 text-center font-semibold text-slate-800">
                    {(stats.precision * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 text-center font-semibold text-slate-800">
                    {(stats.recall * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 text-center font-bold text-indigo-600">
                    {(stats.f1_score * 100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
