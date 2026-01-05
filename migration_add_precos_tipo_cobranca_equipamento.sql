-- Migration para adicionar campos de preço por tipo de cobrança na tabela equipamentos
-- Execute este script no banco de dados

-- Para SQLite, adicionar novas colunas
ALTER TABLE equipamentos ADD COLUMN preco_diaria REAL;
ALTER TABLE equipamentos ADD COLUMN preco_semanal REAL;
ALTER TABLE equipamentos ADD COLUMN preco_quinzenal REAL;
ALTER TABLE equipamentos ADD COLUMN preco_mensal REAL;

-- Migrar dados existentes: copiar preco_unitario para todos os novos campos
UPDATE equipamentos 
SET 
  preco_diaria = COALESCE(preco_unitario, 0),
  preco_semanal = COALESCE(preco_unitario * 7, 0),
  preco_quinzenal = COALESCE(preco_unitario * 15, 0),
  preco_mensal = COALESCE(preco_unitario * 30, 0)
WHERE preco_diaria IS NULL;

-- Para SQLite, não podemos fazer NOT NULL diretamente, então fazemos isso manualmente
-- Ou você pode recriar a tabela. Para produção com PostgreSQL, use:

-- Para PostgreSQL (comentado para referência futura):
-- ALTER TABLE equipamentos ADD COLUMN preco_diaria REAL NOT NULL DEFAULT 0;
-- ALTER TABLE equipamentos ADD COLUMN preco_semanal REAL NOT NULL DEFAULT 0;
-- ALTER TABLE equipamentos ADD COLUMN preco_quinzenal REAL NOT NULL DEFAULT 0;
-- ALTER TABLE equipamentos ADD COLUMN preco_mensal REAL NOT NULL DEFAULT 0;
-- 
-- UPDATE equipamentos 
-- SET 
--   preco_diaria = COALESCE(preco_unitario, 0),
--   preco_semanal = COALESCE(preco_unitario * 7, 0),
--   preco_quinzenal = COALESCE(preco_unitario * 15, 0),
--   preco_mensal = COALESCE(preco_unitario * 30, 0);
--
-- ALTER TABLE equipamentos DROP COLUMN preco_unitario;

