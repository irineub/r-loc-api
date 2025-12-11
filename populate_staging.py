#!/usr/bin/env python3
"""
Script para popular o ambiente de staging com dados realistas
"""
import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

# URL da API de staging
API_URL = "https://srv938431.hstgr.cloud/api"

# Dados realistas para geração
CLIENTES_PF = [
    {"nome": "João Silva", "cpf": "123.456.789-00", "rg": "12.345.678-9", "email": "joao.silva@email.com", "telefone": "(11) 98765-4321"},
    {"nome": "Maria Santos", "cpf": "234.567.890-11", "rg": "23.456.789-0", "email": "maria.santos@email.com", "telefone": "(11) 97654-3210"},
    {"nome": "Pedro Oliveira", "cpf": "345.678.901-22", "rg": "34.567.890-1", "email": "pedro.oliveira@email.com", "telefone": "(11) 96543-2109"},
    {"nome": "Ana Costa", "cpf": "456.789.012-33", "rg": "45.678.901-2", "email": "ana.costa@email.com", "telefone": "(11) 95432-1098"},
    {"nome": "Carlos Ferreira", "cpf": "567.890.123-44", "rg": "56.789.012-3", "email": "carlos.ferreira@email.com", "telefone": "(11) 94321-0987"},
    {"nome": "Juliana Alves", "cpf": "678.901.234-55", "rg": "67.890.123-4", "email": "juliana.alves@email.com", "telefone": "(11) 93210-9876"},
    {"nome": "Roberto Lima", "cpf": "789.012.345-66", "rg": "78.901.234-5", "email": "roberto.lima@email.com", "telefone": "(11) 92109-8765"},
    {"nome": "Fernanda Rocha", "cpf": "890.123.456-77", "rg": "89.012.345-6", "email": "fernanda.rocha@email.com", "telefone": "(11) 91098-7654"},
]

CLIENTES_PJ = [
    {"nome": "Construtora ABC Ltda", "cnpj": "12.345.678/0001-90", "ie": "123.456.789.012", "email": "contato@abc.com.br", "telefone": "(11) 3456-7890"},
    {"nome": "Engenharia XYZ S.A.", "cnpj": "23.456.789/0001-01", "ie": "234.567.890.123", "email": "contato@xyz.com.br", "telefone": "(11) 3456-7891"},
    {"nome": "Construções Modernas EIRELI", "cnpj": "34.567.890/0001-12", "ie": "345.678.901.234", "email": "contato@modernas.com.br", "telefone": "(11) 3456-7892"},
    {"nome": "Obras e Construções Silva", "cnpj": "45.678.901/0001-23", "ie": "456.789.012.345", "email": "contato@obras.com.br", "telefone": "(11) 3456-7893"},
    {"nome": "Construtora Horizonte", "cnpj": "56.789.012/0001-34", "ie": "567.890.123.456", "email": "contato@horizonte.com.br", "telefone": "(11) 3456-7894"},
    {"nome": "Infraestrutura Brasil", "cnpj": "67.890.123/0001-45", "ie": "678.901.234.567", "email": "contato@infra.com.br", "telefone": "(11) 3456-7895"},
    {"nome": "Construções Rápidas", "cnpj": "78.901.234/0001-56", "ie": "789.012.345.678", "email": "contato@rapidas.com.br", "telefone": "(11) 3456-7896"},
    {"nome": "Engenharia e Projetos", "cnpj": "89.012.345/0001-67", "ie": "890.123.456.789", "email": "contato@engenharia.com.br", "telefone": "(11) 3456-7897"},
]

