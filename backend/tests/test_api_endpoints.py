import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.api.router import (
    get_health,
    get_dashboard_summary,
    get_departments,
    get_roles,
    get_managers,
    get_employees,
    get_employee_by_id,
    create_employee,
    get_onboarding_cases,
    get_tasks,
    update_task_status_endpoint,
    get_assets,
    assign_asset_endpoint,
    recover_asset_endpoint,
    get_access_requests,
    create_access_request,
    approve_access_request_endpoint,
    provision_access_endpoint,
    get_approvals,
    get_offboarding_cases,
    initiate_offboarding_endpoint,
    revoke_offboarding_access_endpoint,
    get_audit_events,
    get_anomalies,
    run_validation_endpoint,
    get_metrics_endpoint,
)
from backend.app.schemas.schemas import (
    EmployeeCreate,
    TaskStatusUpdate,
    AssetAssignRequest,
    AssetRecoverRequest,
    AccessRequestCreate,
    AccessApprovalRequest,
    AccessProvisionRequest,
    OffboardingCreate,
    OffboardingRevokeRequest,
)
from backend.app.models.entities import TaskStatus, RequestStatus, EmployeeStatus


def test_api_health():
    res = get_health()
    assert res["status"] == "healthy"
    assert "service" in res


def test_api_dashboard(isolated_db: Session):
    dash = get_dashboard_summary(db=isolated_db)
    assert dash.total_employees >= 25
    assert dash.total_tasks >= 200
    assert dash.total_anomalies > 0


def test_api_employees_crud(isolated_db: Session):
    emps = get_employees(limit=10, offset=0, db=isolated_db)
    assert len(emps) == 10

    first_emp = emps[0]
    single = get_employee_by_id(first_emp.employee_id, db=isolated_db)
    assert single.employee_id == first_emp.employee_id

    # Create employee via API
    new_emp_payload = EmployeeCreate(
        first_name="Ada",
        last_name="Lovelace",
        email="ada.lovelace.test@yottaflex.internal",
        department_id="DEP-01",
        role_id="ROL-01",
        manager_id="MGR-001",
        location_type="REMOTE",
        employment_type="FULL_TIME",
        start_date=datetime.now(timezone.utc),
    )
    created = create_employee(payload=new_emp_payload, db=isolated_db)
    assert created.employee_id.startswith("EMP-")
    assert created.first_name == "Ada"


def test_api_tasks_and_workflow_transition(isolated_db: Session):
    tasks = get_tasks(limit=10, offset=0, db=isolated_db)
    assert len(tasks) > 0

    # Pick task 1 in a case and update it
    task1 = [t for t in tasks if t.template_id == "TPL-001"][0]
    update_payload = TaskStatusUpdate(
        status=TaskStatus.COMPLETED.value,
        actor="API_TEST_RUNNER",
        reason="Manual verification via test",
    )
    res = update_task_status_endpoint(task1.task_id, update_payload, db=isolated_db)
    assert res.status == TaskStatus.COMPLETED.value


def test_api_access_requests_and_approval_flow(isolated_db: Session):
    # Create access request
    req_payload = AccessRequestCreate(
        employee_id="EMP-000001",
        system_name="JIRA_CONFLUENCE",
        access_level="WRITE",
        justification="Project planning tasks",
    )
    new_req = create_access_request(req_payload, db=isolated_db)
    assert new_req.request_id.startswith("ACCREQ-")

    # Approve
    appr_payload = AccessApprovalRequest(
        approver_id="MGR-001",
        decision="APPROVED",
        comments="Approved by lead",
    )
    approved = approve_access_request_endpoint(new_req.request_id, appr_payload, db=isolated_db)
    assert approved.status == RequestStatus.APPROVED.value

    # Provision
    prov_payload = AccessProvisionRequest(provisioner_id="IT_ADMIN")
    grant = provision_access_endpoint(new_req.request_id, prov_payload, db=isolated_db)
    assert grant.grant_id.startswith("GRANT-")
    assert grant.status == "ACTIVE"


def test_api_offboarding_flow(isolated_db: Session):
    off_payload = OffboardingCreate(
        employee_id="EMP-000002",
        reason="RESIGNATION",
        termination_date=datetime.now(timezone.utc),
    )
    off_case = initiate_offboarding_endpoint(off_payload, db=isolated_db)
    assert off_case.offboarding_id.startswith("OFF-2026-")

    # Revoke access
    rev_payload = OffboardingRevokeRequest(actor="SEC_TEST", notes="Revoked all access")
    revoked_case = revoke_offboarding_access_endpoint(off_case.offboarding_id, rev_payload, db=isolated_db)
    assert revoked_case.access_revocation_status == "COMPLETED"


def test_api_validation_and_metrics(isolated_db: Session):
    val_res = run_validation_endpoint(db=isolated_db)
    assert val_res["validation_status"] == "PASSED"
    assert val_res["total_rules_evaluated"] == 10

    metrics = get_metrics_endpoint(db=isolated_db)
    assert metrics.task_sla_adherence_rate >= 0.0
    assert metrics.onboarding_completion_rate >= 0.0
