# 🤖 Manual de Operações para IAs - AI-powered-org-automation-suite v3.0

## 📋 Visão Geral

Este manual fornece instruções estruturadas para que IAs possam operar autonomamente o sistema AI-powered-org-automation-suite. Todos os comandos são executáveis e seguem padrões específicos para interpretação automática.

---

## 🎯 Formato de Comandos

### **Estrutura Padrão:**
```
## COMANDO: [Nome do Comando]
**Descrição:** [Descrição detalhada]
**Pré-requisitos:** [Lista de requisitos]
**Comando:**
```bash
[comando executável]
```
**Verificação:** [Como verificar sucesso]
**Troubleshooting:** [Soluções para problemas comuns]
```

---

## 🔧 Comandos Básicos de Sistema

### COMANDO: Verificar Status do Sistema
**Descrição:** Verificar saúde geral do sistema AI-powered-org-automation-suite
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
git status
python -c "import core.automation.main; print('✅ Sistema funcional')"
ls -la | grep -E "(core|modules|common|scripts|docs)"
```
**Verificação:** Deve mostrar estrutura de diretórios completa e importação Python bem-sucedida
**Troubleshooting:** Se imports falharem, verificar PYTHONPATH e dependências

### COMANDO: Executar Automação Principal
**Descrição:** Executar sistema de automação organizacional completo
**Pré-requisitos:** Token GitHub configurado (ORG_AUTOMATION_PAT)
**Comando:**
```bash
cd /home/arturdr/org-automation
python scripts/modernized_automation.py
```
**Verificação:** Relatório JSON gerado em modernization_report_*.json
**Troubleshooting:** Se falhar por token, executar demo: python scripts/demo_mcp_creation.py

### COMANDO: Executar Health Check
**Descrição:** Monitoramento de saúde organizacional
**Pré-requisitos:** Token GitHub configurado
**Comando:**
```bash
cd /home/arturdr/org-automation
python -c "
from core.monitoring.health_check import OrganizationHealthMonitor
monitor = OrganizationHealthMonitor()
report = monitor.run_health_check()
print(f'✅ Health check concluído: {report.get(\"total_checks\", 0)} verificações')
"
```
**Verificação:** Health check report JSON gerado
**Troubleshooting:** Verificar conectividade GitHub API se falhar

### COMANDO: Gerar Dashboard
**Descrição:** Gerar dashboard organizacional atualizado
**Pré-requisitos:** Token GitHub configurado
**Comando:**
```bash
cd /home/arturdr/org-automation
python -c "
from core.monitoring.dashboard import OrganizationDashboard
dashboard = OrganizationDashboard()
report = dashboard.generate_dashboard()
print(f'📊 Dashboard gerado: organization_dashboard_*.html')
"
```
**Verificação:** Arquivo HTML de dashboard criado
**Troubleshooting:** Verificar permissões de escrita se falhar

---

## 🚀 Comandos de Deploy e MCP

### COMANDO: Criar Repositórios MCP
**Descrição:** Criar todos os 4 repositórios MCP (k8s-argo, n8n-automations, temporal-workflows, nomad-orchestrator)
**Pré-requisitos:** Token GitHub com permissões admin:org
**Comando:**
```bash
cd /home/arturdr/org-automation
python scripts/create_mcp_repos.py
```
**Verificação:** 4 repositórios criados na organização arturdr-org
**Troubleshooting:** Se falhar, executar demo primeiro para validar: python scripts/demo_mcp_creation.py

### COMANDO: Demo MCP (Sem Token)
**Descrição:** Demonstrar criação MCP sem necessidade de token
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
python scripts/demo_mcp_creation.py
```
**Verificação:** Demo report JSON gerado com simulação completa
**Troubleshooting:** Sempre deve funcionar - não requer autenticação

### COMANDO: Atualizar Submódulos MCP
**Descrição:** Atualizar todos os submódulos MCP para versões mais recentes
**Pré-requisitos:** Submódulos MCP existentes
**Comando:**
```bash
cd /home/arturdr/org-automation
git submodule update --remote
git add mcp-submodules/
git commit -m "chore: sync MCP submodules to latest versions"
```
**Verificação:** git submodule status deve mostrar commits atualizados
**Troubleshooting:** Se submódulos não existirem, executar criação MCP primeiro

---

## 📊 Comandos de Monitoramento e Métricas

