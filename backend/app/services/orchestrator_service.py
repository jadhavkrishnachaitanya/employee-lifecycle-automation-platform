from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import json

from backend.app.models.entities import (
    Employee,
    Department,
    Role,
    Manager,
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
    TaskStatus,
    CaseStatus,
    EmployeeStatus,
    RequestStatus,
    ApprovalStatus,
    GrantStatus,
    AssetStatus,
    AssignmentStatus,
    OffboardingStatus,
)


class OrchestrationError(Exception):
    def __init__(self, message: str, code: str = "ORCHESTRATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    old_state: Optional[Dict[str, Any]] = None,
    new_state: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> AuditEvent:
    """Creates an immutable audit event entry."""
    now = timestamp or datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    
    # Generate sequential or deterministic audit id
    count = db.query(AuditEvent).count() + 1
    audit_id = f"AUD-{date_str}-{count:06d}"
    
    event = AuditEvent(
        audit_id=audit_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        old_state_json=json.dumps(old_state, default=str) if old_state else None,
        new_state_json=json.dumps(new_state, default=str) if new_state else None,
        timestamp=now,
        reason=reason,
    )
    db.add(event)
    return event


# ==========================================
# Task Management & Workflow Rules
# ==========================================

def get_task_predecessors(db: Session, task_instance: TaskInstance) -> List[TaskInstance]:
    """Finds all predecessor task instances in the same onboarding case based on template dependencies."""
    dep_templates = (
        db.query(TaskDependency.predecessor_template_id)
        .filter(TaskDependency.successor_template_id == task_instance.template_id)
        .all()
    )
    predecessor_template_ids = [d[0] for d in dep_templates]
    
    if not predecessor_template_ids:
        return []

    return (
        db.query(TaskInstance)
        .filter(
            TaskInstance.case_id == task_instance.case_id,
            TaskInstance.template_id.in_(predecessor_template_ids),
        )
        .all()
    )


def update_task_status(
    db: Session,
    task_id: str,
    new_status: str,
    actor: str = "SYSTEM_ADMIN",
    reason: Optional[str] = None,
    enforce_dependencies: bool = True,
    timestamp: Optional[datetime] = None,
) -> TaskInstance:
    """Updates a task instance status while enforcing prerequisites and workflow rules."""
    now = timestamp or datetime.now(timezone.utc)
    task = db.query(TaskInstance).filter(TaskInstance.task_id == task_id).first()
    if not task:
        raise OrchestrationError(f"Task {task_id} not found", code="TASK_NOT_FOUND")

    old_status = task.status
    if old_status == new_status:
        return task

    # Rule: If completing a task, check all prerequisites
    if new_status == TaskStatus.COMPLETED.value and enforce_dependencies:
        predecessors = get_task_predecessors(db, task)
        uncompleted_preds = [p for p in predecessors if p.status != TaskStatus.COMPLETED.value]
        if uncompleted_preds:
            pred_titles = ", ".join([f"{p.title} ({p.task_id})" for p in uncompleted_preds])
            raise OrchestrationError(
                f"Cannot complete task '{task.title}': Prerequisite task(s) not completed: {pred_titles}",
                code="PREREQUISITE_NOT_MET",
            )

    # Record event
    event_count = db.query(TaskStatusEvent).count() + 1
    tse_id = f"TSE-{event_count:06d}"
    status_event = TaskStatusEvent(
        event_id=tse_id,
        task_id=task.task_id,
        old_status=old_status,
        new_status=new_status,
        actor=actor,
        timestamp=now,
        reason=reason,
    )
    db.add(status_event)

    # Update task fields
    task.status = new_status
    task.updated_at = now
    if new_status == TaskStatus.COMPLETED.value:
        task.completed_at = now
        task.completed_by = actor
        task.is_blocked = False
        task.blocked_reason = None
    elif new_status == TaskStatus.BLOCKED.value:
        task.is_blocked = True
        task.blocked_reason = reason or "Blocked by workflow dependency"

    # Log immutable audit event
    log_audit_event(
        db=db,
        entity_type="TaskInstance",
        entity_id=task.task_id,
        action="UPDATE_STATUS",
        actor=actor,
        old_state={"status": old_status},
        new_state={"status": new_status, "completed_at": task.completed_at},
        reason=reason,
        timestamp=now,
    )

    # Check and update successor tasks' blocked status
    recalculate_case_tasks_blocking(db, task.case_id)

    # Check if OnboardingCase is completed
    check_and_update_case_completion(db, task.case_id, actor=actor, timestamp=now)

    db.commit()
    db.refresh(task)
    return task


def recalculate_case_tasks_blocking(db: Session, case_id: str):
    """Refreshes the is_blocked status and reason for all tasks in an onboarding case."""
    tasks = db.query(TaskInstance).filter(TaskInstance.case_id == case_id).all()
    task_map = {t.template_id: t for t in tasks}

    dependencies = db.query(TaskDependency).all()
    for dep in dependencies:
        successor_task = task_map.get(dep.successor_template_id)
        predecessor_task = task_map.get(dep.predecessor_template_id)

        if successor_task and predecessor_task:
            if successor_task.status in [TaskStatus.PENDING.value, TaskStatus.BLOCKED.value]:
                if predecessor_task.status != TaskStatus.COMPLETED.value:
                    successor_task.is_blocked = True
                    successor_task.blocked_reason = f"Waiting for: {predecessor_task.title}"
                    if successor_task.status == TaskStatus.PENDING.value:
                        successor_task.status = TaskStatus.BLOCKED.value
                else:
                    if successor_task.is_blocked and successor_task.status == TaskStatus.BLOCKED.value:
                        # Check if any OTHER predecessor is still pending
                        all_preds = get_task_predecessors(db, successor_task)
                        still_pending = [p for p in all_preds if p.status != TaskStatus.COMPLETED.value]
                        if not still_pending:
                            successor_task.is_blocked = False
                            successor_task.blocked_reason = None
                            successor_task.status = TaskStatus.PENDING.value


def check_and_update_case_completion(
    db: Session,
    case_id: str,
    actor: str = "SYSTEM",
    timestamp: Optional[datetime] = None,
):
    """If all mandatory tasks in the case are completed, mark OnboardingCase as COMPLETED."""
    now = timestamp or datetime.now(timezone.utc)
    case = db.query(OnboardingCase).filter(OnboardingCase.case_id == case_id).first()
    if not case or case.status == CaseStatus.COMPLETED.value:
        return

    tasks = db.query(TaskInstance).filter(TaskInstance.case_id == case_id).all()
    all_done = all(t.status == TaskStatus.COMPLETED.value for t in tasks)

    if all_done and len(tasks) > 0:
        old_status = case.status
        case.status = CaseStatus.COMPLETED.value
        case.completed_at = now
        case.actual_start_date = case.actual_start_date or case.target_start_date
        case.updated_at = now

        # Update employee status to ACTIVE if PENDING
        if case.employee and case.employee.status == EmployeeStatus.PENDING.value:
            case.employee.status = EmployeeStatus.ACTIVE.value
            case.employee.updated_at = now

        # Record case status event
        c_count = db.query(CaseStatusEvent).count() + 1
        cse = CaseStatusEvent(
            event_id=f"CSE-{c_count:06d}",
            case_id=case.case_id,
            old_status=old_status,
            new_status=CaseStatus.COMPLETED.value,
            actor=actor,
            timestamp=now,
            reason="All required onboarding tasks successfully completed",
        )
        db.add(cse)

        log_audit_event(
            db=db,
            entity_type="OnboardingCase",
            entity_id=case.case_id,
            action="COMPLETE_ONBOARDING",
            actor=actor,
            old_state={"status": old_status},
            new_state={"status": CaseStatus.COMPLETED.value, "completed_at": now},
            reason="All tasks completed",
            timestamp=now,
        )


# ==========================================
# Access Management Workflow
# ==========================================

def approve_access_request(
    db: Session,
    request_id: str,
    approver_id: str,
    decision: str,  # APPROVED or REJECTED
    comments: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> AccessRequest:
    now = timestamp or datetime.now(timezone.utc)
    req = db.query(AccessRequest).filter(AccessRequest.request_id == request_id).first()
    if not req:
        raise OrchestrationError(f"Access request {request_id} not found", code="REQUEST_NOT_FOUND")

    if req.status != RequestStatus.REQUESTED.value:
        raise OrchestrationError(
            f"Cannot decide on request in status '{req.status}'",
            code="INVALID_STATE_TRANSITION",
        )

    # Create approval record
    appr_count = db.query(Approval).count() + 1
    approval = Approval(
        approval_id=f"APPR-{appr_count:06d}",
        request_id=req.request_id,
        approver_id=approver_id,
        approver_role="MANAGER",
        status=ApprovalStatus.APPROVED.value if decision.upper() == "APPROVED" else ApprovalStatus.REJECTED.value,
        decided_at=now,
        comments=comments,
        created_at=now,
    )
    db.add(approval)

    req.status = RequestStatus.APPROVED.value if decision.upper() == "APPROVED" else RequestStatus.REJECTED.value
    req.updated_at = now

    # Log access event & audit
    ace_count = db.query(AccessEvent).count() + 1
    ace = AccessEvent(
        event_id=f"ACE-{ace_count:06d}",
        request_id=req.request_id,
        action=f"ACCESS_{decision.upper()}",
        actor=approver_id,
        timestamp=now,
        details=comments or f"Access request {decision.lower()} by manager",
    )
    db.add(ace)

    log_audit_event(
        db=db,
        entity_type="AccessRequest",
        entity_id=req.request_id,
        action=f"APPROVE_{decision.upper()}",
        actor=approver_id,
        old_state={"status": RequestStatus.REQUESTED.value},
        new_state={"status": req.status},
        reason=comments,
        timestamp=now,
    )

    db.commit()
    db.refresh(req)
    return req


def provision_access_request(
    db: Session,
    request_id: str,
    provisioner_id: str = "IT_ADMIN",
    enforce_approval: bool = True,
    timestamp: Optional[datetime] = None,
) -> AccessGrant:
    """Provisions access ONLY if approved, unless enforce_approval is explicitly False (anomaly injection)."""
    now = timestamp or datetime.now(timezone.utc)
    req = db.query(AccessRequest).filter(AccessRequest.request_id == request_id).first()
    if not req:
        raise OrchestrationError(f"Access request {request_id} not found", code="REQUEST_NOT_FOUND")

    if enforce_approval and req.status != RequestStatus.APPROVED.value:
        raise OrchestrationError(
            f"Illegal provisioning: Request {request_id} is in status '{req.status}', must be APPROVED before provisioning.",
            code="APPROVAL_REQUIRED",
        )

    # Create Grant
    grant_count = db.query(AccessGrant).count() + 1
    grant = AccessGrant(
        grant_id=f"GRANT-{grant_count:06d}",
        request_id=req.request_id,
        employee_id=req.employee_id,
        system_name=req.system_name,
        access_level=req.access_level,
        provisioned_at=now,
        status=GrantStatus.ACTIVE.value,
        created_at=now,
    )
    db.add(grant)

    req.status = RequestStatus.PROVISIONED.value
    req.updated_at = now

    # Access event
    ace_count = db.query(AccessEvent).count() + 1
    ace = AccessEvent(
        event_id=f"ACE-{ace_count:06d}",
        request_id=req.request_id,
        grant_id=grant.grant_id,
        action="ACCESS_PROVISIONED",
        actor=provisioner_id,
        timestamp=now,
        details=f"System {req.system_name} access provisioned at level {req.access_level}",
    )
    db.add(ace)

    log_audit_event(
        db=db,
        entity_type="AccessGrant",
        entity_id=grant.grant_id,
        action="PROVISION_ACCESS",
        actor=provisioner_id,
        new_state={"status": GrantStatus.ACTIVE.value, "system": req.system_name, "level": req.access_level},
        reason=f"Provisioned for request {req.request_id}",
        timestamp=now,
    )

    db.commit()
    db.refresh(grant)
    return grant


# ==========================================
# Asset Allocation & Recovery
# ==========================================

def assign_asset(
    db: Session,
    asset_id: str,
    employee_id: str,
    assigned_date: Optional[datetime] = None,
    return_due_date: Optional[datetime] = None,
    force_override: bool = False,
    actor: str = "FACILITIES_ADMIN",
) -> AssetAssignment:
    now = assigned_date or datetime.now(timezone.utc)
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise OrchestrationError(f"Asset {asset_id} not found", code="ASSET_NOT_FOUND")

    # Check for existing active assignment
    active_assignments = (
        db.query(AssetAssignment)
        .filter(
            AssetAssignment.asset_id == asset_id,
            AssetAssignment.status == AssignmentStatus.ACTIVE.value,
        )
        .all()
    )

    if active_assignments and not force_override:
        current_emp = active_assignments[0].employee_id
        raise OrchestrationError(
            f"Asset {asset_id} is already actively assigned to employee {current_emp}. Overlapping assignment forbidden.",
            code="ASSET_DOUBLE_ASSIGNMENT",
        )

    asgn_count = db.query(AssetAssignment).count() + 1
    assignment = AssetAssignment(
        assignment_id=f"ASGN-{asgn_count:06d}",
        asset_id=asset_id,
        employee_id=employee_id,
        assigned_date=now,
        return_due_date=return_due_date,
        status=AssignmentStatus.ACTIVE.value,
        created_at=now,
    )
    db.add(assignment)

    asset.status = AssetStatus.ASSIGNED.value

    log_audit_event(
        db=db,
        entity_type="AssetAssignment",
        entity_id=assignment.assignment_id,
        action="ASSIGN_ASSET",
        actor=actor,
        new_state={"asset_id": asset_id, "employee_id": employee_id, "status": AssignmentStatus.ACTIVE.value},
        reason="Assigned to employee",
        timestamp=now,
    )

    db.commit()
    db.refresh(assignment)
    return assignment


def recover_asset(
    db: Session,
    asset_id: str,
    returned_date: Optional[datetime] = None,
    actor: str = "FACILITIES_ADMIN",
    notes: Optional[str] = None,
) -> Asset:
    now = returned_date or datetime.now(timezone.utc)
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise OrchestrationError(f"Asset {asset_id} not found", code="ASSET_NOT_FOUND")

    active_asgns = (
        db.query(AssetAssignment)
        .filter(
            AssetAssignment.asset_id == asset_id,
            AssetAssignment.status == AssignmentStatus.ACTIVE.value,
        )
        .all()
    )

    for asgn in active_asgns:
        asgn.status = AssignmentStatus.RETURNED.value
        asgn.returned_date = now

    asset.status = AssetStatus.AVAILABLE.value

    log_audit_event(
        db=db,
        entity_type="Asset",
        entity_id=asset.asset_id,
        action="RECOVER_ASSET",
        actor=actor,
        new_state={"status": AssetStatus.AVAILABLE.value, "returned_date": now},
        reason=notes or "Asset successfully recovered and sanitized",
        timestamp=now,
    )

    db.commit()
    db.refresh(asset)
    return asset


# ==========================================
# Offboarding Workflow
# ==========================================

def initiate_offboarding(
    db: Session,
    employee_id: str,
    reason: str = "RESIGNATION",
    termination_date: Optional[datetime] = None,
    actor: str = "HR_ADMIN",
) -> OffboardingCase:
    now = datetime.now(timezone.utc)
    term_date = termination_date or now

    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise OrchestrationError(f"Employee {employee_id} not found", code="EMPLOYEE_NOT_FOUND")

    # Update employee
    emp.status = EmployeeStatus.TERMINATED.value
    emp.end_date = term_date
    emp.updated_at = now

    off_count = db.query(OffboardingCase).count() + 1
    off_case = OffboardingCase(
        offboarding_id=f"OFF-2026-{off_count:06d}",
        employee_id=employee_id,
        reason=reason,
        termination_date=term_date,
        status=OffboardingStatus.IN_PROGRESS.value,
        access_revocation_status="PENDING",
        asset_recovery_status="PENDING",
        created_at=now,
    )
    db.add(off_case)

    log_audit_event(
        db=db,
        entity_type="Employee",
        entity_id=employee_id,
        action="TERMINATE_EMPLOYEE",
        actor=actor,
        old_state={"status": EmployeeStatus.ACTIVE.value},
        new_state={"status": EmployeeStatus.TERMINATED.value, "termination_date": term_date},
        reason=f"Initiated offboarding ({reason})",
        timestamp=now,
    )

    db.commit()
    db.refresh(off_case)
    return off_case


def revoke_offboarding_access(
    db: Session,
    offboarding_id: str,
    actor: str = "IT_SEC_ADMIN",
    notes: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> OffboardingCase:
    now = timestamp or datetime.now(timezone.utc)
    off_case = db.query(OffboardingCase).filter(OffboardingCase.offboarding_id == offboarding_id).first()
    if not off_case:
        raise OrchestrationError(f"Offboarding case {offboarding_id} not found", code="CASE_NOT_FOUND")

    # Revoke all active grants for employee
    active_grants = (
        db.query(AccessGrant)
        .filter(
            AccessGrant.employee_id == off_case.employee_id,
            AccessGrant.status == GrantStatus.ACTIVE.value,
        )
        .all()
    )

    for grant in active_grants:
        grant.status = GrantStatus.REVOKED.value
        grant.revoked_at = now

        ace_count = db.query(AccessEvent).count() + 1
        ace = AccessEvent(
            event_id=f"ACE-{ace_count:06d}",
            grant_id=grant.grant_id,
            action="ACCESS_REVOKED",
            actor=actor,
            timestamp=now,
            details=f"Access revoked upon employee offboarding: {notes or 'Offboarding standard procedure'}",
        )
        db.add(ace)

        log_audit_event(
            db=db,
            entity_type="AccessGrant",
            entity_id=grant.grant_id,
            action="REVOKE_ACCESS",
            actor=actor,
            old_state={"status": GrantStatus.ACTIVE.value},
            new_state={"status": GrantStatus.REVOKED.value, "revoked_at": now},
            reason="Offboarding revocation",
            timestamp=now,
        )

    off_case.access_revocation_status = "COMPLETED"
    if off_case.asset_recovery_status == "COMPLETED":
        off_case.status = OffboardingStatus.COMPLETED.value
        off_case.completed_at = now

    db.commit()
    db.refresh(off_case)
    return off_case
