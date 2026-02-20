-- Adicionar colunas de data_inicio e data_fim para itens de orçamento
ALTER TABLE itens_orcamento ADD COLUMN data_inicio TIMESTAMP;
ALTER TABLE itens_orcamento ADD COLUMN data_fim TIMESTAMP;

-- Adicionar colunas de data_inicio e data_fim para itens de locação
ALTER TABLE itens_locacao ADD COLUMN data_inicio TIMESTAMP;
ALTER TABLE itens_locacao ADD COLUMN data_fim TIMESTAMP;
