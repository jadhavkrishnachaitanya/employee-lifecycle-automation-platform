# YottaFlex 5-Minute Technical Demonstration Script

This script is structured for an Associate AI Forward Deployed Engineer interview presentation to showcase the full-stack architecture, deterministic data engine, dependency enforcement, and anomaly detection.

---

## ⏱️ Minute 0:00 - 1:00: Problem Context & Architectural Overview
**Speaker Script:**
> *"Hello! Today I am presenting the YottaFlex Employee Lifecycle Orchestrator. When organizations scale, coordinating HR, IT, Facilities, and Managers across onboarding and offboarding often breaks down: tasks get completed out of order, terminated employees retain active access, and hardware gets double-assigned without an audit trail.*
>
> *To solve this, we built a complete, production-grade system:
> 1. A Python FastAPI backend with SQLAlchemy and SQLite.
> 2. A deterministic synthetic data engine producing exact enterprise-scale figures—500 employees, 4,000 tasks, 600 assets, and 300 access requests—using fixed seed 20261022.
> 3. An independent rule-based validator that audits database records for 7 specific lifecycle anomalies without ground-truth leakage.
> 4. A clean React + Vite + Tailwind CSS + Recharts dashboard connecting directly to live REST endpoints."*

---

## ⏱️ Minute 1:00 - 2:00: Deterministic Data Engine & Reproducibility Proof
**Speaker Script:**
> *"Let's first look at the data generator in `Data & Validation` tab:
> - Notice the exact row counts: precisely 500 employees across 8 departments, 50 managers, 12 roles, 500 onboarding cases, 4,000 onboarding tasks (8 per employee), 600 assets, and 300 access requests.
> - Every ID follows zero-padded deterministic schemas like `EMP-000001`, `ONB-2026-000001`, and `AST-LAP-000001`.
> - Crucially, we use a fixed logical reference date (`2026-11-01T00:00:00Z`) to eliminate non-deterministic wall-clock skew in overdue calculations.
> - To prove bit-for-bit reproducibility, our test suite generates the dataset twice into separate directories and verifies that all 20 SHA-256 file checksums match 100% identically."*

---

## ⏱️ Minute 2:00 - 3:00: Workflow Rules & Prerequisite Enforcement
**Speaker Script:**
> *"Now let's navigate to the `Onboarding` and `Tasks` portals to see real business rule enforcement in action:
> - Onboarding is modeled as a Directed Acyclic Graph (DAG) across 8 standardized steps.
> - Identity verification (TPL-001) MUST precede Corporate Email/SSO creation (TPL-003).
> - Let's test what happens if an operator attempts to complete TPL-003 while TPL-001 is still pending:
>   - The backend service catches this immediately, raises an `OrchestrationError` with code `PREREQUISITE_NOT_MET`, and rejects the transition.
> - The same applies to access management: we enforce a strict two-phase commit. An access request cannot transition to `PROVISIONED` without an affirmative `Approval` record by a manager.
> - Every single state transition logs an immutable `AuditEvent` with actor attribution, old state, and new state snapshots."*

---

## ⏱️ Minute 3:00 - 4:00: Seven Injected Anomalies & Ground-Truth Evaluation
**Speaker Script:**
> *"Next, let's explore the core AI / Data Engineering capability: Anomaly Detection.
> We deterministically injected 7 distinct real-world failure modes:
> 1. Tasks completed before their prerequisite.
> 2. Employees with missing direct managers.
> 3. Hardware assets assigned twice with overlapping active dates.
> 4. Employees starting work before background check clearance.
> 5. Terminated employees retaining active system access.
> 6. Overdue incomplete tasks breaching SLA.
> 7. Employees changing departments mid-onboarding.
>
> In the `Anomalies` view, click **Run Independent Validator**:
> - The validator scans raw database tables using relational logic without ever reading the ground truth.
> - In `Analytics`, we evaluate detection performance against the ground-truth manifest:
>   - **Precision: 100.0%**
>   - **Recall: 100.0%**
>   - **F1 Score: 100.0%**
>   - Exactly 36 out of 36 true injected anomalies detected with zero false positives."*

---

## ⏱️ Minute 4:00 - 5:00: Offboarding Reconciliation & Automated Testing
**Speaker Script:**
> *"Finally, let's examine employee exit in `Offboarding`:
> - When an employee resigns or is terminated, the system flags outstanding active grants and hardware in their possession.
> - Clicking **Revoke All Credentials** marks all active access grants as `REVOKED`, stamps `revoked_at`, and generates audit events.
> - In the terminal, our automated pytest suite runs 22 comprehensive tests in 3.55 seconds covering exact counts, ID formatting, DAG acyclicity, prerequisite rejection, asset recovery, all 7 anomalies, and REST endpoints.
>
> The system is fully working, beginner-understandable, and ready for deployment. Thank you!"*
