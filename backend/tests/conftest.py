import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from backend.app.models.entities import Base
from backend.generator.data_generator import SyntheticDataGenerator


@pytest.fixture(scope="session")
def test_generator():
    """Generates an isolated starter dataset for fast, deterministic unit and integration tests."""
    gen = SyntheticDataGenerator(seed=20261022, scale="starter")
    gen.generate_all()
    return gen


@pytest.fixture(scope="function")
def isolated_db():
    """Creates a fresh, completely isolated in-memory SQLite database for each test function."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    
    session = TestingSessionLocal()
    try:
        # Seed basic catalogs and a sample employee/onboarding case
        gen = SyntheticDataGenerator(seed=20261022, scale="starter")
        gen.generate_all()

        session.add_all(gen.departments)
        session.add_all(gen.roles)
        session.add_all(gen.managers)
        session.add_all(gen.employees)
        session.add_all(gen.task_templates)
        session.add_all(gen.task_dependencies)
        session.add_all(gen.onboarding_cases)
        session.add_all(gen.task_instances)
        session.add_all(gen.assets)
        session.add_all(gen.asset_assignments)
        session.add_all(gen.access_requests)
        session.add_all(gen.approvals)
        session.add_all(gen.access_grants)
        session.add_all(gen.offboarding_cases)
        session.add_all(gen.audit_events)
        session.add_all(gen.issue_records)
        session.commit()

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def isolated_full_db():
    """
    Creates a fresh, completely isolated in-memory SQLite database populated with the full deterministic dataset (seed 20261022).
    Session-scoped to allow fast regression validation without mutating or accessing the live application database.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

    session = TestingSession()
    try:
        gen = SyntheticDataGenerator(seed=20261022, scale="full")
        gen.generate_all()

        session.add_all(gen.departments)
        session.add_all(gen.roles)
        session.add_all(gen.managers)
        session.add_all(gen.employees)
        session.add_all(gen.task_templates)
        session.add_all(gen.task_dependencies)
        session.add_all(gen.onboarding_cases)
        session.add_all(gen.task_instances)
        session.add_all(gen.assets)
        session.add_all(gen.asset_assignments)
        session.add_all(gen.access_requests)
        session.add_all(gen.approvals)
        session.add_all(gen.access_grants)
        session.add_all(gen.department_history)
        session.add_all(gen.offboarding_cases)
        session.add_all(gen.audit_events)
        session.add_all(gen.issue_records)
        session.commit()

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
