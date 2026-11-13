# YottaFlex Challenge Acceptance Matrix

This matrix maps every single challenge requirement from the YottaFlex Associate AI Forward Deployed Engineer Round 2 prompt to actual implementation files, REST API endpoints, automated pytest test cases, and empirical verification evidence.

---

## Part A: Project Structure & Scaffolding

| Requirement | Code Files / Artifacts | Verification / Evidence |
| :--- | :--- | :--- |
| `frontend/` (React app) | `frontend/src/` (Vite, React 19, Tailwind CSS, Recharts) | Built cleanly via `npm run build` with zero syntax/bundling errors. |
| `backend/app/` (FastAPI backend) | `backend/app/main.py`, `backend/app/database.py`, `backend/app/api/router.py`, `backend/app/models/entities.py`, `backend/app/services/orchestrator_service.py` | FastAPI server running with complete Pydantic schemas and SQLAlchemy models. |
| `backend/generator/` (Data generation) | `backend/generator/data_generator.py`, `backend/generator/exporter.py`, `backend/generator/validator.py`, `backend/generator/cli.py` | CLI tool generates starter/full datasets deterministically. |
| `backend/tests/` (Automated tests) | `backend/tests/test_generation_and_counts.py`, `backend/tests/test_workflow_rules.py`, `backend/tests/test_anomalies_and_validation.py`, `backend/tests/test_api_endpoints.py` | All 22 pytest tests passing cleanly in 3.55 seconds. |
| `data/starter/` and `data/full/` | `data/starter/` (25 emp, 200 tasks), `data/full/` (500 emp, 4000 tasks) | SQLite databases, CSVs, JSON, SQL seed files, and manifests generated. |
| Documentation | `docs/data_dictionary.md`, `docs/schema.md`, `docs/rules.md`, `docs/reproducibility.md`, `docs/acceptance_matrix.md`, `docs/interview_demo.md`, `README.md` | Comprehensive technical and interview documentation created. |

---

## Part B: Database Model & Data Dictionary

| Requirement | Implementation Files | Evidence / Details |
| :--- | :--- | :--- |
| Core Entities (Employee, Department, Role, Manager, OnboardingCase, TaskTemplate, TaskInstance, Asset, AccessRequest, Approval, AuditEvent) | `backend/app/models/entities.py` | All 11 core entities implemented with primary keys, indexes, and relationships. |
| Supporting Entities (OffboardingCase, TaskDependency, AssetAssignment, AccessGrant, EmployeeDepartmentHistory, CaseStatusEvent, TaskStatusEvent, AccessEvent, IssueRecord) | `backend/app/models/entities.py` | All supporting entities and bridge tables implemented. |
| Data Dictionary | `docs/data_dictionary.md` | Explicit table containing field types, nullability, enums, units, uniqueness, FKs, and rules. |
| Schema & Mermaid ERD | `docs/schema.md` | Full relational cardinality documentation and Mermaid ER diagram. |

---

## Part C: Deterministic Synthetic Data Generator

| Requirement | Code & Configuration | Empirical Evidence / Actual Output |
| :--- | :--- | :--- |
| Fixed seed `20261022` | `backend/generator/data_generator.py` (seed=20261022) | Pinned pseudo-random seed across Faker, Python random, and generators. |
| Configurable `--scale`, `--seed`, `--output` | `backend/generator/cli.py` | CLI flags parsed and verified across starter and full scales. |
| **Exact 500 Employees** | `data_generator.py` (`self.target_employees = 500`) | Exact count verified: 500 records in `employees.csv` & SQLite. |
| **Exact 8 Departments** | `data_generator.py` (`self.target_departments = 8`) | Exact count verified: 8 departments (`DEP-01` to `DEP-08`). |
| **Exact 12 Roles** | `data_generator.py` (`self.target_roles = 12`) | Exact count verified: 12 roles across 8 departments. |
| **Exact 50 Managers** | `data_generator.py` (`self.target_managers = 50`) | Exact count verified: 50 managers across L1 to VP tiers. |
| **Exact 500 Onboarding Cases** | `data_generator.py` (`self.target_cases = 500`) | Exact count verified: 500 onboarding cases (`ONB-2026-000001`+). |
| **Exact 4,000 Task Instances** | `data_generator.py` (500 cases × 8 templates = 4000) | Exact count verified: 4,000 tasks (`TASK-ONB-...`). |
| **Exact 600 Assets** | `data_generator.py` (`self.target_assets = 600`) | Exact count verified: 600 hardware assets (`AST-LAP-000001`+). |
| **Exact 300 Access Requests** | `data_generator.py` (`self.target_access_requests = 300`) | Exact count verified: 300 entitlement requests (`ACCREQ-2026-...`). |
| Deterministic ID Formatting | Zero-padded IDs (`EMP-000001`, `ONB-2026-000001`, `TASK-ONB-ONB-2026-000001-001`, `AST-LAP-000001`) | Tested and verified in `test_id_formatting_and_uniqueness`. |

---

## Part D: Business Workflow & State Enforcement

| Workflow Rule | Service / Model File | Test Case |
| :--- | :--- | :--- |
| DAG Acyclicity | `backend/generator/validator.py` (`_check_acyclic_dependencies`) | `test_dependency_graph_cycle_rejection` |
| Identity Verification precedes Account Creation | `backend/app/services/orchestrator_service.py` (`update_task_status`) | `test_account_creation_blocked_until_identity_verification` |
| Background Check Clearance precedes Work Start | `backend/generator/validator.py` (`_detect_started_before_background_check`) | `test_workflow_rules.py` |
| Access Provisioning requires prior Approval | `backend/app/services/orchestrator_service.py` (`provision_access_request`) | `test_provisioning_blocked_before_approval` |
| Valid Approval and Provisioning Flow | `backend/app/services/orchestrator_service.py` (`approve_access_request`) | `test_successful_approval_and_provisioning_flow` |
| Asset Double-Assignment Prevention | `backend/app/services/orchestrator_service.py` (`assign_asset`) | `test_asset_assignment_and_recovery` |
| Termination initiates Offboarding & Access Revocation | `backend/app/services/orchestrator_service.py` (`initiate_offboarding`, `revoke_offboarding_access`) | `test_offboarding_workflow_and_access_revocation` |
| Immutable Audit Event Preservation | `backend/app/services/orchestrator_service.py` (`log_audit_event`) | `test_task_event_and_audit_preservation` |

