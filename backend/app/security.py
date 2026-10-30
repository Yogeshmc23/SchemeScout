import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

# Exact-host policy, reviewed in docs/source-policy.md. No substring or suffix trust.
OFFICIAL_HOSTS = frozenset({
    "scholarships.gov.in", "scholarship.gov.in", "ssp.karnataka.gov.in",
    "ssp.postmatric.karnataka.gov.in", "www.aicte-india.org", "aicte-india.org",
    "socialjustice.gov.in", "tribal.nic.in", "minorityaffairs.gov.in",
})


class ServiceError(Exception):
    def __init__(self, message: str, code: int = 503):
        self.message = message
        self.code = code
        super().__init__(message)


def safe_url(url: str, official_only: bool = False) -> str:
    try:
        parts = urlsplit(str(url))
        host = (parts.hostname or "").lower()
        if parts.scheme not in {"http", "https"} or not host or parts.username or parts.password:
            raise ValueError()
        if parts.port not in {None, 80, 443} or len(str(url)) > 2048:
            raise ValueError()
        if any(c.isspace() or ord(c) < 32 or c == "\\" for c in str(url)):
            raise ValueError()
        if host == "localhost" or host.endswith((".local", ".internal", ".localhost")):
            raise ValueError()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if host.replace(".", "").isdigit() or ":" in host or "." not in host:
                raise ValueError() from None
        else:
            # Even public IP literals are excluded: scholarship sources must be named domains.
            raise ValueError()
        if official_only and host not in OFFICIAL_HOSTS:
            raise ValueError()
        return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path or "/", parts.query, ""))
    except (ValueError, TypeError):
        raise ServiceError("URL rejected by the public official-source policy.", 422) from None


def is_official(url: str) -> bool:
    try:
        safe_url(url, official_only=True)
        return True
    except ServiceError:
        return False


async def public_official_url(url: str) -> str:
    canonical = safe_url(url, official_only=True)
    host = urlsplit(canonical).hostname
    try:
        addresses = await asyncio.wait_for(
            asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM), timeout=5
        )
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise ServiceError("Source resolves to a non-public address.", 422)
    except (OSError, TimeoutError):
        raise ServiceError("Source hostname could not be safely resolved.", 422) from None
    return canonical
