from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timezone
import json
from collections import defaultdict

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
    Asset,
    AssetAssignment,
    AccessRequest,
    Approval,
    AccessGrant,
    OffboardingCase,
    TaskStatus,
    CaseStatus,
    EmployeeStatus,
    RequestStatus,
    ApprovalStatus,
    GrantStatus,
    AssignmentStatus,
)


class RuleBasedValidator:
    """Independent validator that inspects database tables/records WITHOUT reading ground_truth."""

    def __init__(self, ref_date: Optional[datetime] = None):
        self.ref_date = ref_date or datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
        self.integrity_failures: List[Dict[str, Any]] = []
        self.detected_anomalies: List[Dict[str, Any]] = []

    def validate_dataset(
        self,
        departments: List[Department],
        roles: List[Role],
        managers: List[Manager],
        employees: List[Employee],
        task_templates: List[TaskTemplate],
        task_dependencies: List[TaskDependency],
        onboarding_cases: List[OnboardingCase],
        task_instances: List[TaskInstance],
        assets: List[Asset],
        asset_assignments: List[AssetAssignment],
        access_requests: List[AccessRequest],
        approvals: List[Approval],
        access_grants: List[AccessGrant],
        department_history: List[EmployeeDepartmentHistory],
        offboarding_cases: List[OffboardingCase],
    ) -> Dict[str, Any]:
        """Runs complete validation scan across structural integrity and business rules."""
        self.integrity_failures.clear()
        self.detected_anomalies.clear()

        # Build lookup indices
        dept_map = {d.department_id: d for d in departments}
        role_map = {r.role_id: r for r in roles}
        mgr_map = {m.manager_id: m for m in managers}
        emp_map = {e.employee_id: e for e in employees}
        case_map = {c.case_id: c for c in onboarding_cases}
        template_map = {t.template_id: t for t in task_templates}
        asset_map = {a.asset_id: a for a in assets}
        request_map = {r.request_id: r for r in access_requests}

        # ------------------------------------------------------------------
        # 1. Structural Integrity: PK Uniqueness & Foreign Key References
        # ------------------------------------------------------------------
        self._check_pk_uniqueness("Department", [d.department_id for d in departments])
        self._check_pk_uniqueness("Role", [r.role_id for r in roles])
        self._check_pk_uniqueness("Manager", [m.manager_id for m in managers])
        self._check_pk_uniqueness("Employee", [e.employee_id for e in employees])
        self._check_pk_uniqueness("OnboardingCase", [c.case_id for c in onboarding_cases])
        self._check_pk_uniqueness("TaskInstance", [t.task_id for t in task_instances])
        self._check_pk_uniqueness("Asset", [a.asset_id for a in assets])
        self._check_pk_uniqueness("AssetAssignment", [a.assignment_id for a in asset_assignments])
        self._check_pk_uniqueness("AccessRequest", [r.request_id for r in access_requests])
        self._check_pk_uniqueness("AccessGrant", [g.grant_id for g in access_grants])

        # FK checks
        for r in roles:
            if r.department_id not in dept_map:
                self.integrity_failures.append({
                    "table": "roles",
                    "id": r.role_id,
                    "error": f"Invalid department_id foreign key: {r.department_id}",
                })

        for m in managers:
            if m.department_id not in dept_map:
                self.integrity_failures.append({
                    "table": "managers",
                    "id": m.manager_id,
                    "error": f"Invalid department_id foreign key: {m.department_id}",
                })

        for e in employees:
            if e.department_id not in dept_map:
                self.integrity_failures.append({
                    "table": "employees",
                    "id": e.employee_id,
                    "error": f"Invalid department_id foreign key: {e.department_id}",
                })
            if e.role_id not in role_map:
                self.integrity_failures.append({
                    "table": "employees",
                    "id": e.employee_id,
                    "error": f"Invalid role_id foreign key: {e.role_id}",
                })
            if e.manager_id is not None and e.manager_id not in mgr_map:
                self.integrity_failures.append({
                    "table": "employees",
                    "id": e.employee_id,
                    "error": f"Invalid manager_id foreign key: {e.manager_id}",
                })

        for c in onboarding_cases:
            if c.employee_id not in emp_map:
                self.integrity_failures.append({
                    "table": "onboarding_cases",
                    "id": c.case_id,
                    "error": f"Invalid employee_id foreign key: {c.employee_id}",
                })

        for t in task_instances:
            if t.case_id not in case_map:
                self.integrity_failures.append({
                    "table": "task_instances",
                    "id": t.task_id,
                    "error": f"Invalid case_id foreign key: {t.case_id}",
                })
            if t.template_id not in template_map:
                self.integrity_failures.append({
                    "table": "task_instances",
                    "id": t.task_id,
                    "error": f"Invalid template_id foreign key: {t.template_id}",
                })

        # ------------------------------------------------------------------
        # 2. Dependency Graph Acyclic Verification (Topological Sort)
        # ------------------------------------------------------------------
        self._check_acyclic_dependencies(task_templates, task_dependencies)

        # ------------------------------------------------------------------
        # 3. Business Rule Checks & Anomaly Detection
        # ------------------------------------------------------------------

        # Rule 1: Task completed before prerequisite (RULE-TASK-001)
        self._detect_prerequisite_timing_anomalies(task_instances, task_dependencies)

        # Rule 2: Missing Manager (RULE-ORG-002)
        for emp in employees:
            if emp.manager_id is None:
                self.detected_anomalies.append({
                    "rule_id": "RULE-ORG-002",
                    "issue_type": "MISSING_MANAGER",
                    "entity_id": emp.employee_id,
                    "severity": "HIGH",
                    "evidence": {
                        "employee_id": emp.employee_id,
                        "department_id": emp.department_id,
                        "role_id": emp.role_id,
                        "reason": "Employee has null manager_id in organizational hierarchy",
                    },
                })

        # Rule 3: Asset Double Assignment (RULE-AST-003)
        self._detect_asset_double_assignments(asset_assignments)

        # Rule 4: Employee Started Before Background Check Completion (RULE-ONB-004)
        self._detect_started_before_background_check(employees, onboarding_cases, task_instances)

        # Rule 5: Terminated Employee Retains Active Access (RULE-ACC-005)
        for grant in access_grants:
            if grant.status == GrantStatus.ACTIVE.value:
                emp = emp_map.get(grant.employee_id)
                if emp and emp.status == EmployeeStatus.TERMINATED.value:
                    self.detected_anomalies.append({
                        "rule_id": "RULE-ACC-005",
                        "issue_type": "TERMINATED_EMPLOYEE_ACTIVE_ACCESS",
                        "entity_id": grant.grant_id,
                        "severity": "CRITICAL",
                        "evidence": {
                            "grant_id": grant.grant_id,
                            "employee_id": emp.employee_id,
                            "system_name": grant.system_name,
                            "termination_date": str(emp.end_date),
                            "grant_status": grant.status,
                            "reason": "Active system access grant persists after employee termination",
                        },
                    })

        # Rule 6: Overdue Incomplete Tasks (RULE-TASK-006)
        for task in task_instances:
            if task.status in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, TaskStatus.BLOCKED.value]:
                if task.due_date and task.due_date < self.ref_date:
                    days_overdue = (self.ref_date - task.due_date).days
                    self.detected_anomalies.append({
                        "rule_id": "RULE-TASK-006",
                        "issue_type": "OVERDUE_INCOMPLETE_TASK",
                        "entity_id": task.task_id,
                        "severity": "MEDIUM",
                        "evidence": {
                            "task_id": task.task_id,
                            "case_id": task.case_id,
                            "title": task.title,
                            "due_date": str(task.due_date),
                            "reference_date": str(self.ref_date),
                            "days_overdue": days_overdue,
                            "status": task.status,
                        },
                    })

        # Rule 7: Mid-Process Department Transfer (RULE-ONB-007)
        self._detect_mid_onboarding_dept_changes(department_history, onboarding_cases)

        # Rule 8: Unapproved Access Provisioning Check
        for grant in access_grants:
            req = request_map.get(grant.request_id)
            if not req:
                self.integrity_failures.append({
                    "table": "access_grants",
                    "id": grant.grant_id,
                    "error": f"Orphan grant with missing access request {grant.request_id}",
                })
            elif req.status not in [RequestStatus.PROVISIONED.value, RequestStatus.REVOKED.value]:
                self.detected_anomalies.append({
                    "rule_id": "RULE-ACC-008",
                    "issue_type": "UNAPPROVED_PROVISIONING",
                    "entity_id": grant.grant_id,
                    "severity": "CRITICAL",
                    "evidence": {
                        "grant_id": grant.grant_id,
                        "request_id": req.request_id,
                        "request_status": req.status,
                    },
                })

        counts_by_type = defaultdict(int)
        for a in self.detected_anomalies:
            counts_by_type[a["issue_type"]] += 1

        return {
            "validation_status": "PASSED" if not self.integrity_failures else "FAILED",
            "reference_date": str(self.ref_date),
            "total_records_checked": len(employees) + len(task_instances) + len(assets) + len(access_requests),
            "total_rules_evaluated": 10,
            "total_anomalies_detected": len(self.detected_anomalies),
            "anomaly_counts_by_type": dict(counts_by_type),
            "integrity_failures": self.integrity_failures,
            "detected_issues": self.detected_anomalies,
        }

    def _check_pk_uniqueness(self, entity_name: str, ids: List[str]):
        seen = set()
        duplicates = set()
        for i in ids:
            if i in seen:
                duplicates.add(i)
            seen.add(i)
        if duplicates:
            self.integrity_failures.append({
                "entity": entity_name,
                "error": f"Duplicate primary keys detected in {entity_name}: {list(duplicates)[:5]}",
            })

    def _check_acyclic_dependencies(self, templates: List[TaskTemplate], dependencies: List[TaskDependency]):
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_nodes = {t.template_id for t in templates}

        for node in all_nodes:
            in_degree[node] = 0

        for d in dependencies:
            graph[d.predecessor_template_id].append(d.successor_template_id)
            in_degree[d.successor_template_id] += 1

        queue = [n for n in all_nodes if in_degree[n] == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for nxt in graph[curr]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if visited_count != len(all_nodes):
            self.integrity_failures.append({
                "table": "task_dependencies",
                "error": "Cyclic dependency detected in task dependency graph! Topological sort failed.",
            })

    def _detect_prerequisite_timing_anomalies(
        self,
        tasks: List[TaskInstance],
        dependencies: List[TaskDependency],
    ):
        # Map tasks by (case_id, template_id)
        task_by_case_tmpl = {(t.case_id, t.template_id): t for t in tasks}

        for dep in dependencies:
            pred_id = dep.predecessor_template_id
            succ_id = dep.successor_template_id

            # Find all successor tasks in cases
            for (case_id, tmpl_id), succ_task in task_by_case_tmpl.items():
                if tmpl_id == succ_id and succ_task.status == TaskStatus.COMPLETED.value:
                    pred_task = task_by_case_tmpl.get((case_id, pred_id))
                    if pred_task:
                        # Anomaly condition: Predecessor is NOT completed, or completed AFTER successor
                        is_violation = False
                        if pred_task.status != TaskStatus.COMPLETED.value:
                            is_violation = True
                        elif pred_task.completed_at and succ_task.completed_at and pred_task.completed_at > succ_task.completed_at:
                            is_violation = True

                        if is_violation:
                            self.detected_anomalies.append({
                                "rule_id": "RULE-TASK-001",
                                "issue_type": "TASK_COMPLETED_BEFORE_PREREQUISITE",
                                "entity_id": succ_task.task_id,
                                "severity": "HIGH",
                                "evidence": {
                                    "task_id": succ_task.task_id,
                                    "task_title": succ_task.title,
                                    "prerequisite_task_id": pred_task.task_id,
                                    "prerequisite_task_title": pred_task.title,
                                    "successor_completed_at": str(succ_task.completed_at),
                                    "predecessor_completed_at": str(pred_task.completed_at),
                                    "predecessor_status": pred_task.status,
                                },
                            })

    def _detect_asset_double_assignments(self, assignments: List[AssetAssignment]):
        active_by_asset = defaultdict(list)
        for asgn in assignments:
            if asgn.status == AssignmentStatus.ACTIVE.value:
                active_by_asset[asgn.asset_id].append(asgn)

        for asset_id, asgns in active_by_asset.items():
            if len(asgns) > 1:
                self.detected_anomalies.append({
                    "rule_id": "RULE-AST-003",
                    "issue_type": "ASSET_DOUBLE_ASSIGNMENT",
                    "entity_id": asset_id,
                    "severity": "HIGH",
                    "evidence": {
                        "asset_id": asset_id,
                        "active_assignment_count": len(asgns),
                        "assignment_ids": [a.assignment_id for a in asgns],
                        "employee_ids": [a.employee_id for a in asgns],
                    },
                })

    def _detect_started_before_background_check(
        self,
        employees: List[Employee],
        cases: List[OnboardingCase],
        tasks: List[TaskInstance],
    ):
        case_by_emp = {c.employee_id: c for c in cases}
        bg_tasks_by_case = {t.case_id: t for t in tasks if t.template_id == "TPL-002"}

        for emp in employees:
            if emp.start_date and emp.start_date <= self.ref_date:
                case = case_by_emp.get(emp.employee_id)
                if case:
                    bg_task = bg_tasks_by_case.get(case.case_id)
                    if bg_task:
                        violation = False
                        if bg_task.status != TaskStatus.COMPLETED.value and emp.status == EmployeeStatus.ACTIVE.value:
                            violation = True
                        elif bg_task.completed_at and bg_task.completed_at > emp.start_date:
                            violation = True

                        if violation:
                            self.detected_anomalies.append({
                                "rule_id": "RULE-ONB-004",
                                "issue_type": "STARTED_BEFORE_BACKGROUND_CHECK",
                                "entity_id": emp.employee_id,
                                "severity": "CRITICAL",
                                "evidence": {
                                    "employee_id": emp.employee_id,
                                    "start_date": str(emp.start_date),
                                    "bg_task_id": bg_task.task_id,
                                    "bg_task_status": bg_task.status,
                                    "bg_completed_at": str(bg_task.completed_at),
                                },
                            })

    def _detect_mid_onboarding_dept_changes(
        self,
        history: List[EmployeeDepartmentHistory],
        cases: List[OnboardingCase],
    ):
        case_by_emp = {c.employee_id: c for c in cases}
        history_by_emp = defaultdict(list)
        for h in history:
            history_by_emp[h.employee_id].append(h)

        for emp_id, records in history_by_emp.items():
            if len(records) > 1:
                case = case_by_emp.get(emp_id)
                if case:
                    # Check if transfer occurred while onboarding was active
                    # Onboarding active window: case.created_at to case.completed_at (or ref_date)
                    end_window = case.completed_at or self.ref_date
                    for r in records:
                        if r.effective_start_date > case.created_at and r.effective_start_date <= end_window:
                            self.detected_anomalies.append({
                                "rule_id": "RULE-ONB-007",
                                "issue_type": "DEPARTMENT_CHANGE_MID_PROCESS",
                                "entity_id": emp_id,
                                "severity": "MEDIUM",
                                "evidence": {
                                    "employee_id": emp_id,
                                    "transfer_history_id": r.history_id,
                                    "new_department_id": r.department_id,
                                    "transfer_date": str(r.effective_start_date),
                                    "onboarding_case_id": case.case_id,
                                    "onboarding_status": case.status,
                                },
                            })
                            break


def evaluate_detection(
    detected_anomalies: List[Dict[str, Any]],
    ground_truth: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compares independent rule-based detections against ground truth only during evaluation stage."""
    # Group by (entity_id, issue_type)
    detected_keys = {(d["entity_id"], d["issue_type"]) for d in detected_anomalies}
    ground_truth_keys = {(g["entity_id"], g["issue_type"]) for g in ground_truth}

    tp_keys = detected_keys.intersection(ground_truth_keys)
    fp_keys = detected_keys - ground_truth_keys
    fn_keys = ground_truth_keys - detected_keys

    tp = len(tp_keys)
    fp = len(fp_keys)
    fn = len(fn_keys)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0

    # Per-issue breakdown
    all_issue_types = sorted(list({k[1] for k in detected_keys.union(ground_truth_keys)}))
    breakdown = {}

    for itype in all_issue_types:
        gt_count = sum(1 for g in ground_truth if g["issue_type"] == itype)
        det_count = sum(1 for d in detected_anomalies if d["issue_type"] == itype)
        type_tp = sum(1 for k in tp_keys if k[1] == itype)
        type_fp = sum(1 for k in fp_keys if k[1] == itype)
        type_fn = sum(1 for k in fn_keys if k[1] == itype)

        p = type_tp / (type_tp + type_fp) if (type_tp + type_fp) > 0 else 1.0
        r = type_tp / (type_tp + type_fn) if (type_tp + type_fn) > 0 else 1.0
        f = (2 * p * r) / (p + r) if (p + r) > 0 else 1.0

        breakdown[itype] = {
            "ground_truth_count": gt_count,
            "detected_count": det_count,
            "true_positives": type_tp,
            "false_positives": type_fp,
            "false_negatives": type_fn,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1_score": round(f, 4),
        }

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "total_ground_truth": len(ground_truth),
        "total_detected": len(detected_anomalies),
        "per_issue_breakdown": breakdown,
    }
