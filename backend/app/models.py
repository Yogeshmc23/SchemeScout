from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Profile(Model):
    state: str | None = Field(None, min_length=2, max_length=80)
    course: str | None = Field(None, min_length=2, max_length=120)
    education_level: str | None = Field(None, min_length=2, max_length=80)
    study_year: int | None = Field(None, ge=1, le=12, strict=True)
    annual_income: int | None = Field(None, ge=0, le=1_000_000_000, strict=True)
    category: str | None = Field(None, min_length=2, max_length=80)


class Criterion(Model):
    mandatory: bool = True
    status: Literal["UNKNOWN", "ANY", "RESTRICTED"] = "UNKNOWN"
    values: list[str] = Field(default_factory=list, max_length=50)
    minimum: int | None = Field(None, ge=0, strict=True)
    maximum: int | None = Field(None, ge=0, strict=True)
    minimum_exclusive: bool = False
    maximum_exclusive: bool = False
    evidence: str | None = Field(None, min_length=5, max_length=3000)

    @model_validator(mode="after")
    def valid_rule(self):
        if self.status != "UNKNOWN" and not self.evidence:
            raise ValueError("Known rules require a verbatim source quotation")
        if self.status == "RESTRICTED" and not self.values and self.minimum is None and self.maximum is None:
            raise ValueError("Restricted rules need values or bounds")
        if self.status != "RESTRICTED" and (self.values or self.minimum is not None or self.maximum is not None):
            raise ValueError("Only restricted rules may specify constraints")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("Minimum exceeds maximum")
        if self.minimum_exclusive and self.minimum is None:
            raise ValueError("Exclusive minimum requires a minimum")
        if self.maximum_exclusive and self.maximum is None:
            raise ValueError("Exclusive maximum requires a maximum")
        if self.minimum == self.maximum and self.minimum is not None and (
            self.minimum_exclusive or self.maximum_exclusive
        ):
            raise ValueError("Exclusive equal bounds define an empty interval")
        if any(not value.strip() or len(value) > 160 for value in self.values):
            raise ValueError("Rule values must be nonempty and at most 160 characters")
        return self


class Rules(Model):
    state: Criterion = Field(default_factory=Criterion)
    course: Criterion = Field(default_factory=Criterion)
    education_level: Criterion = Field(default_factory=Criterion)
    study_year: Criterion = Field(default_factory=Criterion)
    annual_income: Criterion = Field(default_factory=Criterion)
    category: Criterion = Field(default_factory=Criterion)

    @model_validator(mode="after")
    def rule_types(self):
        for field in type(self).model_fields:
            rule = getattr(self, field)
            if field in ("study_year", "annual_income"):
                if rule.values:
                    raise ValueError("Numeric criteria use bounds, not text values")
            elif rule.minimum is not None or rule.maximum is not None:
                raise ValueError("Text criteria use exact values, not bounds")
        return self


class Scholarship(Model):
    id: int | None = Field(None, gt=0)
    updated_at: datetime | None = None
    name: str = Field(min_length=3, max_length=250)
    description: str | None = Field(None, max_length=4000)
    benefits: str | None = Field(None, max_length=2000)
    deadline: date | None = None
    application_url: HttpUrl | None = None
    source_url: HttpUrl
    required_documents: list[str] = Field(default_factory=list, max_length=40)
    missing_information: list[str] = Field(default_factory=list, max_length=40)
    fact_evidence: dict[str, str] = Field(default_factory=dict, max_length=12)
    rules: Rules = Field(default_factory=Rules)
    eligibility_complete: bool = False
    # True only when the source explicitly lists the complete eligibility criteria.
    completeness_evidence: str | None = Field(None, max_length=3000)
    extraction_status: Literal["PARTIAL", "EXTRACTED"] = "PARTIAL"
    official_source: bool = False
    last_verified_at: datetime | None = None
    fetched_at: datetime | None = None
    source_evidence: str = Field(default="", max_length=40000)


class Source(Model):
    title: str = Field(max_length=1000)
    url: HttpUrl
    snippet: str = Field(default="", max_length=6000)
    official: bool = False


class Page(Model):
    url: HttpUrl
    content: str = Field(min_length=1, max_length=40000)
    links: list[HttpUrl] = Field(default_factory=list, max_length=30)
    truncated: bool = False
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Status(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    NEEDS_INFORMATION = "NEEDS_INFORMATION"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class Check(Model):
    field: str
    outcome: Literal["PASS", "FAIL", "UNKNOWN"]
    reason: str
    evidence: str | None = None
    mandatory: bool = True
    student_value: str | int | None = None
    requirement: Criterion | None = None


class Match(Model):
    scholarship: Scholarship
    status: Status
    checks: list[Check]


class Query(Model):
    query: str = Field(min_length=3, max_length=500)


class FetchRequest(Model):
    urls: list[HttpUrl] = Field(min_length=1, max_length=3)


class ExtractRequest(Model):
    url: HttpUrl


class FetchResult(Model):
    pages: list[Page]
    errors: list[str]


class MatchRequest(Model):
    profile: Profile
    scholarships: list[Scholarship] = Field(max_length=30)


class AgentRequest(Query):
    mode: Literal["CHAT", "RESEARCH", "DISCOVER"]
    profile: Profile | None = None

    @model_validator(mode="after")
    def profile_required(self):
        if self.mode == "DISCOVER" and self.profile is None:
            raise ValueError("DISCOVER requires a student profile")
        return self


class SourceOutcome(Model):
    url: HttpUrl
    stage: Literal["FETCH", "EXTRACT", "DETAIL_FETCH", "DETAIL_EXTRACT"]
    status: Literal["SUCCESS", "FAILED"]
    message: str


class StageExecution(Model):
    stage: str
    status: Literal["SUCCESS", "FAILED"]
    duration_ms: int = Field(ge=0)


class AgentResult(Model):
    mode: str
    query: str = ""
    source_outcomes: list[SourceOutcome] = Field(default_factory=list)
    summary: str = ""
    sources: list[Source] = Field(default_factory=list)
    scholarships: list[Scholarship] = Field(default_factory=list)
    matches: list[Match] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    stored_count: int = 0
    research_id: str | None = None
    workflow_id: str | None = None
    execution: list[StageExecution] = Field(default_factory=list)


class ExtractionSnapshot(Model):
    id: int
    recorded_at: datetime
    scholarship: Scholarship


class ResearchRun(Model):
    id: str
    query: str
    created_at: datetime
    scholarship_count: int
