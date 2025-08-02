# R-Loc API - Sistema de Locação de Equipamentos

## 📋 Descrição
API REST para o sistema de locação de equipamentos de construção civil, desenvolvida com FastAPI e SQLite.

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- pip

### Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar a aplicação
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Acesso
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

## 📚 Endpoints

### Clientes (`/api/clientes`)
- `POST /` - Criar cliente
- `GET /` - Listar clientes
- `GET /{id}` - Buscar cliente por ID
- `PUT /{id}` - Atualizar cliente
- `DELETE /{id}` - Deletar cliente

### Equipamentos (`/api/equipamentos`)
- `POST /` - Criar equipamento
- `GET /` - Listar equipamentos
- `GET /{id}` - Buscar equipamento por ID
- `PUT /{id}` - Atualizar equipamento
- `DELETE /{id}` - Deletar equipamento

### Orçamentos (`/api/orcamentos`)
- `POST /` - Criar orçamento
- `GET /` - Listar orçamentos
- `GET /{id}` - Buscar orçamento por ID
- `PUT /{id}` - Atualizar orçamento
- `POST /{id}/aprovar` - Aprovar orçamento
- `POST /{id}/rejeitar` - Rejeitar orçamento
- `GET /pendentes/` - Listar orçamentos pendentes
- `GET /aprovados/` - Listar orçamentos aprovados

### Locações (`/api/locacoes`)
- `POST /` - Criar locação
- `GET /` - Listar locações
- `GET /{id}` - Buscar locação por ID
- `PUT /{id}` - Atualizar locação
- `POST /{id}/finalizar` - Finalizar locação
- `POST /{id}/cancelar` - Cancelar locação
- `GET /ativas/` - Listar locações ativas
- `GET /atrasadas/` - Listar locações atrasadas
- `POST /from-orcamento/{id}` - Criar locação a partir de orçamento

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais
- **clientes**: Cadastro de clientes (pessoa física/jurídica)
- **equipamentos**: Catálogo de equipamentos disponíveis
- **orcamentos**: Orçamentos de locação
- **itens_orcamento**: Itens de cada orçamento
- **locacoes**: Contratos de locação ativos
- **itens_locacao**: Itens de cada locação

### Relacionamentos
- Cliente → Orçamentos (1:N)
- Orçamento → Itens (1:N)
- Orçamento → Locação (1:1)
- Locação → Itens (1:N)

## 🔧 Configuração

### Variáveis de Ambiente
O sistema usa SQLite por padrão. Para produção, considere:
- Configurar PostgreSQL ou MySQL
- Definir variáveis de ambiente para conexão
- Configurar CORS adequadamente

### CORS
Configurado para aceitar requisições do frontend Angular (localhost:4200).

## 📊 Status dos Orçamentos
- `pendente`: Aguardando aprovação
- `aprovado`: Aprovado pelo cliente
- `rejeitado`: Rejeitado pelo cliente

## 📊 Status das Locações
- `ativa`: Locação em andamento
- `finalizada`: Locação concluída
- `cancelada`: Locação cancelada
- `atrasada`: Locação em atraso

## 🧪 Testes
```bash
# Executar testes (quando implementados)
pytest
```

## 📝 Logs
Os logs são exibidos no console durante o desenvolvimento.
Para produção, configure logging adequado. 