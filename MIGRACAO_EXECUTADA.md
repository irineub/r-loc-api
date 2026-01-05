# Migração de Preços por Tipo de Cobrança - EXECUTADA

## Data da Execução
Executada em: $(date)

## O que foi feito

1. **Adicionadas novas colunas na tabela equipamentos:**
   - `preco_diaria` (REAL)
   - `preco_semanal` (REAL)
   - `preco_quinzenal` (REAL)
   - `preco_mensal` (REAL)

2. **Migração de dados existentes:**
   - Todos os equipamentos existentes tiveram seus preços migrados:
     - `preco_diaria` = valor do `preco_unitario` antigo
     - `preco_semanal` = `preco_unitario * 7 * 0.9` (10% desconto)
     - `preco_quinzenal` = `preco_unitario * 15 * 0.85` (15% desconto)
     - `preco_mensal` = `preco_unitario * 30 * 0.8` (20% desconto)

3. **Coluna antiga mantida:**
   - A coluna `preco_unitario` foi mantida para compatibilidade, mas não deve ser usada em novos cadastros

## Status
✅ Migração executada com sucesso
✅ Dados migrados corretamente
✅ API retornando dados com novos campos

## Próximos Passos (Opcional)
- Após validar que tudo está funcionando, pode-se considerar remover a coluna `preco_unitario` em uma migração futura

