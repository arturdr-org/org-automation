#!/usr/bin/env python3
"""
Sistema de Monitoramento e Health Check para automação da organização arturdr-org
Verifica o status da automação e gera relatórios de saúde.
"""

import os
import json
import requests
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging

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

class OrganizationHealthMonitor:
    """Classe para monitoramento da saúde da automação."""
    
    def __init__(self):
        self.org_name = ORG_NAME
        self.config_dir = Path(__file__).parent.parent.parent / "common/config"
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "unknown",
            "repositories": {},
            "automation_stats": {
                "total_repos": 0,
                "compliant_repos": 0,
                "compliance_percentage": 0
            },
            "issues_found": [],
            "recommendations": []
        }
    
    def load_expected_config(self) -> Dict:
        """Carrega as configurações esperadas."""
        config = {}
        
        # Labels esperadas
        if (self.config_dir / "labels.yml").exists():
            with open(self.config_dir / "labels.yml", 'r') as f:
                labels_config = yaml.safe_load(f)
                expected_labels = []
                expected_labels.extend(labels_config.get("default_labels", []))
                expected_labels.extend(labels_config.get("org_labels", []))
                config["expected_labels"] = [label["name"] for label in expected_labels]
        
        # Templates esperados
        config["expected_templates"] = [
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/CODEOWNERS"
        ]
        
        # Workflows esperados
        config["expected_workflows"] = [
            ".github/workflows/ci-basic.yml"
        ]
        
        return config
    
    def get_repositories(self) -> List[Dict]:
        """Lista todos os repositórios da organização."""
        repos = []
        page = 1
        
        try:
            while True:
                url = f"https://api.github.com/orgs/{self.org_name}/repos"
                r = requests.get(
                    url,
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
            
            return [repo for repo in repos if not repo.get("archived", False)]
            
        except Exception as e:
            logger.error(f"Erro ao listar repositórios: {e}")
            return []
    
    def check_repository_compliance(self, repo: Dict, expected_config: Dict) -> Dict:
        """Verifica a conformidade de um repositório."""
        repo_name = repo["name"]
        compliance = {
            "name": repo_name,
            "url": repo["html_url"],
            "compliance_score": 0,
            "max_score": 0,
            "issues": [],
            "checks": {
                "labels": {"status": "unknown", "details": []},
                "templates": {"status": "unknown", "details": []},
                "workflows": {"status": "unknown", "details": []},
                "branch_protection": {"status": "unknown", "details": []},
            }
        }
        
        # Verificar labels
        try:
            labels_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/labels"
            labels_resp = requests.get(labels_url, headers=HEADERS, timeout=30)
            if labels_resp.ok:
                existing_labels = {label["name"] for label in labels_resp.json()}
                expected_labels = set(expected_config.get("expected_labels", []))
                
                missing_labels = expected_labels - existing_labels
                compliance["max_score"] += len(expected_labels)
                compliance["compliance_score"] += len(expected_labels) - len(missing_labels)
                
                if missing_labels:
                    compliance["checks"]["labels"]["status"] = "warning"
                    compliance["checks"]["labels"]["details"] = [f"Labels faltando: {', '.join(missing_labels)}"]
                    compliance["issues"].append(f"Faltam {len(missing_labels)} labels padrão")
                else:
                    compliance["checks"]["labels"]["status"] = "ok"
                    compliance["checks"]["labels"]["details"] = ["Todas as labels padrão presentes"]
            else:
                compliance["checks"]["labels"]["status"] = "error"
                compliance["checks"]["labels"]["details"] = ["Não foi possível verificar labels"]
        except Exception as e:
            compliance["checks"]["labels"]["status"] = "error"
            compliance["checks"]["labels"]["details"] = [f"Erro: {str(e)}"]
        
        # Verificar templates
        expected_templates = expected_config.get("expected_templates", [])
        compliance["max_score"] += len(expected_templates)
        templates_found = 0
        missing_templates = []
        
        for template_path in expected_templates:
            try:
                content_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/contents/{template_path}"
                template_resp = requests.get(content_url, headers=HEADERS, timeout=30)
                if template_resp.status_code == 200:
                    templates_found += 1
                    compliance["compliance_score"] += 1
                else:
                    missing_templates.append(template_path)
            except Exception:
                missing_templates.append(template_path)
        
        if missing_templates:
            compliance["checks"]["templates"]["status"] = "warning"
            compliance["checks"]["templates"]["details"] = [f"Templates faltando: {', '.join(missing_templates)}"]
            compliance["issues"].append(f"Faltam {len(missing_templates)} templates")
        else:
            compliance["checks"]["templates"]["status"] = "ok"
            compliance["checks"]["templates"]["details"] = ["Todos os templates presentes"]
        
        # Verificar proteção do branch principal
        try:
            # Primeiro, encontrar o branch padrão
            default_branch = repo.get("default_branch", "main")
            protection_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/branches/{default_branch}/protection"
            protection_resp = requests.get(protection_url, headers=HEADERS, timeout=30)
            
            compliance["max_score"] += 1
            if protection_resp.status_code == 200:
                compliance["compliance_score"] += 1
                compliance["checks"]["branch_protection"]["status"] = "ok"
                compliance["checks"]["branch_protection"]["details"] = [f"Branch '{default_branch}' está protegido"]
            else:
                compliance["checks"]["branch_protection"]["status"] = "warning"
                compliance["checks"]["branch_protection"]["details"] = [f"Branch '{default_branch}' não está protegido"]
                compliance["issues"].append(f"Branch principal '{default_branch}' não protegido")
        except Exception as e:
            compliance["checks"]["branch_protection"]["status"] = "error"
            compliance["checks"]["branch_protection"]["details"] = [f"Erro: {str(e)}"]
        
        # Calcular score final
        if compliance["max_score"] > 0:
            compliance["compliance_percentage"] = round((compliance["compliance_score"] / compliance["max_score"]) * 100, 1)
        else:
            compliance["compliance_percentage"] = 0
        
        return compliance
    
    def check_workflow_health(self) -> Dict:
        """Verifica a saúde dos workflows de automação."""
        workflow_health = {
            "status": "unknown",
            "last_run": None,
            "success_rate": 0,
            "recent_failures": []
        }
        
        try:
            # Verificar execuções recentes do workflow
            runs_url = f"https://api.github.com/repos/{self.org_name}/org-automation/actions/runs"
            runs_resp = requests.get(
                runs_url, 
                headers=HEADERS,
                params={"per_page": 10},
                timeout=30
            )
            
            if runs_resp.ok:
                runs_data = runs_resp.json()
                workflow_runs = runs_data.get("workflow_runs", [])
                
                if workflow_runs:
                    latest_run = workflow_runs[0]
                    workflow_health["last_run"] = {
                        "date": latest_run["created_at"],
                        "status": latest_run["conclusion"],
                        "url": latest_run["html_url"]
                    }
                    
                    # Calcular taxa de sucesso
                    success_count = sum(1 for run in workflow_runs if run["conclusion"] == "success")
                    workflow_health["success_rate"] = round((success_count / len(workflow_runs)) * 100, 1)
                    
                    # Encontrar falhas recentes
                    failures = [run for run in workflow_runs if run["conclusion"] in ["failure", "cancelled"]]
                    workflow_health["recent_failures"] = [
                        {
                            "date": run["created_at"],
                            "status": run["conclusion"],
                            "url": run["html_url"]
                        }
                        for run in failures[:3]
                    ]
                    
                    # Determinar status geral
                    if workflow_health["success_rate"] >= 80:
                        workflow_health["status"] = "healthy"
                    elif workflow_health["success_rate"] >= 60:
                        workflow_health["status"] = "warning"
                    else:
                        workflow_health["status"] = "critical"
                else:
                    workflow_health["status"] = "no_data"
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde dos workflows: {e}")
            workflow_health["status"] = "error"
            workflow_health["error"] = str(e)
        
        return workflow_health
    
    def generate_recommendations(self, repos_compliance: List[Dict]) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        # Analisar problemas comuns
        common_issues = {}
        for repo_compliance in repos_compliance:
            for issue in repo_compliance["issues"]:
                common_issues[issue] = common_issues.get(issue, 0) + 1
        
        # Gerar recomendações baseadas nos problemas mais comuns
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
            if count > len(repos_compliance) * 0.3:  # Se mais de 30% dos repos têm o problema
                recommendations.append(f"Problema comum em {count} repositórios: {issue}")
        
        # Recomendações específicas
        total_repos = len(repos_compliance)
        compliant_repos = sum(1 for repo in repos_compliance if repo["compliance_percentage"] >= 80)
        
        if compliant_repos / total_repos < 0.7:
            recommendations.append("Execute a automação com mais frequência para melhorar a conformidade geral")
        
        if any("Branch principal" in issue for repo in repos_compliance for issue in repo["issues"]):
            recommendations.append("Configure proteções de branch em repositórios críticos")
        
        return recommendations
    
    def run_health_check(self) -> None:
        """Executa verificação completa de saúde."""
        logger.info(f"🏥 Iniciando health check da organização {self.org_name}")
        
        # Carregar configuração esperada
        expected_config = self.load_expected_config()
        
        # Obter repositórios
        repos = self.get_repositories()
        self.health_status["automation_stats"]["total_repos"] = len(repos)
        
        logger.info(f"📊 Analisando {len(repos)} repositórios...")
        
        # Verificar conformidade de cada repositório
        repos_compliance = []
        for repo in repos:
            compliance = self.check_repository_compliance(repo, expected_config)
            repos_compliance.append(compliance)
            self.health_status["repositories"][repo["name"]] = compliance
            
            if compliance["compliance_percentage"] >= 80:
                self.health_status["automation_stats"]["compliant_repos"] += 1
        
        # Calcular estatísticas gerais
        if repos_compliance:
            avg_compliance = sum(repo["compliance_percentage"] for repo in repos_compliance) / len(repos_compliance)
            self.health_status["automation_stats"]["compliance_percentage"] = round(avg_compliance, 1)
        
        # Verificar saúde dos workflows
        workflow_health = self.check_workflow_health()
        self.health_status["workflow_health"] = workflow_health
        
        # Gerar recomendações
        self.health_status["recommendations"] = self.generate_recommendations(repos_compliance)
        
        # Determinar saúde geral
        overall_compliance = self.health_status["automation_stats"]["compliance_percentage"]
        workflow_status = workflow_health["status"]
        
        if overall_compliance >= 80 and workflow_status == "healthy":
            self.health_status["overall_health"] = "healthy"
        elif overall_compliance >= 60 and workflow_status in ["healthy", "warning"]:
            self.health_status["overall_health"] = "warning"
        else:
            self.health_status["overall_health"] = "critical"
        
        logger.info(f"✅ Health check concluído - Status geral: {self.health_status['overall_health']}")
    
    def generate_report(self) -> str:
        """Gera relatório de saúde em formato texto."""
        status = self.health_status
        
        # Símbolos para status
        status_symbols = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴",
            "unknown": "⚪",
            "error": "❌",
            "ok": "✅"
        }
        
        report = f"""
{'='*80}
🏥 RELATÓRIO DE SAÚDE DA AUTOMAÇÃO DA ORGANIZAÇÃO
{'='*80}

🏢 Organização: {self.org_name}
📊 Status Geral: {status_symbols.get(status['overall_health'], '⚪')} {status['overall_health'].upper()}
⏰ Gerado em: {datetime.fromisoformat(status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}

📈 ESTATÍSTICAS GERAIS:
  📁 Total de repositórios: {status['automation_stats']['total_repos']}
  ✅ Repositórios em conformidade (≥80%): {status['automation_stats']['compliant_repos']}
  📊 Taxa de conformidade média: {status['automation_stats']['compliance_percentage']}%

🔄 SAÚDE DOS WORKFLOWS:
  Status: {status_symbols.get(status['workflow_health']['status'], '⚪')} {status['workflow_health']['status']}
  Taxa de sucesso: {status['workflow_health']['success_rate']}%
"""
        
        if status['workflow_health'].get('last_run'):
            last_run = status['workflow_health']['last_run']
            report += f"  Última execução: {last_run['date']} ({last_run['status']})\n"
        
        # Top repositórios com problemas
        problematic_repos = sorted(
            [(name, data) for name, data in status['repositories'].items()],
            key=lambda x: x[1]['compliance_percentage']
        )[:5]
        
        if problematic_repos:
            report += "\n🚨 REPOSITÓRIOS QUE PRECISAM DE ATENÇÃO (top 5):\n"
            for repo_name, repo_data in problematic_repos:
                if repo_data['compliance_percentage'] < 80:
                    report += f"  📁 {repo_name}: {repo_data['compliance_percentage']}% - {len(repo_data['issues'])} problemas\n"
        
        # Recomendações
        if status['recommendations']:
            report += "\n💡 RECOMENDAÇÕES:\n"
            for i, rec in enumerate(status['recommendations'], 1):
                report += f"  {i}. {rec}\n"
        
        report += f"\n{'='*80}\n"
        return report
    
    def save_report(self) -> str:
        """Salva o relatório em arquivos."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar JSON detalhado
        json_file = f"health_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.health_status, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório texto
        txt_file = f"health_report_{timestamp}.txt"
        report_text = self.generate_report()
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return txt_file


def main():
    """Função principal."""
    try:
        monitor = OrganizationHealthMonitor()
        monitor.run_health_check()
        
        # Gerar e exibir relatório
        report = monitor.generate_report()
        print(report)
        
        # Salvar relatório
        report_file = monitor.save_report()
        logger.info(f"📄 Relatório salvo em: {report_file}")
        
        # Exit code baseado na saúde geral
        if monitor.health_status["overall_health"] == "critical":
            exit(2)
        elif monitor.health_status["overall_health"] == "warning":
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        logger.error(f"❌ Erro durante health check: {e}")
        exit(3)


if __name__ == "__main__":
    main()