---

## Part E & F: Seven Injected Anomalies & Rule-Based Validation

| # | Anomaly Type | Rule ID | Ground Truth Records | Independent Detection | Precision | Recall | F1 Score |
| :- | :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| 1 | `TASK_COMPLETED_BEFORE_PREREQUISITE` | `RULE-TASK-001` | 5 | 5 | 1.0000 | 1.0000 | 1.0000 |
| 2 | `MISSING_MANAGER` | `RULE-ORG-002` | 5 | 5 | 1.0000 | 1.0000 | 1.0000 |
| 3 | `ASSET_DOUBLE_ASSIGNMENT` | `RULE-AST-003` | 4 | 4 | 1.0000 | 1.0000 | 1.0000 |
| 4 | `STARTED_BEFORE_BACKGROUND_CHECK` | `RULE-ONB-004` | 5 | 5 | 1.0000 | 1.0000 | 1.0000 |
| 5 | `TERMINATED_EMPLOYEE_ACTIVE_ACCESS` | `RULE-ACC-005` | 5 | 5 | 1.0000 | 1.0000 | 1.0000 |
| 6 | `OVERDUE_INCOMPLETE_TASK` | `RULE-TASK-006` | 7 | 7 | 1.0000 | 1.0000 | 1.0000 |
| 7 | `DEPARTMENT_CHANGE_MID_PROCESS` | `RULE-ONB-007` | 5 | 5 | 1.0000 | 1.0000 | 1.0000 |
| **Total** | **All 7 Required Anomalies** | - | **36** | **36** | **1.0000** | **1.0000** | **1.0000** |

Zero ground-truth leakage verified: `RuleBasedValidator` operates purely on raw database rows without access to `ground_truth.json`.

---

## Part G: Reproducibility & Exports

| Requirement | Code / Tool | Verification Evidence |
| :--- | :--- | :--- |
| Deterministic Hashing Across Runs | `backend/generator/exporter.py` (`export_dataset`) | Two distinct runs in separate temp directories produced identical SHA-256 hashes across all 20 tables/files. |
| Machine-readable Manifest | `data/full/manifest.json` | Contains seed (`20261022`), scale (`full`), reference date, row counts, and checksums. |
| CSV, JSON, SQL Seed Exports | `data/full/*.csv`, `seed.sql`, `ground_truth.json`, `validation_summary.json` | Generated and accessible via `/api/exports/{format}`. |

---

## Part H: REST API Endpoints

All 28 endpoints required by the challenge prompt are implemented and active:
- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/employees`
- `POST /api/employees`
- `GET /api/employees/{id}`
- `GET /api/departments`
- `GET /api/roles`
- `GET /api/managers`
- `GET /api/onboarding`
- `POST /api/onboarding`
- `GET /api/onboarding/{id}`
- `GET /api/tasks`
- `PATCH /api/tasks/{id}/status`
- `GET /api/assets`
- `POST /api/assets/{id}/assign`
- `POST /api/assets/{id}/recover`
- `GET /api/access-requests`
- `POST /api/access-requests`
- `POST /api/access-requests/{id}/approve`
- `POST /api/access-requests/{id}/provision`
- `GET /api/offboarding`
- `POST /api/offboarding`
- `POST /api/offboarding/{id}/revoke-access`
- `GET /api/approvals`
- `GET /api/audit-events`
- `GET /api/anomalies`
- `GET /api/validation`
- `GET /api/metrics`
- `GET /api/exports/{format}`

---

## Part I: Frontend Architecture (12 Views)

1. **Overview Dashboard** (`Dashboard.jsx`): Headcount, task status donut, team bar chart, SLA breach counter, anomaly cards.
2. **Employees** (`Employees.jsx`): Searchable/filterable employee directory, detail modal, new employee creation.
3. **Onboarding** (`Onboarding.jsx`): Case progression, 8-task visual sequence, dependency blocking indicators.
4. **Tasks** (`Tasks.jsx`): Task queue filterable by team/status, status transition buttons with prerequisite rejection feedback.
5. **Approvals** (`Approvals.jsx`): Pending approvals list, Approve/Reject two-phase commit buttons.
6. **Access Management** (`AccessManagement.jsx`): Entitlement requests, approval gating, credential provisioning.
7. **Assets** (`Assets.jsx`): 600-item device fleet, allocation, recovery, double-assignment policy testing.
8. **Offboarding** (`Offboarding.jsx`): Exit cases, zero-trust credential revocation, physical asset reconciliation.
9. **Anomaly Detection** (`Anomalies.jsx`): Interactive review board for all 7 injected anomaly categories with JSON evidence viewer and live re-scan.
10. **Analytics & SLA** (`Analytics.jsx`): Real-time metrics, completion rate, SLA adherence, ground-truth evaluation scorecard.
11. **Audit Trail** (`AuditTrail.jsx`): Chronological ledger of state transitions, actor attribution, and JSON diffs.
12. **Data Generator & Reproducibility** (`DataGenerator.jsx`): Seed 20261022 provenance, exact row count audit, and direct export downloads.
