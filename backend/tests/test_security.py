import socket
from unittest.mock import AsyncMock

import pytest

from app.security import ServiceError, is_official, public_official_url, safe_url


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "ftp://scholarships.gov.in/a", "http://localhost/", "http://127.0.0.1/",
    "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "http://2130706433/",
    "https://user:password@scholarships.gov.in/", "https://scholarships.gov.in:8443/",
    "https://scholarships.gov.in.evil.com/", "https://evil.com/?scholarships.gov.in",
    "https://fake-scholarships.gov.in/", "https://scholarships.gov.in\\@evil.com/",
])
def test_url_policy_rejects(url):
    with pytest.raises(ServiceError):
        safe_url(url, official_only=True)


def test_exact_official_host():
    assert is_official("https://scholarships.gov.in/test")
    assert not is_official("https://scholarships.gov.in.attacker.org/")
    assert safe_url("https://scholarships.gov.in/test#frag") == "https://scholarships.gov.in/test"


async def test_private_dns_rejected(monkeypatch):
    monkeypatch.setattr("asyncio.base_events.BaseEventLoop.getaddrinfo", AsyncMock(return_value=[
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))
    ]))
    with pytest.raises(ServiceError):
        await public_official_url("https://scholarships.gov.in/")
