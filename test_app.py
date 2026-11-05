import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "tasks.sqlite3")})


def test_home_page(app):
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200


def test_health_check(app):
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_add_task_persists_and_trims_title(app, tmp_path):
    client = app.test_client()
    response = client.post("/add", data={"title": "  Test CI/CD  "})

    assert response.status_code == 302
    restarted_app = create_app(
        {"TESTING": True, "DATABASE": str(tmp_path / "tasks.sqlite3")}
    )
    page = restarted_app.test_client().get("/")
    assert b"Test CI/CD" in page.data


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_rejects_invalid_task_titles(app, title):
    client = app.test_client()

    response = client.post("/add", data={"title": title})

    assert response.status_code == 400
    assert b"Task title must be between 1 and 200 characters." in response.data
    assert b"<li>" not in client.get("/").data