import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import json
import os
from faker import Faker

from backend.app.models.entities import (
    Department,
    Role,
    Manager,
    Employee,
    EmployeeDepartmentHistory,
    TaskTemplate,
    TaskDependency,
    OnboardingCase,
    TaskInstance,
    TaskStatusEvent,
    CaseStatusEvent,
    Asset,
    AssetAssignment,
    AccessRequest,
    Approval,
    AccessGrant,
    AccessEvent,
    OffboardingCase,
    AuditEvent,
    IssueRecord,
    LocationType,
    EmploymentType,
    EmployeeStatus,
    CaseStatus,
    TaskStatus,
    TeamOwner,
    AssetCategory,
    AssetStatus,
    AssignmentStatus,
    RequestStatus,
    AccessLevel,
    ApprovalStatus,
    GrantStatus,
    OffboardingStatus,
    IssueSeverity,
    IssueStatus,
)

# Reference date for deterministic evaluations
REFERENCE_DATE = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

DEPARTMENTS_CATALOG = [
    {"department_id": "DEP-01", "name": "Engineering", "code": "ENG", "cost_center": "CC-101"},
    {"department_id": "DEP-02", "name": "Product", "code": "PRD", "cost_center": "CC-102"},
    {"department_id": "DEP-03", "name": "Design", "code": "DSN", "cost_center": "CC-103"},
    {"department_id": "DEP-04", "name": "Sales", "code": "SLS", "cost_center": "CC-201"},
    {"department_id": "DEP-05", "name": "Marketing", "code": "MKT", "cost_center": "CC-202"},
    {"department_id": "DEP-06", "name": "Human Resources", "code": "HRD", "cost_center": "CC-301"},
    {"department_id": "DEP-07", "name": "Finance", "code": "FIN", "cost_center": "CC-302"},
    {"department_id": "DEP-08", "name": "Information Technology", "code": "ITD", "cost_center": "CC-401"},
]

ROLES_CATALOG = [
    {"role_id": "ROL-01", "title": "Software Engineer", "department_id": "DEP-01", "clearance_level": "ELEVATED"},
    {"role_id": "ROL-02", "title": "Senior Staff Engineer", "department_id": "DEP-01", "clearance_level": "RESTRICTED"},
    {"role_id": "ROL-03", "title": "QA Automation Engineer", "department_id": "DEP-01", "clearance_level": "STANDARD"},
    {"role_id": "ROL-04", "title": "Product Manager", "department_id": "DEP-02", "clearance_level": "STANDARD"},
    {"role_id": "ROL-05", "title": "Product Operations Specialist", "department_id": "DEP-02", "clearance_level": "STANDARD"},
    {"role_id": "ROL-06", "title": "Senior UX/UI Designer", "department_id": "DEP-03", "clearance_level": "STANDARD"},
    {"role_id": "ROL-07", "title": "Account Executive", "department_id": "DEP-04", "clearance_level": "STANDARD"},
    {"role_id": "ROL-08", "title": "Sales Development Rep", "department_id": "DEP-04", "clearance_level": "STANDARD"},
    {"role_id": "ROL-09", "title": "Growth Marketing Lead", "department_id": "DEP-05", "clearance_level": "STANDARD"},
    {"role_id": "ROL-10", "title": "People Operations Generalist", "department_id": "DEP-06", "clearance_level": "CONFIDENTIAL"},
    {"role_id": "ROL-11", "title": "Financial Analyst", "department_id": "DEP-07", "clearance_level": "CONFIDENTIAL"},
    {"role_id": "ROL-12", "title": "Systems Infrastructure Engineer", "department_id": "DEP-08", "clearance_level": "ADMIN"},
]