EQUIPAMENTOS = [
    {"descricao": "Betoneira 400L", "unidade": "UN", "preco": 120.0, "estoque": 15},
    {"descricao": "Betoneira 500L", "unidade": "UN", "preco": 150.0, "estoque": 10},
    {"descricao": "Guincho Elétrico 1 Ton", "unidade": "UN", "preco": 200.0, "estoque": 8},
    {"descricao": "Guincho Elétrico 2 Ton", "unidade": "UN", "preco": 280.0, "estoque": 6},
    {"descricao": "Gerador 15 KVA", "unidade": "UN", "preco": 350.0, "estoque": 12},
    {"descricao": "Gerador 30 KVA", "unidade": "UN", "preco": 500.0, "estoque": 8},
    {"descricao": "Andaime Tubular 2x1m", "unidade": "M²", "preco": 8.0, "estoque": 500},
    {"descricao": "Escora Metálica", "unidade": "UN", "preco": 25.0, "estoque": 200},
    {"descricao": "Cimbramento", "unidade": "M²", "preco": 12.0, "estoque": 300},
    {"descricao": "Fôrma de Madeira", "unidade": "M²", "preco": 15.0, "estoque": 400},
    {"descricao": "Rolo Compactador", "unidade": "UN", "preco": 400.0, "estoque": 5},
    {"descricao": "Cortadora de Piso", "unidade": "UN", "preco": 80.0, "estoque": 15},
    {"descricao": "Furadeira de Impacto", "unidade": "UN", "preco": 45.0, "estoque": 30},
    {"descricao": "Serra Circular", "unidade": "UN", "preco": 60.0, "estoque": 20},
    {"descricao": "Martelete Demolidor", "unidade": "UN", "preco": 180.0, "estoque": 10},
    {"descricao": "Plataforma Elevatória 12m", "unidade": "UN", "preco": 600.0, "estoque": 4},
    {"descricao": "Plataforma Elevatória 18m", "unidade": "UN", "preco": 850.0, "estoque": 3},
    {"descricao": "Caminhão Munck", "unidade": "UN", "preco": 1200.0, "estoque": 2},
    {"descricao": "Retroescavadeira", "unidade": "UN", "preco": 1500.0, "estoque": 2},
    {"descricao": "Bobcat", "unidade": "UN", "preco": 800.0, "estoque": 3},
]

FUNCIONARIOS = [
    {"username": "joao.operador", "nome": "João Operador", "senha": "1234"},
    {"username": "maria.vendas", "nome": "Maria Vendas", "senha": "1234"},
    {"username": "pedro.gerente", "nome": "Pedro Gerente", "senha": "1234"},
    {"username": "ana.administrativo", "nome": "Ana Administrativo", "senha": "1234"},
    {"username": "carlos.estoque", "nome": "Carlos Estoque", "senha": "1234"},
]

def criar_cliente_pf(dados: Dict) -> Dict:
    """Cria um cliente pessoa física"""
    return {
        "nome_razao_social": dados["nome"],
        "tipo_pessoa": "fisica",
        "cpf": dados["cpf"],
        "rg": dados["rg"],
        "email": dados["email"],
        "telefone_celular": dados["telefone"],
        "endereco": f"Rua {random.randint(1, 999)}, Bairro Centro, São Paulo - SP",
    }

def criar_cliente_pj(dados: Dict) -> Dict:
    """Cria um cliente pessoa jurídica"""
    return {
        "nome_razao_social": dados["nome"],
        "tipo_pessoa": "juridica",
        "cnpj": dados["cnpj"],
        "inscricao_estadual": dados["ie"],
        "email": dados["email"],
        "telefone_comercial": dados["telefone"],
        "endereco": f"Av. {random.choice(['Paulista', 'Faria Lima', 'Brigadeiro', '9 de Julho'])}, {random.randint(100, 9999)}, São Paulo - SP",
    }

