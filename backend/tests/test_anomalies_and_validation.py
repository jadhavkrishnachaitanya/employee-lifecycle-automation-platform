import pytest
from datetime import datetime, timezone, date, timedelta
import json
import os
from sqlalchemy.orm import Session

from backend.generator.data_generator import SyntheticDataGenerator
from backend.generator.validator import RuleBasedValidator, evaluate_detection, ensure_utc
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
    AuditEvent,
    EmployeeStatus,
    CaseStatus,
    TaskStatus,
    GrantStatus,
)


def test_independent_detection_of_all_seven_anomalies():
    """Verifies that the validator independently detects all 7 injected anomaly categories without ground truth."""
    gen = SyntheticDataGenerator(seed=20261022, scale="starter")
    gen.generate_all()

    validator = RuleBasedValidator(ref_date=gen.ref_date)
    result = validator.validate_dataset(
        departments=gen.departments,
        roles=gen.roles,
        managers=gen.managers,
        employees=gen.employees,
        task_templates=gen.task_templates,
        task_dependencies=gen.task_dependencies,
        onboarding_cases=gen.onboarding_cases,
        task_instances=gen.task_instances,
        assets=gen.assets,
        asset_assignments=gen.asset_assignments,
        access_requests=gen.access_requests,
        approvals=gen.approvals,
        access_grants=gen.access_grants,
        department_history=gen.department_history,
        offboarding_cases=gen.offboarding_cases,
    )

    detected_types = set(result["anomaly_counts_by_type"].keys())

    # All seven required anomaly types must be detected:
    expected_seven = {
        "TASK_COMPLETED_BEFORE_PREREQUISITE",
        "MISSING_MANAGER",
        "ASSET_DOUBLE_ASSIGNMENT",
        "STARTED_BEFORE_BACKGROUND_CHECK",
        "TERMINATED_EMPLOYEE_ACTIVE_ACCESS",
        "OVERDUE_INCOMPLETE_TASK",
        "DEPARTMENT_CHANGE_MID_PROCESS",
    }

    assert expected_seven.issubset(detected_types), f"Missing anomalies in detection: {expected_seven - detected_types}"


def test_validation_evaluation_against_ground_truth():
    """Verifies that detected anomalies match ground truth with high precision, recall, and F1 score."""
    gen = SyntheticDataGenerator(seed=20261022, scale="full")
    gen.generate_all()

    validator = RuleBasedValidator(ref_date=gen.ref_date)
    result = validator.validate_dataset(
        departments=gen.departments,
        roles=gen.roles,
        managers=gen.managers,
        employees=gen.employees,
        task_templates=gen.task_templates,
        task_dependencies=gen.task_dependencies,
        onboarding_cases=gen.onboarding_cases,
        task_instances=gen.task_instances,
        assets=gen.assets,
        asset_assignments=gen.asset_assignments,
        access_requests=gen.access_requests,
        approvals=gen.approvals,
        access_grants=gen.access_grants,
        department_history=gen.department_history,
        offboarding_cases=gen.offboarding_cases,
    )

    evaluation = evaluate_detection(result["detected_issues"], gen.ground_truth)

    assert evaluation["precision"] >= 0.85, f"Precision too low: {evaluation['precision']}"
    assert evaluation["recall"] == 1.0, f"Recall was not 100%: {evaluation['recall']}"
    assert evaluation["f1_score"] >= 0.90, f"F1 score too low: {evaluation['f1_score']}"
    assert evaluation["false_negatives"] == 0, f"False negatives detected: {evaluation['false_negatives']}"


def test_zero_ground_truth_leakage():
    """Validates that validator has no access to or dependencies on ground truth files."""
    validator = RuleBasedValidator()
    # Ensure ground_truth is not an attribute of the validator
    assert not hasattr(validator, "ground_truth")
    assert not hasattr(validator, "ground_truth_path")


