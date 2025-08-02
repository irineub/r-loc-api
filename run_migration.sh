#!/bin/bash

# Script para executar migração do banco de dados
# Execute este script para adicionar o campo tipo_cobranca na tabela itens_orcamento

echo "Executando migração para adicionar campo tipo_cobranca na tabela itens_orcamento..."

# Verificar se o arquivo de migração existe
if [ ! -f "migration_add_tipo_cobranca_item.sql" ]; then
    echo "Erro: Arquivo de migração não encontrado!"
    exit 1
fi

# Executar a migração
# Substitua as variáveis de ambiente conforme necessário
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f migration_add_tipo_cobranca_item.sql

echo "Migração executada com sucesso!"
echo "Campo tipo_cobranca adicionado na tabela itens_orcamento." 