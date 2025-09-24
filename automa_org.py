import os
import sys
import time
import base64
import requests
from typing import List, Optional

# Configurações
ORG_NAME = os.getenv("ORG_NAME", "arturdrr-org")
PROJECT_NUMBER = int(os.getenv("PROJECT_NUMBER", "1"))  # Project v2 da organização
TOKEN = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("[erro] defina ORG_AUTOMATION_PAT (recomendado) ou GITHUB_TOKEN no ambiente")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Labels padrão + personalizadas
LABELS_DEFAULT = [
    {"name": "bug", "color": "d73a4a", "description": "Bug report"},
    {"name": "enhancement", "color": "a2eeef", "description": "New feature or request"},
    {"name": "automation", "color": "5319e7", "description": "Added by org automation"},
    # Custom da org (exemplos):
    {"name": "priority:high", "color": "b60205", "description": "Alta prioridade"},
    {"name": "area:raw", "color": "0e8a16", "description": "Fluxo RAW"},
    {"name": "area:gimp", "color": "1d76db", "description": "GIMP"},
    {"name": "area:metadata", "color": "5319e7", "description": "Metadados/Exif"},
]

# Issue padrão
ISSUE_TITLE = "Automation checklist"
ISSUE_BODY = (
    "- [ ] Ensure workflows configured\n"
    "- [ ] Labels applied\n"
    "- [ ] Project board linked\n"
    "- [ ] Documentation reviewed\n"
)

# Templates padrão
ISSUE_TEMPLATE_PATH = ".github/ISSUE_TEMPLATE/automation-checklist.md"
ISSUE_TEMPLATE_CONTENT = """---
name: Checklist de automação
about: Verificar se o repositório segue os padrões da organização
labels: [automation]
---

## Automação

- [ ] GitHub Actions configurado
- [ ] Labels criadas e usadas
- [ ] Project (v2) vinculado
- [ ] Documentação atualizada
"""

PR_TEMPLATE_PATH = ".github/PULL_REQUEST_TEMPLATE.md"
PR_TEMPLATE_CONTENT = """## Descrição

Descreva o que foi alterado e o porquê.

## Checklist
- [ ] Testes/validação local
- [ ] Atualização de docs/README (se necessário)
- [ ] Labels aplicadas
- [ ] Issue vinculada ao Project (se aplicável)
"""

WORKFLOW_PATH = ".github/workflows/ci-basic.yml"
WORKFLOW_CONTENT = """name: CI Basic Workflow
on: [push, pull_request]

jobs:
  lint-yaml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint YAML files
        uses: ibiqlik/action-yamllint@v1
        with:
          files: '**/*.yml'
"""


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
    # POST retornará 422 se já existir; em seguida tentamos PATCH
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/labels"
    resp = requests.post(url, headers=HEADERS, json={
        "name": name,
        "color": color,
        "description": description,
    }, timeout=30)
    if resp.status_code in (200, 201):
        print(f"[ok] label '{name}' criada em {repo}")
        return
    if resp.status_code == 422:  # já existe -> patch
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


def get_issue_by_title(repo: str, title: str) -> Optional[dict]:
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/issues"
    page = 1
    while True:
        r = requests.get(url, headers=HEADERS, params={"state": "all", "per_page": 100, "page": page}, timeout=30)
        r.raise_for_status()
        items = r.json()
        if not items:
            return None
        for i in items:
            if i.get("title") == title:
                return i
        page += 1
        time.sleep(0.1)


def create_issue(repo: str, title: str, body: str) -> Optional[dict]:
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo}/issues"
    r = requests.post(url, headers=HEADERS, json={"title": title, "body": body, "labels": ["automation"]}, timeout=30)
    if r.status_code in (200, 201):
        issue = r.json()
        print(f"[ok] issue '{title}' criada em {repo}")
        return issue
    else:
        print(f"[aviso] erro criando issue em {repo}: {r.status_code} {r.text}")
        return None


def ensure_file(repo: str, path: str, content: str, message: str) -> None:
    base = f"https://api.github.com/repos/{ORG_NAME}/{repo}/contents/{path}"
    # Verifica se já existe
    r = requests.get(base, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        print(f"[ok] arquivo existente preservado: {repo}:{path}")
        return
    if r.status_code not in (200, 404):
        print(f"[aviso] não foi possível verificar {repo}:{path}: {r.status_code} {r.text}")
        return
    # Cria novo arquivo
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        # opcional: branch
    }
    cr = requests.put(base, headers=HEADERS, json=payload, timeout=30)
    if cr.status_code in (201, 200):
        print(f"[ok] arquivo criado: {repo}:{path}")
    else:
        print(f"[aviso] erro criando {repo}:{path}: {cr.status_code} {cr.text}")


# GraphQL helpers (Projects v2)

def graphql(query: str, variables: dict) -> dict:
    r = requests.post("https://api.github.com/graphql", headers=GRAPHQL_HEADERS, json={"query": query, "variables": variables}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def get_project_id(org_login: str, project_number: int) -> Optional[str]:
    query = """
    query($org: String!, $num: Int!) {
      organization(login: $org) {
        projectV2(number: $num) { id title url }
      }
    }
    """
    try:
        data = graphql(query, {"org": org_login, "num": project_number})
        proj = data.get("organization", {}).get("projectV2")
        if proj and proj.get("id"):
            print(f"[info] project v2: {proj['title']} -> {proj['url']}")
            return proj["id"]
    except Exception as e:
        print(f"[aviso] falha ao obter project v2: {e}")
    return None


def add_issue_to_project(project_id: str, issue_node_id: str) -> None:
    mutation = """
    mutation($project: ID!, $content: ID!) {
      addProjectV2ItemById(input: { projectId: $project, contentId: $content }) {
        item { id }
      }
    }
    """
    try:
        graphql(mutation, {"project": project_id, "content": issue_node_id})
        print("[ok] issue vinculada ao Project v2")
    except Exception as e:
        # Pode já existir; apenas registra aviso
        print(f"[aviso] não foi possível vincular issue ao Project v2: {e}")


def main():
    print(f"[info] organização: {ORG_NAME}")
    project_id = get_project_id(ORG_NAME, PROJECT_NUMBER)
    if not project_id:
        print("[aviso] Project v2 não encontrado ou sem permissões. Prosseguindo sem vínculo.")

    repos = list_repos(ORG_NAME)
    print(f"[info] repositórios encontrados: {len(repos)}")
    for r in repos:
        repo = r["name"]
        print(f"\n[repo] {repo}")
        # 1) Labels
        for l in LABELS_DEFAULT:
            ensure_label(repo, l["name"], l["color"], l.get("description", ""))

        # 2) Templates de issue/PR e Workflow básico (não sobrescreve)
        ensure_file(repo, ISSUE_TEMPLATE_PATH, ISSUE_TEMPLATE_CONTENT, "chore: add automation issue template")
        ensure_file(repo, PR_TEMPLATE_PATH, PR_TEMPLATE_CONTENT, "chore: add PR template")
        ensure_file(repo, WORKFLOW_PATH, WORKFLOW_CONTENT, "chore: add basic CI workflow (yamllint)")

        # 3) Issue checklist e vínculo ao Project v2
        issue = get_issue_by_title(repo, ISSUE_TITLE)
        if not issue:
            issue = create_issue(repo, ISSUE_TITLE, ISSUE_BODY)
        else:
            print(f"[ok] issue '{ISSUE_TITLE}' já existe em {repo}")

        if project_id and issue and issue.get("node_id"):
            add_issue_to_project(project_id, issue["node_id"])


if __name__ == "__main__":
    main()
