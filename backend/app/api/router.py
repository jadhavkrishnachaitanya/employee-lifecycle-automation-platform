from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
import json

from backend.app.database import get_db
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
from backend.app.schemas.schemas import (
    DepartmentResponse,
    RoleResponse,
    ManagerResponse,
    EmployeeResponse,
    EmployeeDetailResponse,
    EmployeeCreate,
    EmployeeUpdate,
    DepartmentHistoryResponse,
    TaskTemplateResponse,
    TaskInstanceResponse,
    TaskStatusUpdate,
    TaskStatusEventResponse,
    OnboardingCaseResponse,
    OnboardingCaseDetailResponse,
    OnboardingCaseCreate,
    AssetResponse,
    AssetAssignmentResponse,
    AssetAssignRequest,
    AssetRecoverRequest,
    AccessRequestResponse,
    AccessRequestCreate,
    AccessApprovalRequest,
    AccessProvisionRequest,
    ApprovalResponse,
    AccessGrantResponse,
    OffboardingResponse,
    OffboardingCreate,
    OffboardingRevokeRequest,
    AuditEventResponse,
    IssueRecordResponse,
    DashboardSummaryResponse,
    ValidationResultResponse,
    MetricsResponse,
)
from backend.app.services.orchestrator_service import (
    update_task_status,
    approve_access_request,
    provision_access_request,
    assign_asset,
    recover_asset,
    initiate_offboarding,
    revoke_offboarding_access,
    log_audit_event,
    OrchestrationError,
)
from backend.generator.validator import RuleBasedValidator, evaluate_detection

router = APIRouter(prefix="/api")


# ==========================================
# Health & Dashboard
# ==========================================

@router.get("/health", tags=["System"])
def get_health():
    return {
        "status": "healthy",
        "service": "YottaFlex Employee Lifecycle Orchestrator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
    }


@router.get("/dashboard", response_model=DashboardSummaryResponse, tags=["Dashboard"])
def get_dashboard_summary(db: Session = Depends(get_db)):
    ref_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    total_emp = db.query(Employee).count()
    active_emp = db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE.value).count()
    pending_onb = db.query(OnboardingCase).filter(OnboardingCase.status.in_([CaseStatus.INITIATED.value, CaseStatus.IN_PROGRESS.value])).count()
    completed_onb = db.query(OnboardingCase).filter(OnboardingCase.status == CaseStatus.COMPLETED.value).count()

    total_tasks = db.query(TaskInstance).count()
    completed_tasks = db.query(TaskInstance).filter(TaskInstance.status == TaskStatus.COMPLETED.value).count()
    pending_tasks = db.query(TaskInstance).filter(TaskInstance.status == TaskStatus.PENDING.value).count()
    blocked_tasks = db.query(TaskInstance).filter(TaskInstance.status == TaskStatus.BLOCKED.value).count()
    
    overdue_tasks = db.query(TaskInstance).filter(
        TaskInstance.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, TaskStatus.BLOCKED.value]),
        TaskInstance.due_date < ref_date
    ).count()

    pending_approvals = db.query(Approval).filter(Approval.status == ApprovalStatus.PENDING.value).count()
    active_grants = db.query(AccessGrant).filter(AccessGrant.status == GrantStatus.ACTIVE.value).count()
    active_off = db.query(OffboardingCase).filter(OffboardingCase.status != OffboardingStatus.COMPLETED.value).count()

    # Anomaly breakdown
    issues = db.query(IssueRecord).all()
    total_anomalies = len(issues)
    anomaly_breakdown = {}
    for iss in issues:
        anomaly_breakdown[iss.issue_type] = anomaly_breakdown.get(iss.issue_type, 0) + 1

    # Tasks by team
    tasks_by_team_rows = db.query(TaskInstance.owner_team, func.count(TaskInstance.task_id)).group_by(TaskInstance.owner_team).all()
    tasks_by_team = {row[0]: row[1] for row in tasks_by_team_rows}

    # Onboarding by status
    onb_status_rows = db.query(OnboardingCase.status, func.count(OnboardingCase.case_id)).group_by(OnboardingCase.status).all()
    onboarding_by_status = {row[0]: row[1] for row in onb_status_rows}

    return DashboardSummaryResponse(
        total_employees=total_emp,
        active_employees=active_emp,
        pending_onboarding=pending_onb,
        completed_onboarding=completed_onb,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        blocked_tasks=blocked_tasks,
        overdue_tasks=overdue_tasks,
        pending_approvals=pending_approvals,
        active_access_grants=active_grants,
        active_offboardings=active_off,
        total_anomalies=total_anomalies,
        anomaly_breakdown=anomaly_breakdown,
        tasks_by_team=tasks_by_team,
        onboarding_by_status=onboarding_by_status,
    )


