#!/bin/bash

# Script de Deploy - Perfil GitHub Eric Ribeiro
# Autor: Eric Ribeiro

echo "🚀 Iniciando deploy do perfil GitHub..."

# Adiciona todos os arquivos
git add .

# Verifica se há mudanças para commit
if git diff --staged --quiet; then
    echo "⚠️  Nenhuma mudança detectada para commit."
    exit 0
fi

# Solicita mensagem de commit ou usa uma padrão
if [ "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="✨ Atualização do perfil GitHub"
fi

echo "📝 Commitando mudanças: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push para o repositório
echo "📤 Fazendo push para o GitHub..."
git push origin main

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: https://github.com/ericvasr"
