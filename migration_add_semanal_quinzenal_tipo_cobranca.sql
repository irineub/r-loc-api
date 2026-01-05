-- Migration para adicionar 'semanal' e 'quinzenal' ao enum tipo_cobranca_item
-- Execute este script no banco de dados PostgreSQL

-- Adicionar novos valores ao enum tipo_cobranca_item
DO $$
BEGIN
    -- Adicionar 'semanal' se não existir
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'semanal' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipo_cobranca_item')) THEN
        ALTER TYPE tipo_cobranca_item ADD VALUE 'semanal';
        RAISE NOTICE 'Valor ''semanal'' adicionado ao enum tipo_cobranca_item';
    ELSE
        RAISE NOTICE 'Valor ''semanal'' já existe no enum tipo_cobranca_item';
    END IF;

    -- Adicionar 'quinzenal' se não existir
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'quinzenal' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tipo_cobranca_item')) THEN
        ALTER TYPE tipo_cobranca_item ADD VALUE 'quinzenal';
        RAISE NOTICE 'Valor ''quinzenal'' adicionado ao enum tipo_cobranca_item';
    ELSE
        RAISE NOTICE 'Valor ''quinzenal'' já existe no enum tipo_cobranca_item';
    END IF;
END $$;

COMMENT ON TYPE tipo_cobranca_item IS 'Tipo de cobrança do item: diaria, semanal, quinzenal ou mensal';

