import os
import sys
import time
import json
import base64
import requests
import yaml
import jwt
from github import Github, Auth
from github.GithubException import GithubException

DEFAULT_LABELS_PATH = os.path.join(os.path.dirname(__file__), "config", "labels.yml")
GITHUB_API = "https://api.github.com"


def load_labels_config(path: str = DEFAULT_LABELS_PATH):
    if not os.path.exists(path):
        print(f"[aviso] Arquivo de labels não encontrado em {path}. Nada a sincronizar.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    labels = data.get("labels", [])
    # Normaliza estrutura mínima
    norm = []
    for item in labels:
        if not item or not item.get("name"):
            continue
        norm.append({
            "name": str(item["name"]).strip(),
            "color": str(item.get("color", "cfd3d7")).strip().lstrip("#").lower(),
            "description": (item.get("description") or "").strip(),
        })
    return norm


def create_app_jwt(app_id: str, private_key_pem: str) -> str:
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 8 * 60,  # 8 minutos
        "iss": app_id,
    }
    token = jwt.encode(payload, private_key_pem, algorithm="RS256")
    # PyJWT>=2 returns str; ensure str
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def get_app_installation_id(org_name: str, app_jwt: str) -> int:
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }
    # Try org installation endpoint (preferred)
    url = f"{GITHUB_API}/orgs/{org_name}/installation"
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        data = r.json()
        return int(data.get("id"))
    # Fallback: list installations accessible to app
    url = f"{GITHUB_API}/app/installations"
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        for inst in r.json():
            account = inst.get("account", {})
            if account.get("login") == org_name:
                return int(inst.get("id"))
    raise RuntimeError(f"Não foi possível localizar installation para org {org_name} (status {r.status_code})")


def get_app_installation_token(org_name: str, app_id: str, private_key_pem: str) -> str:
    app_jwt = create_app_jwt(app_id, private_key_pem)
    inst_id = get_app_installation_id(org_name, app_jwt)
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }
    url = f"{GITHUB_API}/app/installations/{inst_id}/access_tokens"
    r = requests.post(url, headers=headers, timeout=20)
    if r.status_code != 201:
        raise RuntimeError(f"Falha ao obter installation token (status {r.status_code}): {r.text}")
    return r.json().get("token")


def get_token(org_name: str):
    # Preferir GitHub App se variáveis estiverem definidas
    app_id = os.getenv("ORG_APP_ID")
    app_key = os.getenv("ORG_APP_PRIVATE_KEY")
    if app_id and app_key:
        try:
            token = get_app_installation_token(org_name, app_id, app_key)
            if token:
                return token
        except Exception as e:
            print(f"[aviso] Autenticação via GitHub App falhou: {e}. Tentando PAT...")
    # Fallback: PAT/GITHUB_TOKEN
    token = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("[erro] Nenhum token encontrado (GitHub App ou ORG_AUTOMATION_PAT/GITHUB_TOKEN).")
        sys.exit(1)
    return token


def sync_labels_for_repo(repo, desired_labels, dry_run=False):
    existing = {lbl.name.lower(): lbl for lbl in repo.get_labels()}
    created, updated = 0, 0
    for spec in desired_labels:
        name = spec["name"].strip()
        key = name.lower()
        color = spec.get("color", "cfd3d7").strip()
        desc = spec.get("description", "").strip()
        if key in existing:
            lbl = existing[key]
            need_update = (lbl.color.lower() != color.lower()) or ((lbl.description or "") != desc)
            if need_update:
                if dry_run:
                    print(f"  - (dry-run) atualizar label '{name}' -> color={color} desc='{desc}'")
                else:
                    lbl.edit(name=name, color=color, description=desc)
                updated += 1
        else:
            if dry_run:
                print(f"  - (dry-run) criar label '{name}' color={color} desc='{desc}'")
            else:
                repo.create_label(name=name, color=color, description=desc)
            created += 1
    return created, updated


def main():
    org_name = os.getenv("ORG_NAME", "arturdr-org")
    dry_run = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")

    print(f"Executando GitHub MCP para organização: {org_name} (dry_run={dry_run})")

    # Seleciona token (prefere GitHub App se disponível)
    token = get_token(org_name)
    gh = Github(auth=Auth.Token(token))

    # Carrega labels desejadas
    desired_labels = load_labels_config()
    if not desired_labels:
        print("[info] Nenhuma label desejada configurada. Encerrando.")
        return

    try:
        org = gh.get_organization(org_name)
    except GithubException as e:
        print(f"[erro] Não foi possível acessar a organização '{org_name}': {e}")
        sys.exit(1)

    repos = list(org.get_repos())
    print(f"[info] Repositórios na org: {len(repos)}")

    total_created = total_updated = 0
    per_repo = []
    for repo in repos:
        try:
            print(f"[repo] {repo.full_name}")
            created, updated = sync_labels_for_repo(repo, desired_labels, dry_run=dry_run)
            total_created += created
            total_updated += updated
            per_repo.append({
                "name": repo.full_name,
                "created": created,
                "updated": updated,
            })
            # Respeita limitações simples de taxa
            time.sleep(0.1)
        except GithubException as e:
            print(f"  [aviso] Falha ao sincronizar labels em {repo.full_name}: {e}")
            per_repo.append({
                "name": repo.full_name,
                "created": 0,
                "updated": 0,
                "error": str(e),
            })
            continue

    summary_lines = []
    summary_lines.append(f"# MCP Labels Summary\n")
    summary_lines.append(f"Org: {org_name}  ")
    summary_lines.append(f"Dry-run: {dry_run}  ")
    summary_lines.append(f"Repos: {len(repos)}  ")
    summary_lines.append(f"Created: {total_created}  Updated: {total_updated}\n")
    summary_lines.append("## Per-repo results\n")
    for item in per_repo:
        if "error" in item:
            summary_lines.append(f"- {item['name']}: created={item['created']} updated={item['updated']} error={item['error']}")
        else:
            summary_lines.append(f"- {item['name']}: created={item['created']} updated={item['updated']}")

    summary_text = "\n".join(summary_lines)
    print(summary_text)

    # Se estiver rodando em GitHub Actions, publica no Job Summary
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(summary_text + "\n")
        except Exception as e:
            print(f"[aviso] Não foi possível escrever GITHUB_STEP_SUMMARY: {e}")


if __name__ == "__main__":
    main()