TASK_TEMPLATES_CATALOG = [
    {
        "template_id": "TPL-001",
        "title": "Verify Identity & I-9 Documents",
        "description": "HR verifies legal identity documents and I-9 work authorization prior to work start.",
        "owner_team": TeamOwner.HR.value,
        "default_sla_days": 2,
        "is_mandatory": True,
        "sequence_order": 1,
        "phase": "PRE_START",
    },
    {
        "template_id": "TPL-002",
        "title": "Background Check Screening",
        "description": "Third-party criminal, credit, and education background verification clearance.",
        "owner_team": TeamOwner.HR.value,
        "default_sla_days": 5,
        "is_mandatory": True,
        "sequence_order": 2,
        "phase": "PRE_START",
    },
    {
        "template_id": "TPL-003",
        "title": "Create Corporate Email & SSO Identity",
        "description": "IT provisions corporate Google/Okta identity and SSO directory entry.",
        "owner_team": TeamOwner.IT.value,
        "default_sla_days": 1,
        "is_mandatory": True,
        "sequence_order": 3,
        "phase": "DAY_ONE",
    },
    {
        "template_id": "TPL-004",
        "title": "Provision Core Hardware & Peripherals",
        "description": "Facilities/IT ships corporate laptop, monitor, and security token.",
        "owner_team": TeamOwner.FACILITIES.value,
        "default_sla_days": 3,
        "is_mandatory": True,
        "sequence_order": 4,
        "phase": "DAY_ONE",
    },
    {
        "template_id": "TPL-005",
        "title": "Request Role-Specific System Access",
        "description": "IT submits and verifies role-based entitlements in GitHub, AWS, Jira, and ERP.",
        "owner_team": TeamOwner.IT.value,
        "default_sla_days": 2,
        "is_mandatory": True,
        "sequence_order": 5,
        "phase": "DAY_ONE",
    },
    {
        "template_id": "TPL-006",
        "title": "Manager 1-on-1 & Team Introduction",
        "description": "Direct manager conducts initial kickoff, role alignment, and assigns buddy.",
        "owner_team": TeamOwner.MANAGER.value,
        "default_sla_days": 1,
        "is_mandatory": True,
        "sequence_order": 6,
        "phase": "DAY_ONE",
    },
    {
        "template_id": "TPL-007",
        "title": "Security Compliance & Data Privacy Training",
        "description": "Employee completes mandatory SOC2, GDPR, and security awareness modules.",
        "owner_team": TeamOwner.SECURITY.value,
        "default_sla_days": 4,
        "is_mandatory": True,
        "sequence_order": 7,
        "phase": "FIRST_WEEK",
    },
    {
        "template_id": "TPL-008",
        "title": "Final Onboarding Clearance & Sign-Off",
        "description": "HR verifies background check, access, assets, and training completion for full active status.",
        "owner_team": TeamOwner.HR.value,
        "default_sla_days": 1,
        "is_mandatory": True,
        "sequence_order": 8,
        "phase": "POST_START",
    },
]

TASK_DEPENDENCIES = [
    {"dependency_id": "DEP-TPL-01", "predecessor_template_id": "TPL-001", "successor_template_id": "TPL-003", "dependency_type": "FINISH_TO_START"},
    {"dependency_id": "DEP-TPL-02", "predecessor_template_id": "TPL-003", "successor_template_id": "TPL-005", "dependency_type": "FINISH_TO_START"},
    {"dependency_id": "DEP-TPL-03", "predecessor_template_id": "TPL-003", "successor_template_id": "TPL-007", "dependency_type": "FINISH_TO_START"},
    {"dependency_id": "DEP-TPL-04", "predecessor_template_id": "TPL-002", "successor_template_id": "TPL-008", "dependency_type": "FINISH_TO_START"},
    {"dependency_id": "DEP-TPL-05", "predecessor_template_id": "TPL-005", "successor_template_id": "TPL-008", "dependency_type": "FINISH_TO_START"},
    {"dependency_id": "DEP-TPL-06", "predecessor_template_id": "TPL-007", "successor_template_id": "TPL-008", "dependency_type": "FINISH_TO_START"},
]

ENTERPRISE_SYSTEMS = [
    "EMAIL_SLACK",
    "GITHUB",
    "AWS_CLOUD",
    "JIRA_CONFLUENCE",
    "ERP_FINANCE",
    "HRIS",
    "VPN_INTERNAL",
]


