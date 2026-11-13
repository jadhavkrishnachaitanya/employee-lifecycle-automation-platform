import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import {
  UserCheck,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronRight,
  ArrowRight,
  ShieldCheck,
  FileText,
  User,
  Calendar,
} from 'lucide-react';

export function Onboarding() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseDetail, setCaseDetail] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadCases();
  }, [statusFilter]);

  async function loadCases() {
    setLoading(true);
    try {
      const res = await api.getOnboardingCases(statusFilter);
      setCases(res);
      if (res.length > 0 && !selectedCase) {
        loadDetail(res[0].case_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(caseId) {
    setSelectedCase(caseId);
    setDetailLoading(true);
    try {
      const res = await api.getOnboardingCase(caseId);
      setCaseDetail(res);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  }

  const handleTaskComplete = async (taskId) => {
    try {
      await api.updateTaskStatus(taskId, 'COMPLETED', 'Completed in Onboarding view');
      loadDetail(selectedCase);
      loadCases();
    } catch (err) {
      alert(`Workflow Engine Rejected: ${err.message}`);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Filters & summary */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Status Filter:</span>
          <div className="flex items-center bg-white p-1 rounded-lg border border-slate-200 text-xs shadow-2xs">
            {['', 'IN_PROGRESS', 'COMPLETED'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-md font-medium transition ${
                  statusFilter === st
                    ? 'bg-indigo-600 text-white shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {st === '' ? 'All Cases' : st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{cases.length}</span> onboarding cases
        </div>
      </div>

      {/* Two column layout: Case list on left, Task Checklist on right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Case List */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Lifecycle Onboarding Cases
          </div>
          <div className="divide-y divide-slate-100 max-h-[680px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading cases...</div>
            ) : cases.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No onboarding cases found.</div>
            ) : (
              cases.map((c) => {
                const isSelected = selectedCase === c.case_id;
                return (
                  <div
                    key={c.case_id}
                    onClick={() => loadDetail(c.case_id)}
                    className={`p-4 transition cursor-pointer flex items-center justify-between ${
                      isSelected ? 'bg-indigo-50/70 border-l-4 border-indigo-600' : 'hover:bg-slate-50'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-slate-900">{c.case_id}</span>
                        <Badge variant={c.status} size="sm">
                          {c.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-slate-500 mt-1 flex items-center gap-3">
                        <span className="font-mono">{c.employee_id}</span>
                        <span>Start: {c.target_start_date?.split('T')[0]}</span>
                      </div>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`} />
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Selected Case Task Details & Dependency Visualization */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-2xs p-6 space-y-6">
          {detailLoading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading task sequence...</div>
          ) : !caseDetail ? (
            <div className="p-12 text-center text-xs text-slate-400">Select an onboarding case to view tasks</div>
          ) : (
            <>
              {/* Case Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-slate-900">{caseDetail.case_id}</h2>
                    <Badge variant={caseDetail.status}>{caseDetail.status}</Badge>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Employee Ref: <span className="font-mono font-medium text-slate-800">{caseDetail.employee_id}</span> • Target Start: {caseDetail.target_start_date?.split('T')[0]}
                  </div>
                </div>

                <div className="text-xs text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
                  <span>SLA Target: </span>
                  <span className="font-mono font-semibold text-slate-800">
                    {caseDetail.sla_target_date?.split('T')[0]}
                  </span>
                </div>
              </div>

              {/* Task Dependency Rule Explanation */}
              <div className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs text-indigo-900 flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Dependency Enforcement Guard:</span> Identity Verification (TPL-001) must complete before Corporate SSO Identity (TPL-003). Background check (TPL-002) must complete before Final Clearance (TPL-008). Invalid transitions are rejected by the workflow engine.
                </div>
              </div>

              {/* Task Checklist Items */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Orchestrated Task Sequence (8 Steps)
                </h3>

                <div className="space-y-2">
                  {(caseDetail.tasks || []).map((task, idx) => {
                    const isDone = task.status === 'COMPLETED';
                    const isBlocked = task.is_blocked || task.status === 'BLOCKED';

                    return (
                      <div
                        key={task.task_id}
                        className={`p-3.5 rounded-lg border transition flex items-center justify-between gap-4 ${
                          isDone
                            ? 'bg-emerald-50/30 border-emerald-200'
                            : isBlocked
                            ? 'bg-rose-50/30 border-rose-200'
                            : 'bg-white border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${
                              isDone
                                ? 'bg-emerald-600 text-white'
                                : isBlocked
                                ? 'bg-rose-100 text-rose-700'
                                : 'bg-slate-100 text-slate-700 border border-slate-300'
                            }`}
                          >
                            {isDone ? <CheckCircle2 className="w-3.5 h-3.5" /> : idx + 1}
                          </div>

                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-xs text-slate-900">{task.title}</span>
                              <Badge variant={task.owner_team} size="sm">
                                {task.owner_team}
                              </Badge>
                            </div>

                            <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                              {task.task_id} • Due: {task.due_date?.split('T')[0]}
                            </div>

                            {isBlocked && (
                              <div className="text-[11px] text-rose-600 font-medium flex items-center gap-1 mt-1">
                                <AlertCircle className="w-3 h-3" />
                                <span>{task.blocked_reason || 'Blocked by prerequisite dependency'}</span>
                              </div>
                            )}

                            {isDone && task.completed_at && (
                              <div className="text-[11px] text-emerald-600 font-medium mt-0.5">
                                Fulfilled on {task.completed_at.split('T')[0]} by {task.completed_by || 'SYSTEM'}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Action button */}
                        <div>
                          {!isDone && (
                            <button
                              onClick={() => handleTaskComplete(task.task_id)}
                              className={`px-3 py-1.5 text-xs font-semibold rounded-lg shadow-2xs transition ${
                                isBlocked
                                  ? 'bg-slate-100 text-slate-400 border border-slate-200 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300'
                                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                              }`}
                              title={isBlocked ? 'Clicking blocked task tests prerequisite rejection' : 'Mark Completed'}
                            >
                              {isBlocked ? 'Test Block' : 'Complete'}
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
