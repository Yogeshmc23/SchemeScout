import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Criterion, Profile, Rules, Scholarship


@pytest.fixture
def profile():
    return Profile(state="Karnataka", course="B.Tech", education_level="Undergraduate",
                   study_year=2, annual_income=250000, category="OBC")


@pytest.fixture
def scholarship():
    # Synthetic unit-test fixture only; never returned by the running application.
    any_rule = Criterion(status="ANY", evidence="All students may apply.")
    return Scholarship(
        name="Synthetic test scholarship", source_url="https://scholarships.gov.in/test",
        rules=Rules(**{key: any_rule.model_copy() for key in Rules.model_fields}),
        official_source=True, eligibility_complete=True,
        completeness_evidence="All students may apply.", source_evidence="All students may apply.",
    )


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
