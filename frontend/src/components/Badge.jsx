import React from 'react';

export function Badge({ children, variant = 'default', size = 'md' }) {
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-[10px]',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm',
  };

  const variantClasses = {
    // General statuses
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    primary: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-sky-50 text-sky-700 border-sky-200',

    // Tasks & Cases
    COMPLETED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    IN_PROGRESS: 'bg-sky-50 text-sky-700 border-sky-200',
    PENDING: 'bg-slate-100 text-slate-700 border-slate-200',
    BLOCKED: 'bg-rose-50 text-rose-700 border-rose-200',
    INITIATED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    FAILED: 'bg-rose-50 text-rose-700 border-rose-200',

    // Employment
    ACTIVE: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    TERMINATED: 'bg-slate-200 text-slate-800 border-slate-300',

    // Approvals / Grants
    APPROVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    REJECTED: 'bg-rose-50 text-rose-700 border-rose-200',
    REQUESTED: 'bg-amber-50 text-amber-700 border-amber-200',
    PROVISIONED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    REVOKED: 'bg-slate-100 text-slate-600 border-slate-200',

    // Severity
    CRITICAL: 'bg-rose-100 text-rose-800 border-rose-300 font-bold',
    HIGH: 'bg-orange-100 text-orange-800 border-orange-300 font-semibold',
    MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300',
    LOW: 'bg-blue-50 text-blue-700 border-blue-200',

    // Team owners
    HR: 'bg-purple-50 text-purple-700 border-purple-200',
    IT: 'bg-blue-50 text-blue-700 border-blue-200',
    FACILITIES: 'bg-teal-50 text-teal-700 border-teal-200',
    MANAGER: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    SECURITY: 'bg-rose-50 text-rose-700 border-rose-200',
  };

  const style = variantClasses[variant] || variantClasses.default;
  const sizeStyle = sizeClasses[size] || sizeClasses.md;

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${sizeStyle} ${style}`}>
      {children}
    </span>
  );
}
