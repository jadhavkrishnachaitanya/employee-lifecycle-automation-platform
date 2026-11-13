import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { CheckSquare, AlertCircle, CheckCircle2, Clock, Filter, ShieldAlert } from 'lucide-react';

export function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [teamFilter, setTeamFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState(null);

  useEffect(() => {
    loadTasks();
  }, [teamFilter, statusFilter]);

  async function loadTasks() {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (teamFilter) params.owner_team = teamFilter;
      if (statusFilter) params.status = statusFilter;
      const res = await api.getTasks(params);
      setTasks(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleUpdateStatus = async (taskId, newStatus) => {
    setActionMessage(null);
    try {
      await api.updateTaskStatus(taskId, newStatus, 'Status changed in Tasks Portal');
      setActionMessage({ type: 'success', text: `Task ${taskId} successfully updated to ${newStatus}` });
      loadTasks();
    } catch (err) {
      setActionMessage({ type: 'error', text: `Rule Violation: ${err.message}` });
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Filters & feedback banner */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          >
            <option value="">All Teams (HR, IT, Facilities, etc.)</option>
            <option value="HR">HR Team</option>
            <option value="IT">IT Operations</option>
            <option value="FACILITIES">Facilities & Logistics</option>
            <option value="MANAGER">Hiring Manager</option>
            <option value="SECURITY">Security & Compliance</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="BLOCKED">Blocked</option>
          </select>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-800">{tasks.length}</span> instances (4,000 total)
        </div>
      </div>

      {actionMessage && (
        <div
          className={`p-4 rounded-xl border text-xs font-medium flex items-center gap-2 ${
            actionMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {actionMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {/* Tasks Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">Task Title & ID</th>
                <th className="px-6 py-3.5">Onboarding Case</th>
                <th className="px-6 py-3.5">Owner Team</th>
                <th className="px-6 py-3.5">Due Date</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Dependency State</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    Loading task queue...
                  </td>
                </tr>
              ) : tasks.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    No task instances found matching filters.
                  </td>
                </tr>
              ) : (
                tasks.map((task) => {
                  const isDone = task.status === 'COMPLETED';
                  const isBlocked = task.is_blocked || task.status === 'BLOCKED';

                  return (
                    <tr key={task.task_id} className="hover:bg-slate-50/75 transition">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900 leading-tight">{task.title}</div>
                        <div className="text-xs text-slate-400 font-mono mt-0.5">{task.task_id}</div>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">{task.case_id}</td>
                      <td className="px-6 py-4">
                        <Badge variant={task.owner_team} size="sm">
                          {task.owner_team}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">
                        {task.due_date?.split('T')[0]}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={task.status}>{task.status}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        {isBlocked ? (
                          <div className="text-xs text-rose-600 font-medium flex items-center gap-1.5">
                            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                            <span>{task.blocked_reason || 'Blocked'}</span>
                          </div>
                        ) : isDone ? (
                          <div className="text-xs text-emerald-600 font-medium flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                            <span>Fulfilled</span>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-500">Prerequisites Cleared</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {!isDone && (
                          <button
                            onClick={() => handleUpdateStatus(task.task_id, 'COMPLETED')}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-lg shadow-2xs transition ${
                              isBlocked
                                ? 'bg-slate-100 text-slate-500 border border-slate-200 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300'
                                : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                            }`}
                            title={isBlocked ? 'Clicking blocked task tests prerequisite violation rejection' : 'Mark Task Completed'}
                          >
                            Complete
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
    </div>
  );
}
