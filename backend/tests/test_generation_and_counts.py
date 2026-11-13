import pytest
import re
import os
import tempfile
import shutil
from backend.generator.data_generator import SyntheticDataGenerator
from backend.generator.exporter import export_dataset, compute_file_sha256


def test_full_dataset_exact_counts():
    """Validates that full dataset produces EXACTLY the requested row counts."""
    gen = SyntheticDataGenerator(seed=20261022, scale="full")
    gen.generate_all()

    summary = gen.get_summary()
    assert summary["departments"] == 8, f"Expected 8 departments, got {summary['departments']}"
    assert summary["roles"] == 12, f"Expected 12 roles, got {summary['roles']}"
    assert summary["managers"] == 50, f"Expected 50 managers, got {summary['managers']}"
    assert summary["employees"] == 500, f"Expected 500 employees, got {summary['employees']}"
    assert summary["onboarding_cases"] == 500, f"Expected 500 onboarding cases, got {summary['onboarding_cases']}"
    assert summary["task_instances"] == 4000, f"Expected 4000 task instances, got {summary['task_instances']}"
    assert summary["assets"] == 600, f"Expected 600 assets, got {summary['assets']}"
    assert summary["access_requests"] == 300, f"Expected 300 access requests, got {summary['access_requests']}"


def test_id_formatting_and_uniqueness():
    """Validates zero-padded deterministic ID patterns and uniqueness across all entities."""
    gen = SyntheticDataGenerator(seed=20261022, scale="starter")
    gen.generate_all()

    # Employees: EMP-000001
    emp_ids = [e.employee_id for e in gen.employees]
    assert len(emp_ids) == len(set(emp_ids)), "Duplicate Employee IDs detected"
    for eid in emp_ids:
        assert re.match(r"^EMP-\d{6}$", eid), f"Invalid Employee ID format: {eid}"

    # Onboarding cases: ONB-2026-000001
    case_ids = [c.case_id for c in gen.onboarding_cases]
    assert len(case_ids) == len(set(case_ids)), "Duplicate Case IDs detected"
    for cid in case_ids:
        assert re.match(r"^ONB-2026-\d{6}$", cid), f"Invalid Case ID format: {cid}"

    # Tasks: TASK-ONB-<case_id>-001
    task_ids = [t.task_id for t in gen.task_instances]
    assert len(task_ids) == len(set(task_ids)), "Duplicate Task IDs detected"
    for tid in task_ids:
        assert re.match(r"^TASK-ONB-ONB-2026-\d{6}-\d{3}$", tid), f"Invalid Task ID format: {tid}"

    # Assets: AST-LAP-000001, AST-MON-000001, etc.
    asset_ids = [a.asset_id for a in gen.assets]
    assert len(asset_ids) == len(set(asset_ids)), "Duplicate Asset IDs detected"
    for aid in asset_ids:
        assert re.match(r"^AST-[A-Z]{3}-\d{6}$", aid), f"Invalid Asset ID format: {aid}"

    # Access requests: ACCREQ-2026-000001
    req_ids = [r.request_id for r in gen.access_requests]
    assert len(req_ids) == len(set(req_ids)), "Duplicate AccessRequest IDs detected"
    for rid in req_ids:
        assert re.match(r"^ACCREQ-2026-\d{6}$", rid), f"Invalid AccessRequest ID format: {rid}"


def test_foreign_key_and_join_consistency():
    """Verifies that all child entities link to valid parents."""
    gen = SyntheticDataGenerator(seed=20261022, scale="starter")
    gen.generate_all()

    dept_ids = {d.department_id for d in gen.departments}
    role_ids = {r.role_id for r in gen.roles}
    mgr_ids = {m.manager_id for m in gen.managers}
    emp_ids = {e.employee_id for e in gen.employees}
    case_ids = {c.case_id for c in gen.onboarding_cases}
    tmpl_ids = {t.template_id for t in gen.task_templates}

    for r in gen.roles:
        assert r.department_id in dept_ids, f"Role {r.role_id} has invalid department_id {r.department_id}"

    for m in gen.managers:
        assert m.department_id in dept_ids, f"Manager {m.manager_id} has invalid department_id {m.department_id}"

    for e in gen.employees:
        assert e.department_id in dept_ids
        assert e.role_id in role_ids
        if e.manager_id is not None:
            assert e.manager_id in mgr_ids

    for c in gen.onboarding_cases:
        assert c.employee_id in emp_ids

    for t in gen.task_instances:
        assert t.case_id in case_ids
        assert t.template_id in tmpl_ids


def test_deterministic_reproducibility():
    """Verifies that repeated generation with identical seed yields identical file SHA-256 checksums."""
    dir1 = tempfile.mkdtemp(prefix="yotta_run1_")
    dir2 = tempfile.mkdtemp(prefix="yotta_run2_")

    try:
        gen1 = SyntheticDataGenerator(seed=20261022, scale="starter")
        gen1.generate_all()
        m1 = export_dataset(gen1, dir1)

        gen2 = SyntheticDataGenerator(seed=20261022, scale="starter")
        gen2.generate_all()
        m2 = export_dataset(gen2, dir2)

        chk1 = m1["file_checksums"]
        chk2 = m2["file_checksums"]

        assert set(chk1.keys()) == set(chk2.keys())
        for fname in chk1:
            assert chk1[fname] == chk2[fname], f"Checksum mismatch for {fname}: {chk1[fname]} != {chk2[fname]}"
    finally:
        shutil.rmtree(dir1, ignore_errors=True)
        shutil.rmtree(dir2, ignore_errors=True)
