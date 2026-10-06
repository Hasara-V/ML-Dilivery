import json
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:5000"
READY_ATTEMPTS = 20
REQUEST_TIMEOUT = 3


def request_json(url, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if data is None else {"Content-Type": "application/json"}
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def wait_until_ready(base_url):
    last_error = None
    for attempt in range(READY_ATTEMPTS):
        try:
            status, body = request_json(f"{base_url}/")
            if (
                status == 200
                and isinstance(body, dict)
                and body.get("service") == "iris-prediction"
            ):
                return body
            last_error = RuntimeError(
                f"GET / returned status {status} or an unexpected service identity"
            )
        except (OSError, ValueError, urllib.error.URLError) as error:
            last_error = error
        if attempt + 1 < READY_ATTEMPTS:
            time.sleep(1)
    raise RuntimeError(f"Service was not ready after {READY_ATTEMPTS} attempts: {last_error}")


def main():
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} [base-url]", file=sys.stderr)
        return 2

    base_url = (sys.argv[1] if len(sys.argv) == 2 else DEFAULT_BASE_URL).rstrip("/")
    try:
        wait_until_ready(base_url)

        status, body = request_json(
            f"{base_url}/predict",
            {"measurements": [5.1, 3.5, 1.4, 0.2]},
        )
        if (
            status != 200
            or not isinstance(body, dict)
            or body.get("prediction") != "setosa"
        ):
            raise RuntimeError(
                f"Valid prediction check failed: HTTP {status}, response {body!r}"
            )

        status, body = request_json(
            f"{base_url}/predict",
            {"measurements": [5.1, 3.5]},
        )
        if (
            status != 400
            or not isinstance(body, dict)
            or not isinstance(body.get("error"), str)
            or not body["error"]
        ):
            raise RuntimeError(
                f"Invalid-payload check failed: HTTP {status}, response {body!r}"
            )
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as error:
        print(f"Smoke check failed: {error}", file=sys.stderr)
        return 1

    print("Smoke checks passed: service identity, valid prediction, and invalid-payload rejection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
