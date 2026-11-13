# YottaFlex Employee Lifecycle Orchestrator - Data Dictionary

This document defines the schema metadata for every entity in the YottaFlex Employee Lifecycle Orchestrator.
Every entity includes explicit data types, nullability, allowed enums, units, primary/foreign key definitions, and business validation rules.

---

## 1. Catalog & Organizational Entities

### 1.1 `departments`
Catalog of operational departments within the organization.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `department_id` | VARCHAR(32) | Required (PK) | `DEP-01` to `DEP-08` | Unique | None | Primary key. Must follow `DEP-XX` convention. |
| `name` | VARCHAR(100) | Required | Engineering, Product, Design, Sales, Marketing, HR, Finance, IT | Unique | None | Department display name. |
| `code` | VARCHAR(10) | Required | ENG, PRD, DSN, SLS, MKT, HRD, FIN, ITD | Unique | None | 3-letter uppercase department code. |
| `cost_center` | VARCHAR(20) | Required | e.g. `CC-101`, `CC-401` | Non-unique | None | Cost center identifier for finance billing. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Record creation timestamp. |

---

### 1.2 `roles`
Role taxonomy with assigned security clearance level.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `role_id` | VARCHAR(32) | Required (PK) | `ROL-01` to `ROL-12` | Unique | None | Primary key. Must follow `ROL-XX` convention. |
| `title` | VARCHAR(100) | Required | e.g. "Software Engineer" | Non-unique | None | Standard job title. |
| `department_id` | VARCHAR(32) | Required (FK) | Valid `departments.department_id` | Non-unique | `departments(department_id)` | Must reference existing department. |
| `clearance_level`| VARCHAR(20) | Required | STANDARD, ELEVATED, RESTRICTED, CONFIDENTIAL, ADMIN | Non-unique | None | Minimum clearance required for role. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Creation timestamp. |

---

### 1.3 `managers`
Designated leaders responsible for task review, 1-on-1 kickoffs, and access approvals.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `manager_id` | VARCHAR(32) | Required (PK) | `MGR-001` to `MGR-050` | Unique | None | Deterministic zero-padded ID. |
| `name` | VARCHAR(100) | Required | Text | Non-unique | None | Full legal name. |
| `email` | VARCHAR(120) | Required | `*@yottaflex.internal` | Unique | None | Corporate email address. |
| `department_id` | VARCHAR(32) | Required (FK) | Valid `departments.department_id` | Non-unique | `departments(department_id)` | Department the manager belongs to. |
| `management_level` | VARCHAR(20)| Required | L1, L2, L3, DIRECTOR, VP | Non-unique | None | Seniority tier for approval routing. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Creation timestamp. |

---

