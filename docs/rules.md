# YottaFlex Business Workflow Rules & Anomaly Detection Logic

This document specifies the business rules governing employee lifecycle orchestration, state machine transitions, prerequisite graphs, and the detection logic for all seven injected anomalies.

---

## 1. Core Workflow Rules

### Rule 1: Acyclic Task Dependency (RULE-DAG-001)
- The onboarding process is modeled as a Directed Acyclic Graph (DAG) across 8 task templates.
- **Topological Sorting**: Before any task is added or dependency mapped, the dependency graph is checked for cycles. Any cyclic edge (e.g. A depends on B and B depends on A) is rejected immediately.

### Rule 2: Prerequisite Completion Enforcement (RULE-TASK-001)
- A task instance cannot transition to `COMPLETED` if any of its direct predecessor task instances in the same onboarding case are in `PENDING`, `BLOCKED`, or `FAILED` status.
- Example: **TPL-003 (Create Corporate Email & SSO Identity)** strictly requires **TPL-001 (Verify Identity & I-9 Documents)** to be `COMPLETED`. Attempting to complete TPL-003 prior to TPL-001 raises `PREREQUISITE_NOT_MET`.

### Rule 3: Background Check Clearance Before Start (RULE-ONB-004)
- **TPL-002 (Background Check Screening)** is a `PRE_START` task.
- An employee cannot start work or enter `ACTIVE` employment status before their background check has been verified and cleared (`completed_at <= start_date`).

### Rule 4: Two-Phase Gated Access Provisioning (RULE-ACC-008)
- Actual system credentials (`AccessGrant`) can **never** be provisioned directly from a raw request.
- The workflow mandates:
  1. Employee submits `AccessRequest` (status: `REQUESTED`).
  2. Designated manager or security lead reviews and records an `Approval` record with status `APPROVED`.
  3. Only after `request.status == APPROVED` may IT operations provision credentials and create an active `AccessGrant`.

### Rule 5: Non-Overlapping Asset Allocation (RULE-AST-003)
- An IT hardware asset can only be actively in the custody of **one** employee at any point in time.
- Attempting to assign an asset that already has an assignment record with `status == ACTIVE` and `returned_date == NULL` raises `ASSET_DOUBLE_ASSIGNMENT`.

### Rule 6: Zero-Trust Offboarding & Asset Recovery (RULE-OFF-001)
- Initiating employee termination sets `employee.status = TERMINATED` and creates an `OffboardingCase`.
- **Immediate Credential Revocation**: Offboarding cannot close until all active `AccessGrant` records belonging to the employee are updated to `status = REVOKED` and assigned `revoked_at` timestamps.
- **Hardware Reconciliation**: All physical assets in the custodian's possession must be returned and marked `AVAILABLE`.

### Rule 7: Immutable Audit Trail (RULE-AUD-001)
- Overwriting history or in-place silent modifications are strictly forbidden.
- Every state mutation must persist:
  - `TaskStatusEvent` for task lifecycle transitions.
  - `CaseStatusEvent` for case progress milestones.
  - `AccessEvent` for entitlement provisioning and revocation.
  - `AuditEvent` recording entity type, entity ID, actor, old state JSON snapshot, new state JSON snapshot, timestamp, and business justification.

---

## 2. Seven Required Anomaly Categories & Detection Logic

The synthetic generator deterministically injects 7 distinct anomaly types into valid baseline data.
The rule-based validator scans raw database tables **without reading `ground_truth.json`** to detect each issue.

| # | Anomaly Code | Name | Injected Mechanism | Independent Validator Detection Logic | Severity |
| :- | :--- | :--- | :--- | :--- | :- |
| **1** | `TASK_COMPLETED_BEFORE_PREREQUISITE` | Premature Task Completion | TPL-003 completed while predecessor TPL-001 is PENDING, or completed at timestamp earlier than TPL-001. | Inspects each completed task; queries predecessor task instances in the same case; flags if predecessor is not completed or if predecessor's `completed_at > successor.completed_at`. | HIGH |
| **2** | `MISSING_MANAGER` | Missing Direct Supervisor | Employee record generated with `manager_id = None`. | Scans `employees` table for records where `manager_id IS NULL`. | HIGH |
| **3** | `ASSET_DOUBLE_ASSIGNMENT` | Overlapping Asset Custody | Two `AssetAssignment` records for the same device both having `status = ACTIVE` and `returned_date IS NULL`. | Groups active assignments by `asset_id`; flags any asset associated with `len(active_assignments) > 1`. | HIGH |
| **4** | `STARTED_BEFORE_BACKGROUND_CHECK` | Premature Work Start | Employee has `start_date <= REFERENCE_DATE` and `status = ACTIVE`, but TPL-002 background check is `PENDING` or `completed_at > start_date`. | Joins employee with their onboarding case's TPL-002 task; flags employees starting before background check completion. | CRITICAL |
| **5** | `TERMINATED_EMPLOYEE_ACTIVE_ACCESS` | Ghost Credential Retention | Employee has `status = TERMINATED` and `end_date` in past, but possesses an `AccessGrant` with `status = ACTIVE`. | Scans `access_grants` where `status = ACTIVE`; checks whether corresponding employee's status is `TERMINATED`. | CRITICAL |
| **6** | `OVERDUE_INCOMPLETE_TASK` | SLA Deadline Breach | Task is in `PENDING` or `IN_PROGRESS` status and its `due_date < REFERENCE_DATE`. | Queries all incomplete tasks where `due_date < ref_date`. Computes days overdue. | MEDIUM |
| **7** | `DEPARTMENT_CHANGE_MID_PROCESS` | Mid-Onboarding Transfer | Employee's department was changed while their onboarding case was still active (`IN_PROGRESS`). | Scans `employee_department_history` for multiple entries where a transfer occurred between `case.created_at` and `case.completed_at`. | MEDIUM |
