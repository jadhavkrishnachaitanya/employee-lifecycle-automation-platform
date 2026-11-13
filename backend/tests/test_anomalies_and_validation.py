import pytest
from datetime import datetime, timezone
import json
import os

from backend.generator.data_generator import SyntheticDataGenerator
from backend.generator.validator import RuleBasedValidator, evaluate_detection


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
