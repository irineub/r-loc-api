-- Migration para adicionar campo tipo_cobranca na tabela itens_orcamento
-- Execute este script no banco de dados PostgreSQL

-- Adicionar coluna tipo_cobranca na tabela itens_orcamento
ALTER TABLE itens_orcamento 
ADD COLUMN tipo_cobranca VARCHAR(10) NOT NULL DEFAULT 'diaria';

-- Criar enum para tipo_cobranca_item se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_cobranca_item') THEN
        CREATE TYPE tipo_cobranca_item AS ENUM ('diaria', 'mensal');
    END IF;
END $$;

-- Alterar a coluna para usar o enum
ALTER TABLE itens_orcamento 
ALTER COLUMN tipo_cobranca TYPE tipo_cobranca_item USING tipo_cobranca::tipo_cobranca_item;

-- Comentário na coluna
COMMENT ON COLUMN itens_orcamento.tipo_cobranca IS 'Tipo de cobrança do item: diaria ou mensal';

-- Remover coluna tipo_cobranca da tabela orcamentos se existir
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'orcamentos' AND column_name = 'tipo_cobranca') THEN
        ALTER TABLE orcamentos DROP COLUMN tipo_cobranca;
    END IF;
END $$; 