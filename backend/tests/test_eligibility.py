from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.eligibility import match
from app.models import Criterion, Profile, Rules


def test_explicit_any_passes(profile, scholarship):
    assert match(profile, scholarship).status == "ELIGIBLE"


@pytest.mark.parametrize("field,value,allowed", [
    ("state", " Karnataka ", ["karnataka", "Kerala"]),
    ("category", "obc", ["SC", "OBC"]),
    ("education_level", "Undergraduate", ["undergraduate"]),
    ("course", "B.Tech", ["b.tech"]),
])
def test_normalized_exact_values(profile, scholarship, field, value, allowed):
    setattr(profile, field, value)
    setattr(scholarship.rules, field, Criterion(status="RESTRICTED", values=allowed, evidence="Test fixture evidence"))
    assert match(profile, scholarship).status == "ELIGIBLE"


def test_no_silent_course_equivalence(profile, scholarship):
    scholarship.rules.course = Criterion(status="RESTRICTED", values=["Engineering"], evidence="Engineering students only")
    assert match(profile, scholarship).status == "NOT_ELIGIBLE"


@pytest.mark.parametrize("income,status", [(0, "NOT_ELIGIBLE"), (100000, "ELIGIBLE"), (250000, "ELIGIBLE"),
                                         (250001, "NOT_ELIGIBLE"), (None, "NEEDS_INFORMATION")])
def test_income_boundaries(profile, scholarship, income, status):
    profile.annual_income = income
    scholarship.rules.annual_income = Criterion(status="RESTRICTED", minimum=100000, maximum=250000,
                                               evidence="Income from 100000 to 250000")
    assert match(profile, scholarship).status == status


@pytest.mark.parametrize("field", list(Rules.model_fields))
def test_unknown_requirements_never_pass(profile, scholarship, field):
    setattr(scholarship.rules, field, Criterion())
    result = match(profile, scholarship)
    assert result.status == "NEEDS_INFORMATION"
    assert any(c.field == field and c.outcome == "UNKNOWN" for c in result.checks)


@pytest.mark.parametrize("field", ["state", "course", "education_level", "category"])
def test_missing_student_information(profile, scholarship, field):
    setattr(profile, field, None)
    setattr(scholarship.rules, field, Criterion(status="RESTRICTED", values=["test"], evidence="test evidence"))
    assert match(profile, scholarship).status == "NEEDS_INFORMATION"


@pytest.mark.parametrize("flag", ["official_source", "eligibility_complete"])
def test_provenance_and_coverage_required(profile, scholarship, flag):
    setattr(scholarship, flag, False)
    assert match(profile, scholarship).status == "NEEDS_INFORMATION"


def test_expired_deadline(profile, scholarship):
    scholarship.deadline = date.today() - timedelta(days=1)
    assert match(profile, scholarship).status == "NOT_ELIGIBLE"


def test_failure_dominates_unknown(profile, scholarship):
    scholarship.rules.state = Criterion(status="RESTRICTED", values=["Kerala"], evidence="Kerala only")
    scholarship.rules.course = Criterion()
    assert match(profile, scholarship).status == "NOT_ELIGIBLE"


@pytest.mark.parametrize("payload", [
    {"study_year": 0}, {"study_year": True}, {"study_year": 1.5}, {"annual_income": -1},
    {"annual_income": "100"}, {"state": "x"}, {"unknown": "data"},
])
def test_invalid_profiles(payload):
    with pytest.raises(ValidationError):
        Profile(**payload)


@pytest.mark.parametrize("payload", [
    {"status": "ANY"}, {"status": "RESTRICTED", "evidence": "test evidence"},
    {"status": "RESTRICTED", "minimum": 5, "maximum": 2, "evidence": "test evidence"},
    {"status": "UNKNOWN", "maximum": 2},
])
def test_invalid_rules(payload):
    with pytest.raises(ValidationError):
        Criterion(**payload)


def test_rule_field_types():
    with pytest.raises(ValidationError):
        Rules(state=Criterion(status="RESTRICTED", maximum=20, evidence="test evidence"))
    with pytest.raises(ValidationError):
        Rules(study_year=Criterion(status="RESTRICTED", values=["2"], evidence="test evidence"))


@pytest.mark.parametrize("field", ["annual_income", "study_year"])
@pytest.mark.parametrize("value,expected", [(1, "NOT_ELIGIBLE"), (2, "NOT_ELIGIBLE"), (3, "ELIGIBLE"), (4, "NOT_ELIGIBLE")])
def test_exclusive_boundaries(profile, scholarship, field, value, expected):
    setattr(profile, field, value)
    setattr(scholarship.rules, field, Criterion(status="RESTRICTED", minimum=2, maximum=4,
                                              minimum_exclusive=True, maximum_exclusive=True,
                                              evidence="Value strictly between 2 and 4"))
    assert match(profile, scholarship).status == expected


@pytest.mark.parametrize("payload", [
    {"minimum_exclusive": True}, {"maximum_exclusive": True},
    {"status": "RESTRICTED", "minimum": 2, "maximum": 2, "minimum_exclusive": True, "evidence": "test evidence"},
    {"status": "RESTRICTED", "minimum": 2.5, "evidence": "test evidence"},
    {"status": "RESTRICTED", "values": [""], "evidence": "test evidence"},
])
def test_invalid_extended_rules(payload):
    with pytest.raises(ValidationError):
        Criterion(**payload)
