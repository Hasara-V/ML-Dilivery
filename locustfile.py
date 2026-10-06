import os

from locust import HttpUser, between, events, task


P95_LIMIT_MS = float(os.getenv("P95_LIMIT_MS", "1000"))


class IrisUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def predict_setosa(self):
        with self.client.post(
            "/predict",
            json={"measurements": [5.1, 3.5, 1.4, 0.2]},
            timeout=5,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected HTTP 200, got {response.status_code}")
                return
            try:
                body = response.json()
            except ValueError:
                response.failure("Response was not valid JSON")
                return
            if not isinstance(body, dict) or body.get("prediction") != "setosa":
                response.failure(f"Expected setosa prediction, got {body!r}")

    @task(1)
    def check_home(self):
        with self.client.get(
            "/",
            timeout=5,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected HTTP 200, got {response.status_code}")
                return
            try:
                body = response.json()
            except ValueError:
                response.failure("Response was not valid JSON")
                return
            if not isinstance(body, dict) or body.get("service") != "iris-prediction":
                response.failure(f"Unexpected service response: {body!r}")


@events.quitting.add_listener
def enforce_load_gate(environment):
    stats = environment.stats.total
    request_count = stats.num_requests
    failure_ratio = stats.fail_ratio
    p95_ms = stats.get_response_time_percentile(0.95) if request_count else None

    failures = []
    if request_count < 20:
        failures.append(f"only {request_count} requests were recorded (minimum 20)")
    if failure_ratio > 0.01:
        failures.append(f"failure ratio {failure_ratio:.4f} exceeds 0.01")
    if p95_ms is None or p95_ms > P95_LIMIT_MS:
        failures.append(
            f"aggregate p95 {p95_ms!r} ms exceeds or is missing "
            f"(limit {P95_LIMIT_MS:g} ms)"
        )

    if failures:
        environment.process_exit_code = 1
        print("Load gate failed: " + "; ".join(failures))
    else:
        environment.process_exit_code = 0
        print(
            f"Load gate passed: {request_count} requests, "
            f"{failure_ratio:.4f} failure ratio, p95 {p95_ms:.1f} ms."
        )
