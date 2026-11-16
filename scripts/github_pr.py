"""Open/update an authorised PR using Git's credential helper, without printing secrets."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError

REPO = "chpc-tech-eval/switch-squad-hpc-log-viz"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", type=Path, required=True)
    args = parser.parse_args()
    result = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", text=True, capture_output=True, check=True)
    credential = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    auth = base64.b64encode((credential["username"] + ":" + credential["password"]).encode()).decode()

    def api(path, method="GET", data=None):
        request = Request("https://api.github.com/repos/" + REPO + path,
                          data=json.dumps(data).encode() if data is not None else None,
                          headers={"Authorization": "Basic " + auth, "Accept": "application/vnd.github+json", "User-Agent": "switch-squad-project"}, method=method)
        try:
            with urlopen(request) as response:
                return json.load(response)
        except HTTPError as error:
            raise SystemExit(f"GitHub API returned HTTP {error.code}; no credentials printed") from None

    existing = api("/pulls?state=open&per_page=100")
    body = args.body_file.read_text(encoding="utf-8")
    match = next((pr for pr in existing if pr["head"]["ref"] == args.head), None)
    data = {"title": args.title, "body": body, "base": args.base}
    if match:
        pr = api(f'/pulls/{match["number"]}', "PATCH", data)
    else:
        pr = api("/pulls", "POST", {**data, "head": args.head})
    print(pr["html_url"])


if __name__ == "__main__":
    main()