class SyntheticDataGenerator:
    def __init__(self, seed: int = 20261022, scale: str = "full"):
        self.seed = seed
        self.scale = scale
        self.ref_date = REFERENCE_DATE

        random.seed(seed)
        self.faker = Faker()
        Faker.seed(seed)

        if scale == "full":
            self.target_employees = 500
            self.target_managers = 50
            self.target_roles = 12
            self.target_departments = 8
            self.target_cases = 500
            self.target_tasks = 4000
            self.target_assets = 600
            self.target_access_requests = 300
        else:
            self.target_employees = 25
            self.target_managers = 5
            self.target_roles = 12
            self.target_departments = 8
            self.target_cases = 25
            self.target_tasks = 200
            self.target_assets = 35
            self.target_access_requests = 20

        self.departments: List[Department] = []
        self.roles: List[Role] = []
        self.managers: List[Manager] = []
        self.employees: List[Employee] = []
        self.department_history: List[EmployeeDepartmentHistory] = []
        self.task_templates: List[TaskTemplate] = []
        self.task_dependencies: List[TaskDependency] = []
        self.onboarding_cases: List[OnboardingCase] = []
        self.task_instances: List[TaskInstance] = []
        self.task_status_events: List[TaskStatusEvent] = []
        self.case_status_events: List[CaseStatusEvent] = []
        self.assets: List[Asset] = []
        self.asset_assignments: List[AssetAssignment] = []
        self.access_requests: List[AccessRequest] = []
        self.approvals: List[Approval] = []
        self.access_grants: List[AccessGrant] = []
        self.access_events: List[AccessEvent] = []
        self.offboarding_cases: List[OffboardingCase] = []
        self.audit_events: List[AuditEvent] = []
        self.issue_records: List[IssueRecord] = []
        self.ground_truth: List[Dict[str, Any]] = []

        self.audit_seq = 0
        self.tse_seq = 0
        self.cse_seq = 0
        self.ace_seq = 0
        self.asgn_seq = 0
        self.grant_seq = 0
        self.appr_seq = 0
        self.issue_seq = 0
        self.hist_seq = 0

    def next_audit_id(self, date_val: datetime) -> str:
        self.audit_seq += 1
        d_str = date_val.strftime("%Y%m%d")
        return f"AUD-{d_str}-{self.audit_seq:06d}"

    def next_tse_id(self) -> str:
        self.tse_seq += 1
        return f"TSE-{self.tse_seq:06d}"

    def next_cse_id(self) -> str:
        self.cse_seq += 1
        return f"CSE-{self.cse_seq:06d}"

    def next_ace_id(self) -> str:
        self.ace_seq += 1
        return f"ACE-{self.ace_seq:06d}"

    def next_asgn_id(self) -> str:
        self.asgn_seq += 1
        return f"ASGN-{self.asgn_seq:06d}"

    def next_grant_id(self) -> str:
        self.grant_seq += 1
        return f"GRANT-{self.grant_seq:06d}"

    def next_appr_id(self) -> str:
        self.appr_seq += 1
        return f"APPR-{self.appr_seq:06d}"

    def next_issue_id(self) -> str:
        self.issue_seq += 1
        return f"ISS-{self.issue_seq:06d}"

    def next_hist_id(self) -> str:
        self.hist_seq += 1
        return f"EDH-{self.hist_seq:06d}"

    def record_ground_truth(
        self,
        entity_id: str,
        issue_type: str,
        expected_label: str,
        severity: str,
        evidence: Dict[str, Any],
        rule_id: str,
    ):
        issue_id = self.next_issue_id()
        record = {
            "issue_id": issue_id,
            "entity_id": entity_id,
            "issue_type": issue_type,
            "expected_label": expected_label,
            "severity": severity,
            "evidence": json.dumps(evidence),
            "rule_id": rule_id,
        }
        self.ground_truth.append(record)

        self.issue_records.append(
            IssueRecord(
                issue_id=issue_id,
                entity_id=entity_id,
                issue_type=issue_type,
                severity=severity,
                status=IssueStatus.OPEN.value,
                rule_id=rule_id,
                evidence_json=json.dumps(evidence),
                created_at=self.ref_date,
            )
        )

    def generate_catalogs(self):
        for d in DEPARTMENTS_CATALOG[: self.target_departments]:
            dep = Department(
                department_id=d["department_id"],
                name=d["name"],
                code=d["code"],
                cost_center=d["cost_center"],
                created_at=self.ref_date - timedelta(days=365),
            )
            self.departments.append(dep)

        for r in ROLES_CATALOG[: self.target_roles]:
            role = Role(
                role_id=r["role_id"],
                title=r["title"],
                department_id=r["department_id"],
                clearance_level=r["clearance_level"],
                created_at=self.ref_date - timedelta(days=365),
            )
            self.roles.append(role)

        for t in TASK_TEMPLATES_CATALOG:
            tmpl = TaskTemplate(
                template_id=t["template_id"],
                title=t["title"],
                description=t["description"],
                owner_team=t["owner_team"],
                default_sla_days=t["default_sla_days"],
                is_mandatory=t["is_mandatory"],
                sequence_order=t["sequence_order"],
                phase=t["phase"],
            )
            self.task_templates.append(tmpl)

        for dep in TASK_DEPENDENCIES:
            td = TaskDependency(
                dependency_id=dep["dependency_id"],
                predecessor_template_id=dep["predecessor_template_id"],
                successor_template_id=dep["successor_template_id"],
                dependency_type=dep["dependency_type"],
            )
            self.task_dependencies.append(td)

    def generate_managers(self):
        dep_ids = [d.department_id for d in self.departments]
        levels = ["L1", "L2", "L3", "DIRECTOR", "VP"]
        level_weights = [0.45, 0.30, 0.15, 0.07, 0.03]

        for i in range(1, self.target_managers + 1):
            mgr_id = f"MGR-{i:03d}"
            name = self.faker.name()
            clean_name = name.lower().replace(" ", ".").replace("'", "")
            email = f"{clean_name}.mgr@yottaflex.internal"
            dept_id = dep_ids[(i - 1) % len(dep_ids)]
            lvl = random.choices(levels, weights=level_weights, k=1)[0]
            mgr = Manager(
                manager_id=mgr_id,
                name=name,
                email=email,
                department_id=dept_id,
                management_level=lvl,
                created_at=self.ref_date - timedelta(days=300),
            )
            self.managers.append(mgr)

    def generate_employees(self):
        loc_types = [LocationType.REMOTE.value, LocationType.HYBRID.value, LocationType.ONSITE.value]
        loc_weights = [0.40, 0.40, 0.20]
        emp_types = [EmploymentType.FULL_TIME.value, EmploymentType.CONTRACTOR.value]
        emp_weights = [0.85, 0.15]

        mgr_by_dept = {}
        for m in self.managers:
            mgr_by_dept.setdefault(m.department_id, []).append(m.manager_id)

        role_by_dept = {}
        for r in self.roles:
            role_by_dept.setdefault(r.department_id, []).append(r.role_id)

        dep_ids = [d.department_id for d in self.departments]

        missing_mgr_indices = {8, 19} if self.scale == "starter" else {8, 19, 108, 219, 350}
        terminated_indices = {5, 15} if self.scale == "starter" else {5, 15, 30, 115, 230, 345, 410}
        dept_change_indices = {7, 22} if self.scale == "starter" else {7, 22, 107, 222, 360}
        bg_check_anomaly_cases = {12, 25} if self.scale == "starter" else {12, 25, 112, 225, 420}

        for i in range(1, self.target_employees + 1):
            emp_id = f"EMP-{i:06d}"
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@yottaflex.internal"

            dept_id = dep_ids[(i - 1) % len(dep_ids)]
            avail_roles = role_by_dept.get(dept_id, [self.roles[0].role_id])
            role_id = avail_roles[(i - 1) % len(avail_roles)]

            avail_mgrs = mgr_by_dept.get(dept_id, [self.managers[0].manager_id])
            manager_id = avail_mgrs[(i - 1) % len(avail_mgrs)]

            if i in missing_mgr_indices:
                manager_id = None
                self.record_ground_truth(
                    entity_id=emp_id,
                    issue_type="MISSING_MANAGER",
                    expected_label="VIOLATION",
                    severity=IssueSeverity.HIGH.value,
                    evidence={"employee_id": emp_id, "department_id": dept_id, "manager_id": None},
                    rule_id="RULE-ORG-002",
                )

            loc = random.choices(loc_types, weights=loc_weights, k=1)[0]
            etype = random.choices(emp_types, weights=emp_weights, k=1)[0]

            if i in bg_check_anomaly_cases:
                start_date = self.ref_date - timedelta(days=10)
                status = EmployeeStatus.ACTIVE.value
                end_date = None
            elif i in terminated_indices:
                start_date = self.ref_date - timedelta(days=45)
                status = EmployeeStatus.TERMINATED.value
                end_date = self.ref_date - timedelta(days=5)
            elif i % 2 == 0:
                start_date = self.ref_date - timedelta(days=20 + (i % 20))
                status = EmployeeStatus.ACTIVE.value
                end_date = None
            else:
                start_date = self.ref_date + timedelta(days=(i % 15) + 1)
                status = EmployeeStatus.PENDING.value
                end_date = None

            created_at = start_date - timedelta(days=14)

            emp = Employee(
                employee_id=emp_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department_id=dept_id,
                role_id=role_id,
                manager_id=manager_id,
                location_type=loc,
                employment_type=etype,
                status=status,
                start_date=start_date,
                end_date=end_date,
                created_at=created_at,
                updated_at=created_at,
            )
            self.employees.append(emp)

            self.audit_events.append(
                AuditEvent(
                    audit_id=self.next_audit_id(created_at),
                    entity_type="Employee",
                    entity_id=emp_id,
                    action="CREATE_EMPLOYEE",
                    actor="HR_ADMIN",
                    new_state_json=json.dumps(
                        {"employee_id": emp_id, "department_id": dept_id, "role_id": role_id, "start_date": str(start_date)}
                    ),
                    timestamp=created_at,
                    reason="New employee registered in HRIS",
                )
            )

            hist_id = self.next_hist_id()
            self.department_history.append(
                EmployeeDepartmentHistory(
                    history_id=hist_id,
                    employee_id=emp_id,
                    department_id=dept_id,
                    effective_start_date=created_at,
                    effective_end_date=None,
                    change_reason="Initial hire assignment",
                    created_at=created_at,
                )
            )

            # Anomaly #7: Department Change Mid-Process
            if i in dept_change_indices:
                other_dep_id = dep_ids[(dep_ids.index(dept_id) + 1) % len(dep_ids)]
                # Set transfer date to be 6 days after created_at (well before start_date and before ref_date)
                transfer_date = created_at + timedelta(days=6)
                self.department_history[-1].effective_end_date = transfer_date
                new_hist_id = self.next_hist_id()
                self.department_history.append(
                    EmployeeDepartmentHistory(
                        history_id=new_hist_id,
                        employee_id=emp_id,
                        department_id=other_dep_id,
                        effective_start_date=transfer_date,
                        effective_end_date=None,
                        change_reason="Emergency operational reassignment during onboarding",
                        created_at=transfer_date,
                    )
                )
                emp.department_id = other_dep_id
                emp.updated_at = transfer_date

                self.record_ground_truth(
                    entity_id=emp_id,
                    issue_type="DEPARTMENT_CHANGE_MID_PROCESS",
                    expected_label="REVIEW_REQUIRED",
                    severity=IssueSeverity.MEDIUM.value,
                    evidence={
                        "employee_id": emp_id,
                        "original_dept": dept_id,
                        "new_dept": other_dep_id,
                        "transfer_date": str(transfer_date),
                        "onboarding_active": True,
                    },
                    rule_id="RULE-ONB-007",
                )

    def generate_onboarding_cases_and_tasks(self):
        premature_task_cases = {3, 18} if self.scale == "starter" else {3, 18, 103, 218, 380}
        bg_check_anomaly_cases = {12, 25} if self.scale == "starter" else {12, 25, 112, 225, 420}
        overdue_task_cases = {4, 14, 24} if self.scale == "starter" else {4, 14, 24, 104, 214, 324, 450}

        for idx, emp in enumerate(self.employees, start=1):
            case_id = f"ONB-2026-{idx:06d}"
            target_start = emp.start_date
            sla_target = target_start + timedelta(days=7)
            case_created = emp.created_at

            is_completed_case = (
                (emp.status in [EmployeeStatus.ACTIVE.value, EmployeeStatus.TERMINATED.value])
                and (idx not in bg_check_anomaly_cases)
                and (idx not in overdue_task_cases)
                and (idx not in premature_task_cases)
                and (target_start < self.ref_date)
            )

            case_status = CaseStatus.COMPLETED.value if is_completed_case else CaseStatus.IN_PROGRESS.value
            completed_at = target_start + timedelta(days=5) if is_completed_case else None
            actual_start = target_start if (target_start <= self.ref_date) else None

            case = OnboardingCase(
                case_id=case_id,
                employee_id=emp.employee_id,
                status=case_status,
                target_start_date=target_start,
                actual_start_date=actual_start,
                sla_target_date=sla_target,
                completed_at=completed_at,
                created_at=case_created,
                updated_at=case_created,
            )
            self.onboarding_cases.append(case)

            self.case_status_events.append(
                CaseStatusEvent(
                    event_id=self.next_cse_id(),
                    case_id=case_id,
                    old_status=None,
                    new_status=CaseStatus.INITIATED.value,
                    actor="HR_ADMIN",
                    timestamp=case_created,
                    reason="Onboarding case initiated for new hire",
                )
            )

            case_tasks: Dict[str, TaskInstance] = {}
            for t_idx, tmpl in enumerate(self.task_templates, start=1):
                task_id = f"TASK-ONB-{case_id}-{t_idx:03d}"

                if is_completed_case:
                    t_status = TaskStatus.COMPLETED.value
                    is_blocked = False
                    blocked_reason = None
                    if tmpl.template_id == "TPL-001":
                        t_due = target_start - timedelta(days=4)
                        t_completed_at = target_start - timedelta(days=5)
                    elif tmpl.template_id == "TPL-002":
                        t_due = target_start - timedelta(days=2)
                        t_completed_at = target_start - timedelta(days=3)
                    elif tmpl.template_id in ["TPL-003", "TPL-004", "TPL-005", "TPL-006"]:
                        t_due = target_start + timedelta(days=1)
                        t_completed_at = target_start
                    elif tmpl.template_id == "TPL-007":
                        t_due = target_start + timedelta(days=4)
                        t_completed_at = target_start + timedelta(days=3)
                    else:
                        t_due = target_start + timedelta(days=5)
                        t_completed_at = target_start + timedelta(days=5)
                elif idx in overdue_task_cases or idx in premature_task_cases:
                    # Cases where background check completed normally before start date!
                    if tmpl.template_id == "TPL-001":
                        t_status = TaskStatus.COMPLETED.value
                        t_due = target_start - timedelta(days=4)
                        t_completed_at = target_start - timedelta(days=5)
                        is_blocked = False
                        blocked_reason = None
                    elif tmpl.template_id == "TPL-002":
                        # Background check completed normally before work start!
                        t_status = TaskStatus.COMPLETED.value
                        t_due = target_start - timedelta(days=2)
                        t_completed_at = target_start - timedelta(days=3)
                        is_blocked = False
                        blocked_reason = None
                    elif tmpl.template_id == "TPL-003":
                        t_status = TaskStatus.COMPLETED.value
                        t_due = target_start + timedelta(days=1)
                        t_completed_at = target_start
                        is_blocked = False
                        blocked_reason = None
                    elif tmpl.template_id == "TPL-004":
                        t_status = TaskStatus.IN_PROGRESS.value
                        t_due = self.ref_date - timedelta(days=8) if idx in overdue_task_cases else target_start + timedelta(days=2)
                        t_completed_at = None
                        is_blocked = False
                        blocked_reason = None
                    else:
                        t_status = TaskStatus.PENDING.value
                        t_due = self.ref_date + timedelta(days=tmpl.sequence_order)
                        t_completed_at = None
                        is_blocked = True
                        blocked_reason = "Waiting for prerequisite steps"
                else:
                    # Normal in-progress case
                    t_due = max(target_start + timedelta(days=tmpl.sequence_order - 1), self.ref_date + timedelta(days=tmpl.sequence_order))
                    if tmpl.sequence_order == 1:
                        t_status = TaskStatus.COMPLETED.value
                        t_completed_at = case_created + timedelta(days=1)
                        is_blocked = False
                        blocked_reason = None
                    elif tmpl.sequence_order == 2:
                        t_status = TaskStatus.IN_PROGRESS.value
                        t_completed_at = None
                        is_blocked = False
                        blocked_reason = None
                    elif tmpl.sequence_order == 3:
                        t_status = TaskStatus.IN_PROGRESS.value
                        t_completed_at = None
                        is_blocked = False
                        blocked_reason = None
                    else:
                        t_status = TaskStatus.PENDING.value
                        t_completed_at = None
                        is_blocked = True
                        blocked_reason = "Waiting for prerequisite steps"

                task = TaskInstance(
                    task_id=task_id,
                    case_id=case_id,
                    template_id=tmpl.template_id,
                    title=tmpl.title,
                    owner_team=tmpl.owner_team,
                    status=t_status,
                    is_blocked=is_blocked,
                    blocked_reason=blocked_reason,
                    due_date=t_due,
                    completed_at=t_completed_at,
                    completed_by="SYSTEM" if t_completed_at else None,
                    created_at=case_created,
                    updated_at=case_created,
                )
                case_tasks[tmpl.template_id] = task
                self.task_instances.append(task)

            # Injected Anomaly #1: Task completed before prerequisite
            if idx in premature_task_cases:
                t1 = case_tasks["TPL-001"]
                t3 = case_tasks["TPL-003"]
                t3.status = TaskStatus.COMPLETED.value
                t3.completed_at = self.ref_date - timedelta(days=4)
                t1.status = TaskStatus.PENDING.value
                t1.completed_at = None
                # Ensure t1 and t4 are not overdue to isolate the premature completion anomaly
                t1.due_date = self.ref_date + timedelta(days=2)
                if "TPL-004" in case_tasks:
                    case_tasks["TPL-004"].due_date = self.ref_date + timedelta(days=4)

                self.record_ground_truth(
                    entity_id=t3.task_id,
                    issue_type="TASK_COMPLETED_BEFORE_PREREQUISITE",
                    expected_label="VIOLATION",
                    severity=IssueSeverity.HIGH.value,
                    evidence={
                        "task_id": t3.task_id,
                        "task_title": t3.title,
                        "prerequisite_task_id": t1.task_id,
                        "prerequisite_task_title": t1.title,
                        "task_completed_at": str(t3.completed_at),
                        "prerequisite_status": t1.status,
                    },
                    rule_id="RULE-TASK-001",
                )

            # Injected Anomaly #4: Started before background check
            if idx in bg_check_anomaly_cases:
                t2 = case_tasks["TPL-002"]
                t2.status = TaskStatus.PENDING.value
                t2.completed_at = None
                emp.start_date = self.ref_date - timedelta(days=10)
                emp.status = EmployeeStatus.ACTIVE.value
                case.actual_start_date = emp.start_date

                self.record_ground_truth(
                    entity_id=emp.employee_id,
                    issue_type="STARTED_BEFORE_BACKGROUND_CHECK",
                    expected_label="VIOLATION",
                    severity=IssueSeverity.CRITICAL.value,
                    evidence={
                        "employee_id": emp.employee_id,
                        "employee_status": emp.status,
                        "start_date": str(emp.start_date),
                        "bg_task_id": t2.task_id,
                        "bg_task_status": t2.status,
                    },
                    rule_id="RULE-ONB-004",
                )

            # Injected Anomaly #6: Overdue incomplete task
            if idx in overdue_task_cases:
                t4 = case_tasks["TPL-004"]
                t4.status = TaskStatus.IN_PROGRESS.value
                t4.completed_at = None
                t4.due_date = self.ref_date - timedelta(days=8)

                self.record_ground_truth(
                    entity_id=t4.task_id,
                    issue_type="OVERDUE_INCOMPLETE_TASK",
                    expected_label="VIOLATION",
                    severity=IssueSeverity.MEDIUM.value,
                    evidence={
                        "task_id": t4.task_id,
                        "case_id": case_id,
                        "task_title": t4.title,
                        "due_date": str(t4.due_date),
                        "reference_date": str(self.ref_date),
                        "days_overdue": 8,
                        "status": t4.status,
                    },
                    rule_id="RULE-TASK-006",
                )

            for t in case_tasks.values():
                if t.completed_at:
                    self.task_status_events.append(
                        TaskStatusEvent(
                            event_id=self.next_tse_id(),
                            task_id=t.task_id,
                            old_status=TaskStatus.PENDING.value,
                            new_status=TaskStatus.COMPLETED.value,
                            actor="SYSTEM",
                            timestamp=t.completed_at,
                            reason="Task fulfilled according to SOP checklist",
                        )
                    )

    def generate_assets_and_assignments(self):
        double_assign_asset_indices = {3} if self.scale == "starter" else {3, 18, 45, 92}

        categories = [
            (AssetCategory.LAPTOP.value, "LAP", "ThinkPad T14 Gen 4 / MacBook Pro 14", int(self.target_assets * 0.45)),
            (AssetCategory.MONITOR.value, "MON", "Dell UltraSharp 27 4K U2723QE", int(self.target_assets * 0.25)),
            (AssetCategory.SECURITY_KEY.value, "SEC", "YubiKey 5C NFC FIPS", int(self.target_assets * 0.15)),
            (AssetCategory.MOBILE_PHONE.value, "PHN", "Google Pixel 8 Enterprise", int(self.target_assets * 0.08)),
            (AssetCategory.HEADSET.value, "HDS", "Jabra Evolve2 65 Wireless", int(self.target_assets * 0.07)),
        ]

        total_created = 0

        for cat, prefix, model, count in categories:
            for i in range(1, count + 1):
                total_created += 1
                if total_created > self.target_assets:
                    break

                asset_id = f"AST-{prefix}-{i:06d}"
                tag = f"YF-{prefix}-{i:06d}"
                serial = f"SN-{prefix}-{self.seed % 1000}-{i:05d}"
                created_at = self.ref_date - timedelta(days=180)

                asset = Asset(
                    asset_id=asset_id,
                    asset_tag=tag,
                    category=cat,
                    model=model,
                    serial_number=serial,
                    status=AssetStatus.AVAILABLE.value,
                    created_at=created_at,
                )
                self.assets.append(asset)

        while len(self.assets) < self.target_assets:
            idx = len(self.assets) + 1
            asset_id = f"AST-LAP-{idx:06d}"
            tag = f"YF-LAP-{idx:06d}"
            serial = f"SN-LAP-{self.seed % 1000}-{idx:05d}"
            self.assets.append(
                Asset(
                    asset_id=asset_id,
                    asset_tag=tag,
                    category=AssetCategory.LAPTOP.value,
                    model="ThinkPad T14 Gen 4",
                    serial_number=serial,
                    status=AssetStatus.AVAILABLE.value,
                    created_at=self.ref_date - timedelta(days=180),
                )
            )

        emp_count = len(self.employees)
        for idx, asset in enumerate(self.assets, start=1):
            if idx <= emp_count:
                emp = self.employees[idx - 1]
                asgn_date = emp.start_date - timedelta(days=3)
                ret_date = None
                asgn_status = AssignmentStatus.ACTIVE.value

                if emp.status == EmployeeStatus.TERMINATED.value and idx not in double_assign_asset_indices:
                    asgn_status = AssignmentStatus.RETURNED.value
                    ret_date = emp.end_date
                    asset.status = AssetStatus.AVAILABLE.value
                else:
                    asset.status = AssetStatus.ASSIGNED.value

                asgn = AssetAssignment(
                    assignment_id=self.next_asgn_id(),
                    asset_id=asset.asset_id,
                    employee_id=emp.employee_id,
                    assigned_date=asgn_date,
                    return_due_date=None,
                    returned_date=ret_date,
                    status=asgn_status,
                    created_at=asgn_date,
                )
                self.asset_assignments.append(asgn)

                if idx in double_assign_asset_indices and emp_count > 1:
                    other_emp = self.employees[(idx % emp_count)]
                    conflict_asgn_date = asgn_date + timedelta(days=2)
                    asgn_conflict = AssetAssignment(
                        assignment_id=self.next_asgn_id(),
                        asset_id=asset.asset_id,
                        employee_id=other_emp.employee_id,
                        assigned_date=conflict_asgn_date,
                        return_due_date=None,
                        returned_date=None,
                        status=AssignmentStatus.ACTIVE.value,
                        created_at=conflict_asgn_date,
                    )
                    self.asset_assignments.append(asgn_conflict)

                    self.record_ground_truth(
                        entity_id=asset.asset_id,
                        issue_type="ASSET_DOUBLE_ASSIGNMENT",
                        expected_label="VIOLATION",
                        severity=IssueSeverity.HIGH.value,
                        evidence={
                            "asset_id": asset.asset_id,
                            "asset_tag": asset.asset_tag,
                            "assignment_1": {
                                "id": asgn.assignment_id,
                                "employee_id": asgn.employee_id,
                                "assigned_date": str(asgn.assigned_date),
                                "status": asgn.status,
                            },
                            "assignment_2": {
                                "id": asgn_conflict.assignment_id,
                                "employee_id": asgn_conflict.employee_id,
                                "assigned_date": str(asgn_conflict.assigned_date),
                                "status": asgn_conflict.status,
                            },
                        },
                        rule_id="RULE-AST-003",
                    )

    def generate_access_requests_and_grants(self):
        terminated_with_access = {5, 15} if self.scale == "starter" else {5, 15, 30, 115, 230}

        req_status_choices = [
            RequestStatus.PROVISIONED.value,
            RequestStatus.APPROVED.value,
            RequestStatus.REQUESTED.value,
            RequestStatus.REJECTED.value,
        ]
        req_weights = [0.70, 0.15, 0.10, 0.05]

        emp_count = len(self.employees)

        for i in range(1, self.target_access_requests + 1):
            req_id = f"ACCREQ-2026-{i:06d}"
            emp = self.employees[(i - 1) % emp_count]
            emp_num = (i - 1) % emp_count + 1

            system_name = ENTERPRISE_SYSTEMS[(i - 1) % len(ENTERPRISE_SYSTEMS)]
            access_lvl = AccessLevel.READ.value if i % 2 == 0 else AccessLevel.WRITE.value
            created_at = emp.created_at + timedelta(days=2)

            status = random.choices(req_status_choices, weights=req_weights, k=1)[0]
            if emp_num in terminated_with_access and emp.status == EmployeeStatus.TERMINATED.value:
                status = RequestStatus.PROVISIONED.value

            req = AccessRequest(
                request_id=req_id,
                employee_id=emp.employee_id,
                system_name=system_name,
                access_level=access_lvl,
                status=status,
                justification=f"Core entitlement requested for {emp.role_id} in {emp.department_id}",
                created_at=created_at,
                updated_at=created_at + timedelta(hours=12),
            )
            self.access_requests.append(req)

            if status in [RequestStatus.APPROVED.value, RequestStatus.PROVISIONED.value, RequestStatus.REJECTED.value]:
                appr_status = ApprovalStatus.APPROVED.value if status != RequestStatus.REJECTED.value else ApprovalStatus.REJECTED.value
                decided_at = created_at + timedelta(hours=4)
                appr = Approval(
                    approval_id=self.next_appr_id(),
                    request_id=req_id,
                    approver_id=emp.manager_id or "MGR-001",
                    approver_role="MANAGER",
                    status=appr_status,
                    decided_at=decided_at,
                    comments="Approved per departmental role matrix" if appr_status == ApprovalStatus.APPROVED.value else "Access rejected: exceeds principle of least privilege",
                    created_at=created_at,
                )
                self.approvals.append(appr)

            if status == RequestStatus.PROVISIONED.value:
                grant_id = self.next_grant_id()
                prov_date = created_at + timedelta(hours=8)
                grant_status = GrantStatus.ACTIVE.value
                revoked_at = None

                if emp.status == EmployeeStatus.TERMINATED.value:
                    if emp_num in terminated_with_access:
                        grant_status = GrantStatus.ACTIVE.value
                        revoked_at = None

                        self.record_ground_truth(
                            entity_id=grant_id,
                            issue_type="TERMINATED_EMPLOYEE_ACTIVE_ACCESS",
                            expected_label="VIOLATION",
                            severity=IssueSeverity.CRITICAL.value,
                            evidence={
                                "grant_id": grant_id,
                                "employee_id": emp.employee_id,
                                "employee_status": emp.status,
                                "termination_date": str(emp.end_date),
                                "system_name": system_name,
                                "grant_status": grant_status,
                            },
                            rule_id="RULE-ACC-005",
                        )
                    else:
                        grant_status = GrantStatus.REVOKED.value
                        revoked_at = emp.end_date

                grant = AccessGrant(
                    grant_id=grant_id,
                    request_id=req_id,
                    employee_id=emp.employee_id,
                    system_name=system_name,
                    access_level=access_lvl,
                    provisioned_at=prov_date,
                    revoked_at=revoked_at,
                    status=grant_status,
                    created_at=prov_date,
                )
                self.access_grants.append(grant)

                self.access_events.append(
                    AccessEvent(
                        event_id=self.next_ace_id(),
                        request_id=req_id,
                        grant_id=grant_id,
                        action="ACCESS_PROVISIONED",
                        actor="IT_ADMIN",
                        timestamp=prov_date,
                        details=f"Entitlement {system_name} ({access_lvl}) granted",
                    )
                )

    def generate_offboarding_cases(self):
        term_emps = [e for e in self.employees if e.status == EmployeeStatus.TERMINATED.value]
        for idx, emp in enumerate(term_emps, start=1):
            off_id = f"OFF-2026-{idx:06d}"
            has_active_grants = any(g.employee_id == emp.employee_id and g.status == GrantStatus.ACTIVE.value for g in self.access_grants)
            rev_status = "PENDING" if has_active_grants else "COMPLETED"
            off_status = OffboardingStatus.IN_PROGRESS.value if has_active_grants else OffboardingStatus.COMPLETED.value
            comp_at = None if has_active_grants else emp.end_date

            off = OffboardingCase(
                offboarding_id=off_id,
                employee_id=emp.employee_id,
                reason="RESIGNATION" if idx % 2 == 0 else "CONTRACT_END",
                termination_date=emp.end_date or self.ref_date,
                status=off_status,
                access_revocation_status=rev_status,
                asset_recovery_status="COMPLETED",
                completed_at=comp_at,
                created_at=emp.end_date or self.ref_date,
            )
            self.offboarding_cases.append(off)

    def generate_all(self):
        self.generate_catalogs()
        self.generate_managers()
        self.generate_employees()
        self.generate_onboarding_cases_and_tasks()
        self.generate_assets_and_assignments()
        self.generate_access_requests_and_grants()
        self.generate_offboarding_cases()

    def get_summary(self) -> Dict[str, int]:
        return {
            "departments": len(self.departments),
            "roles": len(self.roles),
            "managers": len(self.managers),
            "employees": len(self.employees),
            "onboarding_cases": len(self.onboarding_cases),
            "task_instances": len(self.task_instances),
            "assets": len(self.assets),
            "asset_assignments": len(self.asset_assignments),
            "access_requests": len(self.access_requests),
            "approvals": len(self.approvals),
            "access_grants": len(self.access_grants),
            "offboarding_cases": len(self.offboarding_cases),
            "ground_truth_issues": len(self.ground_truth),
        }