### 1.4 `employees`
Master employee record containing employment parameters.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `employee_id` | VARCHAR(32) | Required (PK) | `EMP-000001` to `EMP-000500` | Unique | None | Immutable zero-padded ID. |
| `first_name` | VARCHAR(60) | Required | Text | Non-unique | None | Legal first name. |
| `last_name` | VARCHAR(60) | Required | Text | Non-unique | None | Legal last name. |
| `email` | VARCHAR(120) | Required | `*@yottaflex.internal` | Unique | None | Work email. |
| `department_id` | VARCHAR(32) | Required (FK) | Valid `departments.department_id` | Non-unique | `departments(department_id)` | Current active department. |
| `role_id` | VARCHAR(32) | Required (FK) | Valid `roles.role_id` | Non-unique | `roles(role_id)` | Current active role. |
| `manager_id` | VARCHAR(32) | Optional (FK) | Valid `managers.manager_id` or NULL | Non-unique | `managers(manager_id)` | Nullable for Anomaly #2 (Missing Manager). |
| `location_type` | VARCHAR(20) | Required | REMOTE, HYBRID, ONSITE | Non-unique | None | Work arrangement location. |
| `employment_type`| VARCHAR(20) | Required | FULL_TIME, CONTRACTOR | Non-unique | None | Contractual relationship. |
| `status` | VARCHAR(20) | Required | PENDING, ACTIVE, TERMINATED | Non-unique | None | Lifecycle state. |
| `start_date` | DATETIME | Required | UTC timestamp | Non-unique | None | First day of employment. |
| `end_date` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Effective exit date for terminated staff. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Record initiation timestamp. |
| `updated_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Last mutation timestamp. |

---

### 1.5 `employee_department_history`
Effective-dated tracking for inter-departmental transfers and organizational changes.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `history_id` | VARCHAR(32) | Required (PK) | `EDH-000001`+ | Unique | None | Sequential history record ID. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Non-unique | `employees(employee_id)` | Affected employee. |
| `department_id` | VARCHAR(32) | Required (FK) | Valid `departments.department_id` | Non-unique | `departments(department_id)` | Department during this interval. |
| `effective_start_date` | DATETIME | Required | UTC timestamp | Non-unique | None | Beginning of effective interval. |
| `effective_end_date` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | End of interval (NULL if current). |
| `change_reason` | VARCHAR(255)| Required | Text | Non-unique | None | Justification for transfer. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Creation timestamp. |

---

## 2. Onboarding Workflow & Task Entities

### 2.1 `task_templates`
Standardized blueprint for employee onboarding milestones.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `template_id` | VARCHAR(32) | Required (PK) | `TPL-001` to `TPL-008` | Unique | None | Template identifier. |
| `title` | VARCHAR(120) | Required | Text | Non-unique | None | Task name. |
| `description` | TEXT | Required | Text | Non-unique | None | SOP instructions for task fulfillment. |
| `owner_team` | VARCHAR(20) | Required | HR, IT, FACILITIES, MANAGER, SECURITY | Non-unique | None | Functional team accountable. |
| `default_sla_days` | INTEGER | Required | 1 to 5 days | Non-unique | None | Standard SLA in days. |
| `is_mandatory` | BOOLEAN | Required | True / False | Non-unique | None | Completion required for clearance. |
| `sequence_order` | INTEGER | Required | 1 to 8 | Non-unique | None | Standard ordinal step. |
| `phase` | VARCHAR(30) | Required | PRE_START, DAY_ONE, FIRST_WEEK, POST_START | Non-unique | None | Milestone phase. |

---

### 2.2 `task_dependencies`
Directed acyclic graph edges defining prerequisite rules between tasks.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dependency_id` | VARCHAR(32) | Required (PK) | `DEP-TPL-01`+ | Unique | None | Dependency rule ID. |
| `predecessor_template_id` | VARCHAR(32) | Required (FK) | Valid `task_templates.template_id` | Non-unique | `task_templates(template_id)` | Prerequisite task template. |
| `successor_template_id` | VARCHAR(32) | Required (FK) | Valid `task_templates.template_id` | Non-unique | `task_templates(template_id)` | Successor task template. |
| `dependency_type` | VARCHAR(20) | Required | FINISH_TO_START | Non-unique | None | Successor cannot complete before predecessor. |

---

### 2.3 `onboarding_cases`
Lifecycle container for a new hire's onboarding process.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `case_id` | VARCHAR(32) | Required (PK) | `ONB-2026-000001`+ | Unique | None | Onboarding case number. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Unique | `employees(employee_id)` | 1:1 relationship with Employee. |
| `status` | VARCHAR(20) | Required | INITIATED, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED | Non-unique | None | Case lifecycle status. |
| `target_start_date`| DATETIME | Required | UTC timestamp | Non-unique | None | Planned start date. |
| `actual_start_date`| DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Actual work start date. |
| `sla_target_date` | DATETIME | Required | UTC timestamp | Non-unique | None | Maximum allowable completion deadline. |
| `completed_at` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Timestamp when all 8 tasks completed. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Initiation timestamp. |
| `updated_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Mutation timestamp. |

---

### 2.4 `task_instances`
Concrete execution instances generated per onboarding case (8 instances per case = 4,000 tasks total).

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `task_id` | VARCHAR(64) | Required (PK) | `TASK-ONB-<case_id>-001` to `008` | Unique | None | Unique task instance identifier. |
| `case_id` | VARCHAR(32) | Required (FK) | Valid `onboarding_cases.case_id` | Non-unique | `onboarding_cases(case_id)` | Parent onboarding case. |
| `template_id` | VARCHAR(32) | Required (FK) | Valid `task_templates.template_id` | Non-unique | `task_templates(template_id)` | Blueprint template. |
| `title` | VARCHAR(120) | Required | Text | Non-unique | None | Task name. |
| `owner_team` | VARCHAR(20) | Required | HR, IT, FACILITIES, MANAGER, SECURITY | Non-unique | None | Accountable department. |
| `status` | VARCHAR(20) | Required | PENDING, BLOCKED, IN_PROGRESS, COMPLETED, FAILED | Non-unique | None | Current task progress. |
| `is_blocked` | BOOLEAN | Required | True / False | Non-unique | None | Flag indicating pending prerequisites. |
| `blocked_reason` | VARCHAR(255)| Optional | Text or NULL | Non-unique | None | Reason why task cannot proceed. |
| `due_date` | DATETIME | Required | UTC timestamp | Non-unique | None | Target SLA deadline. |
| `completed_at` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Actual fulfillment timestamp. |
| `completed_by` | VARCHAR(60) | Optional | Text or NULL | Non-unique | None | Actor who completed the task. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Generation timestamp. |
| `updated_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Update timestamp. |

