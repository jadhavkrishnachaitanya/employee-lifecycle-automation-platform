import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import {
  Users,
  UserCheck,
  CheckCircle2,
  Clock,
  ShieldCheck,
  KeyRound,
  UserX,
  AlertOctagon,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

const PIE_COLORS = ['#10b981', '#0ea5e9', '#f59e0b', '#ef4444', '#8b5cf6'];

export function Dashboard({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    try {
      const res = await api.getDashboard();
      setData(res);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500 font-medium">Aggregating lifecycle telemetry...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm">
          Failed to load dashboard: {error}
        </div>
      </div>
    );
  }

  // Format data for Recharts
  const statusPieData = Object.entries(data.onboarding_by_status || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const teamBarData = Object.entries(data.tasks_by_team || {}).map(([team, count]) => ({
    team,
    tasks: count,
  }));

  const anomalyBarData = Object.entries(data.anomaly_breakdown || {}).map(([type, count]) => ({
    name: type.replace(/_/g, ' '),
    count,
  }));

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Headcount</span>
            <Users className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{data.total_employees}</span>
            <span className="text-xs text-emerald-600 font-medium flex items-center">
              {data.active_employees} active
            </span>
          </div>
          <div className="mt-3 text-xs text-slate-500 flex justify-between border-t border-slate-100 pt-2">
            <span>Pending Onboarding</span>
            <span className="font-semibold text-slate-700">{data.pending_onboarding}</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Task Execution</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{data.completed_tasks}</span>
            <span className="text-xs text-slate-500 font-medium">/ {data.total_tasks} tasks</span>
          </div>
          <div className="mt-3 text-xs text-slate-500 flex justify-between border-t border-slate-100 pt-2">
            <span>Blocked Prereqs</span>
            <span className="font-semibold text-rose-600">{data.blocked_tasks}</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Overdue & Approvals</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-amber-600">{data.overdue_tasks}</span>
            <span className="text-xs text-slate-500">SLA breaches</span>
          </div>
          <div className="mt-3 text-xs text-slate-500 flex justify-between border-t border-slate-100 pt-2">
            <span>Pending Approvals</span>
            <span className="font-semibold text-indigo-600">{data.pending_approvals}</span>
          </div>
        </div>

        <div
          onClick={() => onNavigate('anomalies')}
          className="bg-white p-5 rounded-xl border border-rose-200 shadow-2xs hover:border-rose-300 hover:shadow-xs transition cursor-pointer group"
        >
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-rose-700">Anomalies Injected</span>
            <AlertOctagon className="w-4 h-4 text-rose-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-rose-600">{data.total_anomalies}</span>
            <span className="text-xs text-rose-600 font-medium">Detected across 7 rules</span>
          </div>
          <div className="mt-3 text-xs text-rose-600 flex justify-between border-t border-rose-100 pt-2 font-medium group-hover:underline">
            <span>Review Anomaly Board</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>

      {/* Visual Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Onboarding Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Onboarding Lifecycle Distribution</h3>
              <p className="text-xs text-slate-500">Case status breakdown across all 500 cases</p>
            </div>
            <Badge variant="primary">Real-Time DB</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tasks by Owner Team */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Task Allocation by Functional Team</h3>
              <p className="text-xs text-slate-500">Distribution across HR, IT, Facilities, Manager, Security</p>
            </div>
            <Badge variant="default">4,000 Tasks Total</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamBarData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis dataKey="team" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="tasks" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Action Banner */}
      <div className="bg-gradient-to-r from-indigo-900 to-slate-900 rounded-xl p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="warning" size="sm">Verification Suite</Badge>
            <span className="text-xs text-indigo-300 font-medium">Deterministic Evaluation Ready</span>
          </div>
          <h2 className="text-base font-semibold text-white">Rule-Based Anomaly Detection & SLA Auditing</h2>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl">
            Scan all 500 employee records, 4,000 task instances, and 600 asset assignments against business rules.
            Compare independent detections against synthetic ground truth for Precision, Recall, and F1 scoring.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => onNavigate('anomalies')}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-lg shadow-sm transition"
          >
            View Detected Anomalies
          </button>
          <button
            onClick={() => onNavigate('analytics')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs rounded-lg border border-slate-700 transition"
          >
            Full Evaluation Metrics
          </button>
        </div>
      </div>
    </div>
  );
}
