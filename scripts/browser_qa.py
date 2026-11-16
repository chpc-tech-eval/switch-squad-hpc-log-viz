"""Check the real Grafana UI and capture evidence with an installed Chrome."""
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from scripts.project import ROOT


def main():
    output = ROOT / "submission/assets"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.getenv("BROWSER_CHANNEL", "chrome"), headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        failures = []
        query_responses = []
        page.on("pageerror", lambda error: failures.append(str(error)))
        page.on("response", lambda response: query_responses.append(response.status) if "/api/ds/query" in response.url else None)
        page.goto("http://127.0.0.1:3000/d/switch-squad-hpc?orgId=1&kiosk", wait_until="networkidle")
        page.get_by_text("Accepted snapshots in range", exact=True).wait_for()
        page.wait_for_timeout(3000)
        page.screenshot(path=str(output / "dashboard-overview.png"))
        page.get_by_role("combobox").first.click()
        page.get_by_role("option", name="1 hour", exact=True).click()
        page.wait_for_timeout(2000)
        assert "var-bucket=1" in page.url, "Bucket selection did not update dashboard state"
        (ROOT / "artifacts").mkdir(exist_ok=True)
        (ROOT / "artifacts/dashboard-body.txt").write_text(page.locator("body").inner_text(), encoding="utf-8")
        page.get_by_text("Running-node percentage", exact=True).scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        page.screenshot(path=str(output / "dashboard-trends.png"))
        # Absolute source-date filter and finer aggregation through Grafana's own URL state.
        page.goto("http://127.0.0.1:3000/d/switch-squad-hpc?orgId=1&from=1750896000000&to=1750982400000&var-bucket=1%20hour&kiosk", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(output / "dashboard-filtered.png"))
        text = page.locator("body").inner_text()
        assert "1 hour" in text, "Bucket URL state was not reflected in the UI"
        assert "No data" not in text, "Expected data in known historical range"
        assert not any(status >= 400 for status in query_responses), query_responses
        assert not failures, failures
        evidence = {"browser": browser.version, "overview_loaded": True,
                    "absolute_date_filter_loaded": True, "hour_bucket_loaded": True,
                    "bucket_dropdown_clicked": True,
                    "query_http_statuses": query_responses, "page_errors": failures,
                    "screenshots": ["dashboard-overview.png", "dashboard-trends.png", "dashboard-filtered.png"]}
        (ROOT / "docs/evidence/browser-qa.json").write_text(json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(evidence, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