---

## 3. Hardware Fleet & Asset Lifecycle

### 3.1 `assets`
Physical IT inventory items (600 devices total).

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `asset_id` | VARCHAR(32) | Required (PK) | `AST-LAP-000001`, `AST-MON-000001`, etc. | Unique | None | Asset ID with category code. |
| `asset_tag` | VARCHAR(32) | Required | `YF-LAP-000001`+ | Unique | None | Physical barcode tag. |
| `category` | VARCHAR(30) | Required | LAPTOP, MONITOR, SECURITY_KEY, MOBILE_PHONE, HEADSET | Non-unique | None | Asset hardware type. |
| `model` | VARCHAR(80) | Required | Text | Non-unique | None | Make and model description. |
| `serial_number` | VARCHAR(50) | Required | Unique hardware SN | Unique | None | Manufacturer serial number. |
| `status` | VARCHAR(20) | Required | AVAILABLE, ASSIGNED, MAINTENANCE, RETIRED | Non-unique | None | Inventory allocation status. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Inventory procurement date. |

---

### 3.2 `asset_assignments`
Assignment ledger connecting assets to employees.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `assignment_id` | VARCHAR(32) | Required (PK) | `ASGN-000001`+ | Unique | None | Assignment ledger ID. |
| `asset_id` | VARCHAR(32) | Required (FK) | Valid `assets.asset_id` | Non-unique | `assets(asset_id)` | Assigned device. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Non-unique | `employees(employee_id)` | Device custodian. |
| `assigned_date` | DATETIME | Required | UTC timestamp | Non-unique | None | Custody transfer timestamp. |
| `return_due_date`| DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Expected return date. |
| `returned_date` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Physical recovery date. |
| `status` | VARCHAR(20) | Required | ACTIVE, RETURNED, OVERDUE | Non-unique | None | Custody state. Overlapping ACTIVE is Anomaly #3. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Record creation timestamp. |

---

## 4. Access Management & Approvals

