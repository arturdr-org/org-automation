#!/usr/bin/env python3
"""
Dashboard Avançado de Monitoramento Organizacional
Consolida métricas, relatórios e alertas de toda a organização arturdr-org
"""

import os
import json
import requests
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict
import statistics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
ORG_NAME = os.getenv("ORG_NAME", "arturdr-org")
TOKEN = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    logger.error("Token não encontrado")
    exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

class OrganizationDashboard:
    """Dashboard consolidado da organização."""
    
    def __init__(self):
        self.org_name = ORG_NAME
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "organization": {
                "name": self.org_name,
                "total_repos": 0,
                "languages": {},
                "topics": {},
                "visibility": {"public": 0, "private": 0}
            },
            "automation": {
                "compliance_rate": 0,
                "workflows_health": {},
                "last_automation_run": None
            },
            "development": {
                "commits_last_week": 0,
                "prs_last_week": 0,
                "issues_last_week": 0,
                "active_contributors": 0,
                "avg_pr_time": 0
            },
            "security": {
                "vulnerabilities": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "secret_scanning_alerts": 0,
                "dependency_alerts": 0
            },
            "quality": {
                "avg_code_coverage": 0,
                "workflow_success_rate": 0,
                "failed_workflows": []
            },
            "repositories": {}
        }
    
    def collect_organization_metrics(self) -> None:
        """Coleta métricas gerais da organização."""
        try:
            # Obter informações da organização
            org_url = f"https://api.github.com/orgs/{self.org_name}"
            org_resp = requests.get(org_url, headers=HEADERS, timeout=30)
            
            if org_resp.ok:
                org_data = org_resp.json()
                self.metrics["organization"].update({
                    "description": org_data.get("description", ""),
                    "created_at": org_data.get("created_at", ""),
                    "public_repos": org_data.get("public_repos", 0),
                    "private_repos": org_data.get("total_private_repos", 0),
                    "members": org_data.get("public_members", 0)
                })
            
            # Obter repositórios
            repos = self._get_repositories()
            self.metrics["organization"]["total_repos"] = len(repos)
            
            # Analisar repositórios
            for repo in repos:
                self._analyze_repository(repo)
                
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da organização: {e}")
    
    def _get_repositories(self) -> List[Dict]:
        """Obter todos os repositórios da organização."""
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/orgs/{self.org_name}/repos"
            params = {"per_page": 100, "page": page, "type": "all"}
            
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if not resp.ok:
                break
                
            data = resp.json()
            if not data:
                break
                
            repos.extend(data)
            page += 1
        
        return [repo for repo in repos if not repo.get("archived", False)]
    
    def _analyze_repository(self, repo: Dict) -> None:
        """Analisa um repositório individual."""
        repo_name = repo["name"]
        
        # Métricas básicas
        language = repo.get("language")
        if language:
            self.metrics["organization"]["languages"][language] = \
                self.metrics["organization"]["languages"].get(language, 0) + 1
        
        # Visibilidade
        if repo.get("private"):
            self.metrics["organization"]["visibility"]["private"] += 1
        else:
            self.metrics["organization"]["visibility"]["public"] += 1
        
        # Topics
        topics = repo.get("topics", [])
        for topic in topics:
            self.metrics["organization"]["topics"][topic] = \
                self.metrics["organization"]["topics"].get(topic, 0) + 1
        
        # Análise detalhada do repositório
        repo_metrics = {
            "name": repo_name,
            "language": language,
            "size": repo.get("size", 0),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "issues": repo.get("open_issues_count", 0),
            "last_push": repo.get("pushed_at", ""),
            "workflows": {},
            "security": {},
            "compliance": {}
        }
        
        # Analisar workflows
        self._analyze_repository_workflows(repo_name, repo_metrics)
        
        # Analisar atividade recente
        self._analyze_repository_activity(repo_name, repo_metrics)
        
        # Verificar compliance
        self._check_repository_compliance(repo_name, repo_metrics)
        
        self.metrics["repositories"][repo_name] = repo_metrics
    
    def _analyze_repository_workflows(self, repo_name: str, repo_metrics: Dict) -> None:
        """Analisa workflows do repositório."""
        try:
            # Obter workflows
            workflows_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/actions/workflows"
            workflows_resp = requests.get(workflows_url, headers=HEADERS, timeout=30)
            
            if workflows_resp.ok:
                workflows = workflows_resp.json().get("workflows", [])
                repo_metrics["workflows"]["total"] = len(workflows)
                repo_metrics["workflows"]["active"] = len([w for w in workflows if w.get("state") == "active"])
                
                # Analisar execuções recentes
                runs_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/actions/runs"
                runs_resp = requests.get(
                    runs_url, 
                    headers=HEADERS, 
                    params={"per_page": 50},
                    timeout=30
                )
                
                if runs_resp.ok:
                    runs = runs_resp.json().get("workflow_runs", [])
                    if runs:
                        success_count = len([r for r in runs if r.get("conclusion") == "success"])
                        repo_metrics["workflows"]["success_rate"] = round(
                            (success_count / len(runs)) * 100, 1
                        )
                        
                        # Workflows falhando
                        failed_runs = [r for r in runs if r.get("conclusion") == "failure"]
                        if failed_runs:
                            self.metrics["quality"]["failed_workflows"].extend([
                                {
                                    "repo": repo_name,
                                    "workflow": run.get("name"),
                                    "date": run.get("created_at"),
                                    "url": run.get("html_url")
                                }
                                for run in failed_runs[:3]  # Últimas 3 falhas
                            ])
                    
        except Exception as e:
            logger.warning(f"Erro ao analisar workflows de {repo_name}: {e}")
    
    def _analyze_repository_activity(self, repo_name: str, repo_metrics: Dict) -> None:
        """Analisa atividade recente do repositório."""
        try:
            # Data de uma semana atrás
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            # Commits da última semana
            commits_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/commits"
            commits_resp = requests.get(
                commits_url,
                headers=HEADERS,
                params={"since": week_ago, "per_page": 100},
                timeout=30
            )
            
            if commits_resp.ok:
                commits = commits_resp.json()
                repo_metrics["commits_last_week"] = len(commits)
                self.metrics["development"]["commits_last_week"] += len(commits)
                
                # Contribuidores únicos
                contributors = set(
                    commit.get("author", {}).get("login", "unknown")
                    for commit in commits
                    if commit.get("author")
                )
                repo_metrics["active_contributors"] = len(contributors)
            
            # PRs da última semana
            prs_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/pulls"
            prs_resp = requests.get(
                prs_url,
                headers=HEADERS,
                params={"state": "all", "since": week_ago},
                timeout=30
            )
            
            if prs_resp.ok:
                prs = prs_resp.json()
                recent_prs = [
                    pr for pr in prs
                    if datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")) > 
                       datetime.fromisoformat(week_ago.replace("Z", "+00:00"))
                ]
                repo_metrics["prs_last_week"] = len(recent_prs)
                self.metrics["development"]["prs_last_week"] += len(recent_prs)
                
                # Tempo médio de PR
                merged_prs = [pr for pr in recent_prs if pr.get("merged_at")]
                if merged_prs:
                    pr_times = []
                    for pr in merged_prs:
                        created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                        merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
                        pr_times.append((merged - created).total_seconds() / 3600)  # em horas
                    
                    repo_metrics["avg_pr_time_hours"] = round(statistics.mean(pr_times), 1)
            
            # Issues da última semana
            issues_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/issues"
            issues_resp = requests.get(
                issues_url,
                headers=HEADERS,
                params={"since": week_ago, "per_page": 100},
                timeout=30
            )
            
            if issues_resp.ok:
                issues = issues_resp.json()
                # Filtrar apenas issues (não PRs)
                recent_issues = [
                    issue for issue in issues
                    if not issue.get("pull_request") and
                    datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00")) > 
                    datetime.fromisoformat(week_ago.replace("Z", "+00:00"))
                ]
                repo_metrics["issues_last_week"] = len(recent_issues)
                self.metrics["development"]["issues_last_week"] += len(recent_issues)
                
        except Exception as e:
            logger.warning(f"Erro ao analisar atividade de {repo_name}: {e}")
    
    def _check_repository_compliance(self, repo_name: str, repo_metrics: Dict) -> None:
        """Verifica compliance do repositório."""
        compliance_score = 0
        max_score = 0
        
        try:
            # Verificar labels padrão
            labels_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/labels"
            labels_resp = requests.get(labels_url, headers=HEADERS, timeout=30)
            
            if labels_resp.ok:
                labels = {label["name"] for label in labels_resp.json()}
                expected_labels = {"bug", "enhancement", "automation", "priority:high"}
                
                max_score += len(expected_labels)
                compliance_score += len(expected_labels & labels)
                
                repo_metrics["compliance"]["labels"] = {
                    "found": len(expected_labels & labels),
                    "total": len(expected_labels),
                    "missing": list(expected_labels - labels)
                }
            
            # Verificar templates
            templates_to_check = [
                ".github/ISSUE_TEMPLATE/bug_report.md",
                ".github/PULL_REQUEST_TEMPLATE.md",
                ".github/CODEOWNERS"
            ]
            
            templates_found = 0
            for template_path in templates_to_check:
                content_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/contents/{template_path}"
                template_resp = requests.get(content_url, headers=HEADERS, timeout=30)
                if template_resp.status_code == 200:
                    templates_found += 1
            
            max_score += len(templates_to_check)
            compliance_score += templates_found
            
            repo_metrics["compliance"]["templates"] = {
                "found": templates_found,
                "total": len(templates_to_check)
            }
            
            # Verificar proteção de branch
            default_branch = repo_metrics.get("default_branch", "main")
            protection_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/branches/{default_branch}/protection"
            protection_resp = requests.get(protection_url, headers=HEADERS, timeout=30)
            
            max_score += 1
            if protection_resp.status_code == 200:
                compliance_score += 1
                repo_metrics["compliance"]["branch_protection"] = True
            else:
                repo_metrics["compliance"]["branch_protection"] = False
            
            # Calcular score final
            if max_score > 0:
                repo_metrics["compliance"]["score"] = round((compliance_score / max_score) * 100, 1)
            else:
                repo_metrics["compliance"]["score"] = 0
                
        except Exception as e:
            logger.warning(f"Erro ao verificar compliance de {repo_name}: {e}")
            repo_metrics["compliance"]["score"] = 0
    
    def calculate_summary_metrics(self) -> None:
        """Calcula métricas resumidas."""
        repos = list(self.metrics["repositories"].values())
        
        if not repos:
            return
        
        # Compliance médio
        compliance_scores = [
            repo.get("compliance", {}).get("score", 0)
            for repo in repos
        ]
        if compliance_scores:
            self.metrics["automation"]["compliance_rate"] = round(
                statistics.mean(compliance_scores), 1
            )
        
        # Taxa de sucesso dos workflows
        workflow_rates = [
            repo.get("workflows", {}).get("success_rate", 0)
            for repo in repos
            if repo.get("workflows", {}).get("success_rate") is not None
        ]
        if workflow_rates:
            self.metrics["quality"]["workflow_success_rate"] = round(
                statistics.mean(workflow_rates), 1
            )
        
        # Contribuidores ativos únicos
        all_contributors = set()
        for repo in repos:
            contributors = repo.get("active_contributors", 0)
            if contributors > 0:
                # Simplificação: assumindo que cada repo tem contribuidores únicos
                all_contributors.add(f"repo_{repo['name']}_contributors")
        
        self.metrics["development"]["active_contributors"] = len(repos)  # Aproximação
        
        # Tempo médio de PR
        pr_times = [
            repo.get("avg_pr_time_hours", 0)
            for repo in repos
            if repo.get("avg_pr_time_hours", 0) > 0
        ]
        if pr_times:
            self.metrics["development"]["avg_pr_time"] = round(statistics.mean(pr_times), 1)
    
    def generate_dashboard_html(self) -> str:
        """Gera dashboard em HTML."""
        html_template = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📊 Dashboard - {org_name}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f6f8fa;
                }}
                .dashboard {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .metric-card h3 {{
                    margin: 0 0 15px 0;
                    color: #1f2328;
                }}
                .big-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #0969da;
                    margin: 10px 0;
                }}
                .status-good {{ color: #1a7f37; }}
                .status-warning {{ color: #bf8700; }}
                .status-critical {{ color: #cf222e; }}
                .repo-list {{
                    max-height: 300px;
                    overflow-y: auto;
                }}
                .repo-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                }}
                .chart {{
                    margin: 20px 0;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 20px;
                    background: #eee;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #1a7f37, #26a641);
                }}
                .timestamp {{
                    text-align: center;
                    color: #656d76;
                    font-size: 0.9em;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>📊 Dashboard Organizacional</h1>
                    <h2>{org_name}</h2>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>🏢 Visão Geral</h3>
                        <div class="big-number">{total_repos}</div>
                        <p>Repositórios Ativos</p>
                        <p>📊 Públicos: {public_repos} | Privados: {private_repos}</p>
                    </div>
                    
                    <div class="metric-card">
                        <h3>🔄 Automação</h3>
                        <div class="big-number {compliance_status}">{compliance_rate}%</div>
                        <p>Taxa de Conformidade</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {compliance_rate}%"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>👨‍💻 Desenvolvimento</h3>
                        <div class="big-number">{commits_week}</div>
                        <p>Commits (última semana)</p>
                        <p>📋 PRs: {prs_week} | 🐛 Issues: {issues_week}</p>
                    </div>
                    
                    <div class="metric-card">
                        <h3>✅ Qualidade</h3>
                        <div class="big-number {workflow_status}">{workflow_success}%</div>
                        <p>Taxa de Sucesso Workflows</p>
                        <p>⏱️ Tempo médio PR: {avg_pr_time}h</p>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>🔧 Linguagens Principais</h3>
                        <div class="chart">
                            {languages_chart}
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>📊 Repositórios por Compliance</h3>
                        <div class="repo-list">
                            {compliance_list}
                        </div>
                    </div>
                </div>
                
                {failed_workflows_section}
                
                <div class="timestamp">
                    <p>📅 Última atualização: {timestamp}</p>
                    <p>🤖 Gerado automaticamente pelo sistema de automação arturdr-org</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Determinar status de compliance
        compliance_rate = self.metrics["automation"]["compliance_rate"]
        if compliance_rate >= 80:
            compliance_status = "status-good"
        elif compliance_rate >= 60:
            compliance_status = "status-warning"
        else:
            compliance_status = "status-critical"
        
        # Determinar status de workflows
        workflow_success = self.metrics["quality"]["workflow_success_rate"]
        if workflow_success >= 80:
            workflow_status = "status-good"
        elif workflow_success >= 60:
            workflow_status = "status-warning"
        else:
            workflow_status = "status-critical"
        
        # Gerar gráfico de linguagens
        languages = self.metrics["organization"]["languages"]
        languages_chart = ""
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / self.metrics["organization"]["total_repos"]) * 100
            languages_chart += f"""
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 100px;">{lang}</span>
                    <div style="display: inline-block; width: 150px; background: #eee; border-radius: 3px;">
                        <div style="width: {percentage}%; height: 20px; background: #0969da; border-radius: 3px;"></div>
                    </div>
                    <span style="margin-left: 10px;">{count}</span>
                </div>
            """
        
        # Gerar lista de compliance
        compliance_list = ""
        repos_by_compliance = sorted(
            self.metrics["repositories"].items(),
            key=lambda x: x[1].get("compliance", {}).get("score", 0),
            reverse=True
        )
        
        for repo_name, repo_data in repos_by_compliance[:10]:
            score = repo_data.get("compliance", {}).get("score", 0)
            if score >= 80:
                status_class = "status-good"
            elif score >= 60:
                status_class = "status-warning"
            else:
                status_class = "status-critical"
                
            compliance_list += f"""
                <div class="repo-item">
                    <span>{repo_name}</span>
                    <span class="{status_class}">{score}%</span>
                </div>
            """
        
        # Seção de workflows falhando
        failed_workflows_section = ""
        if self.metrics["quality"]["failed_workflows"]:
            failed_workflows_section = """
                <div class="metric-card">
                    <h3>⚠️ Workflows com Falhas Recentes</h3>
                    <div class="repo-list">
            """
            
            for workflow in self.metrics["quality"]["failed_workflows"][:10]:
                failed_workflows_section += f"""
                    <div class="repo-item">
                        <div>
                            <strong>{workflow['repo']}</strong><br>
                            <small>{workflow['workflow']}</small>
                        </div>
                        <small>{workflow['date'][:10]}</small>
                    </div>
                """
            
            failed_workflows_section += "</div></div>"
        
        return html_template.format(
            org_name=self.org_name,
            total_repos=self.metrics["organization"]["total_repos"],
            public_repos=self.metrics["organization"]["visibility"]["public"],
            private_repos=self.metrics["organization"]["visibility"]["private"],
            compliance_rate=compliance_rate,
            compliance_status=compliance_status,
            commits_week=self.metrics["development"]["commits_last_week"],
            prs_week=self.metrics["development"]["prs_last_week"],
            issues_week=self.metrics["development"]["issues_last_week"],
            workflow_success=workflow_success,
            workflow_status=workflow_status,
            avg_pr_time=self.metrics["development"]["avg_pr_time"],
            languages_chart=languages_chart,
            compliance_list=compliance_list,
            failed_workflows_section=failed_workflows_section,
            timestamp=datetime.fromisoformat(self.metrics["timestamp"]).strftime("%d/%m/%Y %H:%M:%S")
        )
    
    def save_dashboard(self) -> str:
        """Salva dashboard e métricas."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar métricas JSON
        json_file = f"dashboard_metrics_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        # Salvar dashboard HTML
        html_file = f"dashboard_{timestamp}.html"
        html_content = self.generate_dashboard_html()
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📊 Dashboard salvo: {html_file}")
        logger.info(f"📊 Métricas salvas: {json_file}")
        
        return html_file
    
    def run(self) -> None:
        """Executa coleta completa de métricas e geração de dashboard."""
        logger.info(f"📊 Coletando métricas da organização {self.org_name}...")
        
        self.collect_organization_metrics()
        self.calculate_summary_metrics()
        
        # Salvar dashboard
        dashboard_file = self.save_dashboard()
        
        # Imprimir resumo
        print("\n" + "="*60)
        print("📊 DASHBOARD ORGANIZACIONAL - RESUMO")
        print("="*60)
        print(f"🏢 Organização: {self.org_name}")
        print(f"📁 Repositórios: {self.metrics['organization']['total_repos']}")
        print(f"🔄 Compliance: {self.metrics['automation']['compliance_rate']}%")
        print(f"✅ Workflows: {self.metrics['quality']['workflow_success_rate']}%")
        print(f"💻 Commits (7d): {self.metrics['development']['commits_last_week']}")
        print(f"📋 PRs (7d): {self.metrics['development']['prs_last_week']}")
        print(f"🐛 Issues (7d): {self.metrics['development']['issues_last_week']}")
        print(f"📊 Dashboard: {dashboard_file}")
        print("="*60)


def main():
    """Função principal."""
    try:
        dashboard = OrganizationDashboard()
        dashboard.run()
    except Exception as e:
        logger.error(f"❌ Erro no dashboard: {e}")
        exit(1)


if __name__ == "__main__":
    main()