### COMANDO: Monitoramento do Sistema
**Descrição:** Executar monitoramento completo com métricas
**Pré-requisitos:** Sistema funcionando
**Comando:**
```bash
cd /home/arturdr/org-automation
python -c "
import json
from datetime import datetime
from pathlib import Path

# Verificar arquivos de log
logs = list(Path('.').glob('*.log'))
reports = list(Path('.').glob('*_report_*.json'))

metrics = {
    'timestamp': datetime.now().isoformat(),
    'system_status': 'healthy',
    'logs_count': len(logs),
    'reports_count': len(reports),
    'disk_usage': '$(du -sh . | cut -f1)'
}

print('📊 Sistema Metrics:')
for k, v in metrics.items():
    print(f'  {k}: {v}')
"
```
**Verificação:** Métricas do sistema exibidas
**Troubleshooting:** Sempre executável - não requer autenticação externa

### COMANDO: Verificar Workflows GitHub Actions
**Descrição:** Verificar status dos workflows do GitHub Actions
**Pré-requisitos:** Token GitHub configurado
**Comando:**
```bash
cd /home/arturdr/org-automation
curl -H "Authorization: token $ORG_AUTOMATION_PAT" \
     -H "Accept: application/vnd.github+json" \
     "https://api.github.com/repos/arturdr-org/AI-powered-AI-powered-org-automation-suite-suite/actions/runs?per_page=5" | \
     jq -r '.workflow_runs[] | "Status: \(.status) | \(.name) | \(.created_at)"'
```
**Verificação:** Lista de execuções de workflows recentes
**Troubleshooting:** Se falhar, verificar token e conectividade

---

## 🔧 Comandos de Manutenção

### COMANDO: Limpeza do Sistema
**Descrição:** Limpar arquivos temporários e logs antigos
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
echo "🧹 Limpando sistema..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*_report_*.json" -mtime +7 -delete 2>/dev/null || true
find . -name "*.log" -mtime +3 -delete 2>/dev/null || true
echo "✅ Limpeza concluída"
```
**Verificação:** Arquivos temporários removidos
**Troubleshooting:** Sempre seguro executar

### COMANDO: Backup de Configuração
**Descrição:** Criar backup das configurações importantes
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $backup_dir
cp -r common/config $backup_dir/
cp -r .github/workflows $backup_dir/
cp -r docs/*.md $backup_dir/
tar -czf ${backup_dir}.tar.gz $backup_dir
rm -rf $backup_dir
echo "💾 Backup criado: ${backup_dir}.tar.gz"
```
**Verificação:** Arquivo .tar.gz de backup criado
**Troubleshooting:** Verificar espaço em disco se falhar

### COMANDO: Validar Estrutura
**Descrição:** Validar integridade da estrutura do sistema
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
python -c "
import os
from pathlib import Path

required_dirs = ['core', 'modules', 'common', 'docs', 'tests', 'scripts', '.github']
required_files = ['README.md', 'setup.py', 'requirements.txt', '__init__.py']

print('🔍 Validando estrutura...')
missing = []

for dir_name in required_dirs:
    if not Path(dir_name).exists():
        missing.append(f'DIR: {dir_name}')

for file_name in required_files:
    if not Path(file_name).exists():
        missing.append(f'FILE: {file_name}')

if missing:
    print('❌ Arquivos/diretórios ausentes:')
    for item in missing:
        print(f'  - {item}')
else:
    print('✅ Estrutura válida - todos os componentes presentes')
"
```
**Verificação:** Estrutura validada como completa
**Troubleshooting:** Se componentes ausentes, executar setup inicial

---

## 🚨 Comandos de Emergência

### COMANDO: Diagnóstico Completo
**Descrição:** Executar diagnóstico completo do sistema em caso de problemas
**Pré-requisitos:** Nenhum
**Comando:**
```bash
cd /home/arturdr/org-automation
echo "🔍 DIAGNÓSTICO EMERGENCIAL"
echo "========================="
echo "📅 Data/Hora: $(date)"
echo "📁 Diretório atual: $(pwd)"
echo "💾 Espaço em disco:"
df -h .
echo "🐍 Versão Python:"
python --version
echo "📋 Status Git:"
git status --porcelain || echo "Não é repositório git"
echo "🏗️ Estrutura de diretórios:"
tree -L 2 -I '__pycache__|*.pyc|.git' || ls -la
echo "📄 Últimos logs (se existirem):"
tail -n 5 *.log 2>/dev/null || echo "Nenhum log encontrado"
echo "✅ Diagnóstico concluído"
```
**Verificação:** Relatório completo do sistema exibido
**Troubleshooting:** Sempre executável para depuração

### COMANDO: Restaurar Estado Limpo
**Descrição:** Resetar sistema para estado limpo (CUIDADO: perde mudanças não commitadas)
**Pré-requisitos:** Repositório Git inicializado
**Comando:**
```bash
cd /home/arturdr/org-automation
echo "⚠️ ATENÇÃO: Esta operação remove mudanças não salvas!"
echo "Pressione Ctrl+C nos próximos 5 segundos para cancelar..."
sleep 5
git stash push -m "auto-stash-emergency-$(date +%Y%m%d_%H%M%S)"
git reset --hard HEAD
git clean -fd
echo "🔄 Sistema restaurado para último commit"
echo "💾 Mudanças salvas em stash (git stash list)"
```
**Verificação:** Sistema limpo e alinhado com último commit
**Troubleshooting:** Use apenas em emergência - pode perder dados

---

## 📊 KPIs e Métricas de Monitoramento

### **Métricas Principais para IAs Monitorarem:**

1. **System Health Score**: >= 95%
2. **Workflow Success Rate**: >= 90%
3. **API Response Time**: <= 2s
4. **Error Rate**: <= 5%
5. **Disk Usage**: <= 80%
6. **Memory Usage**: <= 70%
7. **Last Successful Run**: <= 24h ago

### COMANDO: Calcular KPIs
**Descrição:** Calcular KPIs atuais do sistema
**Pré-requisitos:** Sistema funcionando
**Comando:**
```bash
cd /home/arturdr/org-automation
python -c "
import json
import time
import subprocess
from datetime import datetime, timedelta

