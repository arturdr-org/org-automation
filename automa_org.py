import os
import sys
import time
import requests
from typing import List

ORG_NAME = os.getenv("ORG_NAME", "arturdrr-org")
TOKEN = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("[erro] defina ORG_AUTOMATION_PAT (recomendado) ou GITHUB_TOKEN no ambiente")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

LABELS_DEFAULT = [
    {"name": "bug", "color": "d73a4a", "description": "Bug report"},
    {"name": "enhancement", "color": "a2eeef", "description": "New feature or request"},
    {"name": "automation", "color": "5319e7", "description": "Added by org automation"},
]

ISSUE_TITLE = "Automation checklist"
ISSUE_BODY = (
    "- [ ] Ensure workflows configured\n"
    "- [ ] Labels applied\n"
    "- [ ] Project board linked\n"
    "- [ ] Documentation reviewed\n"
)


def list_repos(org: str) -> List[dict]:
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/orgs/{org}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page, "type": "all"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        time.sleep(0.1)
    return repos


def ensure_label(repo: str, name: str, color: str, description: str = "") -> None:
    # POST will 422 if exists; try PATCH on conflict.
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/labels"
    resp = requests.post(url, headers=HEADERS, json={
        "name": name,
        "color": color,
        "description": description,
    }, timeout=30)
    if resp.status_code in (200, 201):
        print(f"[ok] label '{name}' criada em {repo}")
        return
    if resp.status_code == 422:  # possibly exists -> patch
        patch = requests.patch(
            f"{url}/{name}",
            headers=HEADERS,
            json={"new_name": name, "color": color, "description": description},
            timeout=30,
        )
        if patch.ok:
            print(f"[ok] label '{name}' atualizada em {repo}")
            return
        print(f"[aviso] não foi possível atualizar label '{name}' em {repo}: {patch.status_code} {patch.text}")
        return
    print(f"[aviso] erro criando label '{name}' em {repo}: {resp.status_code} {resp.text}")


def issue_exists(repo: str, title: str) -> bool:
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/issues"
    page = 1
    while True:
        r = requests.get(url, headers=HEADERS, params={"state": "all", "per_page": 100, "page": page}, timeout=30)
        r.raise_for_status()
        items = r.json()
        if not items:
            return False
        if any(i.get("title") == title for i in items):
            return True
        page += 1
        time.sleep(0.1)


def create_issue(repo: str, title: str, body: str) -> None:
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/issues"
    r = requests.post(url, headers=HEADERS, json={"title": title, "body": body, "labels": ["automation"]}, timeout=30)
    if r.status_code in (200, 201):
        print(f"[ok] issue '{title}' criada em {repo}")
    else:
        print(f"[aviso] erro criando issue em {repo}: {r.status_code} {r.text}")


def main():
    print(f"[info] organização: {ORG_NAME}")
    repos = list_repos(ORG_NAME)
    print(f"[info] repositórios encontrados: {len(repos)}")
    for r in repos:
        repo = r["name"]
        print(f"\n[repo] {repo}")
        # labels
        for l in LABELS_DEFAULT:
            ensure_label(repo, l["name"], l["color"], l.get("description", ""))
        # issue checklist
        if not issue_exists(repo, ISSUE_TITLE):
            create_issue(repo, ISSUE_TITLE, ISSUE_BODY)
        else:
            print(f"[ok] issue '{ISSUE_TITLE}' já existe em {repo}")


if __name__ == "__main__":
    main()
