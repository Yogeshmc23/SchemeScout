from app.eligibility import match
from app.models import Criterion


def test_optional_failure_does_not_disqualify(profile, scholarship):
    scholarship.rules.category = Criterion(status='RESTRICTED', values=['Other'], evidence='Other preferred', mandatory=False)
    result = match(profile, scholarship)
    assert result.status == 'ELIGIBLE'
    check = next(c for c in result.checks if c.field == 'category')
    assert check.outcome == 'FAIL'
    assert check.mandatory is False
    assert check.student_value == profile.category
    assert check.requirement == scholarship.rules.category


def test_optional_unknown_does_not_block(profile, scholarship):
    scholarship.rules.category = Criterion(mandatory=False)
    assert match(profile, scholarship).status == 'ELIGIBLE'


def test_failed_mandatory_beats_unknown(profile, scholarship):
    scholarship.rules.category = Criterion()
    scholarship.rules.state = Criterion(status='RESTRICTED', values=['Other'], evidence='Only Other students')
    assert match(profile, scholarship).status == 'NOT_ELIGIBLE'