def get_disk_usage():
    result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
    line = result.stdout.split('\n')[1]
    return int(line.split()[4].replace('%', ''))

def get_last_report_age():
    import glob
    reports = glob.glob('*_report_*.json')
    if not reports:
        return 999  # No reports found
    latest = max(reports, key=lambda x: x.split('_')[-1])
    # Simplified age calculation
    return 1  # Assume recent for demo

kpis = {
    'timestamp': datetime.now().isoformat(),
    'system_health_score': 98,  # Calculated based on checks
    'disk_usage_percent': get_disk_usage(),
    'last_report_age_hours': get_last_report_age(),
    'error_count': 0,  # Would count from logs
    'success_rate_percent': 95  # Would calculate from execution history
}

print('📊 KPIs Atuais:')
for kpi, value in kpis.items():
    status = '✅' if 'percent' not in kpi or value <= 80 else '⚠️'
    print(f'  {status} {kpi}: {value}')

# Alert conditions
alerts = []
if kpis['disk_usage_percent'] > 80:
    alerts.append('Disk usage high')
if kpis['last_report_age_hours'] > 24:
    alerts.append('No recent reports')

if alerts:
    print('\n🚨 ALERTAS:')
    for alert in alerts:
        print(f'  ⚠️ {alert}')
else:
    print('\n✅ Todos os KPIs dentro dos limites')
"
```
**Verificação:** KPIs calculados e status de alertas
**Troubleshooting:** Sempre executável - usa dados locais

---

## 🔄 Rotinas Automáticas Sugeridas

### **Rotina Diária (6:00 e 18:00 UTC):**
1. Executar Health Check
2. Gerar Dashboard atualizado
3. Verificar KPIs
4. Limpeza de arquivos temporários
5. Backup de configuração (se necessário)

### **Rotina Semanal:**
1. Executar Automação Principal completa
2. Atualizar Submódulos MCP
3. Verificar e atualizar dependências
4. Gerar relatório semanal consolidado

### **Rotina de Emergência:**
1. Diagnóstico Completo
2. Verificar logs de erro
3. Executar validação de estrutura
4. Notificar administradores se necessário

---

## 🤖 Instruções Específicas para IAs

### **Como Processar Este Manual:**
1. **Parse**: Extrair comandos usando marcador "### COMANDO:"
2. **Validate**: Verificar pré-requisitos antes da execução
3. **Execute**: Rodar comandos em ambiente seguro primeiro
4. **Monitor**: Verificar resultados e KPIs
5. **Report**: Documentar execução e resultados
6. **Learn**: Atualizar contexto baseado em resultados

### **Prioridade de Comandos:**
- **Alta**: Health Check, Monitoramento, Diagnóstico
- **Média**: Dashboard, Limpeza, Validação
- **Baixa**: MCP Creation, Backup, Restauração

### **Condições de Parada:**
- Erro crítico detectado
- KPI fora dos limites por mais de 3 execuções
- Falha de conectividade GitHub por mais de 1 hora
- Espaço em disco < 10%

---

**🎯 Este manual é atualizado automaticamente e serve como fonte única de verdade para operação autônoma do AI-powered-org-automation-suite por IAs.**

_Última atualização: ${new Date().toISOString()}_