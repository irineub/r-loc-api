-- Migration para adicionar coluna endereco_entrega na tabela locacoes
-- Execute este script no banco de dados

-- Para SQLite
ALTER TABLE locacoes ADD COLUMN endereco_entrega TEXT;

-- Para PostgreSQL (comentado - use apenas se necessário)
-- ALTER TABLE locacoes ADD COLUMN endereco_entrega TEXT;

