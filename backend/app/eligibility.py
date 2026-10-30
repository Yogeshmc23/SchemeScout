import re
from datetime import date

from .models import Check, Match, Profile, Scholarship, Status


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


def match(profile: Profile, scholarship: Scholarship) -> Match:
    checks = []
    for field in type(scholarship.rules).model_fields:
        rule = getattr(scholarship.rules, field)
        value = getattr(profile, field)
        outcome, reason = "UNKNOWN", "The source does not specify this requirement."
        if rule.status == "ANY":
            outcome, reason = "PASS", "Source explicitly states no restriction on this criterion."
        elif rule.status == "RESTRICTED":
            if value is None:
                reason = "Student information is missing."
            elif isinstance(value, int):
                lower_pass = rule.minimum is None or (
                    value > rule.minimum if rule.minimum_exclusive else value >= rule.minimum
                )
                upper_pass = rule.maximum is None or (
                    value < rule.maximum if rule.maximum_exclusive else value <= rule.maximum
                )
                passed = lower_pass and upper_pass
                outcome = "PASS" if passed else "FAIL"
                lower = ">" if rule.minimum_exclusive else ">="
                upper = "<" if rule.maximum_exclusive else "<="
                bounds = []
                if rule.minimum is not None:
                    bounds.append(f"{lower} {rule.minimum}")
                if rule.maximum is not None:
                    bounds.append(f"{upper} {rule.maximum}")
                reason = f"Student value {value}; required {' and '.join(bounds)}."
            else:
                passed = normalized(value) in {normalized(v) for v in rule.values}
                outcome = "PASS" if passed else "FAIL"
                reason = f"Student value '{value}'; explicit allowed values: {', '.join(rule.values)}."
        checks.append(Check(field=field, outcome=outcome, reason=reason, evidence=rule.evidence))
    if not scholarship.official_source:
        checks.append(Check(field="source", outcome="UNKNOWN", reason="Not verified against an approved official source."))
    if not scholarship.eligibility_complete:
        checks.append(Check(field="coverage", outcome="UNKNOWN", reason="The full set of mandatory requirements is not confirmed."))
    if scholarship.deadline and scholarship.deadline < date.today():
        checks.append(Check(field="deadline", outcome="FAIL", reason="The recorded application deadline has passed."))
    status = Status.NEEDS_INFORMATION
    if any(c.outcome == "FAIL" for c in checks):
        status = Status.NOT_ELIGIBLE
    elif all(c.outcome == "PASS" for c in checks):
        status = Status.ELIGIBLE
    return Match(scholarship=scholarship, status=status, checks=checks)
