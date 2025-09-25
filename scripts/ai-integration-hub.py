#!/usr/bin/env python3
"""
🤖 AI Integration Hub - Hub Central para Múltiplos Sistemas de IA

Este script serve como hub central para integrar e coordenar múltiplos
sistemas de IA (Claude, GPT, Gemini, etc.) com o manual de operações,
permitindo operações autônomas colaborativas entre diferentes IAs.

Autor: Sistema AI-Powered
Versão: 1.0.0
"""

import json
import os
import sys
import logging
import argparse
import asyncio
import aiohttp
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# ============================================
# 🏗️ Configuração e Tipos de Dados
# ============================================

class AIProvider(Enum):
    """Provedores de IA suportados"""
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    GITHUB_COPILOT = "github_copilot"
    LOCAL_LLM = "local_llm"
    WARP_AGENT = "warp_agent"

class RequestStatus(Enum):
    """Status das requisições de IA"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AIRequest:
    """Estrutura de uma requisição de IA"""
    id: str
    provider: AIProvider
    operation: str
    parameters: Dict[str, Any]
    priority: int = 5  # 1=highest, 10=lowest
    created_at: datetime = None
    status: RequestStatus = RequestStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class AIResponse:
    """Estrutura de uma resposta de IA"""
    request_id: str
    provider: AIProvider
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now(timezone.utc)

# ============================================
# 🧠 Classe Principal do Hub de IA
# ============================================

class AIIntegrationHub:
    """Hub central para integração de múltiplas IAs"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o hub de integração de IA
        
        Args:
            config_path: Caminho para arquivo de configuração customizado
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.request_queue: List[AIRequest] = []
        self.active_requests: Dict[str, AIRequest] = {}
        self.providers: Dict[AIProvider, Dict[str, Any]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Estatísticas do hub
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'providers_status': {},
            'start_time': datetime.now(timezone.utc)
        }
        
        self._initialize_providers()
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Carrega configuração do hub"""
        default_config = {
            'hub': {
                'max_concurrent_requests': 10,
                'request_timeout': 300,
                'retry_attempts': 3,
                'log_level': 'INFO'
            },
            'providers': {
                'claude': {
                    'enabled': True,
                    'api_key_env': 'CLAUDE_API_KEY',
                    'base_url': 'https://api.anthropic.com/v1',
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 4000,
                    'rate_limit': 5  # requests per minute
                },
                'gpt': {
                    'enabled': True,
                    'api_key_env': 'OPENAI_API_KEY',
                    'base_url': 'https://api.openai.com/v1',
                    'model': 'gpt-4-turbo-preview',
                    'max_tokens': 4000,
                    'rate_limit': 10
                },
                'gemini': {
                    'enabled': True,
                    'api_key_env': 'GEMINI_API_KEY',
                    'base_url': 'https://generativelanguage.googleapis.com/v1',
                    'model': 'gemini-pro',
                    'max_tokens': 2048,
                    'rate_limit': 15
                },
                'warp_agent': {
                    'enabled': True,
                    'local': True,
                    'manual_path': 'docs/ai-operations-manual.md',
                    'parser_script': 'scripts/ai-manual-parser.py'
                }
            },
            'operations': {
                'allowed_commands': [
                    'Verificar Status do Sistema',
                    'Monitorar Recursos',
                    'Análise de Logs',
                    'Health Check',
                    'Deploy Status',
                    'Security Check'
                ],
                'emergency_only': [
                    'Restart Services',
                    'Rollback Deployment',
                    'Security Incident Response'
                ]
            },
            'notifications': {
                'slack_webhook': os.getenv('SLACK_WEBHOOK_URL'),
                'email_enabled': False,
                'pagerduty_key': os.getenv('PAGERDUTY_INTEGRATION_KEY')
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                print(f"⚠️ Erro ao carregar config customizada: {e}")
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging"""
        log_level = getattr(logging, self.config['hub'].get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_integration_hub.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    def _initialize_providers(self):
        """Inicializa provedores de IA"""
        self.logger.info("🚀 Inicializando provedores de IA...")
        
        for provider_name, config in self.config['providers'].items():
            if not config.get('enabled', False):
                continue
                
            provider = AIProvider(provider_name)
            self.providers[provider] = {
                'config': config,
                'status': 'initializing',
                'requests_count': 0,
                'last_request': None,
                'rate_limit_reset': datetime.now(timezone.utc)
            }
            
            # Verificar dependências do provedor
            if not config.get('local', False):
                api_key_env = config.get('api_key_env')
                if api_key_env and not os.getenv(api_key_env):
                    self.logger.warning(
                        f"⚠️ API key não encontrada para {provider_name}: {api_key_env}"
                    )
                    self.providers[provider]['status'] = 'disabled'
                else:
                    self.providers[provider]['status'] = 'ready'
            else:
                self.providers[provider]['status'] = 'ready'
        
        self.logger.info(
            f"✅ {len([p for p in self.providers.values() if p['status'] == 'ready'])} "
            f"provedores prontos de {len(self.providers)} configurados"
        )

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    # ============================================
    # 🎯 Gerenciamento de Requisições
    # ============================================

    def submit_request(
        self, 
        provider: Union[AIProvider, str], 
        operation: str,
        parameters: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """
        Submete uma nova requisição para processamento
        
        Args:
            provider: Provedor de IA
            operation: Operação a ser executada
            parameters: Parâmetros da operação
            priority: Prioridade (1=alta, 10=baixa)
            
        Returns:
            ID da requisição
        """
        if isinstance(provider, str):
            provider = AIProvider(provider)
        
        # Validar provedor
        if provider not in self.providers:
            raise ValueError(f"Provedor não configurado: {provider.value}")
        
        if self.providers[provider]['status'] != 'ready':
            raise ValueError(f"Provedor não disponível: {provider.value}")
        
        # Validar operação
        allowed_ops = self.config['operations']['allowed_commands']
        emergency_ops = self.config['operations']['emergency_only']
        
        if operation not in allowed_ops and operation not in emergency_ops:
            raise ValueError(f"Operação não permitida: {operation}")
        
        # Criar requisição
        request_id = f"{provider.value}_{int(time.time() * 1000)}"
        request = AIRequest(
            id=request_id,
            provider=provider,
            operation=operation,
            parameters=parameters,
            priority=priority
        )
        
        # Adicionar à fila ordenada por prioridade
        self.request_queue.append(request)
        self.request_queue.sort(key=lambda r: r.priority)
        
        self.stats['total_requests'] += 1
        self.logger.info(
            f"📝 Nova requisição: {request_id} ({provider.value}) - {operation}"
        )
        
        return request_id

    async def process_requests(self):
        """Processa requisições na fila"""
        self.logger.info("🔄 Iniciando processamento de requisições...")
        
        max_concurrent = self.config['hub']['max_concurrent_requests']
        
        while True:
            # Processar requisições pendentes
            while (
                self.request_queue and 
                len(self.active_requests) < max_concurrent
            ):
                request = self.request_queue.pop(0)
                self.active_requests[request.id] = request
                
                # Processar requisição de forma assíncrona
                asyncio.create_task(self._process_single_request(request))
            
            # Aguardar um pouco antes da próxima verificação
            await asyncio.sleep(1)
    
    async def _process_single_request(self, request: AIRequest):
        """Processa uma única requisição"""
        start_time = time.time()
        
        try:
            request.status = RequestStatus.PROCESSING
            self.logger.info(f"🔄 Processando: {request.id}")
            
            # Executar baseado no provedor
            if request.provider == AIProvider.WARP_AGENT:
                result = await self._process_warp_agent(request)
            else:
                result = await self._process_api_provider(request)
            
            request.result = result
            request.status = RequestStatus.COMPLETED
            self.stats['successful_requests'] += 1
            
            self.logger.info(f"✅ Concluído: {request.id}")
            
        except Exception as e:
            request.error = str(e)
            request.status = RequestStatus.FAILED
            self.stats['failed_requests'] += 1
            
            self.logger.error(f"❌ Falhou: {request.id} - {e}")
            
            # Notificar falha crítica
            await self._notify_failure(request, e)
        
        finally:
            request.execution_time = time.time() - start_time
            
            # Remover da lista ativa
            if request.id in self.active_requests:
                del self.active_requests[request.id]
            
            # Atualizar estatísticas do provedor
            self.providers[request.provider]['requests_count'] += 1
            self.providers[request.provider]['last_request'] = datetime.now(timezone.utc)

    async def _process_warp_agent(self, request: AIRequest) -> Dict[str, Any]:
        """Processa requisição para Warp Agent (local)"""
        parser_script = self.providers[AIProvider.WARP_AGENT]['config']['parser_script']
        
        # Construir comando
        cmd_parts = ['python', parser_script]
        
        if request.operation in self.config['operations']['allowed_commands']:
            cmd_parts.extend(['--command', f'"{request.operation}"'])
        
        # Adicionar parâmetros
        if request.parameters.get('dry_run', True):
            cmd_parts.append('--dry-run')
        
        # Executar comando
        proc = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise Exception(f"Warp Agent error: {stderr.decode()}")
        
        return {
            'output': stdout.decode(),
            'exit_code': proc.returncode,
            'command': ' '.join(cmd_parts)
        }

    async def _process_api_provider(self, request: AIRequest) -> Dict[str, Any]:
        """Processa requisição para provedor de API externa"""
        provider_config = self.providers[request.provider]['config']
        
        # Preparar headers
        headers = {'Content-Type': 'application/json'}
        
        # Adicionar autenticação
        api_key = os.getenv(provider_config['api_key_env'])
        if not api_key:
            raise Exception(f"API key não encontrada: {provider_config['api_key_env']}")
        
        if request.provider == AIProvider.CLAUDE:
            headers['x-api-key'] = api_key
            headers['anthropic-version'] = '2023-06-01'
        elif request.provider == AIProvider.GPT:
            headers['Authorization'] = f'Bearer {api_key}'
        elif request.provider == AIProvider.GEMINI:
            # Gemini usa API key na URL
            pass
        
        # Preparar payload
        payload = self._prepare_api_payload(request, provider_config)
        
        # Fazer requisição
        url = self._build_api_url(request.provider, provider_config)
        
        timeout = aiohttp.ClientTimeout(total=self.config['hub']['request_timeout'])
        
        async with self.session.post(url, json=payload, headers=headers, timeout=timeout) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API error {response.status}: {error_text}")
            
            return await response.json()

    def _prepare_api_payload(self, request: AIRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara payload para API do provedor"""
        operation_prompt = self._build_operation_prompt(request)
        
        if request.provider == AIProvider.CLAUDE:
            return {
                "model": config['model'],
                "max_tokens": config['max_tokens'],
                "messages": [
                    {
                        "role": "user",
                        "content": operation_prompt
                    }
                ]
            }
        
        elif request.provider == AIProvider.GPT:
            return {
                "model": config['model'],
                "max_tokens": config['max_tokens'],
                "messages": [
                    {
                        "role": "user",
                        "content": operation_prompt
                    }
                ]
            }
        
        elif request.provider == AIProvider.GEMINI:
            return {
                "contents": [
                    {
                        "parts": [
                            {"text": operation_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": config['max_tokens']
                }
            }
        
        else:
            raise ValueError(f"Payload não implementado para: {request.provider}")

    def _build_api_url(self, provider: AIProvider, config: Dict[str, Any]) -> str:
        """Constrói URL da API"""
        base_url = config['base_url']
        
        if provider == AIProvider.CLAUDE:
            return f"{base_url}/messages"
        elif provider == AIProvider.GPT:
            return f"{base_url}/chat/completions"
        elif provider == AIProvider.GEMINI:
            api_key = os.getenv(config['api_key_env'])
            return f"{base_url}/models/{config['model']}:generateContent?key={api_key}"
        else:
            raise ValueError(f"URL não implementada para: {provider}")

    def _build_operation_prompt(self, request: AIRequest) -> str:
        """Constrói prompt para a operação"""
        base_prompt = f"""
Você é um assistente de IA especializado em operações de infraestrutura.
Execute a seguinte operação: {request.operation}

Parâmetros:
{json.dumps(request.parameters, indent=2)}

Contexto:
- Este é um sistema de automação de organizações
- Você deve seguir as melhores práticas de segurança
- Forneça respostas estruturadas e acionáveis
- Se necessário, sugira próximos passos

Responda no formato JSON com as seguintes chaves:
- "status": "success" ou "error"
- "data": dados da operação
- "message": mensagem explicativa
- "next_actions": lista de próximas ações sugeridas (se aplicável)
"""
        
        # Adicionar contexto específico baseado na operação
        if request.operation == "Verificar Status do Sistema":
            base_prompt += "\nFoque em métricas de CPU, memória, disco e rede."
        elif request.operation == "Análise de Logs":
            base_prompt += "\nAnalise padrões, erros e anomalias nos logs."
        elif request.operation == "Security Check":
            base_prompt += "\nVerifique vulnerabilidades e configurações de segurança."
        
        return base_prompt

    # ============================================
    # 📊 Monitoramento e Estatísticas
    # ============================================

    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do hub"""
        uptime = datetime.now(timezone.utc) - self.stats['start_time']
        
        return {
            'hub_status': 'active',
            'uptime_seconds': uptime.total_seconds(),
            'statistics': self.stats.copy(),
            'queue_size': len(self.request_queue),
            'active_requests': len(self.active_requests),
            'providers': {
                provider.value: {
                    'status': config['status'],
                    'requests_count': config['requests_count'],
                    'last_request': config['last_request'].isoformat() if config['last_request'] else None
                }
                for provider, config in self.providers.items()
            },
            'performance': {
                'success_rate': (
                    self.stats['successful_requests'] / max(self.stats['total_requests'], 1)
                ) * 100,
                'avg_queue_wait': self._calculate_avg_wait_time(),
                'provider_availability': self._calculate_provider_availability()
            }
        }

    def _calculate_avg_wait_time(self) -> float:
        """Calcula tempo médio de espera na fila"""
        if not self.request_queue:
            return 0.0
        
        now = datetime.now(timezone.utc)
        total_wait = sum(
            (now - req.created_at).total_seconds() 
            for req in self.request_queue
        )
        
        return total_wait / len(self.request_queue)

    def _calculate_provider_availability(self) -> Dict[str, float]:
        """Calcula disponibilidade dos provedores"""
        availability = {}
        
        for provider, config in self.providers.items():
            if config['requests_count'] == 0:
                availability[provider.value] = 100.0
            else:
                # Simplificado: baseado no status atual
                availability[provider.value] = 100.0 if config['status'] == 'ready' else 0.0
        
        return availability

    async def _notify_failure(self, request: AIRequest, error: Exception):
        """Notifica falha crítica"""
        notification_data = {
            'request_id': request.id,
            'provider': request.provider.value,
            'operation': request.operation,
            'error': str(error),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Slack
        slack_url = self.config['notifications']['slack_webhook']
        if slack_url and self.session:
            try:
                await self.session.post(
                    slack_url,
                    json={
                        'text': f'🚨 AI Hub Failure: {request.operation}',
                        'attachments': [{
                            'color': 'danger',
                            'fields': [
                                {'title': 'Provider', 'value': request.provider.value, 'short': True},
                                {'title': 'Operation', 'value': request.operation, 'short': True},
                                {'title': 'Error', 'value': str(error)[:500], 'short': False}
                            ]
                        }]
                    }
                )
            except Exception as e:
                self.logger.error(f"Falha ao enviar notificação Slack: {e}")

    # ============================================
    # 🎛️ Interface de Linha de Comando
    # ============================================

    def list_providers(self):
        """Lista provedores disponíveis"""
        print("🤖 Provedores de IA Configurados:")
        print("=" * 50)
        
        for provider, config in self.providers.items():
            status_emoji = {
                'ready': '✅',
                'disabled': '❌', 
                'initializing': '🔄'
            }.get(config['status'], '❓')
            
            print(f"{status_emoji} {provider.value.upper()}")
            print(f"   Status: {config['status']}")
            print(f"   Requests: {config['requests_count']}")
            
            if config['last_request']:
                print(f"   Última Req: {config['last_request']}")
            
            print()

    def list_operations(self):
        """Lista operações disponíveis"""
        print("🎯 Operações Disponíveis:")
        print("=" * 50)
        
        print("📋 Comandos Regulares:")
        for cmd in self.config['operations']['allowed_commands']:
            print(f"   • {cmd}")
        
        print("\n🚨 Comandos de Emergência:")
        for cmd in self.config['operations']['emergency_only']:
            print(f"   • {cmd}")

# ============================================
# 🚀 Função Principal
# ============================================

async def main():
    """Função principal do hub"""
    parser = argparse.ArgumentParser(
        description="🤖 AI Integration Hub - Hub Central de Múltiplas IAs"
    )
    
    parser.add_argument(
        '--config', 
        help='Arquivo de configuração customizado'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando start - iniciar hub
    start_parser = subparsers.add_parser('start', help='Iniciar hub de IA')
    start_parser.add_argument(
        '--daemon', 
        action='store_true', 
        help='Executar como daemon'
    )
    
    # Comando status - mostrar status
    status_parser = subparsers.add_parser('status', help='Mostrar status do hub')
    
    # Comando request - fazer requisição
    request_parser = subparsers.add_parser('request', help='Fazer requisição para IA')
    request_parser.add_argument('provider', help='Provedor de IA')
    request_parser.add_argument('operation', help='Operação a executar')
    request_parser.add_argument(
        '--parameters', 
        default='{}', 
        help='Parâmetros JSON da operação'
    )
    request_parser.add_argument(
        '--priority', 
        type=int, 
        default=5, 
        help='Prioridade (1-10)'
    )
    
    # Comando list - listar informações
    list_parser = subparsers.add_parser('list', help='Listar informações')
    list_subparsers = list_parser.add_subparsers(dest='list_type')
    list_subparsers.add_parser('providers', help='Listar provedores')
    list_subparsers.add_parser('operations', help='Listar operações')
    
    args = parser.parse_args()
    
    # Executar comando
    async with AIIntegrationHub(args.config) as hub:
        
        if args.command == 'start':
            if args.daemon:
                print("🚀 Iniciando AI Hub em modo daemon...")
                await hub.process_requests()
            else:
                print("🚀 AI Hub inicializado. Use Ctrl+C para parar.")
                try:
                    await hub.process_requests()
                except KeyboardInterrupt:
                    print("\n👋 AI Hub finalizado.")
        
        elif args.command == 'status':
            status = hub.get_status()
            print("📊 Status do AI Integration Hub:")
            print("=" * 50)
            print(json.dumps(status, indent=2, default=str))
        
        elif args.command == 'request':
            try:
                parameters = json.loads(args.parameters)
                request_id = hub.submit_request(
                    args.provider,
                    args.operation, 
                    parameters,
                    args.priority
                )
                print(f"✅ Requisição submetida: {request_id}")
            except Exception as e:
                print(f"❌ Erro ao submeter requisição: {e}")
                sys.exit(1)
        
        elif args.command == 'list':
            if args.list_type == 'providers':
                hub.list_providers()
            elif args.list_type == 'operations':
                hub.list_operations()
            else:
                print("❓ Tipo de listagem inválido. Use: providers, operations")
        
        else:
            parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AI Integration Hub finalizado.")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)