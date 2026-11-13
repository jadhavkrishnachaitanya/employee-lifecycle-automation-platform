import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import { Search, Plus, Filter, User, Building, Briefcase, Calendar, Check, X } from 'lucide-react';

export function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [roles, setRoles] = useState([]);
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modals & Selection
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    department_id: '',
    role_id: '',
    manager_id: '',
    location_type: 'REMOTE',
    employment_type: 'FULL_TIME',
    start_date: new Date().toISOString().split('T')[0],
  });
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    loadCatalogs();
    loadEmployees();
  }, [deptFilter, statusFilter]);

  async function loadCatalogs() {
    try {
      const [depts, rls, mgrs] = await Promise.all([
        api.getDepartments(),
        api.getRoles(),
        api.getManagers(),
      ]);
      setDepartments(depts);
      setRoles(rls);
      setManagers(mgrs);
      if (depts.length > 0) {
        setCreateForm((prev) => ({
          ...prev,
          department_id: depts[0].department_id,
          role_id: rls.find((r) => r.department_id === depts[0].department_id)?.role_id || rls[0]?.role_id,
        }));
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function loadEmployees() {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (deptFilter) params.department_id = deptFilter;
      if (statusFilter) params.status = statusFilter;
      if (search) params.search = search;
      const res = await api.getEmployees(params);
      setEmployees(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadEmployees();
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setActionError(null);
    try {
      await api.createEmployee({
        ...createForm,
        start_date: new Date(createForm.start_date).toISOString(),
        manager_id: createForm.manager_id || null,
      });
      setShowCreateModal(false);
      loadEmployees();
    } catch (err) {
      setActionError(err.message);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name, email, or EMP-ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition"
          />
        </form>

        <div className="flex items-center gap-3">
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.department_id} value={d.department_id}>
                {d.name} ({d.code})
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="PENDING">Pending</option>
            <option value="TERMINATED">Terminated</option>
          </select>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-xs transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Employee</span>
          </button>
        </div>
      </div>

      {/* Employees Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3.5">ID & Name</th>
                <th className="px-6 py-3.5">Department & Role</th>
                <th className="px-6 py-3.5">Manager</th>
                <th className="px-6 py-3.5">Location / Type</th>
                <th className="px-6 py-3.5">Start Date</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    Loading directory...
                  </td>
                </tr>
              ) : employees.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-400">
                    No employees matching filter criteria.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.employee_id} className="hover:bg-slate-50/75 transition">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900 leading-tight">
                        {emp.first_name} {emp.last_name}
                      </div>
                      <div className="text-xs text-slate-400 font-mono mt-0.5">{emp.employee_id}</div>
                      <div className="text-xs text-slate-500">{emp.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-800">{emp.department_id}</div>
                      <div className="text-xs text-slate-500">{emp.role_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      {emp.manager_id ? (
                        <span className="font-mono text-xs text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                          {emp.manager_id}
                        </span>
                      ) : (
                        <Badge variant="danger" size="sm">
                          Missing Manager (Anomaly)
                        </Badge>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-xs text-slate-700 font-medium">{emp.location_type}</div>
                      <div className="text-[11px] text-slate-400">{emp.employment_type}</div>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-600 font-mono">
                      {emp.start_date?.split('T')[0]}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={emp.status}>{emp.status}</Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedEmp(emp)}
                        className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
                      >
                        Inspect Record
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspect Employee Modal */}
      {selectedEmp && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Employee Lifecycle Record</h3>
              <button
                onClick={() => setSelectedEmp(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Identifier</span>
                  <span className="font-mono font-bold text-slate-800 text-sm">{selectedEmp.employee_id}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Lifecycle Status</span>
                  <Badge variant={selectedEmp.status}>{selectedEmp.status}</Badge>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Full Name</span>
                  <span className="font-semibold text-slate-800">{selectedEmp.first_name} {selectedEmp.last_name}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Work Email</span>
                  <span className="text-slate-700">{selectedEmp.email}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Department</span>
                  <span className="font-medium text-slate-800">{selectedEmp.department_id}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Role Catalog</span>
                  <span className="font-medium text-slate-800">{selectedEmp.role_id}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Reporting Manager</span>
                  <span className="font-mono text-slate-700">{selectedEmp.manager_id || 'UNASSIGNED (Violation)'}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase tracking-wider block text-[10px]">Start Date</span>
                  <span className="font-mono text-slate-700">{selectedEmp.start_date?.split('T')[0]}</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedEmp(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Employee Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="text-base font-bold text-slate-900">Provision New Employee</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {actionError && (
              <div className="p-3 mb-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                {actionError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-medium mb-1">First Name</label>
                  <input
                    type="text"
                    required
                    value={createForm.first_name}
                    onChange={(e) => setCreateForm({ ...createForm, first_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Last Name</label>
                  <input
                    type="text"
                    required
                    value={createForm.last_name}
                    onChange={(e) => setCreateForm({ ...createForm, last_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-700 font-medium mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  placeholder="name@yottaflex.internal"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Department</label>
                  <select
                    value={createForm.department_id}
                    onChange={(e) => {
                      const dId = e.target.value;
                      const roleMatch = roles.find((r) => r.department_id === dId)?.role_id || roles[0]?.role_id;
                      setCreateForm({ ...createForm, department_id: dId, role_id: roleMatch });
                    }}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    {departments.map((d) => (
                      <option key={d.department_id} value={d.department_id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Role Title</label>
                  <select
                    value={createForm.role_id}
                    onChange={(e) => setCreateForm({ ...createForm, role_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    {roles
                      .filter((r) => !createForm.department_id || r.department_id === createForm.department_id)
                      .map((r) => (
                        <option key={r.role_id} value={r.role_id}>
                          {r.title}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Manager</label>
                  <select
                    value={createForm.manager_id}
                    onChange={(e) => setCreateForm({ ...createForm, manager_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    <option value="">None (Flag as Missing)</option>
                    {managers.map((m) => (
                      <option key={m.manager_id} value={m.manager_id}>
                        {m.name} ({m.manager_id})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={createForm.start_date}
                    onChange={(e) => setCreateForm({ ...createForm, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium shadow-xs"
                >
                  Create Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
