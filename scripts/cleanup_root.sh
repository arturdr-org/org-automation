#!/bin/bash
# 🧹 Script de Limpeza Final da Raiz do Repositório
# Remove todos os arquivos desnecessários da raiz

echo "🧹 Iniciando limpeza final da raiz do repositório..."
echo "=================================================="

# ============================================
# 1. Identificar Arquivos Essenciais na Raiz
# ============================================

# Lista de arquivos que DEVEM permanecer na raiz
essential_files=(
    "README.md"
    "CONTRIBUTING.md"
    "GOVERNANCE.md"
    "SETUP.md"
    "requirements.txt"
    "setup.py"
    ".gitignore"
    ".gitattributes"
    "sonar-project.properties"
    "LICENSE"  # Se existir
)

echo "📋 Arquivos essenciais que devem ficar na raiz:"
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚪ $file (não encontrado)"
    fi
done

# ============================================
# 2. Mover Logs Soltos
# ============================================

echo ""
echo "📊 Movendo logs soltos para pasta logs/..."

# Mover qualquer log na raiz para logs/
for log_file in *.log; do
    if [ -f "$log_file" ]; then
        echo "   📁 Movendo: $log_file → logs/"
        mv "$log_file" logs/
    fi
done

# Verificar outros tipos de arquivo de log
for pattern in "*.json" "ai_*" "*_report*"; do
    for file in $pattern; do
        if [ -f "$file" ] && [[ "$file" == *"report"* || "$file" == *"ai_"* ]]; then
            echo "   📁 Movendo relatório: $file → logs/"
            mv "$file" logs/ 2>/dev/null || true
        fi
    done
done

echo "✅ Logs organizados"

# ============================================
# 3. Verificar Arquivos Python Soltos
# ============================================

echo ""
echo "🐍 Verificando arquivos Python na raiz..."

found_python=false
for py_file in *.py; do
    if [ -f "$py_file" ] && [ "$py_file" != "setup.py" ]; then
        echo "   ⚠️  Arquivo Python encontrado: $py_file"
        echo "      🤔 Deveria estar em scripts/ ou core/?"
        
        # Perguntar onde mover (automaticamente para scripts se for um script)
        if [[ "$py_file" == *"script"* ]] || [[ "$py_file" == *"demo"* ]] || [[ "$py_file" == *"test"* ]]; then
            echo "      📜 Movendo para scripts/: $py_file"
            mv "$py_file" scripts/
        else
            echo "      🧠 Movendo para core/: $py_file"
            mv "$py_file" core/
        fi
        found_python=true
    fi
done

if [ "$found_python" = false ]; then
    echo "   ✅ Nenhum arquivo Python solto encontrado"
fi

# ============================================
# 4. Verificar Documentos Soltos
# ============================================

echo ""
echo "📚 Verificando documentos na raiz..."

found_docs=false
for doc_file in *.md; do
    if [ -f "$doc_file" ]; then
        # Verificar se é um arquivo essencial
        is_essential=false
        for essential in "${essential_files[@]}"; do
            if [ "$doc_file" = "$essential" ]; then
                is_essential=true
                break
            fi
        done
        
        if [ "$is_essential" = false ]; then
            echo "   📁 Documento não essencial: $doc_file"
            echo "      📚 Movendo para docs/: $doc_file"
            mv "$doc_file" docs/
            found_docs=true
        fi
    fi
done

if [ "$found_docs" = false ]; then
    echo "   ✅ Apenas documentos essenciais na raiz"
fi

# ============================================
# 5. Verificar Arquivos de Configuração Soltos
# ============================================

echo ""
echo "⚙️ Verificando configurações soltas..."

found_configs=false
for config_pattern in "*.json" "*.yaml" "*.yml" "*.toml" "*.ini" "*.cfg"; do
    for config_file in $config_pattern; do
        if [ -f "$config_file" ]; then
            # Verificar se é essencial (como sonar-project.properties já está na lista)
            is_essential=false
            for essential in "${essential_files[@]}"; do
                if [ "$config_file" = "$essential" ]; then
                    is_essential=true
                    break
                fi
            done
            
            # Alguns arquivos de config que podem ficar na raiz
            root_configs=("package.json" "pyproject.toml" "Pipfile" "docker-compose.yml")
            for root_config in "${root_configs[@]}"; do
                if [ "$config_file" = "$root_config" ]; then
                    is_essential=true
                    break
                fi
            done
            
            if [ "$is_essential" = false ]; then
                echo "   📁 Configuração encontrada: $config_file"
                echo "      ⚙️ Movendo para shared/config/: $config_file"
                mv "$config_file" shared/config/
                found_configs=true
            fi
        fi
    done
done

if [ "$found_configs" = false ]; then
    echo "   ✅ Apenas configurações essenciais na raiz"
fi

# ============================================
# 6. Verificar Outros Arquivos Soltos
# ============================================

echo ""
echo "🔍 Verificando outros arquivos soltos..."

# Lista de extensões que não devem estar na raiz (exceto essenciais)
unwanted_patterns=("*.tmp" "*.temp" "*.bak" "*.old" "*.orig" "*.swp" "*.swo" "*~")

found_unwanted=false
for pattern in "${unwanted_patterns[@]}"; do
    for unwanted_file in $pattern; do
        if [ -f "$unwanted_file" ]; then
            echo "   🗑️ Removendo arquivo temporário: $unwanted_file"
            rm "$unwanted_file"
            found_unwanted=true
        fi
    done
done

if [ "$found_unwanted" = false ]; then
    echo "   ✅ Nenhum arquivo temporário encontrado"
fi

# ============================================
# 7. Relatório Final da Raiz
# ============================================

echo ""
echo "📊 RELATÓRIO FINAL DA RAIZ"
echo "=========================="

echo ""
echo "📁 Arquivos na raiz após limpeza:"
ls -la | grep -v '^d' | tail -n +2 | while read -r line; do
    filename=$(echo "$line" | awk '{print $9}')
    if [ -n "$filename" ] && [ "$filename" != "." ] && [ "$filename" != ".." ]; then
        echo "   📄 $filename"
    fi
done

echo ""
echo "📊 Estatísticas:"
total_files=$(ls -la | grep -v '^d' | wc -l)
total_files=$((total_files - 1))  # Remove header
echo "   • Total de arquivos na raiz: $total_files"

essential_count=0
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        essential_count=$((essential_count + 1))
    fi
done
echo "   • Arquivos essenciais presentes: $essential_count"

if [ $total_files -le 10 ]; then
    echo "   ✅ Raiz limpa e organizada!"
else
    echo "   ⚠️ Ainda há muitos arquivos na raiz ($total_files)"
fi

echo ""
echo "🎯 ESTRUTURA IDEAL DA RAIZ:"
echo "=========================="
cat << 'EOF'
AI-powered-org-automation-suite/
├── 📄 README.md              # Documentação principal
├── 🤝 CONTRIBUTING.md        # Guia de contribuição
├── 📋 GOVERNANCE.md          # Governança do projeto
├── 🛠️ SETUP.md               # Guia de instalação
├── 📦 requirements.txt       # Dependências Python
├── 🔧 setup.py               # Configuração do pacote
├── 🚫 .gitignore             # Arquivos ignorados pelo Git
├── ⚙️ .gitattributes         # Atributos do Git
├── 📊 sonar-project.properties # Configuração SonarQube
└── 📜 LICENSE                # Licença (se aplicável)

TOTAL: ≤ 10 arquivos essenciais apenas!
EOF

echo ""
echo "✅ Limpeza da raiz concluída!"
echo "🚀 Repositório enterprise-grade com raiz limpa!"