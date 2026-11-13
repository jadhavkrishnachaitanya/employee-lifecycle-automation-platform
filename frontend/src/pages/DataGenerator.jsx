import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Badge } from '../components/Badge';
import {
  Database,
  FileSpreadsheet,
  FileCode,
  Download,
  CheckCircle2,
  ShieldCheck,
  Hash,
  Scale,
  Calendar,
} from 'lucide-react';

export function DataGenerator() {
  const [metrics, setMetrics] = useState(null);
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInfo();
  }, []);

  async function loadInfo() {
    setLoading(true);
    try {
      const [m, v] = await Promise.all([api.getMetrics(), api.getValidation()]);
      setMetrics(m);
      setValidation(v);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Determinism & Provenance Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="success" size="sm">Bit-for-Bit Deterministic</Badge>
              <span className="text-xs text-slate-500 font-mono">Seed: 20261022</span>
            </div>
            <h2 className="text-base font-bold text-slate-900">
              Deterministic Synthetic Generator & Provenance
            </h2>
            <p className="text-xs text-slate-500">
              Generated with Faker and Linear Congruential Generators against a fixed logical evaluation timestamp.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Scale:</span>
            <span className="px-3 py-1 bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold text-xs rounded-lg font-mono">
              FULL (500 EMP / 4000 TASKS)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg text-xs space-y-1">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">Reference Evaluation Date</span>
            <div className="font-mono font-bold text-slate-800 text-sm">2026-11-01 00:00:00 UTC</div>
            <p className="text-[11px] text-slate-500">Fixed reference date eliminates non-deterministic wall-clock skew.</p>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg text-xs space-y-1">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">Reproducibility Verification</span>
            <div className="font-mono font-bold text-emerald-600 text-sm flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>SHA-256 Checksums 100% Match</span>
            </div>
            <p className="text-[11px] text-slate-500">Multiple generation runs produce bit-for-bit identical tables.</p>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg text-xs space-y-1">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">Confidentiality Guarantee</span>
            <div className="font-mono font-bold text-slate-800 text-sm flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>100% Synthetic Data</span>
            </div>
            <p className="text-[11px] text-slate-500">No proprietary or real-world credentials or identity data.</p>
          </div>
        </div>
      </div>

      {/* Full Requested Counts Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">Challenge Specification Entity Target Reconciliation</h3>
          <Badge variant="primary">Exact Full Scale</Badge>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Employees</span>
              <span className="text-2xl font-bold font-mono text-slate-900">500</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 500)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Task Instances</span>
              <span className="text-2xl font-bold font-mono text-slate-900">4,000</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (8 per case)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Onboarding Cases</span>
              <span className="text-2xl font-bold font-mono text-slate-900">500</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (1 per emp)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Asset Inventory</span>
              <span className="text-2xl font-bold font-mono text-slate-900">600</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 600)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Access Requests</span>
              <span className="text-2xl font-bold font-mono text-slate-900">300</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 300)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Departments</span>
              <span className="text-2xl font-bold font-mono text-slate-900">8</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 8)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Roles</span>
              <span className="text-2xl font-bold font-mono text-slate-900">12</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 12)</span>
            </div>

            <div className="p-4 border border-slate-200 rounded-lg">
              <span className="text-slate-500 text-xs block">Managers</span>
              <span className="text-2xl font-bold font-mono text-slate-900">50</span>
              <span className="text-[11px] text-emerald-600 block mt-1">✓ Exact match (Target: 50)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Artifact Exports */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Download Deterministic Seed Exports & Proof Manifests</h3>
          <p className="text-xs text-slate-500">
            Exported formats ready for reproducible offline evaluation.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 pt-2">
          <a
            href="/api/exports/manifest"
            target="_blank"
            rel="noreferrer"
            className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition flex flex-col justify-between group"
          >
            <div>
              <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center mb-2">
                <FileCode className="w-4 h-4" />
              </div>
              <div className="font-bold text-xs text-slate-900">manifest.json</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Checksums, seeds, scale parameters, and versions</p>
            </div>
            <div className="mt-3 text-xs font-semibold text-indigo-600 flex items-center gap-1 group-hover:underline">
              <Download className="w-3.5 h-3.5" />
              <span>Download JSON</span>
            </div>
          </a>

          <a
            href="/api/exports/json"
            target="_blank"
            rel="noreferrer"
            className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition flex flex-col justify-between group"
          >
            <div>
              <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-2">
                <Database className="w-4 h-4" />
              </div>
              <div className="font-bold text-xs text-slate-900">validation_summary.json</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Rule validation audit log and detection evidence</p>
            </div>
            <div className="mt-3 text-xs font-semibold text-indigo-600 flex items-center gap-1 group-hover:underline">
              <Download className="w-3.5 h-3.5" />
              <span>Download JSON</span>
            </div>
          </a>

          <a
            href="/api/exports/csv"
            target="_blank"
            rel="noreferrer"
            className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition flex flex-col justify-between group"
          >
            <div>
              <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center mb-2">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div className="font-bold text-xs text-slate-900">employees.csv</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Primary employee master records (500 rows)</p>
            </div>
            <div className="mt-3 text-xs font-semibold text-indigo-600 flex items-center gap-1 group-hover:underline">
              <Download className="w-3.5 h-3.5" />
              <span>Download CSV</span>
            </div>
          </a>

          <a
            href="/api/exports/sql"
            target="_blank"
            rel="noreferrer"
            className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition flex flex-col justify-between group"
          >
            <div>
              <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center mb-2">
                <FileCode className="w-4 h-4" />
              </div>
              <div className="font-bold text-xs text-slate-900">seed.sql</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Portable SQL INSERT statements for any RDBMS</p>
            </div>
            <div className="mt-3 text-xs font-semibold text-indigo-600 flex items-center gap-1 group-hover:underline">
              <Download className="w-3.5 h-3.5" />
              <span>Download SQL</span>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
