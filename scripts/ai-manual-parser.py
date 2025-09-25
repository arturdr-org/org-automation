#!/usr/bin/env python3
"""
🤖 AI Manual Parser - org-automation v3.0

Parser automático para extrair e executar comandos do manual de operações para IAs.
Permite que IAs leiam o manual e executem operações de forma autônoma.
"""

import os
import re
import sys
import json
import subprocess
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_manual_parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIManualParser:
    """Parser para extrair comandos do manual de operações."""
    
    def __init__(self, manual_path: Optional[str] = None):
        """Inicializar parser."""
        self.root_dir = Path(__file__).parent.parent
        self.manual_path = Path(manual_path) if manual_path else self.root_dir / "docs" / "ai-operations-manual.md"
        self.commands = {}
        
        if not self.manual_path.exists():
            raise FileNotFoundError(f"Manual não encontrado: {self.manual_path}")
        
        logger.info(f"🤖 AI Manual Parser iniciado - Manual: {self.manual_path}")
    
    def parse_manual(self) -> Dict[str, Dict[str, Any]]:
        """Extrair todos os comandos do manual."""
        logger.info("📖 Parseando manual de operações...")
        
        with open(self.manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para extrair comandos
        command_pattern = r'### COMANDO: (.+?)\n\*\*Descrição:\*\* (.+?)\n\*\*Pré-requisitos:\*\* (.+?)\n\*\*Comando:\*\*\n```bash\n(.*?)\n```\n\*\*Verificação:\*\* (.+?)\n\*\*Troubleshooting:\*\* (.+?)(?=\n###|\n---|\n##|\Z)'
        
        matches = re.findall(command_pattern, content, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            command_name = match[0].strip()
            description = match[1].strip()
            prerequisites = match[2].strip()
            command_code = match[3].strip()
            verification = match[4].strip()
            troubleshooting = match[5].strip()
            
            self.commands[command_name] = {
                'description': description,
                'prerequisites': prerequisites,
                'command': command_code,
                'verification': verification,
                'troubleshooting': troubleshooting,
                'priority': self._determine_priority(command_name, description)
            }
        
        logger.info(f"✅ {len(self.commands)} comandos extraídos do manual")
        return self.commands
    
    def _determine_priority(self, name: str, description: str) -> str:
        """Determinar prioridade do comando baseado em nome e descrição."""
        high_priority_keywords = ['health', 'monitoramento', 'diagnóstico', 'emergência', 'status']
        medium_priority_keywords = ['dashboard', 'limpeza', 'validação', 'backup']
        
        text = f"{name} {description}".lower()
        
        if any(keyword in text for keyword in high_priority_keywords):
            return 'alta'
        elif any(keyword in text for keyword in medium_priority_keywords):
            return 'média'
        else:
            return 'baixa'
    
    def get_command(self, command_name: str) -> Optional[Dict[str, Any]]:
        """Obter comando específico."""
        return self.commands.get(command_name)
    
    def list_commands(self, priority_filter: Optional[str] = None) -> List[str]:
        """Listar comandos disponíveis, opcionalmente filtrados por prioridade."""
        if not self.commands:
            self.parse_manual()
        
        if priority_filter:
            return [name for name, cmd in self.commands.items() if cmd['priority'] == priority_filter]
        else:
            return list(self.commands.keys())
    
    def get_commands_by_category(self) -> Dict[str, List[str]]:
        """Agrupar comandos por categoria."""
        categories = {
            'Sistema': [],
            'Deploy e MCP': [],
            'Monitoramento': [],
            'Manutenção': [],
            'Emergência': []
        }
        
        for name, cmd in self.commands.items():
            desc = cmd['description'].lower()
            
            if any(word in desc for word in ['sistema', 'status', 'estrutura']):
                categories['Sistema'].append(name)
            elif any(word in desc for word in ['mcp', 'repositório', 'deploy']):
                categories['Deploy e MCP'].append(name)
            elif any(word in desc for word in ['monitoramento', 'dashboard', 'métricas']):
                categories['Monitoramento'].append(name)
            elif any(word in desc for word in ['limpeza', 'backup', 'manutenção']):
                categories['Manutenção'].append(name)
            elif any(word in desc for word in ['diagnóstico', 'emergência', 'restaurar']):
                categories['Emergência'].append(name)
            else:
                categories['Sistema'].append(name)  # Default
        
        return categories


class AIOperationsBot:
    """Bot para execução automatizada de operações."""
    
    def __init__(self, parser: AIManualParser):
        """Inicializar bot de operações."""
        self.parser = parser
        self.execution_log = []
        
        logger.info("🤖 AI Operations Bot iniciado")
    
    def check_prerequisites(self, command_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Verificar se pré-requisitos são atendidos."""
        prerequisites = command_data['prerequisites'].lower()
        
        # Verificações básicas
        if 'token github' in prerequisites and 'nenhum' not in prerequisites:
            if not os.getenv('ORG_AUTOMATION_PAT') and not os.getenv('GITHUB_TOKEN'):
                return False, "Token GitHub não configurado"
        
        # Sistema deve estar funcionando
        if not Path(self.parser.root_dir).exists():
            return False, "Diretório do sistema não encontrado"
        
        # Verificar se é repositório git (se necessário)
        if 'repositório git' in prerequisites:
            git_dir = self.parser.root_dir / '.git'
            if not git_dir.exists():
                return False, "Não é um repositório Git"
        
        return True, "Pré-requisitos atendidos"
    
    def execute_command(self, command_name: str, dry_run: bool = True) -> Dict[str, Any]:
        """Executar comando específico."""
        logger.info(f"🔄 Executando comando: {command_name} (dry_run={dry_run})")
        
        if not self.parser.commands:
            self.parser.parse_manual()
        
        command_data = self.parser.get_command(command_name)
        if not command_data:
            return {
                'success': False,
                'error': f'Comando não encontrado: {command_name}',
                'output': '',
                'dry_run': dry_run
            }
        
        # Verificar pré-requisitos
        prereq_ok, prereq_msg = self.check_prerequisites(command_data)
        if not prereq_ok:
            return {
                'success': False,
                'error': f'Pré-requisitos não atendidos: {prereq_msg}',
                'output': '',
                'dry_run': dry_run
            }
        
        # Preparar comando
        command_code = command_data['command']
        
        if dry_run:
            # Em dry_run, apenas simular
            result = {
                'success': True,
                'output': f'[DRY_RUN] Comando simulado:\n{command_code}',
                'error': None,
                'dry_run': True,
                'command_data': command_data
            }
            logger.info(f"✅ Dry run concluído para: {command_name}")
        else:
            # Execução real
            try:
                result = self._execute_bash_command(command_code)
                result['dry_run'] = False
                result['command_data'] = command_data
                
                if result['success']:
                    logger.info(f"✅ Comando executado com sucesso: {command_name}")
                else:
                    logger.error(f"❌ Falha na execução: {command_name}")
                    
            except Exception as e:
                result = {
                    'success': False,
                    'error': str(e),
                    'output': '',
                    'dry_run': False
                }
                logger.error(f"❌ Erro na execução de {command_name}: {e}")
        
        # Log da execução
        execution_entry = {
            'timestamp': datetime.now().isoformat(),
            'command_name': command_name,
            'success': result['success'],
            'dry_run': dry_run,
            'error': result.get('error'),
            'output_length': len(result.get('output', ''))
        }
        self.execution_log.append(execution_entry)
        
        return result
    
    def _execute_bash_command(self, command_code: str) -> Dict[str, Any]:
        """Executar comando bash e capturar resultado."""
        try:
            # Preparar ambiente
            env = os.environ.copy()
            
            # Executar comando
            process = subprocess.run(
                command_code,
                shell=True,
                cwd=self.parser.root_dir,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minutos timeout
            )
            
            return {
                'success': process.returncode == 0,
                'output': process.stdout,
                'error': process.stderr if process.returncode != 0 else None,
                'return_code': process.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Comando excedeu timeout de 5 minutos',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def run_routine(self, routine_type: str = 'daily') -> Dict[str, Any]:
        """Executar rotina automatizada."""
        logger.info(f"🔄 Executando rotina: {routine_type}")
        
        routines = {
            'daily': [
                'Verificar Status do Sistema',
                'Executar Health Check',
                'Gerar Dashboard',
                'Calcular KPIs',
                'Limpeza do Sistema'
            ],
            'weekly': [
                'Executar Automação Principal',
                'Atualizar Submódulos MCP',
                'Backup de Configuração',
                'Validar Estrutura'
            ],
            'emergency': [
                'Diagnóstico Completo',
                'Validar Estrutura',
                'Calcular KPIs'
            ]
        }
        
        commands_to_run = routines.get(routine_type, routines['daily'])
        results = {
            'routine_type': routine_type,
            'start_time': datetime.now().isoformat(),
            'commands_executed': [],
            'success_count': 0,
            'failure_count': 0,
            'total_commands': len(commands_to_run)
        }
        
        for command_name in commands_to_run:
            logger.info(f"🔄 Executando: {command_name}")
            
            # Primeiro dry_run para validar
            dry_result = self.execute_command(command_name, dry_run=True)
            
            if dry_result['success']:
                # Se dry_run passou, executar real (mas só para comandos seguros)
                safe_commands = [
                    'Verificar Status do Sistema',
                    'Gerar Dashboard', 
                    'Calcular KPIs',
                    'Limpeza do Sistema',
                    'Diagnóstico Completo',
                    'Validar Estrutura'
                ]
                
                if command_name in safe_commands:
                    real_result = self.execute_command(command_name, dry_run=False)
                else:
                    # Para comandos não seguros, apenas dry_run
                    real_result = dry_result
                    real_result['note'] = 'Executado apenas dry_run por segurança'
            else:
                real_result = dry_result
            
            results['commands_executed'].append({
                'command': command_name,
                'success': real_result['success'],
                'dry_run': real_result.get('dry_run', True),
                'error': real_result.get('error'),
                'note': real_result.get('note')
            })
            
            if real_result['success']:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
        
        results['end_time'] = datetime.now().isoformat()
        results['success_rate'] = (results['success_count'] / results['total_commands']) * 100
        
        logger.info(f"✅ Rotina {routine_type} concluída - Sucesso: {results['success_count']}/{results['total_commands']}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Gerar relatório de execuções."""
        report = {
            'generation_time': datetime.now().isoformat(),
            'total_executions': len(self.execution_log),
            'successful_executions': sum(1 for log in self.execution_log if log['success']),
            'failed_executions': sum(1 for log in self.execution_log if not log['success']),
            'dry_runs': sum(1 for log in self.execution_log if log['dry_run']),
            'real_executions': sum(1 for log in self.execution_log if not log['dry_run']),
            'recent_executions': self.execution_log[-10:],  # Últimas 10
            'available_commands': len(self.parser.commands or {}),
            'command_categories': self.parser.get_commands_by_category() if self.parser.commands else {}
        }
        
        return report


def main():
    """Função principal com CLI."""
    parser = argparse.ArgumentParser(description='AI Manual Parser & Operations Bot')
    parser.add_argument('--command', '-c', help='Nome do comando para executar')
    parser.add_argument('--routine', '-r', choices=['daily', 'weekly', 'emergency'], help='Tipo de rotina para executar')
    parser.add_argument('--list', '-l', action='store_true', help='Listar comandos disponíveis')
    parser.add_argument('--dry-run', action='store_true', help='Executar apenas simulação (dry run)')
    parser.add_argument('--priority', '-p', choices=['alta', 'média', 'baixa'], help='Filtrar comandos por prioridade')
    parser.add_argument('--report', action='store_true', help='Gerar relatório de execuções')
    parser.add_argument('--manual', help='Caminho para manual personalizado')
    
    args = parser.parse_args()
    
    try:
        # Inicializar parser e bot
        manual_parser = AIManualParser(args.manual)
        manual_parser.parse_manual()
        
        operations_bot = AIOperationsBot(manual_parser)
        
        if args.list:
            # Listar comandos
            commands = manual_parser.list_commands(args.priority)
            categories = manual_parser.get_commands_by_category()
            
            print(f"\n📋 Comandos Disponíveis ({len(commands)} total):")
            print("=" * 50)
            
            for category, cmd_list in categories.items():
                if cmd_list and (not args.priority or any(manual_parser.commands[cmd]['priority'] == args.priority for cmd in cmd_list)):
                    print(f"\n🎯 {category}:")
                    for cmd in cmd_list:
                        if not args.priority or manual_parser.commands[cmd]['priority'] == args.priority:
                            priority = manual_parser.commands[cmd]['priority']
                            print(f"  • {cmd} [{priority}]")
            
        elif args.command:
            # Executar comando específico
            result = operations_bot.execute_command(args.command, dry_run=args.dry_run)
            
            print(f"\n🔄 Resultado do Comando: {args.command}")
            print("=" * 50)
            print(f"Status: {'✅ Sucesso' if result['success'] else '❌ Falha'}")
            print(f"Modo: {'🧪 Dry Run' if result['dry_run'] else '🚀 Execução Real'}")
            
            if result.get('error'):
                print(f"Erro: {result['error']}")
            
            if result.get('output'):
                print(f"\nOutput:\n{result['output']}")
                
            if result.get('note'):
                print(f"Nota: {result['note']}")
        
        elif args.routine:
            # Executar rotina
            result = operations_bot.run_routine(args.routine)
            
            print(f"\n🔄 Resultado da Rotina: {args.routine.upper()}")
            print("=" * 50)
            print(f"Comandos executados: {result['success_count']}/{result['total_commands']}")
            print(f"Taxa de sucesso: {result['success_rate']:.1f}%")
            
            print(f"\n📋 Detalhes dos Comandos:")
            for cmd in result['commands_executed']:
                status = "✅" if cmd['success'] else "❌"
                mode = "🧪" if cmd.get('dry_run') else "🚀"
                print(f"  {status} {mode} {cmd['command']}")
                if cmd.get('error'):
                    print(f"    ⚠️ {cmd['error']}")
                if cmd.get('note'):
                    print(f"    ℹ️ {cmd['note']}")
        
        elif args.report:
            # Gerar relatório
            report = operations_bot.generate_report()
            
            print(f"\n📊 Relatório de Execuções")
            print("=" * 50)
            print(f"Total de execuções: {report['total_executions']}")
            print(f"Sucessos: {report['successful_executions']}")
            print(f"Falhas: {report['failed_executions']}")
            print(f"Dry runs: {report['dry_runs']}")
            print(f"Execuções reais: {report['real_executions']}")
            print(f"Comandos disponíveis: {report['available_commands']}")
            
            # Salvar relatório
            report_file = f"ai_operations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Relatório salvo: {report_file}")
        
        else:
            # Mostrar ajuda
            parser.print_help()
            
            # Mostrar resumo do sistema
            print(f"\n🤖 AI Manual Parser & Operations Bot")
            print("=" * 50)
            print(f"📖 Manual: {manual_parser.manual_path}")
            print(f"📋 Comandos disponíveis: {len(manual_parser.commands)}")
            
            categories = manual_parser.get_commands_by_category()
            for category, cmds in categories.items():
                if cmds:
                    print(f"  🎯 {category}: {len(cmds)} comandos")
    
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()