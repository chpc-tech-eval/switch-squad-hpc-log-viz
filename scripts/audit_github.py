"""Read public requirements and discussion/PR evidence without exposing credentials."""
import base64
import json
import re
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from scripts.project import ROOT

REPO = "chpc-tech-eval/switch-squad-hpc-log-viz"


def clean_public_evidence(value):
    """Omit quoted notification mail and redact notification tokens in public posts."""
    if isinstance(value, dict):
        return {key: clean_public_evidence(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_public_evidence(item) for item in value]
    if isinstance(value, str):
        value = re.split(r"\nOn (?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),", value, maxsplit=1)[0]
        value = re.sub(r"email_token=[^&\s<>\"#]+", "email_token=[redacted]", value)
        return re.sub(r"(github\.com/notifications/(?:unsubscribe-auth|mobile/(?:ios|android))/)[A-Za-z0-9]+", r"\1[redacted]", value)
    return value


def main():
    result = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", text=True, capture_output=True, check=True)
    credential = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    auth = base64.b64encode((credential["username"] + ":" + credential["password"]).encode()).decode()

    def request(url, data=None):
        req = Request(url, data=json.dumps(data).encode() if data else None,
                      headers={"Authorization": "Basic " + auth, "User-Agent": "switch-squad-audit", "Accept": "application/vnd.github+json"})
        for attempt in range(3):
            try:
                with urlopen(req, timeout=30) as response:
                    return json.load(response)
            except (OSError, ConnectionError):
                if attempt == 2:
                    raise
                time.sleep(1)

    base = "https://api.github.com/repos/" + REPO
    issues = request(base + "/issues?state=all&per_page=100")
    original = [issue for issue in issues if issue["number"] <= 27]
    entries = []
    for issue in original:
        entry = {key: issue[key] for key in ("number", "title", "state", "body", "html_url")}
        if issue["comments"]:
            entry["comments"] = [{"body": item["body"], "url": item["html_url"]} for item in request(issue["comments_url"] + "?per_page=100")]
        if "pull_request" in issue:
            number = issue["number"]
            entry["reviews"] = [{"state": review["state"], "body": review["body"]} for review in request(base + f"/pulls/{number}/reviews?per_page=100")]
            entry["inline_comments"] = [{"path": comment["path"], "body": comment["body"]} for comment in request(base + f"/pulls/{number}/comments?per_page=100")]
        entries.append(entry)
    query = '{repository(owner:"chpc-tech-eval",name:"switch-squad-hpc-log-viz"){hasDiscussionsEnabled discussions(first:20){nodes{title body url comments(first:50){nodes{body url replies(first:50){nodes{body url} pageInfo{hasNextPage}}} pageInfo{hasNextPage}}} pageInfo{hasNextPage}}}}'
    try:
        discussions = request("https://api.github.com/graphql", {"query": query})
    except HTTPError as error:
        discussions = {"access_error_http_status": error.code}
    runs = request(base + "/actions/runs?per_page=20")["workflow_runs"]
    output = {"reviewed_on": "2026-11-16", "original_entries": entries, "discussions": discussions,
              "recent_ci": [{key: run[key] for key in ("id", "head_sha", "head_branch", "status", "conclusion", "html_url")} for run in runs]}
    path = ROOT / "docs/evidence/github-audit.json"
    output = clean_public_evidence(output)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Read {len(entries)} original issue/PR entries, including reviews and inline comments.")
    print("Discussion audit saved; quoted notification mail omitted from evidence.")


if __name__ == "__main__":
    main()
