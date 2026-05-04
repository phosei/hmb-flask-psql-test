"""Push local file changes to GitHub via API (no git binary needed)."""
import base64
import json
import os
import sys
import urllib.request

REPO = "phosei/hmb-flask-psql-test"
BRANCH = "main"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

if not TOKEN:
    print("ERROR: GITHUB_TOKEN env var not set")
    sys.exit(1)

BASE = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "push.py",
    "X-GitHub-Api-Version": "2022-11-28",
}

FILES = [
    "Dockerfile",
    "app.py",
    "k8s/01-deployment.yaml",
    "k8s/02-service.yaml",
    "k8s/03-ingress.yaml",
    "k8s/04-postgresql.yaml",
]


def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {method} {url}: {e.read().decode()}")
        sys.exit(1)


def get_sha(path):
    try:
        data = api("GET", f"/contents/{path}?ref={BRANCH}")
        return data["sha"]
    except SystemExit:
        return None


for rel_path in FILES:
    local_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    existing_sha = get_sha(rel_path)
    body = {
        "message": f"deploy: add/update {rel_path}",
        "content": content,
        "branch": BRANCH,
    }
    if existing_sha:
        body["sha"] = existing_sha

    api("PUT", f"/contents/{rel_path}", body)
    action = "updated" if existing_sha else "created"
    print(f"  {action}: {rel_path}")

print("\nDone — alle Dateien gepusht.")
