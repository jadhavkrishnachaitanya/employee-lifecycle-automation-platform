import React, { useState } from 'react';
import { Sidebar, NAV_ITEMS } from './components/Sidebar';
import { Header } from './components/Header';

import { Dashboard } from './pages/Dashboard';
import { Employees } from './pages/Employees';
import { Onboarding } from './pages/Onboarding';
import { Tasks } from './pages/Tasks';
import { Approvals } from './pages/Approvals';
import { AccessManagement } from './pages/AccessManagement';
import { Assets } from './pages/Assets';
import { Offboarding } from './pages/Offboarding';
import { Anomalies } from './pages/Anomalies';
import { Analytics } from './pages/Analytics';
import { AuditTrail } from './pages/AuditTrail';
import { DataGenerator } from './pages/DataGenerator';

const PAGE_METADATA = {
  dashboard: { title: 'Executive Overview', subtitle: 'Live telemetry across HR, IT, Facilities and Management' },
  employees: { title: 'Employee Directory', subtitle: 'Master organization hierarchy, role catalog, and employment history' },
  onboarding: { title: 'Onboarding Orchestrator', subtitle: '8-step standardized lifecycle case management and dependency enforcement' },
  tasks: { title: 'Task Execution Ledger', subtitle: 'Prerequisite checking, SLA due-date monitoring, and workflow transitions' },
  approvals: { title: 'Access Approvals', subtitle: 'Two-phase commit verification by designated managers and security leads' },
  access: { title: 'Access & Entitlements', subtitle: 'Role-based access provisioning, enterprise system grants, and revocation' },
  assets: { title: 'Hardware & Asset Fleet', subtitle: 'Asset allocation, serial tracking, recovery, and overlap prevention' },
  offboarding: { title: 'Employee Offboarding', subtitle: 'Zero-trust credential revocation and physical asset reconciliation' },
  anomalies: { title: 'Seven Injected Anomalies & Ground Truth', subtitle: 'Rule-based independent anomaly detection with evidence payload inspection' },
  analytics: { title: 'Analytics & SLA Benchmarking', subtitle: 'Precision, recall, and F1 scorecard evaluated against deterministic ground truth' },
  audit: { title: 'Immutable Audit Trail', subtitle: 'Timestamped diffs, state mutations, authorized actors, and business reasons' },
  generator: { title: 'Data Generator & Reproducibility', subtitle: 'Deterministic seed parameters, SHA-256 manifests, and file exports' },
};

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [refreshKey, setRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setRefreshKey((prev) => prev + 1);
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const meta = PAGE_METADATA[currentTab] || { title: 'YottaFlex Orchestrator', subtitle: '' };

  const renderContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return <Dashboard key={refreshKey} onNavigate={(tab) => setCurrentTab(tab)} />;
      case 'employees':
        return <Employees key={refreshKey} />;
      case 'onboarding':
        return <Onboarding key={refreshKey} />;
      case 'tasks':
        return <Tasks key={refreshKey} />;
      case 'approvals':
        return <Approvals key={refreshKey} />;
      case 'access':
        return <AccessManagement key={refreshKey} />;
      case 'assets':
        return <Assets key={refreshKey} />;
      case 'offboarding':
        return <Offboarding key={refreshKey} />;
      case 'anomalies':
        return <Anomalies key={refreshKey} />;
      case 'analytics':
        return <Analytics key={refreshKey} />;
      case 'audit':
        return <AuditTrail key={refreshKey} />;
      case 'generator':
        return <DataGenerator key={refreshKey} />;
      default:
        return <Dashboard key={refreshKey} onNavigate={(tab) => setCurrentTab(tab)} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      {/* Navigation Sidebar */}
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={meta.title}
          subtitle={meta.subtitle}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />
        <main className="flex-1 pb-16">{renderContent()}</main>
      </div>
    </div>
  );
}
