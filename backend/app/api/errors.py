"""Consistent safe errors; the legacy detail key remains backward compatible."""
from fastapi import Request
from fastapi.responses import JSONResponse

from ..models import Model


class ErrorInfo(Model):
    code: str
    message: str
    request_id: str


class ErrorResponse(Model):
    detail: str | list[dict]
    error: ErrorInfo


def error_response(request: Request, status: int, detail: str | list[dict]):
    identifier = getattr(request.state, "request_id", "unavailable")
    code = {404: "NOT_FOUND", 413: "BODY_TOO_LARGE", 422: "VALIDATION_ERROR", 429: "CAPACITY_EXCEEDED",
            502: "PROVIDER_ERROR", 503: "SERVICE_UNAVAILABLE", 504: "TIMEOUT"}.get(status, "INTERNAL_ERROR")
    payload = ErrorResponse(detail=detail, error=ErrorInfo(code=code,
                            message=detail if isinstance(detail, str) else "Request validation failed.",
                            request_id=identifier))
    return JSONResponse(status_code=status, content=payload.model_dump(), headers={"X-Request-ID": identifier})
