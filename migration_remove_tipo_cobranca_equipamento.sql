-- Migração para remover o campo tipo_cobranca da tabela equipamentos
-- Este campo foi movido para a tabela itens_orcamento conforme documentado em CORRECOES_ORCAMENTO.md

-- Verificar se a coluna existe antes de tentar removê-la
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'equipamentos' 
        AND column_name = 'tipo_cobranca'
    ) THEN
        ALTER TABLE equipamentos DROP COLUMN tipo_cobranca;
        RAISE NOTICE 'Coluna tipo_cobranca removida da tabela equipamentos';
    ELSE
        RAISE NOTICE 'Coluna tipo_cobranca não existe na tabela equipamentos';
    END IF;
END $$;

-- Verificar se o enum tipo_cobranca ainda é usado em outras tabelas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE column_name = 'tipo_cobranca'
    ) THEN
        DROP TYPE IF EXISTS tipo_cobranca;
        RAISE NOTICE 'Enum tipo_cobranca removido pois não é mais usado';
    ELSE
        RAISE NOTICE 'Enum tipo_cobranca mantido pois ainda é usado em outras tabelas';
    END IF;
END $$; 