def criar_equipamento(dados: Dict) -> Dict:
    """Cria um equipamento"""
    return {
        "descricao": dados["descricao"],
        "unidade": dados["unidade"],
        "preco_unitario": dados["preco"],
        "estoque": dados["estoque"],
        "estoque_alugado": random.randint(0, dados["estoque"] // 3),
    }

def criar_funcionario(dados: Dict) -> Dict:
    """Cria um funcionário"""
    return {
        "username": dados["username"],
        "nome": dados["nome"],
        "senha": dados["senha"],
        "ativo": True,
    }

def criar_orcamento(cliente_id: int, equipamentos_ids: List[int], funcionario_username: str) -> Dict:
    """Cria um orçamento realista"""
    data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
    data_fim = data_inicio + timedelta(days=random.randint(5, 30))
    dias = (data_fim - data_inicio).days
    
    itens = []
    total = 0.0
    
    num_itens = random.randint(1, 5)
    equipamentos_selecionados = random.sample(equipamentos_ids, min(num_itens, len(equipamentos_ids)))
    
    for equip_id in equipamentos_selecionados:
        quantidade = random.randint(1, 3)
        preco = random.uniform(50, 500)
        subtotal = quantidade * preco * dias
        total += subtotal
        
        itens.append({
            "equipamento_id": equip_id,
            "quantidade": quantidade,
            "preco_unitario": preco,
            "dias": dias,
            "tipo_cobranca": random.choice(["diaria", "mensal"]),
            "subtotal": subtotal,
        })
    
    desconto = random.choice([0, 0, 0, 0.05, 0.1])  # 80% sem desconto, 20% com desconto
    frete = random.choice([0, 0, 0, 100, 200, 300])  # 60% sem frete
    
    total_final = total * (1 - desconto) + frete
    
    return {
        "cliente_id": cliente_id,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "desconto": total * desconto,
        "frete": frete,
        "total_final": total_final,
        "observacoes": random.choice([
            "Orçamento para obra residencial",
            "Orçamento para obra comercial",
            "Orçamento para reforma",
            "Orçamento para construção nova",
            "Orçamento urgente",
            None,
        ]),
        "itens": itens,
    }, funcionario_username

def popular_dados():
    """Função principal para popular o banco"""
    print("🚀 Iniciando popularização do ambiente de staging...")
    print(f"📡 Conectando em: {API_URL}\n")
    
    clientes_criados = []
    equipamentos_criados = []
    funcionarios_criados = []
    orcamentos_criados = []
    locacoes_criadas = []
    
    # 1. Criar Funcionários
    print("👨‍💼 Criando funcionários...")
    for func_data in FUNCIONARIOS:
        try:
            response = requests.post(
                f"{API_URL}/funcionarios/",
                json=criar_funcionario(func_data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                func = response.json()
                funcionarios_criados.append(func)
                print(f"  ✅ {func['nome']} ({func['username']})")
            else:
                print(f"  ❌ Erro ao criar {func_data['nome']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar {func_data['nome']}: {e}")
    
    print(f"\n✅ {len(funcionarios_criados)} funcionários criados\n")
    
    # 2. Criar Clientes PF
    print("👥 Criando clientes (Pessoa Física)...")
    for cliente_data in CLIENTES_PF:
        try:
            response = requests.post(
                f"{API_URL}/clientes/",
                json=criar_cliente_pf(cliente_data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                cliente = response.json()
                clientes_criados.append(cliente)
                print(f"  ✅ {cliente['nome_razao_social']}")
            else:
                print(f"  ❌ Erro ao criar {cliente_data['nome']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar {cliente_data['nome']}: {e}")
    
    # 3. Criar Clientes PJ
    print("\n🏢 Criando clientes (Pessoa Jurídica)...")
    for cliente_data in CLIENTES_PJ:
        try:
            response = requests.post(
                f"{API_URL}/clientes/",
                json=criar_cliente_pj(cliente_data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                cliente = response.json()
                clientes_criados.append(cliente)
                print(f"  ✅ {cliente['nome_razao_social']}")
            else:
                print(f"  ❌ Erro ao criar {cliente_data['nome']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar {cliente_data['nome']}: {e}")
    
    print(f"\n✅ {len(clientes_criados)} clientes criados\n")
    
    # 4. Criar Equipamentos
    print("🔧 Criando equipamentos...")
    for equip_data in EQUIPAMENTOS:
        try:
            response = requests.post(
                f"{API_URL}/equipamentos/",
                json=criar_equipamento(equip_data),
                timeout=10
            )
            if response.status_code in [200, 201]:
                equip = response.json()
                equipamentos_criados.append(equip)
                print(f"  ✅ {equip['descricao']} - R$ {equip['preco_unitario']:.2f}")
            else:
                print(f"  ❌ Erro ao criar {equip_data['descricao']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar {equip_data['descricao']}: {e}")
    
    print(f"\n✅ {len(equipamentos_criados)} equipamentos criados\n")
    
    if not equipamentos_criados or not clientes_criados or not funcionarios_criados:
        print("❌ Não foi possível criar dados suficientes. Abortando criação de orçamentos.")
        return
    
    equipamentos_ids = [e["id"] for e in equipamentos_criados]
    
    # 5. Criar Orçamentos
    print("📋 Criando orçamentos...")
    for i in range(30):  # Criar 30 orçamentos
        cliente = random.choice(clientes_criados)
        funcionario = random.choice(funcionarios_criados)
        
        try:
            orcamento_data, func_username = criar_orcamento(
                cliente["id"],
                equipamentos_ids,
                funcionario["username"]
            )
            
            response = requests.post(
                f"{API_URL}/orcamentos/",
                json=orcamento_data,
                headers={"X-Funcionario-Username": func_username},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                orcamento = response.json()
                orcamentos_criados.append(orcamento)
                
                # Aprovar/rejeitar alguns orçamentos
                if random.random() < 0.6:  # 60% de chance de aprovar
                    aprovar_response = requests.post(
                        f"{API_URL}/orcamentos/{orcamento['id']}/aprovar",
                        headers={"X-Funcionario-Username": func_username},
                        timeout=10
                    )
                    if aprovar_response.status_code == 200:
                        orcamento["status"] = "aprovado"
                        print(f"  ✅ Orçamento #{orcamento['id']} criado e aprovado para {cliente['nome_razao_social']}")
                    else:
                        print(f"  ✅ Orçamento #{orcamento['id']} criado para {cliente['nome_razao_social']}")
                elif random.random() < 0.2:  # 20% de chance de rejeitar
                    requests.post(
                        f"{API_URL}/orcamentos/{orcamento['id']}/rejeitar",
                        headers={"X-Funcionario-Username": func_username},
                        timeout=10
                    )
                    print(f"  ✅ Orçamento #{orcamento['id']} criado e rejeitado para {cliente['nome_razao_social']}")
                else:
                    print(f"  ✅ Orçamento #{orcamento['id']} criado (pendente) para {cliente['nome_razao_social']}")
            else:
                print(f"  ❌ Erro ao criar orçamento: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar orçamento: {e}")
    
    print(f"\n✅ {len(orcamentos_criados)} orçamentos criados\n")
    
    # 6. Criar Locações a partir de orçamentos aprovados
    print("📦 Criando locações...")
    orcamentos_aprovados = [o for o in orcamentos_criados if o.get("status") == "aprovado"]
    
    for orcamento in orcamentos_aprovados[:15]:  # Criar até 15 locações
        funcionario = random.choice(funcionarios_criados)
        
        try:
            response = requests.post(
                f"{API_URL}/locacoes/from-orcamento/{orcamento['id']}",
                headers={"X-Funcionario-Username": funcionario["username"]},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                locacao = response.json()["locacao"]
                locacoes_criadas.append(locacao)
                
                # Finalizar algumas locações
                if random.random() < 0.3:  # 30% de chance de finalizar
                    requests.post(
                        f"{API_URL}/locacoes/{locacao['id']}/finalizar",
                        headers={"X-Funcionario-Username": funcionario["username"]},
                        timeout=10
                    )
                    print(f"  ✅ Locação #{locacao['id']} criada e finalizada")
                else:
                    print(f"  ✅ Locação #{locacao['id']} criada")
            else:
                print(f"  ❌ Erro ao criar locação do orçamento {orcamento['id']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Erro ao criar locação: {e}")
    
    print(f"\n✅ {len(locacoes_criadas)} locações criadas\n")
    
    # Resumo final
    print("=" * 60)
    print("📊 RESUMO DA POPULARIZAÇÃO")
    print("=" * 60)
    print(f"👨‍💼 Funcionários: {len(funcionarios_criados)}")
    print(f"👥 Clientes: {len(clientes_criados)}")
    print(f"🔧 Equipamentos: {len(equipamentos_criados)}")
    print(f"📋 Orçamentos: {len(orcamentos_criados)}")
    print(f"📦 Locações: {len(locacoes_criadas)}")
    print("=" * 60)
    print("✅ Popularização concluída com sucesso!")
    print(f"🌐 Acesse: https://srv938431.hstgr.cloud/")

if __name__ == "__main__":
    popular_dados()

