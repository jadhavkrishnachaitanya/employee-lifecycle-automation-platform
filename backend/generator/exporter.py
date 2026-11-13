import os
import csv
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from backend.app.models.entities import Base
from backend.generator.data_generator import SyntheticDataGenerator
from backend.generator.validator import RuleBasedValidator, evaluate_detection


def compute_file_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def export_dataset(generator: SyntheticDataGenerator, output_dir: str) -> Dict[str, Any]:
    """Exports generated dataset into SQLite, CSVs, JSON, SQL seed, and manifest."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Populate SQLite Database
    db_path = os.path.join(output_dir, "orchestrator.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)

    with Session(engine, expire_on_commit=False) as session:
        session.add_all(generator.departments)
        session.add_all(generator.roles)
        session.add_all(generator.managers)
        session.add_all(generator.employees)
        session.add_all(generator.department_history)
        session.add_all(generator.task_templates)
        session.add_all(generator.task_dependencies)
        session.add_all(generator.onboarding_cases)
        session.add_all(generator.task_instances)
        session.add_all(generator.task_status_events)
        session.add_all(generator.case_status_events)
        session.add_all(generator.assets)
        session.add_all(generator.asset_assignments)
        session.add_all(generator.access_requests)
        session.add_all(generator.approvals)
        session.add_all(generator.access_grants)
        session.add_all(generator.access_events)
        session.add_all(generator.offboarding_cases)
        session.add_all(generator.audit_events)
        session.add_all(generator.issue_records)
        session.commit()

    # 2. Export CSVs (deterministic sort)
    tables_to_export = [
        ("departments", generator.departments, ["department_id", "name", "code", "cost_center", "created_at"]),
        ("roles", generator.roles, ["role_id", "title", "department_id", "clearance_level", "created_at"]),
        ("managers", generator.managers, ["manager_id", "name", "email", "department_id", "management_level", "created_at"]),
        ("employees", generator.employees, ["employee_id", "first_name", "last_name", "email", "department_id", "role_id", "manager_id", "location_type", "employment_type", "status", "start_date", "end_date", "created_at", "updated_at"]),
        ("task_templates", generator.task_templates, ["template_id", "title", "description", "owner_team", "default_sla_days", "is_mandatory", "sequence_order", "phase"]),
        ("task_dependencies", generator.task_dependencies, ["dependency_id", "predecessor_template_id", "successor_template_id", "dependency_type"]),
        ("onboarding_cases", generator.onboarding_cases, ["case_id", "employee_id", "status", "target_start_date", "actual_start_date", "sla_target_date", "completed_at", "created_at", "updated_at"]),
        ("task_instances", generator.task_instances, ["task_id", "case_id", "template_id", "title", "owner_team", "status", "is_blocked", "blocked_reason", "due_date", "completed_at", "completed_by", "created_at", "updated_at"]),
        ("assets", generator.assets, ["asset_id", "asset_tag", "category", "model", "serial_number", "status", "created_at"]),
        ("asset_assignments", generator.asset_assignments, ["assignment_id", "asset_id", "employee_id", "assigned_date", "return_due_date", "returned_date", "status", "created_at"]),
        ("access_requests", generator.access_requests, ["request_id", "employee_id", "system_name", "access_level", "status", "justification", "created_at", "updated_at"]),
        ("approvals", generator.approvals, ["approval_id", "request_id", "approver_id", "approver_role", "status", "decided_at", "comments", "created_at"]),
        ("access_grants", generator.access_grants, ["grant_id", "request_id", "employee_id", "system_name", "access_level", "provisioned_at", "revoked_at", "status", "created_at"]),
        ("offboarding_cases", generator.offboarding_cases, ["offboarding_id", "employee_id", "reason", "termination_date", "status", "access_revocation_status", "asset_recovery_status", "completed_at", "created_at"]),
        ("employee_department_history", generator.department_history, ["history_id", "employee_id", "department_id", "effective_start_date", "effective_end_date", "change_reason", "created_at"]),
    ]

    for table_name, rows, columns in tables_to_export:
        csv_file = os.path.join(output_dir, f"{table_name}.csv")
        # Sort rows deterministically by their primary key (first column)
        pk_col = columns[0]
        sorted_rows = sorted(rows, key=lambda obj: getattr(obj, pk_col))
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for r in sorted_rows:
                writer.writerow({col: getattr(r, col) for col in columns})

    # 3. Export Ground Truth CSV & JSON
    gt_csv = os.path.join(output_dir, "ground_truth.csv")
    gt_cols = ["issue_id", "entity_id", "issue_type", "expected_label", "severity", "evidence", "rule_id"]
    sorted_gt = sorted(generator.ground_truth, key=lambda x: x["issue_id"])
    with open(gt_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=gt_cols)
        writer.writeheader()
        for g in sorted_gt:
            writer.writerow(g)

    gt_json = os.path.join(output_dir, "ground_truth.json")
    with open(gt_json, "w", encoding="utf-8") as f:
        json.dump(sorted_gt, f, indent=2)

    # 4. Run Rule-Based Validation & Evaluation
    validator = RuleBasedValidator(ref_date=generator.ref_date)
    validation_summary = validator.validate_dataset(
        departments=generator.departments,
        roles=generator.roles,
        managers=generator.managers,
        employees=generator.employees,
        task_templates=generator.task_templates,
        task_dependencies=generator.task_dependencies,
        onboarding_cases=generator.onboarding_cases,
        task_instances=generator.task_instances,
        assets=generator.assets,
        asset_assignments=generator.asset_assignments,
        access_requests=generator.access_requests,
        approvals=generator.approvals,
        access_grants=generator.access_grants,
        department_history=generator.department_history,
        offboarding_cases=generator.offboarding_cases,
    )

    evaluation = evaluate_detection(validation_summary["detected_issues"], generator.ground_truth)
    validation_summary["evaluation_metrics"] = evaluation

    val_json = os.path.join(output_dir, "validation_summary.json")
    with open(val_json, "w", encoding="utf-8") as f:
        json.dump(validation_summary, f, indent=2, default=str)

    # 5. Generate SQL Seed file
    sql_seed_path = os.path.join(output_dir, "seed.sql")
    with open(sql_seed_path, "w", encoding="utf-8") as f:
        f.write("-- YottaFlex Employee Lifecycle Orchestrator SQL Seed Data\n")
        f.write(f"-- Scale: {generator.scale}, Seed: {generator.seed}\n\n")
        for table_name, rows, columns in tables_to_export:
            f.write(f"-- Table: {table_name}\n")
            for r in rows:
                vals = []
                for c in columns:
                    v = getattr(r, c)
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, (int, float)):
                        vals.append(str(v))
                    elif isinstance(v, bool):
                        vals.append("1" if v else "0")
                    else:
                        val_str = str(v).replace("'", "''")
                        vals.append(f"'{val_str}'")
                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(vals)});\n")
            f.write("\n")

    # 6. Generate Manifest with SHA-256 Checksums
    checksums = {}
    files_to_hash = [
        "orchestrator.db",
        "ground_truth.csv",
        "ground_truth.json",
        "validation_summary.json",
        "seed.sql",
    ] + [f"{t[0]}.csv" for t in tables_to_export]

    for fname in sorted(files_to_hash):
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            checksums[fname] = compute_file_sha256(fpath)

    row_counts = {
        "departments": len(generator.departments),
        "roles": len(generator.roles),
        "managers": len(generator.managers),
        "employees": len(generator.employees),
        "onboarding_cases": len(generator.onboarding_cases),
        "task_instances": len(generator.task_instances),
        "assets": len(generator.assets),
        "asset_assignments": len(generator.asset_assignments),
        "access_requests": len(generator.access_requests),
        "approvals": len(generator.approvals),
        "access_grants": len(generator.access_grants),
        "offboarding_cases": len(generator.offboarding_cases),
        "ground_truth_records": len(generator.ground_truth),
        "detected_anomalies": len(validation_summary["detected_issues"]),
    }

    manifest = {
        "manifest_version": "1.0.0",
        "project": "YottaFlex Employee Lifecycle Orchestrator",
        "generator_version": "2.0.0",
        "seed": generator.seed,
        "scale": generator.scale,
        "reference_date": str(generator.ref_date),
        "provenance": {
            "synthetic_engine": "Faker + Deterministic LCG + Rule-Based Anomaly Injector",
            "confidentiality_statement": "100% synthetic data generated for challenge evaluation. No proprietary or real credentials used.",
        },
        "row_counts": row_counts,
        "file_checksums": checksums,
        "evaluation_metrics": evaluation,
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest
