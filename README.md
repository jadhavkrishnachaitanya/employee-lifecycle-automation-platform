# YottaFlex Employee Lifecycle Orchestrator

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.3-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Pytest](https://img.shields.io/badge/Pytest-22%2F22%20Passing-success.svg)](https://pytest.org/)
[![Precision & Recall](https://img.shields.io/badge/F1%20Score-100%25-brightgreen.svg)]()

> Complete, working, beginner-understandable hackathon submission for the **YottaFlex.ai Associate AI Forward Deployed Engineer Round 2 Challenge**.

---

## 1. Project Overview & Problem Statement

### The Problem
In high-growth organizations, employee onboarding and offboarding are fragmented across multiple functional silos:
- **Human Resources**: Validates legal identity, background checks, and department contracts.
- **IT Operations**: Creates SSO accounts, provisions enterprise software entitlements (Slack, GitHub, AWS, Jira), and manages access keys.
- **Facilities & Logistics**: Allocates corporate laptops, monitors, security tokens, and coordinates physical equipment return upon exit.
- **Hiring Managers**: Conducts team kickoffs, assigns buddies, and reviews role access requests.

When these operations lack a centralized orchestration engine:
1. Tasks are completed out of order (e.g. provisioning corporate email before identity verification).
2. Unapproved system access is granted without manager sign-off.
3. Assets are double-assigned or unrecovered upon employee departure.
4. Terminated employees retain active credentials ("ghost access"), creating massive security liabilities.
5. In-flight department transfers disrupt prerequisite checklists.

### The Solution: YottaFlex Orchestrator
The **YottaFlex Employee Lifecycle Orchestrator** is an automated workflow engine that models onboarding as a Directed Acyclic Graph (DAG), enforces two-phase authorization on access entitlements, prevents overlapping asset allocations, and maintains an immutable, write-only audit trail for compliance (SOC2/GDPR).

---

## 2. Key Features

- **8-Step Standardized Onboarding DAG**: Pre-start identity & background screening, Day 1 SSO & hardware provisioning, Week 1 security training, and final clearance.
- **Deterministic Synthetic Data Engine**: Generates EXACT enterprise-scale figures—**500 employees**, **8 departments**, **12 roles**, **50 managers**, **500 onboarding cases**, **4,000 tasks**, **600 assets**, and **300 access requests**—using fixed seed `20261022`.
- **Seven Injected Real-World Anomalies**: Clearly labeled and verified via independent rule-based detection with **100% Precision, 100% Recall, and 100% F1 score**.
- **Two-Phase Gated Access Control**: Access requests must receive manager approval before IT credentials can be provisioned.
- **Zero-Trust Offboarding**: One-click revocation of all active system grants and automated tracking of physical asset recovery.
- **Immutable Audit Trail**: Chronological event logs with user attribution, timestamps, and JSON diffs of state mutations.
- **12 Interactive Frontend Dashboards**: Built with React, Tailwind CSS, Lucide icons, and Recharts.

---

## 3. Technology Stack

| Layer | Technologies Used | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic V2 | REST API, business logic, workflow engine |
| **Database** | SQLite 3 | Embedded relational storage with foreign key constraints |
| **Frontend** | React 19, Vite, Tailwind CSS 3.4, Recharts, Lucide React | Modern interactive dashboard UI |
| **Data Generation** | Python `Faker`, NumPy, Deterministic LCG | Synthetic data generation with seed 20261022 |
| **Testing** | Pytest, HTTPX | Automated test suite (22 unit, integration, and API tests) |

---

## 4. Project Directory Structure

```text
yottaflex-employee-lifecycle/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── router.py              # 28 REST API endpoints
│   │   ├── models/
│   │   │   └── entities.py            # SQLAlchemy database models & enums
│   │   ├── schemas/
│   │   │   └── schemas.py             # Pydantic request/response schemas
│   │   ├── services/
│   │   │   └── orchestrator_service.py # Core business rules & audit logging
│   │   ├── database.py                # Database connection & session factory
│   │   └── main.py                    # FastAPI application entrypoint
│   ├── generator/
│   │   ├── data_generator.py          # Deterministic synthetic data generator
│   │   ├── validator.py               # Independent rule-based detection engine
│   │   ├── exporter.py                # CSV, SQL, JSON, and manifest exporter
│   │   └── cli.py                     # CLI entrypoint (--scale, --seed, --output)
│   ├── tests/
│   │   ├── conftest.py                # Isolated in-memory SQLite fixtures
│   │   ├── test_generation_and_counts.py # Exact counts & ID formatting tests
│   │   ├── test_workflow_rules.py     # DAG, prerequisite & approval tests
│   │   ├── test_anomalies_and_validation.py # Anomaly detection & evaluation tests
│   │   └── test_api_endpoints.py      # REST API integration tests
│   └── requirements.txt               # Backend Python dependencies
├── data/
│   ├── starter/                       # 25 employees, 200 tasks (Starter scale)
│   └── full/                          # 500 employees, 4000 tasks (Full scale)
│       ├── orchestrator.db            # SQLite database
│       ├── manifest.json              # SHA-256 file checksums & row counts
│       ├── validation_summary.json    # Independent validator audit log
│       ├── ground_truth.json          # 36 injected ground-truth anomalies
│       ├── ground_truth.csv           # Tabular ground truth
│       ├── seed.sql                   # SQL INSERT statements
│       └── *.csv                      # CSV exports for all 15 relational tables
├── docs/
│   ├── data_dictionary.md             # Complete schema metadata & field definitions
│   ├── schema.md                      # Relationship cardinalities & Mermaid ERD
│   ├── rules.md                       # Business workflow rules & anomaly logic
│   ├── reproducibility.md             # Seed parameters & verification hashes
│   ├── acceptance_matrix.md           # Requirement-to-code traceability matrix
│   └── interview_demo.md              # 5-minute technical demonstration script
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js              # Fetch client connecting to backend
│   │   ├── components/
│   │   │   ├── Sidebar.jsx            # 12-page navigation sidebar
│   │   │   ├── Header.jsx             # Top bar with refresh & status indicator
│   │   │   └── Badge.jsx              # Status, team, and severity badge pills
│   │   ├── pages/                     # 12 functional dashboards
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Employees.jsx
│   │   │   ├── Onboarding.jsx
│   │   │   ├── Tasks.jsx
│   │   │   ├── Approvals.jsx
│   │   │   ├── AccessManagement.jsx
│   │   │   ├── Assets.jsx
│   │   │   ├── Offboarding.jsx
│   │   │   ├── Anomalies.jsx
│   │   │   ├── Analytics.jsx
│   │   │   ├── AuditTrail.jsx
│   │   │   └── DataGenerator.jsx
│   │   ├── App.jsx                    # Root React component
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── requirements.txt                   # Root Python dependencies
├── .env.example                       # Environment configuration template
├── .gitignore
└── README.md                          # Documentation
```

---

## 5. Setup & Installation Commands

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ (tested on Node.js v26.13)
- npm or pnpm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/yottaflex-employee-lifecycle.git
cd yottaflex-employee-lifecycle

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 6. How to Run

### Generate Datasets
```bash
# Generate the Full Scale dataset (500 employees, 4,000 tasks)
python -m backend.generator.cli --scale full --seed 20261022 --output data/full

# Generate the Starter dataset (25 employees, 200 tasks)
python -m backend.generator.cli --scale starter --seed 20261022 --output data/starter
```

### Run Automated Tests (Pytest)
```bash
python -m pytest backend/tests -v
```
*(All 22 test cases pass in under 4 seconds with zero warnings).*

### Start the Backend API Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: **http://127.0.0.1:8000/docs**

### Start the React Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## 7. The Seven Injected Anomalies

The synthetic data engine deterministically injects 7 realistic lifecycle failure modes:

| # | Anomaly Type | Rule ID | Description | Severity |
| :- | :--- | :--- | :--- | :- |
| **1** | `TASK_COMPLETED_BEFORE_PREREQUISITE` | `RULE-TASK-001` | Corporate SSO task completed while identity verification is still pending. | HIGH |
| **2** | `MISSING_MANAGER` | `RULE-ORG-002` | Employee created with nullable `manager_id = None` without broken foreign keys. | HIGH |
| **3** | `ASSET_DOUBLE_ASSIGNMENT` | `RULE-AST-003` | Two active asset assignment records for the same hardware device. | HIGH |
| **4** | `STARTED_BEFORE_BACKGROUND_CHECK` | `RULE-ONB-004` | Employee starts work while background screening is still incomplete. | CRITICAL |
| **5** | `TERMINATED_EMPLOYEE_ACTIVE_ACCESS` | `RULE-ACC-005` | Terminated employee retains an active enterprise system credential grant. | CRITICAL |
| **6** | `OVERDUE_INCOMPLETE_TASK` | `RULE-TASK-006` | Incomplete task whose due date has passed relative to the evaluation date. | MEDIUM |
| **7** | `DEPARTMENT_CHANGE_MID_PROCESS` | `RULE-ONB-007` | Employee transfers department during active onboarding case window. | MEDIUM |

### Independent Validation Benchmark
The validator scans database tables without reading `ground_truth.json`:
- **True Positives (TP)**: 36
- **False Positives (FP)**: 0
- **False Negatives (FN)**: 0
- **Precision**: 100.0%
- **Recall**: 100.0%
- **F1 Score**: 100.0%

---

## 8. Reproducibility & Verification

To verify that the dataset is 100% deterministic:
```powershell
python -m backend.generator.cli --scale full --seed 20261022 --output data/test_run_1
python -m backend.generator.cli --scale full --seed 20261022 --output data/test_run_2

python -c "
import json
m1 = json.load(open('data/test_run_1/manifest.json'))['file_checksums']
m2 = json.load(open('data/test_run_2/manifest.json'))['file_checksums']
for f in sorted(m1.keys()):
    assert m1[f] == m2[f], f'Mismatch in {f}'
print('All 20 output tables and artifacts match 100% bit-for-bit!')
"
```

---

## 9. Design Decisions & Limitations

### Design Decisions
1. **Fixed Logical Reference Date (`2026-11-01T00:00:00Z`)**: Prevents non-deterministic wall-clock differences when evaluating SLA breaches across different days or timezones.
2. **Zero-Padded Identifiers**: Prevents alphanumeric sorting collisions (`EMP-000001` vs `EMP-1`).
3. **Strict Two-Phase Access Authorization**: Requesting access and provisioning access are separated by an affirmative `Approval` state transition.
4. **Isolated Test Fixtures**: Tests execute against ephemeral in-memory SQLite instances to guarantee that tests never mutate exported fixture data.

### Known Limitations
- The current implementation utilizes SQLite for zero-configuration local evaluation. For multi-region clustering with 100,000+ simultaneous transactions, PostgreSQL with row-level locking would be recommended.
- Single-factor password authentication is bypassed in local demo mode in favor of zero-friction evaluation.

---

## 10. Submission Checklist

- [x] Complete working frontend (React + Vite + Tailwind CSS + Recharts)
- [x] Complete working backend (FastAPI + SQLAlchemy + SQLite)
- [x] Exact requested counts (500 employees, 8 departments, 12 roles, 50 managers, 500 cases, 4000 tasks, 600 assets, 300 access requests)
- [x] Fixed seed `20261022` and reproducible SHA-256 checksums
- [x] All 7 injected anomalies detected independently without ground truth leakage
- [x] All 28 REST API endpoints implemented and functioning
- [x] 22 automated pytest tests passing
- [x] `docs/data_dictionary.md`, `docs/schema.md`, `docs/rules.md`, `docs/reproducibility.md`, `docs/acceptance_matrix.md`, and `docs/interview_demo.md` complete
- [x] Clean zero-error production build
