import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.app.models.entities import (
    TaskTemplate,
    TaskDependency,
    TaskInstance,
    OnboardingCase,
    Employee,
    AccessRequest,
    Approval,
    AccessGrant,
    Asset,
    AssetAssignment,
    OffboardingCase,
    AuditEvent,
    TaskStatusEvent,
    TaskStatus,
    RequestStatus,
    ApprovalStatus,
    GrantStatus,
    AssetStatus,
    AssignmentStatus,
    EmployeeStatus,
)
from backend.app.services.orchestrator_service import (
    update_task_status,
    approve_access_request,
    provision_access_request,
    assign_asset,
    recover_asset,
    initiate_offboarding,
    revoke_offboarding_access,
    OrchestrationError,
)
from backend.generator.validator import RuleBasedValidator


def test_dependency_graph_cycle_rejection():
    """Verifies that cycles in the task dependency graph are caught and rejected."""
    validator = RuleBasedValidator()
    
    # Create cyclical templates
    t1 = TaskTemplate(template_id="T1", title="A", description="A", owner_team="HR", sequence_order=1, phase="PRE")
    t2 = TaskTemplate(template_id="T2", title="B", description="B", owner_team="IT", sequence_order=2, phase="DAY")
    
    # Cyclic dependencies: T1 -> T2 and T2 -> T1
    d1 = TaskDependency(dependency_id="D1", predecessor_template_id="T1", successor_template_id="T2")
    d2 = TaskDependency(dependency_id="D2", predecessor_template_id="T2", successor_template_id="T1")

    validator._check_acyclic_dependencies([t1, t2], [d1, d2])
    assert len(validator.integrity_failures) > 0
    assert "Cyclic dependency" in validator.integrity_failures[0]["error"]


def test_invalid_task_completion_rejection(isolated_db: Session):
    """Verifies that completing a task whose predecessor is still pending raises OrchestrationError."""
    # Find a case with pending tasks
    case = isolated_db.query(OnboardingCase).first()
    assert case is not None

    # TPL-003 (SSO Identity) requires TPL-001 (Identity verification)
    task1 = (
        isolated_db.query(TaskInstance)
        .filter(TaskInstance.case_id == case.case_id, TaskInstance.template_id == "TPL-001")
        .first()
    )
    task3 = (
        isolated_db.query(TaskInstance)
        .filter(TaskInstance.case_id == case.case_id, TaskInstance.template_id == "TPL-003")
        .first()
    )

    # Ensure task1 is PENDING
    task1.status = TaskStatus.PENDING.value
    task1.completed_at = None
    task3.status = TaskStatus.PENDING.value
    task3.completed_at = None
    isolated_db.commit()

    # Attempting to complete task3 while task1 is pending must fail!
    with pytest.raises(OrchestrationError) as exc_info:
        update_task_status(
            db=isolated_db,
            task_id=task3.task_id,
            new_status=TaskStatus.COMPLETED.value,
            actor="TEST_RUNNER",
            enforce_dependencies=True,
        )
    assert "Prerequisite task(s) not completed" in str(exc_info.value)
    assert exc_info.value.code == "PREREQUISITE_NOT_MET"


def test_account_creation_blocked_until_identity_verification(isolated_db: Session):
    """Verifies that SSO / Corporate Account Creation (TPL-003) is blocked until Identity Verification (TPL-001) completes."""
    case = isolated_db.query(OnboardingCase).first()
    t1 = isolated_db.query(TaskInstance).filter(TaskInstance.case_id == case.case_id, TaskInstance.template_id == "TPL-001").first()
    t3 = isolated_db.query(TaskInstance).filter(TaskInstance.case_id == case.case_id, TaskInstance.template_id == "TPL-003").first()

    t1.status = TaskStatus.PENDING.value
    t1.completed_at = None
    isolated_db.commit()

    # Must be blocked
    with pytest.raises(OrchestrationError):
        update_task_status(isolated_db, t3.task_id, TaskStatus.COMPLETED.value)

    # Now complete t1
    update_task_status(isolated_db, t1.task_id, TaskStatus.COMPLETED.value, actor="HR_VERIFIER")
    assert t1.status == TaskStatus.COMPLETED.value

    # Now t3 can complete cleanly!
    update_task_status(isolated_db, t3.task_id, TaskStatus.COMPLETED.value, actor="IT_ADMIN")
    assert t3.status == TaskStatus.COMPLETED.value


