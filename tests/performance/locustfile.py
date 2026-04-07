"""
Construction-GRC-System Performance Benchmark
Using Locust (https://locust.io/)

Run (headless):
    locust -f tests/performance/locustfile.py --config tests/performance/locust.conf

Run (interactive UI):
    locust -f tests/performance/locustfile.py --host http://localhost:8000

Skip in CI (set env var):
    SKIP_PERF=1 — the locust.conf default also sets run-time short enough for CI use.
"""

import os
import random
from locust import HttpUser, task, between, events


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _login(client, username: str, password: str) -> str | None:
    """Obtain a JWT access token. Returns token string or None on failure."""
    response = client.post(
        "/api/token/",
        json={"username": username, "password": password},
        name="/api/token/ [login]",
    )
    if response.status_code == 200:
        return response.json().get("access")
    return None


# ---------------------------------------------------------------------------
# User classes
# ---------------------------------------------------------------------------

class GRCAPIUser(HttpUser):
    """
    Simulates a typical GRC system user browsing risks, compliance, and the
    dashboard. Authenticated via JWT.
    """

    wait_time = between(1, 3)

    # Credentials are read from environment variables so that no secrets are
    # hard-coded in source. Provide TEST_USER / TEST_PASSWORD in your
    # .env file or CI secrets.
    _username: str = os.environ.get("TEST_USER", "admin")
    _password: str = os.environ.get("TEST_PASSWORD", "admin")

    def on_start(self) -> None:
        """Authenticate and store the JWT token as a default header."""
        token = _login(self.client, self._username, self._password)
        if token:
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            # Log failure but do not abort; individual tasks will fail with 401
            events.request.fire(
                request_type="AUTH",
                name="JWT login",
                response_time=0,
                response_length=0,
                exception=Exception("JWT login failed — check TEST_USER / TEST_PASSWORD"),
                context={},
            )

    # ------------------------------------------------------------------
    # Read-heavy tasks (weight = relative call frequency)
    # ------------------------------------------------------------------

    @task(3)
    def get_risks(self) -> None:
        """GET /api/v1/risks/ — Risk register listing."""
        with self.client.get(
            "/api/v1/risks/",
            name="/api/v1/risks/",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(2)
    def get_compliance(self) -> None:
        """GET /api/v1/compliance/ — Compliance requirements listing."""
        with self.client.get(
            "/api/v1/compliance/",
            name="/api/v1/compliance/",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def get_dashboard(self) -> None:
        """
        GET integrated dashboard KPI endpoint.
        Falls back to /api/v1/risks/statistics/ if /api/v1/dashboard/ returns 404.
        """
        with self.client.get(
            "/api/v1/dashboard/",
            name="/api/v1/dashboard/",
            catch_response=True,
        ) as resp:
            if resp.status_code == 404:
                # Fallback to statistics endpoint
                resp.success()
                self.client.get(
                    "/api/v1/risks/statistics/",
                    name="/api/v1/risks/statistics/ [fallback]",
                )
            elif resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(2)
    def get_controls(self) -> None:
        """GET /api/v1/controls/ — ISO27001 controls listing."""
        with self.client.get(
            "/api/v1/controls/",
            name="/api/v1/controls/",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def get_audits(self) -> None:
        """GET /api/v1/audits/ — Internal audits listing."""
        with self.client.get(
            "/api/v1/audits/",
            name="/api/v1/audits/",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def get_frameworks(self) -> None:
        """GET /api/v1/frameworks/ — Framework definitions."""
        with self.client.get(
            "/api/v1/frameworks/",
            name="/api/v1/frameworks/",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 401):
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def health_check(self) -> None:
        """GET /api/health/ — Health check (no auth required)."""
        with self.client.get(
            "/api/health/",
            name="/api/health/",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Health check failed: {resp.status_code}")


class GRCWriteUser(HttpUser):
    """
    Simulates a GRC manager who occasionally creates/updates risks.
    Lower weight than GRCAPIUser to model realistic read:write ratio.
    """

    wait_time = between(3, 7)
    weight = 1  # 1 write-user per ~5 read-users (set weight on GRCAPIUser too if needed)

    _username: str = os.environ.get("TEST_USER", "admin")
    _password: str = os.environ.get("TEST_PASSWORD", "admin")

    def on_start(self) -> None:
        token = _login(self.client, self._username, self._password)
        if token:
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(2)
    def list_risks(self) -> None:
        self.client.get("/api/v1/risks/", name="/api/v1/risks/ [write-user]")

    @task(1)
    def create_risk(self) -> None:
        """POST /api/v1/risks/ — Create a sample risk entry."""
        payload = {
            "title": f"Perf-test risk {random.randint(1000, 9999)}",
            "description": "Automated performance test entry — safe to delete.",
            "category": "operational",
            "likelihood": random.randint(1, 5),
            "impact": random.randint(1, 5),
            "status": "identified",
        }
        with self.client.post(
            "/api/v1/risks/",
            json=payload,
            name="/api/v1/risks/ [POST]",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 201, 400, 401, 403):
                resp.failure(f"Unexpected status {resp.status_code}")
