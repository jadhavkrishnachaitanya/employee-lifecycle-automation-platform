import React from 'react';
import {
  LayoutDashboard,
  Users,
  UserCheck,
  CheckSquare,
  ShieldCheck,
  KeyRound,
  Laptop,
  UserX,
  AlertTriangle,
  BarChart3,
  History,
  DatabaseZap,
} from 'lucide-react';

export const NAV_ITEMS = [
  { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
  { id: 'employees', label: 'Employees', icon: Users },
  { id: 'onboarding', label: 'Onboarding', icon: UserCheck },
  { id: 'tasks', label: 'Tasks', icon: CheckSquare },
  { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
  { id: 'access', label: 'Access Control', icon: KeyRound },
  { id: 'assets', label: 'Assets', icon: Laptop },
  { id: 'offboarding', label: 'Offboarding', icon: UserX },
  { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, badge: '7 Injected' },
  { id: 'analytics', label: 'Analytics & SLA', icon: BarChart3 },
  { id: 'audit', label: 'Audit Trail', icon: History },
  { id: 'generator', label: 'Data & Validation', icon: DatabaseZap },
];

export function Sidebar({ currentTab, onSelectTab }) {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-md">
          YF
        </div>
        <div>
          <div className="font-semibold text-white tracking-wide leading-tight text-sm">YottaFlex.ai</div>
          <div className="text-xs text-indigo-400 font-medium">Lifecycle Orchestrator</div>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Workflow Management
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span>Engine State:</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Operational
          </span>
        </div>
        <div className="text-slate-400 text-[11px]">Ref Date: 2026-11-01</div>
        <div className="text-slate-400 text-[11px]">Seed: 20261022</div>
      </div>
    </aside>
  );
}