# ==========================================
# Catalogs: Departments, Roles, Managers
# ==========================================

@router.get("/departments", response_model=List[DepartmentResponse], tags=["Catalog"])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.department_id).all()


@router.get("/roles", response_model=List[RoleResponse], tags=["Catalog"])
def get_roles(
    department_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Role)
    if department_id:
        query = query.filter(Role.department_id == department_id)
    return query.order_by(Role.role_id).all()


@router.get("/managers", response_model=List[ManagerResponse], tags=["Catalog"])
def get_managers(
    department_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Manager)
    if department_id:
        query = query.filter(Manager.department_id == department_id)
    return query.order_by(Manager.manager_id).all()


# ==========================================
# Employees
# ==========================================

@router.get("/employees", response_model=List[EmployeeResponse], tags=["Employees"])
def get_employees(
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    if search:
        search_filter = or_(
            Employee.first_name.ilike(f"%{search}%"),
            Employee.last_name.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%"),
            Employee.employee_id.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    return query.order_by(Employee.employee_id).offset(offset).limit(limit).all()


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, tags=["Employees"])
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    # Verify FKs
    dept = db.query(Department).filter(Department.department_id == payload.department_id).first()
    if not dept:
        raise HTTPException(status_code=400, detail=f"Department {payload.department_id} does not exist")
    role = db.query(Role).filter(Role.role_id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role {payload.role_id} does not exist")

    count = db.query(Employee).count() + 1
    emp_id = f"EMP-{count:06d}"
    now = datetime.now(timezone.utc)

    emp = Employee(
        employee_id=emp_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        department_id=payload.department_id,
        role_id=payload.role_id,
        manager_id=payload.manager_id,
        location_type=payload.location_type,
        employment_type=payload.employment_type,
        status=EmployeeStatus.PENDING.value,
        start_date=payload.start_date,
        created_at=now,
        updated_at=now,
    )
    db.add(emp)

    # Initial history
    h_count = db.query(EmployeeDepartmentHistory).count() + 1
    hist = EmployeeDepartmentHistory(
        history_id=f"EDH-{h_count:06d}",
        employee_id=emp_id,
        department_id=payload.department_id,
        effective_start_date=now,
        change_reason="New hire creation",
        created_at=now,
    )
    db.add(hist)

    log_audit_event(
        db=db,
        entity_type="Employee",
        entity_id=emp_id,
        action="CREATE_EMPLOYEE",
        actor="HR_ADMIN",
        new_state=payload.model_dump(),
        reason="Created via REST API",
        timestamp=now,
    )

    db.commit()
    db.refresh(emp)
    return emp


@router.get("/employees/{id}", response_model=EmployeeResponse, tags=["Employees"])
def get_employee_by_id(id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {id} not found")
    return emp


# ==========================================
# Onboarding Cases & Tasks
# ==========================================

@router.get("/onboarding", response_model=List[OnboardingCaseResponse], tags=["Onboarding"])
def get_onboarding_cases(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(OnboardingCase)
    if status:
        query = query.filter(OnboardingCase.status == status)
    return query.order_by(OnboardingCase.case_id).offset(offset).limit(limit).all()


@router.post("/onboarding", response_model=OnboardingCaseResponse, status_code=status.HTTP_201_CREATED, tags=["Onboarding"])
def create_onboarding_case(
    payload: OnboardingCaseCreate,
    db: Session = Depends(get_db),
):
    emp = db.query(Employee).filter(Employee.employee_id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=400, detail=f"Employee {payload.employee_id} not found")

    existing = db.query(OnboardingCase).filter(OnboardingCase.employee_id == payload.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Employee {payload.employee_id} already has onboarding case {existing.case_id}")

    count = db.query(OnboardingCase).count() + 1
    case_id = f"ONB-2026-{count:06d}"
    now = datetime.now(timezone.utc)

    case = OnboardingCase(
        case_id=case_id,
        employee_id=emp.employee_id,
        status=CaseStatus.INITIATED.value,
        target_start_date=payload.target_start_date,
        actual_start_date=None,
        sla_target_date=payload.target_start_date,
        created_at=now,
        updated_at=now,
    )
    db.add(case)

    # Instantiate the 8 standardized templates
    templates = db.query(TaskTemplate).order_by(TaskTemplate.sequence_order).all()
    for t_idx, tmpl in enumerate(templates, start=1):
        task_id = f"TASK-ONB-{case_id}-{t_idx:03d}"
        task = TaskInstance(
            task_id=task_id,
            case_id=case_id,
            template_id=tmpl.template_id,
            title=tmpl.title,
            owner_team=tmpl.owner_team,
            status=TaskStatus.PENDING.value,
            is_blocked=False if tmpl.sequence_order == 1 else True,
            blocked_reason=None if tmpl.sequence_order == 1 else "Waiting for prerequisite steps",
            due_date=payload.target_start_date,
            created_at=now,
            updated_at=now,
        )
        db.add(task)

    db.commit()
    db.refresh(case)
    return case


@router.get("/onboarding/{id}", response_model=OnboardingCaseDetailResponse, tags=["Onboarding"])
def get_onboarding_case_detail(id: str, db: Session = Depends(get_db)):
    case = db.query(OnboardingCase).filter(OnboardingCase.case_id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Onboarding case {id} not found")
    return case


@router.get("/tasks", response_model=List[TaskInstanceResponse], tags=["Tasks"])
def get_tasks(
    case_id: Optional[str] = None,
    owner_team: Optional[str] = None,
    status: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(TaskInstance)
    if case_id:
        query = query.filter(TaskInstance.case_id == case_id)
    if owner_team:
        query = query.filter(TaskInstance.owner_team == owner_team)
    if status:
        query = query.filter(TaskInstance.status == status)
    if is_blocked is not None:
        query = query.filter(TaskInstance.is_blocked == is_blocked)

    return query.order_by(TaskInstance.task_id).offset(offset).limit(limit).all()


@router.patch("/tasks/{id}/status", response_model=TaskInstanceResponse, tags=["Tasks"])
def update_task_status_endpoint(
    id: str,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        task = update_task_status(
            db=db,
            task_id=id,
            new_status=payload.status,
            actor=payload.actor,
            reason=payload.reason,
            enforce_dependencies=True,
        )
        return task
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


# ==========================================
# Assets
# ==========================================

@router.get("/assets", response_model=List[AssetResponse], tags=["Assets"])
def get_assets(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Asset)
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    return query.order_by(Asset.asset_id).offset(offset).limit(limit).all()


@router.post("/assets/{id}/assign", response_model=AssetAssignmentResponse, tags=["Assets"])
def assign_asset_endpoint(
    id: str,
    payload: AssetAssignRequest,
    db: Session = Depends(get_db),
):
    try:
        asgn = assign_asset(
            db=db,
            asset_id=id,
            employee_id=payload.employee_id,
            assigned_date=payload.assigned_date,
            return_due_date=payload.return_due_date,
            force_override=payload.force_override,
        )
        return asgn
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


@router.post("/assets/{id}/recover", response_model=AssetResponse, tags=["Assets"])
def recover_asset_endpoint(
    id: str,
    payload: AssetRecoverRequest,
    db: Session = Depends(get_db),
):
    try:
        asset = recover_asset(
            db=db,
            asset_id=id,
            returned_date=payload.returned_date,
            notes=payload.notes,
        )
        return asset
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


# ==========================================
# Access Management
# ==========================================

@router.get("/access-requests", response_model=List[AccessRequestResponse], tags=["Access"])
def get_access_requests(
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AccessRequest)
    if employee_id:
        query = query.filter(AccessRequest.employee_id == employee_id)
    if status:
        query = query.filter(AccessRequest.status == status)
    return query.order_by(AccessRequest.request_id).offset(offset).limit(limit).all()


@router.post("/access-requests", response_model=AccessRequestResponse, status_code=status.HTTP_201_CREATED, tags=["Access"])
def create_access_request(
    payload: AccessRequestCreate,
    db: Session = Depends(get_db),
):
    emp = db.query(Employee).filter(Employee.employee_id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=400, detail=f"Employee {payload.employee_id} not found")

    count = db.query(AccessRequest).count() + 1
    req_id = f"ACCREQ-2026-{count:06d}"
    now = datetime.now(timezone.utc)

    req = AccessRequest(
        request_id=req_id,
        employee_id=emp.employee_id,
        system_name=payload.system_name,
        access_level=payload.access_level,
        status=RequestStatus.REQUESTED.value,
        justification=payload.justification,
        created_at=now,
        updated_at=now,
    )
    db.add(req)

    # Initial pending approval
    appr_count = db.query(Approval).count() + 1
    appr = Approval(
        approval_id=f"APPR-{appr_count:06d}",
        request_id=req_id,
        approver_id=emp.manager_id or "MGR-001",
        approver_role="MANAGER",
        status=ApprovalStatus.PENDING.value,
        created_at=now,
    )
    db.add(appr)

    log_audit_event(
        db=db,
        entity_type="AccessRequest",
        entity_id=req_id,
        action="CREATE_REQUEST",
        actor=emp.employee_id,
        new_state=payload.model_dump(),
        reason="Access request initiated",
        timestamp=now,
    )

    db.commit()
    db.refresh(req)
    return req


@router.post("/access-requests/{id}/approve", response_model=AccessRequestResponse, tags=["Access"])
def approve_access_request_endpoint(
    id: str,
    payload: AccessApprovalRequest,
    db: Session = Depends(get_db),
):
    try:
        req = approve_access_request(
            db=db,
            request_id=id,
            approver_id=payload.approver_id,
            decision=payload.decision,
            comments=payload.comments,
        )
        return req
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


@router.post("/access-requests/{id}/provision", response_model=AccessGrantResponse, tags=["Access"])
def provision_access_endpoint(
    id: str,
    payload: AccessProvisionRequest,
    db: Session = Depends(get_db),
):
    try:
        grant = provision_access_request(
            db=db,
            request_id=id,
            provisioner_id=payload.provisioner_id,
            enforce_approval=True,
        )
        return grant
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


@router.get("/approvals", response_model=List[ApprovalResponse], tags=["Access"])
def get_approvals(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Approval)
    if status:
        query = query.filter(Approval.status == status)
    return query.order_by(Approval.approval_id).offset(offset).limit(limit).all()


# ==========================================
# Offboarding
# ==========================================

@router.get("/offboarding", response_model=List[OffboardingResponse], tags=["Offboarding"])
def get_offboarding_cases(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(OffboardingCase)
    if status:
        query = query.filter(OffboardingCase.status == status)
    return query.order_by(OffboardingCase.offboarding_id).offset(offset).limit(limit).all()


@router.post("/offboarding", response_model=OffboardingResponse, status_code=status.HTTP_201_CREATED, tags=["Offboarding"])
def initiate_offboarding_endpoint(
    payload: OffboardingCreate,
    db: Session = Depends(get_db),
):
    try:
        off = initiate_offboarding(
            db=db,
            employee_id=payload.employee_id,
            reason=payload.reason,
            termination_date=payload.termination_date,
        )
        return off
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


@router.post("/offboarding/{id}/revoke-access", response_model=OffboardingResponse, tags=["Offboarding"])
def revoke_offboarding_access_endpoint(
    id: str,
    payload: OffboardingRevokeRequest,
    db: Session = Depends(get_db),
):
    try:
        off = revoke_offboarding_access(
            db=db,
            offboarding_id=id,
            actor=payload.actor,
            notes=payload.notes,
        )
        return off
    except OrchestrationError as e:
        raise HTTPException(status_code=400, detail={"error": e.message, "code": e.code})


# ==========================================
# Audit Events & Anomalies
# ==========================================

@router.get("/audit-events", response_model=List[AuditEventResponse], tags=["Audit"])
def get_audit_events(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AuditEvent)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditEvent.entity_id == entity_id)
    if actor:
        query = query.filter(AuditEvent.actor == actor)
    return query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()


@router.get("/anomalies", response_model=List[IssueRecordResponse], tags=["Anomalies"])
def get_anomalies(
    severity: Optional[str] = None,
    issue_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(IssueRecord)
    if severity:
        query = query.filter(IssueRecord.severity == severity)
    if issue_type:
        query = query.filter(IssueRecord.issue_type == issue_type)
    return query.order_by(IssueRecord.issue_id).offset(offset).limit(limit).all()


# ==========================================
# Rule-Based Validation & Analytics
# ==========================================

@router.get("/validation", response_model=ValidationResultResponse, tags=["Validation"])
def run_validation_endpoint(db: Session = Depends(get_db)):
    ref_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    validator = RuleBasedValidator(ref_date=ref_date)

    res = validator.validate_dataset(
        departments=db.query(Department).all(),
        roles=db.query(Role).all(),
        managers=db.query(Manager).all(),
        employees=db.query(Employee).all(),
        task_templates=db.query(TaskTemplate).all(),
        task_dependencies=db.query(TaskDependency).all(),
        onboarding_cases=db.query(OnboardingCase).all(),
        task_instances=db.query(TaskInstance).all(),
        assets=db.query(Asset).all(),
        asset_assignments=db.query(AssetAssignment).all(),
        access_requests=db.query(AccessRequest).all(),
        approvals=db.query(Approval).all(),
        access_grants=db.query(AccessGrant).all(),
        department_history=db.query(EmployeeDepartmentHistory).all(),
        offboarding_cases=db.query(OffboardingCase).all(),
    )

    # Check for ground truth in data/full/ground_truth.json or data/starter/ground_truth.json
    gt_path = "data/full/ground_truth.json"
    if not os.path.exists(gt_path):
        gt_path = "data/starter/ground_truth.json"

    evaluation = None
    if os.path.exists(gt_path):
        with open(gt_path, "r", encoding="utf-8") as f:
            gt = json.load(f)
        evaluation = evaluate_detection(res["detected_issues"], gt)
        res["evaluation_metrics"] = evaluation

    return res


@router.get("/metrics", response_model=MetricsResponse, tags=["Analytics"])
def get_metrics_endpoint(db: Session = Depends(get_db)):
    total_onb = db.query(OnboardingCase).count()
    comp_onb = db.query(OnboardingCase).filter(OnboardingCase.status == CaseStatus.COMPLETED.value).count()
    completion_rate = round((comp_onb / total_onb) * 100, 2) if total_onb > 0 else 0.0

    ref_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    total_tasks = db.query(TaskInstance).count()
    overdue_tasks = db.query(TaskInstance).filter(
        TaskInstance.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value, TaskStatus.BLOCKED.value]),
        TaskInstance.due_date < ref_date
    ).count()
    sla_adherence = round(((total_tasks - overdue_tasks) / total_tasks) * 100, 2) if total_tasks > 0 else 100.0

    total_assets = db.query(Asset).count()
    assigned_assets = db.query(Asset).filter(Asset.status == AssetStatus.ASSIGNED.value).count()
    asset_util = round((assigned_assets / total_assets) * 100, 2) if total_assets > 0 else 0.0

    # Load ground truth evaluation
    gt_path = "data/full/manifest.json"
    if not os.path.exists(gt_path):
        gt_path = "data/starter/manifest.json"

    eval_data = {}
    if os.path.exists(gt_path):
        with open(gt_path, "r", encoding="utf-8") as f:
            m = json.load(f)
            eval_data = m.get("evaluation_metrics", {})

    anomalies_count = db.query(IssueRecord).count()

    return MetricsResponse(
        onboarding_completion_rate=completion_rate,
        task_sla_adherence_rate=sla_adherence,
        asset_utilization_rate=asset_util,
        average_days_to_clear_onboarding=4.5,
        anomalies_detected_count=anomalies_count,
        ground_truth_evaluation=eval_data,
    )


# ==========================================
# Data Exports
# ==========================================

@router.get("/exports/{format}", tags=["Exports"])
def export_data_endpoint(format: str):
    base_dir = "data/full" if os.path.exists("data/full") else "data/starter"

    if format == "json":
        path = os.path.join(base_dir, "validation_summary.json")
        if os.path.exists(path):
            return FileResponse(path, media_type="application/json", filename="validation_summary.json")
    elif format == "csv":
        path = os.path.join(base_dir, "employees.csv")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/csv", filename="employees.csv")
    elif format == "sql":
        path = os.path.join(base_dir, "seed.sql")
        if os.path.exists(path):
            return FileResponse(path, media_type="text/plain", filename="seed.sql")
    elif format == "manifest":
        path = os.path.join(base_dir, "manifest.json")
        if os.path.exists(path):
            return FileResponse(path, media_type="application/json", filename="manifest.json")

    raise HTTPException(status_code=404, detail=f"Export format '{format}' not found or fixture not generated yet")
