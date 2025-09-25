#!/usr/bin/env python3
"""
Atualiza a seção "About" do repositório no GitHub (descrição e tópicos).

Uso:
  # Defina os envs antes de rodar
  export GITHUB_TOKEN=...   # ou ORG_AUTOMATION_PAT
  export REPO_OWNER=arturdr-org
  export REPO_NAME=org-automation

  python scripts/update_github_about.py \
    --description "Repositório central para desenvolvimento e integração de sistemas DevOps orientados a IA e multi-infraestrutura." \
    --topics "python,workflow,devops,automation,mcp,ci-cd,orchestration,multi-cloud,github-actions,ai-integration"

Observações:
- Requer escopo/repo adequado para PATCH do repositório e PUT de tópicos.
- Não imprime o token.
"""
import os
import sys
import json
import argparse
import requests

API = "https://api.github.com"


def get_token() -> str:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("ORG_AUTOMATION_PAT")
    if not token:
        print("[erro] defina GITHUB_TOKEN ou ORG_AUTOMATION_PAT no ambiente", file=sys.stderr)
        sys.exit(1)
    return token


def get_owner_repo() -> tuple[str, str]:
    owner = os.getenv("REPO_OWNER") or os.getenv("ORG_NAME") or "arturdr-org"
    repo = os.getenv("REPO_NAME") or "org-automation"
    return owner, repo


def update_description(session: requests.Session, owner: str, repo: str, description: str) -> bool:
    url = f"{API}/repos/{owner}/{repo}"
    resp = session.patch(url, json={"description": description})
    if resp.status_code in (200, 201):
        print("[ok] descrição atualizada")
        return True
    print(f"[aviso] falha ao atualizar descrição: {resp.status_code} {resp.text}")
    return False


def update_topics(session: requests.Session, owner: str, repo: str, topics: list[str]) -> bool:
    url = f"{API}/repos/{owner}/{repo}/topics"
    # A API moderna aceita application/vnd.github+json
    resp = session.put(url, headers={"Accept": "application/vnd.github+json"}, json={"names": topics})
    if resp.status_code in (200, 201):
        print("[ok] tópicos atualizados")
        return True
    print(f"[aviso] falha ao atualizar tópicos: {resp.status_code} {resp.text}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Atualiza About (descrição e tópicos) do repositório GitHub")
    parser.add_argument("--description", required=True, help="Descrição para About")
    parser.add_argument("--topics", required=True, help="Lista de tópicos separados por vírgula")
    args = parser.parse_args()

    token = get_token()
    owner, repo = get_owner_repo()

    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "org-automation-about-updater"
    })

    topics = [t.strip() for t in args.topics.split(",") if t.strip()]

    ok_desc = update_description(session, owner, repo, args.description)
    ok_topics = update_topics(session, owner, repo, topics)

    return 0 if (ok_desc and ok_topics) else 1


if __name__ == "__main__":
    raise SystemExit(main())
