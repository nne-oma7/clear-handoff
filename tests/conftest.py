import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Base, get_db
import main

TEST_USERNAME = "staff"
TEST_PASSWORD = "test-password"


@pytest.fixture()
def anonymous_client(monkeypatch):
    monkeypatch.setenv("STAFF_USERNAME", TEST_USERNAME)
    monkeypatch.setenv("STAFF_PASSWORD", TEST_PASSWORD)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, autocommit=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    yield TestClient(main.app)
    main.app.dependency_overrides.clear()


@pytest.fixture()
def client(anonymous_client):
    anonymous_client.auth = (TEST_USERNAME, TEST_PASSWORD)
    return anonymous_client