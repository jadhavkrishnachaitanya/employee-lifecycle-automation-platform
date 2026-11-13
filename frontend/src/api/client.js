const API_BASE = '/api';

async function request(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!res.ok) {
      let errorData;
      try {
        errorData = await res.json();
      } catch (e) {
        errorData = { detail: res.statusText };
      }
      const message = errorData.detail?.error || errorData.detail || 'API request failed';
      throw new Error(typeof message === 'object' ? JSON.stringify(message) : message);
    }
    
    return await res.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  getHealth: () => request('/health'),
  getDashboard: () => request('/dashboard'),
  getDepartments: () => request('/departments'),
  getRoles: (deptId) => request(`/roles${deptId ? `?department_id=${deptId}` : ''}`),
  getManagers: (deptId) => request(`/managers${deptId ? `?department_id=${deptId}` : ''}`),
  getEmployees: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/employees${q ? `?${q}` : ''}`);
  },
  getEmployee: (id) => request(`/employees/${id}`),
  createEmployee: (data) => request('/employees', { method: 'POST', body: JSON.stringify(data) }),
  getOnboardingCases: (status) => request(`/onboarding${status ? `?status=${status}` : ''}`),
  getOnboardingCase: (id) => request(`/onboarding/${id}`),
  createOnboardingCase: (data) => request('/onboarding', { method: 'POST', body: JSON.stringify(data) }),
  getTasks: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/tasks${q ? `?${q}` : ''}`);
  },
  updateTaskStatus: (id, status, reason = 'Updated in UI') =>
    request(`/tasks/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, actor: 'UI_USER', reason }),
    }),
  getAssets: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/assets${q ? `?${q}` : ''}`);
  },
  assignAsset: (id, employeeId, returnDueDate = null, force = false) =>
    request(`/assets/${id}/assign`, {
      method: 'POST',
      body: JSON.stringify({ employee_id: employeeId, return_due_date: returnDueDate, force_override: force }),
    }),
  recoverAsset: (id, notes = 'Recovered in portal') =>
    request(`/assets/${id}/recover`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    }),
  getAccessRequests: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/access-requests${q ? `?${q}` : ''}`);
  },
  createAccessRequest: (data) => request('/access-requests', { method: 'POST', body: JSON.stringify(data) }),
  approveAccessRequest: (id, decision, comments = '') =>
    request(`/access-requests/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approver_id: 'MGR-001', decision, comments }),
    }),
  provisionAccessRequest: (id) =>
    request(`/access-requests/${id}/provision`, {
      method: 'POST',
      body: JSON.stringify({ provisioner_id: 'IT_ADMIN' }),
    }),
  getApprovals: (status) => request(`/approvals${status ? `?status=${status}` : ''}`),
  getOffboardingCases: (status) => request(`/offboarding${status ? `?status=${status}` : ''}`),
  initiateOffboarding: (data) => request('/offboarding', { method: 'POST', body: JSON.stringify(data) }),
  revokeOffboardingAccess: (id) =>
    request(`/offboarding/${id}/revoke-access`, {
      method: 'POST',
      body: JSON.stringify({ actor: 'IT_ADMIN', notes: 'Portal revocation action' }),
    }),
  getAuditEvents: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/audit-events${q ? `?${q}` : ''}`);
  },
  getAnomalies: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/anomalies${q ? `?${q}` : ''}`);
  },
  getValidation: () => request('/validation'),
  getMetrics: () => request('/metrics'),
};