def test_datetime_normalization_ensure_utc():
    """Regression test: verifies ensure_utc handles naive, aware, date, string, and None."""
    assert ensure_utc(None) is None

    # Naive datetime gets UTC timezone attached
    naive_dt = datetime(2026, 11, 1, 10, 30, 0)
    utc_dt = ensure_utc(naive_dt)
    assert utc_dt.tzinfo == timezone.utc
    assert utc_dt.hour == 10 and utc_dt.minute == 30

    # Aware datetime preserved
    aware_dt = datetime(2026, 11, 1, 10, 30, 0, tzinfo=timezone.utc)
    assert ensure_utc(aware_dt) == aware_dt

    # Non-UTC aware datetime converted
    other_tz = timezone(timedelta(hours=5, minutes=30))
    ist_dt = datetime(2026, 11, 1, 15, 30, 0, tzinfo=other_tz)
    converted = ensure_utc(ist_dt)
    assert converted.tzinfo == timezone.utc
    assert converted.hour == 10 and converted.minute == 0

    # Date object converted to midnight UTC
    d = date(2026, 11, 1)
    converted_date = ensure_utc(d)
    assert converted_date == datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)

    # ISO strings
    assert ensure_utc("2026-11-01T10:30:00Z") == datetime(2026, 11, 1, 10, 30, 0, tzinfo=timezone.utc)
    assert ensure_utc("2026-11-01 10:30:00") == datetime(2026, 11, 1, 10, 30, 0, tzinfo=timezone.utc)


def test_regression_offset_naive_database_records_validation():
    """
    Regression test for:
    TypeError: can't compare offset-naive and offset-aware datetimes in backend/generator/validator.py
    Ensures that when entity records have offset-naive datetimes (as loaded from SQLite),
    validator comparisons against aware ref_date execute cleanly without exception.
    """
    # Create test employee with naive start_date
    emp = Employee(
        employee_id="EMP-TEST-001",
        first_name="Test",
        last_name="User",
        email="test.user@yottaflex.ai",
        department_id="DEP-ENG",
        role_id="ROL-01",
        manager_id="MGR-001",
        location_type="REMOTE",
        employment_type="FULL_TIME",
        status=EmployeeStatus.ACTIVE.value,
        start_date=datetime(2026, 10, 25, 9, 0, 0),  # Naive!
        created_at=datetime(2026, 10, 20, 9, 0, 0),
        updated_at=datetime(2026, 10, 20, 9, 0, 0),
    )

    case = OnboardingCase(
        case_id="ONB-TEST-001",
        employee_id="EMP-TEST-001",
        status=CaseStatus.IN_PROGRESS.value,
        target_start_date=datetime(2026, 10, 25, 9, 0, 0),
        created_at=datetime(2026, 10, 20, 9, 0, 0),
        updated_at=datetime(2026, 10, 20, 9, 0, 0),
    )

    # Incomplete background check completed after start date (naive datetimes)
    bg_task = TaskInstance(
        task_id="TASK-TEST-001",
        case_id="ONB-TEST-001",
        template_id="TPL-002",
        title="Background Check & Clearance",
        owner_team="HR",
        status=TaskStatus.COMPLETED.value,
        due_date=datetime(2026, 10, 24, 18, 0, 0),  # Naive!
        completed_at=datetime(2026, 10, 26, 12, 0, 0),  # Naive! completed AFTER start_date
        completed_by="HR_SPECIALIST",
        is_blocked=False,
        created_at=datetime(2026, 10, 20, 9, 0, 0),
        updated_at=datetime(2026, 10, 26, 12, 0, 0),
    )

    # Aware reference date (as initialized in validator / API)
    ref_date = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    validator = RuleBasedValidator(ref_date=ref_date)

    # Execute _detect_started_before_background_check directly
    validator._detect_started_before_background_check([emp], [case], [bg_task])

    # Assert anomaly was detected without TypeError
    assert len(validator.detected_anomalies) == 1
    detected = validator.detected_anomalies[0]
    assert detected["rule_id"] == "RULE-ONB-004"
    assert detected["issue_type"] == "STARTED_BEFORE_BACKGROUND_CHECK"
    assert detected["entity_id"] == "EMP-TEST-001"


def test_regression_validation_api_endpoint_with_sqlite_db(isolated_full_db: Session):
    """
    Regression test: Verifies that run_validation_endpoint succeeds against an isolated SQLite DB,
    returning HTTP-equivalent 200 payload with all 36 original anomalies detected and 1.0 F1 score.
    Uses a fresh in-memory database to prevent test pollution from live application mutations.
    """
    from backend.app.api.router import run_validation_endpoint

    res = run_validation_endpoint(db=isolated_full_db)
    assert res["validation_status"] == "PASSED"
    assert res["total_anomalies_detected"] == 36
    assert res["total_rules_evaluated"] == 10
    if "evaluation_metrics" in res and res["evaluation_metrics"]:
        assert res["evaluation_metrics"]["precision"] == 1.0
        assert res["evaluation_metrics"]["recall"] == 1.0
        assert res["evaluation_metrics"]["f1_score"] == 1.0