### 4.1 `access_requests`
Formal requests for enterprise system entitlements (300 requests total).

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `request_id` | VARCHAR(32) | Required (PK) | `ACCREQ-2026-000001`+ | Unique | None | Request ID. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Non-unique | `employees(employee_id)` | Requesting employee. |
| `system_name` | VARCHAR(60) | Required | EMAIL_SLACK, GITHUB, AWS_CLOUD, JIRA_CONFLUENCE, ERP_FINANCE, HRIS, VPN_INTERNAL | Non-unique | None | Target enterprise platform. |
| `access_level` | VARCHAR(20) | Required | READ, WRITE, ADMIN | Non-unique | None | Entitlement tier. |
| `status` | VARCHAR(20) | Required | REQUESTED, APPROVED, REJECTED, PROVISIONED, REVOKED | Non-unique | None | Lifecycle state. |
| `justification` | VARCHAR(255)| Required | Text | Non-unique | None | Business necessity statement. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Submission timestamp. |
| `updated_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Update timestamp. |

---

### 4.2 `approvals`
Manager and security lead approvals gating access provisioning.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `approval_id` | VARCHAR(32) | Required (PK) | `APPR-000001`+ | Unique | None | Approval record ID. |
| `request_id` | VARCHAR(32) | Required (FK) | Valid `access_requests.request_id` | Non-unique | `access_requests(request_id)` | Linked access request. |
| `approver_id` | VARCHAR(32) | Required | Valid `managers.manager_id` or actor | Non-unique | None | Reviewing authority. |
| `approver_role` | VARCHAR(30) | Required | MANAGER, IT_ADMIN, SECURITY_LEAD | Non-unique | None | Role context. |
| `status` | VARCHAR(20) | Required | PENDING, APPROVED, REJECTED | Non-unique | None | Decision outcome. |
| `decided_at` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Timestamp of decision. |
| `comments` | VARCHAR(255)| Optional | Text or NULL | Non-unique | None | Reviewer notes. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Creation timestamp. |

---

### 4.3 `access_grants`
Active system access authorizations provisioned after approval.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `grant_id` | VARCHAR(32) | Required (PK) | `GRANT-000001`+ | Unique | None | Provisioned grant ID. |
| `request_id` | VARCHAR(32) | Required (FK) | Valid `access_requests.request_id` | Non-unique | `access_requests(request_id)` | Gating approved request. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Non-unique | `employees(employee_id)` | Granted employee. |
| `system_name` | VARCHAR(60) | Required | Valid enterprise platform | Non-unique | None | Active system. |
| `access_level` | VARCHAR(20) | Required | READ, WRITE, ADMIN | Non-unique | None | Entitlement level. |
| `provisioned_at`| DATETIME | Required | UTC timestamp | Non-unique | None | Credential issuance timestamp. |
| `revoked_at` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Revocation timestamp. |
| `status` | VARCHAR(20) | Required | ACTIVE, REVOKED | Non-unique | None | State. ACTIVE on terminated user is Anomaly #5. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Record timestamp. |

---

## 5. Offboarding & Audit Entities

### 5.1 `offboarding_cases`
Exit workflow for separating employees.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `offboarding_id`| VARCHAR(32) | Required (PK) | `OFF-2026-000001`+ | Unique | None | Case ID. |
| `employee_id` | VARCHAR(32) | Required (FK) | Valid `employees.employee_id` | Unique | `employees(employee_id)` | Terminated employee. |
| `reason` | VARCHAR(50) | Required | RESIGNATION, TERMINATION, CONTRACT_END | Non-unique | None | Reason for departure. |
| `termination_date`| DATETIME | Required | UTC timestamp | Non-unique | None | Last day of employment. |
| `status` | VARCHAR(20) | Required | INITIATED, IN_PROGRESS, COMPLETED | Non-unique | None | Exit workflow state. |
| `access_revocation_status` | VARCHAR(20) | Required | PENDING, IN_PROGRESS, COMPLETED | Non-unique | None | Status of IT credential de-provisioning. |
| `asset_recovery_status` | VARCHAR(20) | Required | PENDING, IN_PROGRESS, COMPLETED | Non-unique | None | Status of hardware returns. |
| `completed_at` | DATETIME | Optional | UTC timestamp or NULL | Non-unique | None | Completion timestamp. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Initiation timestamp. |

---

### 5.2 `audit_events`
Immutable write-only audit trail preserving state transitions and actor attribution.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `audit_id` | VARCHAR(64) | Required (PK) | `AUD-<YYYYMMDD>-000001`+ | Unique | None | Audit event sequence key. |
| `entity_type` | VARCHAR(40) | Required | Employee, TaskInstance, OnboardingCase, Asset, AccessGrant, etc. | Non-unique | None | Mutated entity model. |
| `entity_id` | VARCHAR(64) | Required | Target entity PK | Non-unique | None | Entity identifier. |
| `action` | VARCHAR(50) | Required | CREATE, UPDATE_STATUS, APPROVE, PROVISION, REVOKE, ASSIGN, RECOVER | Non-unique | None | Operation executed. |
| `actor` | VARCHAR(60) | Required | HR_ADMIN, IT_ADMIN, SYSTEM, MGR-XXX, etc. | Non-unique | None | Authorized initiator. |
| `old_state_json`| TEXT | Optional | JSON string or NULL | Non-unique | None | Previous attributes snapshot. |
| `new_state_json`| TEXT | Optional | JSON string or NULL | Non-unique | None | New attributes snapshot. |
| `timestamp` | DATETIME | Required | UTC timestamp | Non-unique | None | Exact wall-clock event time. |
| `reason` | VARCHAR(255)| Optional | Text or NULL | Non-unique | None | Business justification. |

---

### 5.3 `issue_records`
Ground truth and detected issue register.

| Field Name | Type | Required? | Allowed Values / Enum | Uniqueness | Foreign Key | Validation / Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `issue_id` | VARCHAR(32) | Required (PK) | `ISS-000001`+ | Unique | None | Issue record key. |
| `entity_id` | VARCHAR(64) | Required | Primary key of affected entity | Non-unique | None | Target entity. |
| `issue_type` | VARCHAR(60) | Required | One of the 7 anomaly types | Non-unique | None | Classification code. |
| `severity` | VARCHAR(20) | Required | CRITICAL, HIGH, MEDIUM, LOW | Non-unique | None | Risk severity rating. |
| `status` | VARCHAR(20) | Required | OPEN, RESOLVED, SUPPRESSED | Non-unique | None | Resolution state. |
| `rule_id` | VARCHAR(40) | Required | e.g. `RULE-TASK-001` | Non-unique | None | Specific rule breached. |
| `evidence_json` | TEXT | Required | JSON string | Non-unique | None | Structured audit evidence. |
| `created_at` | DATETIME | Required | UTC timestamp | Non-unique | None | Detection / injection timestamp. |
