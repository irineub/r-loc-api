-- Migration para adicionar campo tipo_cobranca na tabela orcamentos
-- Execute este script no banco de dados PostgreSQL

-- Adicionar coluna tipo_cobranca na tabela orcamentos
ALTER TABLE orcamentos 
ADD COLUMN tipo_cobranca VARCHAR(10) NOT NULL DEFAULT 'diaria';

-- Criar enum para tipo_cobranca se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_cobranca_orcamento') THEN
        CREATE TYPE tipo_cobranca_orcamento AS ENUM ('diaria', 'mensal');
    END IF;
END $$;

-- Alterar a coluna para usar o enum
ALTER TABLE orcamentos 
ALTER COLUMN tipo_cobranca TYPE tipo_cobranca_orcamento USING tipo_cobranca::tipo_cobranca_orcamento;

-- Comentário na coluna
COMMENT ON COLUMN orcamentos.tipo_cobranca IS 'Tipo de cobrança do orçamento: diaria ou mensal'; 