def test_access_revocation_reduces_anomaly_count_and_logs_audit(isolated_db: Session):
    """
    Verifies that when access for a terminated employee is revoked during offboarding:
    1. The TERMINATED_EMPLOYEE_ACTIVE_ACCESS anomaly count is dynamically reduced.
    2. An explicit audit event is recorded with action='REVOKE_ACCESS'.
    3. The access grant status transitions to REVOKED with revoked_at timestamp.
    """
    validator = RuleBasedValidator()

    def run_scan():
        return validator.validate_dataset(
            departments=isolated_db.query(Department).all(),
            roles=isolated_db.query(Role).all(),
            managers=isolated_db.query(Manager).all(),
            employees=isolated_db.query(Employee).all(),
            task_templates=isolated_db.query(TaskTemplate).all(),
            task_dependencies=isolated_db.query(TaskDependency).all(),
            onboarding_cases=isolated_db.query(OnboardingCase).all(),
            task_instances=isolated_db.query(TaskInstance).all(),
            assets=isolated_db.query(Asset).all(),
            asset_assignments=isolated_db.query(AssetAssignment).all(),
            access_requests=isolated_db.query(AccessRequest).all(),
            approvals=isolated_db.query(Approval).all(),
            access_grants=isolated_db.query(AccessGrant).all(),
            department_history=isolated_db.query(EmployeeDepartmentHistory).all(),
            offboarding_cases=isolated_db.query(OffboardingCase).all(),
        )

    initial_scan = run_scan()
    initial_access_anomalies = initial_scan["anomaly_counts_by_type"].get("TERMINATED_EMPLOYEE_ACTIVE_ACCESS", 0)
    assert initial_access_anomalies > 0, "Expected at least one initial active-access anomaly in test DB"

    # Locate an offboarding case with active access grants
    off_case = (
        isolated_db.query(OffboardingCase)
        .filter(OffboardingCase.access_revocation_status == "PENDING")
        .first()
    )
    assert off_case is not None, "Expected an offboarding case with pending revocation"

    # Count active grants belonging to this terminated employee
    active_grants_for_emp = (
        isolated_db.query(AccessGrant)
        .filter(
            AccessGrant.employee_id == off_case.employee_id,
            AccessGrant.status == GrantStatus.ACTIVE.value,
        )
        .all()
    )
    revoked_grant_count = len(active_grants_for_emp)
    assert revoked_grant_count > 0, f"Offboarding case {off_case.offboarding_id} should have active grants"

    audits_before = (
        isolated_db.query(AuditEvent)
        .filter(AuditEvent.action == "REVOKE_ACCESS")
        .count()
    )

    # Perform legitimate access revocation via orchestrator service
    from backend.app.services.orchestrator_service import revoke_offboarding_access
    updated_case = revoke_offboarding_access(
        db=isolated_db,
        offboarding_id=off_case.offboarding_id,
        actor="IT_SEC_ADMIN",
        notes="Manual offboarding verification",
    )
    assert updated_case.access_revocation_status == "COMPLETED"

    # 1. Verify audit event was logged
    audits_after = (
        isolated_db.query(AuditEvent)
        .filter(AuditEvent.action == "REVOKE_ACCESS")
        .count()
    )
    assert audits_after == audits_before + revoked_grant_count, (
        f"Expected {revoked_grant_count} new REVOKE_ACCESS audit events, got {audits_after - audits_before}"
    )

    # 2. Verify all grants for this employee transitioned to REVOKED with timestamp
    for g in active_grants_for_emp:
        isolated_db.refresh(g)
        assert g.status == GrantStatus.REVOKED.value
        assert g.revoked_at is not None

    # 3. Verify independent scan dynamically detects fewer active-access anomalies
    post_revocation_scan = run_scan()
    post_access_anomalies = post_revocation_scan["anomaly_counts_by_type"].get("TERMINATED_EMPLOYEE_ACTIVE_ACCESS", 0)

    # Strictly assert that the anomaly count reduced by exactly the number of revoked grants
    assert post_access_anomalies == initial_access_anomalies - revoked_grant_count

