"""Exercise provisioned Grafana queries through its real datasource API."""
import json
import time
from urllib.request import Request, urlopen

from scripts.project import ROOT

URL = "http://127.0.0.1:3000"


def api(path, body=None):
    request = Request(URL + path, data=json.dumps(body).encode() if body else None,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def run_query(query, start, end, bucket):
    query = dict(query)
    query["rawSql"] = query["rawSql"].replace("${bucket}", bucket)
    result = api("/api/ds/query", {"queries": [query], "from": start, "to": end})
    response = result["results"]["A"]
    if response.get("error"):
        raise RuntimeError(response["error"])
    frames = response.get("frames", [])
    return sum(len(frame["data"]["values"][0]) if frame["data"]["values"] else 0 for frame in frames)


def main():
    for attempt in range(30):
        try:
            api("/api/health")
            break
        except (OSError, ConnectionError):
            if attempt == 29:
                raise
            time.sleep(1)
    dashboard = api("/api/dashboards/uid/switch-squad-hpc")
    assert dashboard["meta"]["provisioned"]
    checks = []
    for bucket in ("1 hour", "1 day", "1 week"):
        for item in dashboard["dashboard"]["panels"]:
            if item.get("targets"):
                rows = run_query(item["targets"][0], "1485073500000", "1759504200000", bucket)
                assert rows > 0, item["title"]
                checks.append({"panel": item["title"], "bucket": bucket, "returned_rows": rows})
    # Empty date ranges are valid and must not return historical samples.
    count_query = next(p["targets"][0] for p in dashboard["dashboard"]["panels"] if p["title"] == "Accepted snapshots in range")
    request_query = dict(count_query)
    full = api("/api/ds/query", {"queries": [request_query], "from": "1485073500000", "to": "1759504200000"})
    assert full["results"]["A"]["frames"][0]["data"]["values"][0][0] == 903522
    response = api("/api/ds/query", {"queries": [request_query], "from": "1893456000000", "to": "1893542400000"})
    assert response["results"]["A"]["frames"][0]["data"]["values"][0][0] == 0
    output = {"health": api("/api/health"), "provisioned": True, "panel_query_checks": checks, "full_range_count": 903522, "empty_range_count": 0}
    path = ROOT / "docs/evidence/dashboard-api.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Passed {len(checks)} panel queries and empty-range check; {path}")


if __name__ == "__main__":
    main()
