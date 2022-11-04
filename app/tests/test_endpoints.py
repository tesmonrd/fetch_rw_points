from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from pathlib import Path
import pytest
import os


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def cleanup_db():
    # locate project root
    parent_dir = str(Path(__file__).parent.parent.parent)
    os.remove(parent_dir+"/base_db.db")
    os.remove(parent_dir+"/test.db")


def _create_transactions(bulk=False):
    """Helper method to populate db with transactions."""
    if not bulk:
        response = client.post(
            "/transaction/add/",
            json={"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"},
        )
        return response
    else:
        response = client.post(
            "/transaction/add/bulk/",
            json=[{"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"},
                  {"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"},
                  {"payer": "DANNON", "points": -200, "timestamp": "2022-10-31T15:00:00Z"},
                  {"payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"},
                  {"payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"}
                  ]
        )
        return response


def test_create_transaction(test_db):
    response = _create_transactions(bulk=False)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["payer"] == "DANNON"
    assert "id" in data


def test_invalid_transaction(test_db):
    response = client.post(
        "/transaction/add/",
        json={"payer": "DANNON", "timestamp": "2022-10-31T10:00:00Z"},
    )
    assert response.status_code == 422, response.text


def test_create_bulk_transactions(test_db):
    response = _create_transactions(bulk=True)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 5


def test_check_balance(test_db):
    _create_transactions(bulk=True)
    response = client.get("/balances/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert {'payer': 'MILLER COORS', 'points': 10000} in data
    assert {'payer': 'UNILEVER', 'points': 200} in data
    assert {'payer': 'DANNON', 'points': 1100} in data


def test_spend(test_db):
    _create_transactions(bulk=True)
    response = client.post("/spend/?spend_amt=5000")
    data = response.json()
    assert response.status_code == 200, response.text
    assert len(data) == 3
    pts = [d["points"] for d in data]
    for pt in pts:
        assert pt < 0


def test_show_transactions(test_db):
    _create_transactions(bulk=False)
    _create_transactions(bulk=True)
    response = client.get("/transactions/")
    data = response.json()
    assert len(data) == 6
    cleanup_db()
