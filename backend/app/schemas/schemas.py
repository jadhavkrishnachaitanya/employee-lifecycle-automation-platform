from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Base config for ORM mode
class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


# ==========================================
# Departments & Roles & Managers
# ==========================================

class DepartmentBase(ORMBase):
    department_id: str
    name: str
    code: str
    cost_center: str


class DepartmentResponse(DepartmentBase):
    created_at: datetime


class RoleBase(ORMBase):
    role_id: str
    title: str
    department_id: str
    clearance_level: str


class RoleResponse(RoleBase):
    created_at: datetime


class ManagerBase(ORMBase):
    manager_id: str
    name: str
    email: str
    department_id: str
    management_level: str


class ManagerResponse(ManagerBase):
    created_at: datetime


# ==========================================
# Employee
# ==========================================

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    department_id: str
    role_id: str
    manager_id: Optional[str] = None
    location_type: str = "REMOTE"  # REMOTE, HYBRID, ONSITE
    employment_type: str = "FULL_TIME"  # FULL_TIME, CONTRACTOR
    start_date: datetime


class EmployeeUpdate(BaseModel):
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    location_type: Optional[str] = None
    status: Optional[str] = None


class EmployeeResponse(ORMBase):
    employee_id: str
    first_name: str
    last_name: str
    email: str
    department_id: str
    role_id: str
    manager_id: Optional[str]
    location_type: str
    employment_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class DepartmentHistoryResponse(ORMBase):
    history_id: str
    employee_id: str
    department_id: str
    effective_start_date: datetime
    effective_end_date: Optional[datetime]
    change_reason: str
    created_at: datetime


class EmployeeDetailResponse(EmployeeResponse):
    department: Optional[DepartmentResponse] = None
    role: Optional[RoleResponse] = None
    manager: Optional[ManagerResponse] = None
    department_history: List[DepartmentHistoryResponse] = []


# ==========================================
# Tasks & Onboarding
# ==========================================

class TaskTemplateResponse(ORMBase):
    template_id: str
    title: str
    description: str
    owner_team: str
    default_sla_days: int
    is_mandatory: bool
    sequence_order: int
    phase: str


class TaskInstanceResponse(ORMBase):
    task_id: str
    case_id: str
    template_id: str
    title: str
    owner_team: str
    status: str
    is_blocked: bool
    blocked_reason: Optional[str]
    due_date: datetime
    completed_at: Optional[datetime]
    completed_by: Optional[str]
    created_at: datetime
    updated_at: datetime


class TaskStatusUpdate(BaseModel):
    status: str  # COMPLETED, IN_PROGRESS, FAILED
    actor: str = "SYSTEM_ADMIN"
    reason: Optional[str] = "Status updated via orchestration portal"


class TaskStatusEventResponse(ORMBase):
    event_id: str
    task_id: str
    old_status: Optional[str]
    new_status: str
    actor: str
    timestamp: datetime
    reason: Optional[str]


class OnboardingCaseCreate(BaseModel):
    employee_id: str
    target_start_date: datetime


class OnboardingCaseResponse(ORMBase):
    case_id: str
    employee_id: str
    status: str
    target_start_date: datetime
    actual_start_date: Optional[datetime]
    sla_target_date: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class OnboardingCaseDetailResponse(OnboardingCaseResponse):
    employee: Optional[EmployeeResponse] = None
    tasks: List[TaskInstanceResponse] = []


# ==========================================
# Assets
# ==========================================

class AssetResponse(ORMBase):
    asset_id: str
    asset_tag: str
    category: str
    model: str
    serial_number: str
    status: str
    created_at: datetime


class AssetAssignmentResponse(ORMBase):
    assignment_id: str
    asset_id: str
    employee_id: str
    assigned_date: datetime
    return_due_date: Optional[datetime]
    returned_date: Optional[datetime]
    status: str
    created_at: datetime


class AssetAssignRequest(BaseModel):
    employee_id: str
    assigned_date: Optional[datetime] = None
    return_due_date: Optional[datetime] = None
    force_override: bool = False  # If True, bypass duplicate check (used for testing or specific admin override)


class AssetRecoverRequest(BaseModel):
    returned_date: Optional[datetime] = None
    notes: Optional[str] = "Asset recovered during offboarding"


# ==========================================
# Access Management
# ==========================================

class AccessRequestCreate(BaseModel):
    employee_id: str
    system_name: str
    access_level: str = "READ"
    justification: str


class ApprovalResponse(ORMBase):
    approval_id: str
    request_id: str
    approver_id: str
    approver_role: str
    status: str
    decided_at: Optional[datetime]
    comments: Optional[str]
    created_at: datetime


class AccessGrantResponse(ORMBase):
    grant_id: str
    request_id: str
    employee_id: str
    system_name: str
    access_level: str
    provisioned_at: datetime
    revoked_at: Optional[datetime]
    status: str
    created_at: datetime


class AccessRequestResponse(ORMBase):
    request_id: str
    employee_id: str
    system_name: str
    access_level: str
    status: str
    justification: str
    created_at: datetime
    updated_at: datetime
    approvals: List[ApprovalResponse] = []
    grants: List[AccessGrantResponse] = []


class AccessApprovalRequest(BaseModel):
    approver_id: str
    decision: str  # APPROVED, REJECTED
    comments: Optional[str] = None


class AccessProvisionRequest(BaseModel):
    provisioner_id: str = "IT_ADMIN"


# ==========================================
# Offboarding
# ==========================================

class OffboardingCreate(BaseModel):
    employee_id: str
    reason: str = "RESIGNATION"
    termination_date: datetime


class OffboardingResponse(ORMBase):
    offboarding_id: str
    employee_id: str
    reason: str
    termination_date: datetime
    status: str
    access_revocation_status: str
    asset_recovery_status: str
    completed_at: Optional[datetime]
    created_at: datetime


class OffboardingRevokeRequest(BaseModel):
    actor: str = "IT_SEC_ADMIN"
    notes: Optional[str] = "Revoked all active accounts during offboarding"


# ==========================================
# Audit Events & Anomalies
# ==========================================

class AuditEventResponse(ORMBase):
    audit_id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    old_state_json: Optional[str]
    new_state_json: Optional[str]
    timestamp: datetime
    reason: Optional[str]


class IssueRecordResponse(ORMBase):
    issue_id: str
    entity_id: str
    issue_type: str
    severity: str
    status: str
    rule_id: str
    evidence_json: str
    created_at: datetime


# ==========================================
# Dashboards & Analytics
# ==========================================

class DashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    pending_onboarding: int
    completed_onboarding: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    pending_approvals: int
    active_access_grants: int
    active_offboardings: int
    total_anomalies: int
    anomaly_breakdown: Dict[str, int]
    tasks_by_team: Dict[str, int]
    onboarding_by_status: Dict[str, int]


class ValidationResultResponse(BaseModel):
    validation_status: str
    reference_date: str
    total_records_checked: int
    total_rules_evaluated: int
    total_anomalies_detected: int
    anomaly_counts_by_type: Dict[str, int]
    integrity_failures: List[Dict[str, Any]]
    detected_issues: List[Dict[str, Any]]
    evaluation_metrics: Optional[Dict[str, Any]] = None


class MetricsResponse(BaseModel):
    onboarding_completion_rate: float
    task_sla_adherence_rate: float
    asset_utilization_rate: float
    average_days_to_clear_onboarding: float
    anomalies_detected_count: int
    ground_truth_evaluation: Dict[str, Any]
