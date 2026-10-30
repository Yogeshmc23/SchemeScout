"""Real HTTP smoke checks through the Next.js proxy. Run both servers first."""
import json
import os
import urllib.error
import urllib.request

BASE = os.getenv("SCHEMERADAR_SMOKE_URL", "http://127.0.0.1:3000")


def request(path, body=None):
    req = urllib.request.Request(BASE + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        response = exc
    return response.status, response.read().decode()


for path in ("/", "/profile", "/discover", "/eligibility", "/research", "/assistant", "/about"):
    status, body = request(path)
    assert status == 200 and "SchemeRadar" in body, (path, status)
    print(f"PASS page {path}")
status, body = request("/api/health")
assert status == 200 and json.loads(body)["status"] == "ok"
print("PASS Next.js → FastAPI health proxy")
status, body = request("/api/profile", {
    "state": "Karnataka", "course": "B.Tech", "education_level": "Undergraduate",
    "study_year": 2, "annual_income": 250000, "category": "OBC",
})
assert status == 200 and json.loads(body)["state"] == "Karnataka"
print("PASS actual profile submission through frontend proxy")
status, body = request("/api/profile", {"annual_income": -1})
assert status == 422
print("PASS invalid profile rejection through frontend proxy")
status, body = request("/api/scholarships")
assert status in {200, 503}
print(f"Database listing HTTP {status}: {'available' if status == 200 else 'blocked by missing/unavailable database'}")

status, body = request("/api/openapi.json")
assert status == 200
schema = json.loads(body)
assert "/api/eligibility" in schema["paths"]
print("PASS actual OpenAPI includes stored eligibility endpoint")