def test_provisioning_blocked_before_approval(isolated_db: Session):
    """Verifies that an unapproved AccessRequest CANNOT be provisioned."""
    req = AccessRequest(
        request_id="ACCREQ-TEST-0001",
        employee_id="EMP-000001",
        system_name="AWS_CLOUD",
        access_level="ADMIN",
        status=RequestStatus.REQUESTED.value,
        justification="Cloud engineering tests",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    isolated_db.add(req)
    isolated_db.commit()

    # Attempting to provision without approval raises OrchestrationError
    with pytest.raises(OrchestrationError) as exc:
        provision_access_request(isolated_db, req.request_id, enforce_approval=True)
    assert "Illegal provisioning" in str(exc.value)
    assert exc.value.code == "APPROVAL_REQUIRED"


def test_successful_approval_and_provisioning_flow(isolated_db: Session):
    """Verifies the complete valid flow: Request -> Approval -> Provision -> Grant created."""
    req = AccessRequest(
        request_id="ACCREQ-TEST-0002",
        employee_id="EMP-000001",
        system_name="GITHUB",
        access_level="WRITE",
        status=RequestStatus.REQUESTED.value,
        justification="Repository contributor access",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    isolated_db.add(req)
    isolated_db.commit()

    # 1. Approve
    approved_req = approve_access_request(
        db=isolated_db,
        request_id=req.request_id,
        approver_id="MGR-001",
        decision="APPROVED",
        comments="Approved for daily development",
    )
    assert approved_req.status == RequestStatus.APPROVED.value

    # 2. Provision
    grant = provision_access_request(
        db=isolated_db,
        request_id=req.request_id,
        provisioner_id="IT_ADMIN",
    )
    assert grant is not None
    assert grant.status == GrantStatus.ACTIVE.value
    assert grant.system_name == "GITHUB"
    assert approved_req.status == RequestStatus.PROVISIONED.value


def test_task_event_and_audit_preservation(isolated_db: Session):
    """Verifies that state transitions write immutable audit and event records rather than overwriting history."""
    case = isolated_db.query(OnboardingCase).first()
    t1 = isolated_db.query(TaskInstance).filter(TaskInstance.case_id == case.case_id, TaskInstance.template_id == "TPL-001").first()

    t1.status = TaskStatus.PENDING.value
    t1.completed_at = None
    isolated_db.commit()

    initial_audit_count = isolated_db.query(AuditEvent).count()
    initial_tse_count = isolated_db.query(TaskStatusEvent).count()

    update_task_status(
        db=isolated_db,
        task_id=t1.task_id,
        new_status=TaskStatus.COMPLETED.value,
        actor="AUDIT_VERIFIER",
        reason="Verified legal ID in person",
    )

    new_audit_count = isolated_db.query(AuditEvent).count()
    new_tse_count = isolated_db.query(TaskStatusEvent).count()

    assert new_audit_count > initial_audit_count
    assert new_tse_count > initial_tse_count

    event = (
        isolated_db.query(TaskStatusEvent)
        .filter(TaskStatusEvent.task_id == t1.task_id)
        .order_by(TaskStatusEvent.timestamp.desc())
        .first()
    )
    assert event.new_status == TaskStatus.COMPLETED.value
    assert event.actor == "AUDIT_VERIFIER"


def test_offboarding_workflow_and_access_revocation(isolated_db: Session):
    """Verifies that terminating an employee initiates offboarding, and revoking access updates grants."""
    emp = isolated_db.query(Employee).filter(Employee.status == EmployeeStatus.ACTIVE.value).first()
    assert emp is not None

    # Provision an active grant
    req = AccessRequest(
        request_id="ACCREQ-TEST-TERM",
        employee_id=emp.employee_id,
        system_name="VPN_INTERNAL",
        access_level="READ",
        status=RequestStatus.APPROVED.value,
        justification="VPN access",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    isolated_db.add(req)
    isolated_db.commit()

    grant = provision_access_request(isolated_db, req.request_id)
    assert grant.status == GrantStatus.ACTIVE.value

    # Initiate offboarding
    off_case = initiate_offboarding(
        db=isolated_db,
        employee_id=emp.employee_id,
        reason="RESIGNATION",
    )
    assert off_case is not None
    assert emp.status == EmployeeStatus.TERMINATED.value
    assert off_case.access_revocation_status == "PENDING"

    # Revoke access
    updated_off = revoke_offboarding_access(
        db=isolated_db,
        offboarding_id=off_case.offboarding_id,
        actor="SEC_OFFICER",
    )
    assert updated_off.access_revocation_status == "COMPLETED"

    # Verify grant is revoked
    isolated_db.refresh(grant)
    assert grant.status == GrantStatus.REVOKED.value
    assert grant.revoked_at is not None


def test_asset_assignment_and_recovery(isolated_db: Session):
    """Verifies asset assignment, double-assignment rejection, and asset recovery."""
    asset = Asset(
        asset_id="AST-TST-000001",
        asset_tag="YF-TST-000001",
        category="LAPTOP",
        model="Dell Latitude 7440",
        serial_number="SN-TEST-9999",
        status=AssetStatus.AVAILABLE.value,
        created_at=datetime.now(timezone.utc),
    )
    isolated_db.add(asset)
    isolated_db.commit()

    emp1 = isolated_db.query(Employee).first()
    emp2 = isolated_db.query(Employee).offset(1).first()

    # Assign to emp1
    asgn1 = assign_asset(isolated_db, asset.asset_id, emp1.employee_id)
    assert asgn1.status == AssignmentStatus.ACTIVE.value
    assert asset.status == AssetStatus.ASSIGNED.value

    # Attempting to assign to emp2 while actively assigned must fail!
    with pytest.raises(OrchestrationError) as exc:
        assign_asset(isolated_db, asset.asset_id, emp2.employee_id, force_override=False)
    assert "Overlapping assignment forbidden" in str(exc.value)

    # Recover asset
    recovered_asset = recover_asset(isolated_db, asset.asset_id, notes="Returned at exit desk")
    assert recovered_asset.status == AssetStatus.AVAILABLE.value
    isolated_db.refresh(asgn1)
    assert asgn1.status == AssignmentStatus.RETURNED.value
