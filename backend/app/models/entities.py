from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


# ==========================================
# Enumerations
# ==========================================

class LocationType(str, enum.Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    CONTRACTOR = "CONTRACTOR"


class EmployeeStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"


class CaseStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TeamOwner(str, enum.Enum):
    HR = "HR"
    IT = "IT"
    FACILITIES = "FACILITIES"
    MANAGER = "MANAGER"
    SECURITY = "SECURITY"


class AssetCategory(str, enum.Enum):
    LAPTOP = "LAPTOP"
    MONITOR = "MONITOR"
    SECURITY_KEY = "SECURITY_KEY"
    MOBILE_PHONE = "MOBILE_PHONE"
    HEADSET = "HEADSET"


class AssetStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"


class AssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class RequestStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROVISIONED = "PROVISIONED"
    REVOKED = "REVOKED"


class AccessLevel(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class GrantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class OffboardingStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class IssueSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IssueStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    SUPPRESSED = "SUPPRESSED"


# ==========================================
# Core Catalog & Organizational Models
# ==========================================

class Department(Base):
    __tablename__ = "departments"

    department_id = Column(String(32), primary_key=True)  # e.g. DEP-01
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)
    cost_center = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    roles = relationship("Role", back_populates="department")
    employees = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String(32), primary_key=True)  # e.g. ROL-01
    title = Column(String(100), nullable=False)
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    clearance_level = Column(String(20), default="STANDARD", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    department = relationship("Department", back_populates="roles")
    employees = relationship("Employee", back_populates="role")


class Manager(Base):
    __tablename__ = "managers"

    manager_id = Column(String(32), primary_key=True)  # e.g. MGR-001
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    management_level = Column(String(20), default="L1", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    managed_employees = relationship("Employee", back_populates="manager", foreign_keys="[Employee.manager_id]")


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(32), primary_key=True)  # EMP-000001
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    role_id = Column(String(32), ForeignKey("roles.role_id"), nullable=False)
    manager_id = Column(String(32), ForeignKey("managers.manager_id"), nullable=True)  # Nullable for Anomaly #2
    location_type = Column(String(20), default=LocationType.REMOTE.value, nullable=False)
    employment_type = Column(String(20), default=EmploymentType.FULL_TIME.value, nullable=False)
    status = Column(String(20), default=EmployeeStatus.PENDING.value, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    role = relationship("Role", back_populates="employees")
    manager = relationship("Manager", back_populates="managed_employees", foreign_keys=[manager_id])
    onboarding_cases = relationship("OnboardingCase", back_populates="employee")
    offboarding_cases = relationship("OffboardingCase", back_populates="employee")
    asset_assignments = relationship("AssetAssignment", back_populates="employee")
    access_requests = relationship("AccessRequest", back_populates="employee")
    access_grants = relationship("AccessGrant", back_populates="employee")
    department_history = relationship("EmployeeDepartmentHistory", back_populates="employee")


class EmployeeDepartmentHistory(Base):
    __tablename__ = "employee_department_history"

    history_id = Column(String(32), primary_key=True)  # EDH-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    effective_start_date = Column(DateTime, nullable=False)
    effective_end_date = Column(DateTime, nullable=True)
    change_reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="department_history")
    department = relationship("Department")


# ==========================================
# Task Workflow & Dependency Models
# ==========================================

class TaskTemplate(Base):
    __tablename__ = "task_templates"

    template_id = Column(String(32), primary_key=True)  # TPL-001
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    owner_team = Column(String(20), nullable=False)  # HR, IT, FACILITIES, MANAGER, SECURITY
    default_sla_days = Column(Integer, default=2, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    sequence_order = Column(Integer, default=1, nullable=False)
    phase = Column(String(30), default="PRE_START", nullable=False)


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    dependency_id = Column(String(32), primary_key=True)  # DEP-TPL-001
    predecessor_template_id = Column(String(32), ForeignKey("task_templates.template_id"), nullable=False)
    successor_template_id = Column(String(32), ForeignKey("task_templates.template_id"), nullable=False)
    dependency_type = Column(String(20), default="FINISH_TO_START", nullable=False)

    __table_args__ = (
        UniqueConstraint("predecessor_template_id", "successor_template_id", name="uq_task_dependency"),
    )


class OnboardingCase(Base):
    __tablename__ = "onboarding_cases"

    case_id = Column(String(32), primary_key=True)  # ONB-2026-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    status = Column(String(20), default=CaseStatus.INITIATED.value, nullable=False)
    target_start_date = Column(DateTime, nullable=False)
    actual_start_date = Column(DateTime, nullable=True)
    sla_target_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="onboarding_cases")
    tasks = relationship("TaskInstance", back_populates="case", cascade="all, delete-orphan")
    status_events = relationship("CaseStatusEvent", back_populates="case", cascade="all, delete-orphan")


class TaskInstance(Base):
    __tablename__ = "task_instances"

    task_id = Column(String(64), primary_key=True)  # TASK-ONB-<case-id>-001
    case_id = Column(String(32), ForeignKey("onboarding_cases.case_id"), nullable=False)
    template_id = Column(String(32), ForeignKey("task_templates.template_id"), nullable=False)
    title = Column(String(120), nullable=False)
    owner_team = Column(String(20), nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING.value, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_reason = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(String(60), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    case = relationship("OnboardingCase", back_populates="tasks")
    template = relationship("TaskTemplate")
    status_events = relationship("TaskStatusEvent", back_populates="task", cascade="all, delete-orphan")


class TaskStatusEvent(Base):
    __tablename__ = "task_status_events"

    event_id = Column(String(32), primary_key=True)  # TSE-000001
    task_id = Column(String(64), ForeignKey("task_instances.task_id"), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    actor = Column(String(60), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(String(255), nullable=True)

    task = relationship("TaskInstance", back_populates="status_events")


class CaseStatusEvent(Base):
    __tablename__ = "case_status_events"

    event_id = Column(String(32), primary_key=True)  # CSE-000001
    case_id = Column(String(32), ForeignKey("onboarding_cases.case_id"), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    actor = Column(String(60), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(String(255), nullable=True)

    case = relationship("OnboardingCase", back_populates="status_events")


# ==========================================
# Asset Lifecycle Models
# ==========================================

class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String(32), primary_key=True)  # AST-LAP-000001
    asset_tag = Column(String(32), nullable=False, unique=True)
    category = Column(String(30), nullable=False)
    model = Column(String(80), nullable=False)
    serial_number = Column(String(50), nullable=False, unique=True)
    status = Column(String(20), default=AssetStatus.AVAILABLE.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    assignments = relationship("AssetAssignment", back_populates="asset")


class AssetAssignment(Base):
    __tablename__ = "asset_assignments"

    assignment_id = Column(String(32), primary_key=True)  # ASGN-000001
    asset_id = Column(String(32), ForeignKey("assets.asset_id"), nullable=False)
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    assigned_date = Column(DateTime, nullable=False)
    return_due_date = Column(DateTime, nullable=True)
    returned_date = Column(DateTime, nullable=True)
    status = Column(String(20), default=AssignmentStatus.ACTIVE.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", back_populates="asset_assignments")


# ==========================================
# Access Management & Approvals
# ==========================================

class AccessRequest(Base):
    __tablename__ = "access_requests"

    request_id = Column(String(32), primary_key=True)  # ACCREQ-2026-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    system_name = Column(String(60), nullable=False)
    access_level = Column(String(20), default=AccessLevel.READ.value, nullable=False)
    status = Column(String(20), default=RequestStatus.REQUESTED.value, nullable=False)
    justification = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="access_requests")
    approvals = relationship("Approval", back_populates="request")
    grants = relationship("AccessGrant", back_populates="request")


class Approval(Base):
    __tablename__ = "approvals"

    approval_id = Column(String(32), primary_key=True)  # APPR-000001
    request_id = Column(String(32), ForeignKey("access_requests.request_id"), nullable=False)
    approver_id = Column(String(32), nullable=False)
    approver_role = Column(String(30), default="MANAGER", nullable=False)
    status = Column(String(20), default=ApprovalStatus.PENDING.value, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    comments = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    request = relationship("AccessRequest", back_populates="approvals")


class AccessGrant(Base):
    __tablename__ = "access_grants"

    grant_id = Column(String(32), primary_key=True)  # GRANT-000001
    request_id = Column(String(32), ForeignKey("access_requests.request_id"), nullable=False)
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    system_name = Column(String(60), nullable=False)
    access_level = Column(String(20), nullable=False)
    provisioned_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    status = Column(String(20), default=GrantStatus.ACTIVE.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    request = relationship("AccessRequest", back_populates="grants")
    employee = relationship("Employee", back_populates="access_grants")


class AccessEvent(Base):
    __tablename__ = "access_events"

    event_id = Column(String(32), primary_key=True)  # ACE-000001
    request_id = Column(String(32), ForeignKey("access_requests.request_id"), nullable=True)
    grant_id = Column(String(32), ForeignKey("access_grants.grant_id"), nullable=True)
    action = Column(String(30), nullable=False)
    actor = Column(String(60), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    details = Column(String(255), nullable=True)


# ==========================================
# Offboarding Lifecycle Models
# ==========================================

class OffboardingCase(Base):
    __tablename__ = "offboarding_cases"

    offboarding_id = Column(String(32), primary_key=True)  # OFF-2026-000001
    employee_id = Column(String(32), ForeignKey("employees.employee_id"), nullable=False)
    reason = Column(String(50), default="RESIGNATION", nullable=False)
    termination_date = Column(DateTime, nullable=False)
    status = Column(String(20), default=OffboardingStatus.INITIATED.value, nullable=False)
    access_revocation_status = Column(String(20), default="PENDING", nullable=False)
    asset_recovery_status = Column(String(20), default="PENDING", nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", back_populates="offboarding_cases")


# ==========================================
# Immutable Audit & Issue Tracking
# ==========================================

class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_id = Column(String(64), primary_key=True)  # AUD-YYYYMMDD-000001
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(String(64), nullable=False)
    action = Column(String(50), nullable=False)
    actor = Column(String(60), nullable=False)
    old_state_json = Column(Text, nullable=True)
    new_state_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_timestamp", "timestamp"),
    )


class IssueRecord(Base):
    __tablename__ = "issue_records"

    issue_id = Column(String(32), primary_key=True)  # ISS-000001
    entity_id = Column(String(64), nullable=False)
    issue_type = Column(String(60), nullable=False)
    severity = Column(String(20), default=IssueSeverity.HIGH.value, nullable=False)
    status = Column(String(20), default=IssueStatus.OPEN.value, nullable=False)
    rule_id = Column(String(40), nullable=False)
    evidence_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
