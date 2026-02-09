#!/usr/bin/env python3
"""
Script para popular o ambiente de staging com dados realistas
"""
import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict

# URL da API (alterar para staging quando necessário)
API_URL = "http://137.131.201.11/api/api"
# API_URL = "https://srv938431.hstgr.cloud/api"
# Dados realistas para geração
CLIENTES_PF = [
    {"nome": "João Silva", "cpf": "123.456.789-00", "rg": "12.345.678-9", "email": "joao.silva@email.com", "telefone": "(92) 98765-4321"},
    {"nome": "Maria Santos", "cpf": "234.567.890-11", "rg": "23.456.789-0", "email": "maria.santos@email.com", "telefone": "(92) 97654-3210"},
    {"nome": "Pedro Oliveira", "cpf": "345.678.901-22", "rg": "34.567.890-1", "email": "pedro.oliveira@email.com", "telefone": "(92) 96543-2109"},
    {"nome": "Ana Costa", "cpf": "456.789.012-33", "rg": "45.678.901-2", "email": "ana.costa@email.com", "telefone": "(92) 95432-1098"},
    {"nome": "Carlos Ferreira", "cpf": "567.890.123-44", "rg": "56.789.012-3", "email": "carlos.ferreira@email.com", "telefone": "(92) 94321-0987"},
    {"nome": "Juliana Alves", "cpf": "678.901.234-55", "rg": "67.890.123-4", "email": "juliana.alves@email.com", "telefone": "(92) 93210-9876"},
    {"nome": "Roberto Lima", "cpf": "789.012.345-66", "rg": "78.901.234-5", "email": "roberto.lima@email.com", "telefone": "(92) 92109-8765"},
    {"nome": "Fernanda Rocha", "cpf": "890.123.456-77", "rg": "89.012.345-6", "email": "fernanda.rocha@email.com", "telefone": "(92) 91098-7654"},
    {"nome": "Rafael Souza", "cpf": "901.234.567-88", "rg": "90.123.456-7", "email": "rafael.souza@email.com", "telefone": "(92) 99988-7766"},
    {"nome": "Patricia Lima", "cpf": "012.345.678-99", "rg": "01.234.567-8", "email": "patricia.lima@email.com", "telefone": "(92) 98877-6655"},
]

CLIENTES_PJ = [
    {"nome": "Construtora ABC Ltda", "cnpj": "12.345.678/0001-90", "ie": "123.456.789.012", "email": "contato@abc.com.br", "telefone": "(92) 3456-7890"},
    {"nome": "Engenharia XYZ S.A.", "cnpj": "23.456.789/0001-01", "ie": "234.567.890.123", "email": "contato@xyz.com.br", "telefone": "(92) 3456-7891"},
    {"nome": "Construções Modernas EIRELI", "cnpj": "34.567.890/0001-12", "ie": "345.678.901.234", "email": "contato@modernas.com.br", "telefone": "(92) 3456-7892"},
    {"nome": "Obras e Construções Silva", "cnpj": "45.678.901/0001-23", "ie": "456.789.012.345", "email": "contato@obras.com.br", "telefone": "(92) 3456-7893"},
    {"nome": "Construtora Horizonte", "cnpj": "56.789.012/0001-34", "ie": "567.890.123.456", "email": "contato@horizonte.com.br", "telefone": "(92) 3456-7894"},
    {"nome": "Infraestrutura Brasil", "cnpj": "67.890.123/0001-45", "ie": "678.901.234.567", "email": "contato@infra.com.br", "telefone": "(92) 3456-7895"},
    {"nome": "Construções Rápidas", "cnpj": "78.901.234/0001-56", "ie": "789.012.345.678", "email": "contato@rapidas.com.br", "telefone": "(92) 3456-7896"},
    {"nome": "Engenharia e Projetos", "cnpj": "89.012.345/0001-67", "ie": "890.123.456.789", "email": "contato@engenharia.com.br", "telefone": "(92) 3456-7897"},
    {"nome": "Amazônia Construções", "cnpj": "90.123.456/0001-78", "ie": "901.234.567.890", "email": "contato@amazonia.com.br", "telefone": "(92) 3344-5566"},
    {"nome": "Rio Negro Obras", "cnpj": "01.234.567/0001-89", "ie": "012.345.678.901", "email": "contato@rionegro.com.br", "telefone": "(92) 3234-5678"},
]

EQUIPAMENTOS = [
    # Equipamentos com estoque alto (para uso geral)
    {"descricao": "Betoneira 400L", "unidade": "UN", "preco": 120.0, "estoque": 15},
    {"descricao": "Betoneira 500L", "unidade": "UN", "preco": 150.0, "estoque": 10},
    {"descricao": "Guincho Elétrico 1 Ton", "unidade": "UN", "preco": 200.0, "estoque": 8},
    {"descricao": "Guincho Elétrico 2 Ton", "unidade": "UN", "preco": 280.0, "estoque": 6},
    {"descricao": "Gerador 15 KVA", "unidade": "UN", "preco": 350.0, "estoque": 12},
    {"descricao": "Andaime Tubular 2x1m", "unidade": "M²", "preco": 8.0, "estoque": 500},
    {"descricao": "Escora Metálica", "unidade": "UN", "preco": 25.0, "estoque": 200},
    # Equipamentos com estoque BAIXO para testar validação
    {"descricao": "Gerador 30 KVA", "unidade": "UN", "preco": 500.0, "estoque": 1},  # Estoque baixo para testar
    {"descricao": "Rolo Compactador", "unidade": "UN", "preco": 400.0, "estoque": 2},  # Estoque baixo
    {"descricao": "Plataforma Elevatória 18m", "unidade": "UN", "preco": 850.0, "estoque": 2},  # Estoque baixo
]

FUNCIONARIOS = [
    {"username": "joao.operador", "nome": "João Operador", "senha": "1234"},
    {"username": "maria.vendas", "nome": "Maria Vendas", "senha": "1234"},
    {"username": "pedro.gerente", "nome": "Pedro Gerente", "senha": "1234"},
    {"username": "ana.administrativo", "nome": "Ana Administrativo", "senha": "1234"},
    {"username": "carlos.estoque", "nome": "Carlos Estoque", "senha": "1234"},
]

def criar_cliente_pf(dados: Dict) -> Dict:
    """Cria um cliente pessoa física com endereço de Manaus"""
    ruas_manaus = [
        "Av. Djalma Batista", "Av. Getúlio Vargas", "Av. Constantino Nery", 
        "Av. Torquato Tapajós", "Av. Eduardo Ribeiro", "Rua 10 de Julho",
        "Rua São Luís", "Rua Barroso", "Rua Ramos Ferreira", "Rua Recife",
        "Av. Tancredo Neves", "Av. Max Teixeira", "Rua José Clemente",
        "Rua Libertador", "Rua 24 de Maio", "Av. Paraíba"
    ]
    bairros_manaus = [
        "Centro", "Aleixo", "Adrianópolis", "Chapada", "Coroado",
        "São Raimundo", "Educandos", "Tarumã", "Ponta Negra", "Japiim",
        "Planalto", "Cidade Nova", "Alvorada", "Jorge Teixeira", "Compensa"
    ]
    return {
        "nome_razao_social": dados["nome"],
        "tipo_pessoa": "fisica",
        "cpf": dados["cpf"],
        "rg": dados["rg"],
        "email": dados["email"],
        "telefone_celular": dados["telefone"],
        "endereco": f"{random.choice(ruas_manaus)}, {random.randint(100, 9999)}, {random.choice(bairros_manaus)} - Manaus/AM",
    }

def criar_cliente_pj(dados: Dict) -> Dict:
    """Cria um cliente pessoa jurídica com endereço de Manaus"""
    avenidas_manaus = [
        "Av. Djalma Batista", "Av. Getúlio Vargas", "Av. Constantino Nery",
        "Av. Torquato Tapajós", "Av. Eduardo Ribeiro", "Av. Tancredo Neves",
        "Av. Max Teixeira", "Av. Paraíba", "Av. Umberto Calderaro",
        "Av. Dom Pedro I", "Av. Brasil", "Av. Autaz Mirim"
    ]
    bairros_manaus_pj = [
        "Centro", "Aleixo", "Adrianópolis", "Chapada", "Distrito Industrial",
        "Ponta Negra", "Cidade Nova", "Japiim", "Alvorada", "Compensa"
    ]
    return {
        "nome_razao_social": dados["nome"],
        "tipo_pessoa": "juridica",
        "cnpj": dados["cnpj"],
        "inscricao_estadual": dados["ie"],
        "email": dados["email"],
        "telefone_comercial": dados["telefone"],
        "endereco": f"{random.choice(avenidas_manaus)}, {random.randint(100, 9999)}, {random.choice(bairros_manaus_pj)} - Manaus/AM",
    }

def criar_equipamento(dados: Dict) -> Dict:
    """Cria um equipamento com preços por tipo de cobrança"""
    preco_base = dados["preco"]
    return {
        "descricao": dados["descricao"],
        "unidade": dados["unidade"],
        "preco_diaria": round(preco_base, 2),
        "preco_semanal": round(preco_base * 7 * 0.9, 2),  # 10% de desconto para semanal
        "preco_quinzenal": round(preco_base * 15 * 0.85, 2),  # 15% de desconto para quinzenal
        "preco_mensal": round(preco_base * 30 * 0.8, 2),  # 20% de desconto para mensal
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

def criar_orcamento(cliente_id: int, equipamentos_ids: List[int], funcionario_username: str, equipamentos_info: List[Dict] = None) -> Dict:
    """Cria um orçamento realista, respeitando estoque disponível"""
    data_inicio = datetime.now() + timedelta(days=random.randint(1, 30))
    data_fim = data_inicio + timedelta(days=random.randint(5, 30))
    dias = (data_fim - data_inicio).days
    
    itens = []
    total = 0.0
    
    # Criar um dicionário de equipamentos para consulta rápida
    equip_dict = {}
    if equipamentos_info:
        for equip in equipamentos_info:
            equip_dict[equip["id"]] = equip
    
    num_itens = random.randint(1, min(5, len(equipamentos_ids)))
    equipamentos_selecionados = random.sample(equipamentos_ids, num_itens)
    
    # Rastrear quantidades por equipamento para não exceder estoque
    quantidades_por_equip = {}
    
    for equip_id in equipamentos_selecionados:
        # Obter estoque disponível do equipamento
        estoque_disponivel = 999  # Default alto
        preco_base = random.uniform(50, 500)
        
        if equip_id in equip_dict:
            equip_info = equip_dict[equip_id]
            estoque_disponivel = equip_info.get("estoque", 999) - equip_info.get("estoque_alugado", 0)
            # Tentar usar o preço real do equipamento
            preco_base = equip_info.get("preco_diaria", preco_base)
        
        # Garantir que não exceda o estoque disponível
        max_quantidade = min(3, max(1, estoque_disponivel))
        quantidade = random.randint(1, max_quantidade)
        
        # Se já temos este equipamento no orçamento, somar
        if equip_id in quantidades_por_equip:
            quantidade_total = quantidades_por_equip[equip_id] + quantidade
            if quantidade_total > estoque_disponivel:
                quantidade = max(0, estoque_disponivel - quantidades_por_equip[equip_id])
            quantidades_por_equip[equip_id] += quantidade
        else:
            quantidades_por_equip[equip_id] = quantidade
        
        if quantidade > 0:
            subtotal = quantidade * preco_base * dias
            total += subtotal
            
            itens.append({
                "equipamento_id": equip_id,
                "quantidade": quantidade,
                "preco_unitario": preco_base,
                "dias": dias,
                "tipo_cobranca": random.choice(["diaria", "semanal", "quinzenal", "mensal"]),
                "subtotal": subtotal,
            })
    
    # Variar desconto e frete para testar diferentes cenários
    # 40% sem desconto, 30% com desconto pequeno, 20% com desconto médio, 10% com desconto grande
    desconto_percent = random.choice([0, 0, 0, 0, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15])
    desconto_valor = total * desconto_percent
    
    # 50% sem frete, 30% com frete baixo, 15% com frete médio, 5% com frete alto
    frete = random.choice([0, 0, 0, 0, 0, 50, 50, 50, 100, 100, 150, 200, 250, 300, 500])
    
    total_final = total - desconto_valor + frete
    
    return {
        "cliente_id": cliente_id,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "desconto": desconto_valor,
        "frete": frete,
        "total_final": max(0, total_final),  # Garantir que não seja negativo
        "observacoes": random.choice([
            "Orçamento para obra residencial",
            "Orçamento para obra comercial",
            "Orçamento para reforma",
            "Orçamento para construção nova",
            "Orçamento urgente",
            "Orçamento com desconto especial",
            "Orçamento com frete incluído",
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
    
    # 1. Criar ou buscar Funcionários
    print("👨‍💼 Criando ou buscando funcionários...")
    
    # Primeiro, tentar buscar funcionários existentes
    try:
        # Tentar buscar com usuário master (assumindo que existe "rloc" ou similar)
        response = requests.get(
            f"{API_URL}/funcionarios/",
            headers={"X-Funcionario-Username": "rloc"},
            timeout=10
        )
        if response.status_code == 200:
            funcionarios_existentes = response.json()
            if funcionarios_existentes:
                funcionarios_criados = funcionarios_existentes[:5]  # Usar até 5 existentes
                print(f"  ✅ Encontrados {len(funcionarios_criados)} funcionários existentes")
                for func in funcionarios_criados:
                    print(f"    - {func.get('nome', 'N/A')} ({func.get('username', 'N/A')})")
    except Exception as e:
        print(f"  ⚠️  Não foi possível buscar funcionários existentes: {e}")
    
    # Se não encontrou funcionários, tentar criar (requer autenticação master)
    if not funcionarios_criados:
        print("  📝 Tentando criar novos funcionários...")
        for func_data in FUNCIONARIOS:
            try:
                response = requests.post(
                    f"{API_URL}/funcionarios/",
                    json=criar_funcionario(func_data),
                    headers={"X-Funcionario-Username": "rloc"},  # Tentar com usuário master
                    timeout=10
                )
                if response.status_code in [200, 201]:
                    func = response.json()
                    funcionarios_criados.append(func)
                    print(f"  ✅ {func['nome']} ({func['username']})")
                else:
                    error_detail = ""
                    try:
                        error_detail = response.json().get('detail', '')
                    except Exception:
                        error_detail = response.text[:100]
                    print(f"  ❌ Erro ao criar {func_data['nome']}: {response.status_code} - {error_detail}")
            except Exception as e:
                print(f"  ❌ Erro ao criar {func_data['nome']}: {e}")
    
    # Se ainda não tem funcionários, usar um username padrão
    if not funcionarios_criados:
        print("  ⚠️  Nenhum funcionário encontrado ou criado.")
        print("  ℹ️  O script continuará usando 'rloc' como username padrão nos headers.")
        print("  ℹ️  Certifique-se de que existe um usuário 'rloc' no sistema ou ajuste o script.")
        # Criar um funcionário fictício para usar nos headers
        funcionarios_criados = [{"username": "rloc", "nome": "Sistema (rloc)", "id": 0}]
    
    print(f"\n✅ {len(funcionarios_criados)} funcionário(s) disponível(is) para uso\n")
    
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
            equip_payload = criar_equipamento(equip_data)
            response = requests.post(
                f"{API_URL}/equipamentos/",
                json=equip_payload,
                timeout=10
            )
            if response.status_code in [200, 201]:
                equip = response.json()
                equipamentos_criados.append(equip)
                print(f"  ✅ {equip['descricao']} - Diária: R$ {equip.get('preco_diaria', 0):.2f}")
            else:
                error_detail = ""
                try:
                    error_detail = response.json().get('detail', '')
                except Exception:
                    error_detail = response.text[:100]
                print(f"  ❌ Erro ao criar {equip_data['descricao']}: {response.status_code} - {error_detail}")
        except Exception as e:
            print(f"  ❌ Erro ao criar {equip_data['descricao']}: {e}")
    
    print(f"\n✅ {len(equipamentos_criados)} equipamentos criados\n")
    
    if not equipamentos_criados or not clientes_criados:
        print("❌ Não foi possível criar dados suficientes. Abortando criação de orçamentos.")
        return
    
    # Se não há funcionários, criar um funcionário padrão para usar nos headers
    if not funcionarios_criados:
        print("⚠️  Nenhum funcionário encontrado. Usando 'rloc' como padrão para headers.")
        funcionarios_criados = [{"username": "rloc", "nome": "Sistema", "id": 0}]
    
    equipamentos_ids = [e["id"] for e in equipamentos_criados]
    
    # 5. Criar Orçamentos com diferentes cenários para testar todas as funcionalidades
    print("📋 Criando orçamentos (testando desconto, frete, estoque, status)...")
    
    # Criar orçamentos pendentes (30%)
    print("\n  📝 Criando orçamentos PENDENTES (editáveis)...")
    for i in range(10):
        cliente = random.choice(clientes_criados)
        funcionario = random.choice(funcionarios_criados)
        
        try:
            orcamento_data, func_username = criar_orcamento(
                cliente["id"],
                equipamentos_ids,
                funcionario["username"],
                equipamentos_criados
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
                desc_frete = f" | Desconto: R$ {orcamento_data['desconto']:.2f}" if orcamento_data['desconto'] > 0 else ""
                desc_frete += f" | Frete: R$ {orcamento_data['frete']:.2f}" if orcamento_data['frete'] > 0 else ""
                print(f"  ✅ Orçamento #{orcamento['id']} (PENDENTE) para {cliente['nome_razao_social']}{desc_frete}")
            else:
                error_detail = ""
                try:
                    error_detail = response.json().get('detail', '')
                except Exception:
                    error_detail = response.text[:100]
                print(f"  ❌ Erro ao criar orçamento: {response.status_code} - {error_detail}")
        except Exception as e:
            print(f"  ❌ Erro ao criar orçamento: {e}")
    
    # Criar orçamentos aprovados SEM contrato (30%) - editáveis
    print("\n  ✅ Criando orçamentos APROVADOS (sem contrato, editáveis)...")
    for i in range(10):
        cliente = random.choice(clientes_criados)
        funcionario = random.choice(funcionarios_criados)
        
        try:
            orcamento_data, func_username = criar_orcamento(
                cliente["id"],
                equipamentos_ids,
                funcionario["username"],
                equipamentos_criados
            )
            
            response = requests.post(
                f"{API_URL}/orcamentos/",
                json=orcamento_data,
                headers={"X-Funcionario-Username": func_username},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                orcamento = response.json()
                
                # Aprovar o orçamento
                aprovar_response = requests.post(
                    f"{API_URL}/orcamentos/{orcamento['id']}/aprovar",
                    headers={"X-Funcionario-Username": func_username},
                    timeout=10
                )
                if aprovar_response.status_code == 200:
                    orcamento["status"] = "aprovado"
                    orcamentos_criados.append(orcamento)
                    desc_frete = f" | Desconto: R$ {orcamento_data['desconto']:.2f}" if orcamento_data['desconto'] > 0 else ""
                    desc_frete += f" | Frete: R$ {orcamento_data['frete']:.2f}" if orcamento_data['frete'] > 0 else ""
                    print(f"  ✅ Orçamento #{orcamento['id']} (APROVADO - sem contrato) para {cliente['nome_razao_social']}{desc_frete}")
        except Exception as e:
            print(f"  ❌ Erro ao criar orçamento: {e}")
    
    # Criar orçamentos rejeitados (20%) - editáveis (voltam a pendente ao editar)
    print("\n  ❌ Criando orçamentos REJEITADOS (editáveis, voltam a pendente)...")
    for i in range(10):
        cliente = random.choice(clientes_criados)
        funcionario = random.choice(funcionarios_criados)
        
        try:
            orcamento_data, func_username = criar_orcamento(
                cliente["id"],
                equipamentos_ids,
                funcionario["username"],
                equipamentos_criados
            )
            
            response = requests.post(
                f"{API_URL}/orcamentos/",
                json=orcamento_data,
                headers={"X-Funcionario-Username": func_username},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                orcamento = response.json()
                
                # Rejeitar o orçamento
                rejeitar_response = requests.post(
                    f"{API_URL}/orcamentos/{orcamento['id']}/rejeitar",
                    headers={"X-Funcionario-Username": func_username},
                    timeout=10
                )
                if rejeitar_response.status_code == 200:
                    orcamento["status"] = "rejeitado"
                    orcamentos_criados.append(orcamento)
                    desc_frete = f" | Desconto: R$ {orcamento_data['desconto']:.2f}" if orcamento_data['desconto'] > 0 else ""
                    desc_frete += f" | Frete: R$ {orcamento_data['frete']:.2f}" if orcamento_data['frete'] > 0 else ""
                    print(f"  ✅ Orçamento #{orcamento['id']} (REJEITADO - editável) para {cliente['nome_razao_social']}{desc_frete}")
        except Exception as e:
            print(f"  ❌ Erro ao criar orçamento: {e}")
    
    # Criar orçamentos aprovados COM contrato (20%) - NÃO editáveis
    print("\n  📦 Criando orçamentos APROVADOS (com contrato, NÃO editáveis)...")
    for i in range(10):
        cliente = random.choice(clientes_criados)
        funcionario = random.choice(funcionarios_criados)
        
        try:
            orcamento_data, func_username = criar_orcamento(
                cliente["id"],
                equipamentos_ids,
                funcionario["username"],
                equipamentos_criados
            )
            
            response = requests.post(
                f"{API_URL}/orcamentos/",
                json=orcamento_data,
                headers={"X-Funcionario-Username": func_username},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                orcamento = response.json()
                
                # Aprovar o orçamento
                aprovar_response = requests.post(
                    f"{API_URL}/orcamentos/{orcamento['id']}/aprovar",
                    headers={"X-Funcionario-Username": func_username},
                    timeout=10
                )
                if aprovar_response.status_code == 200:
                    orcamento["status"] = "aprovado"
                    orcamentos_criados.append(orcamento)
                    desc_frete = f" | Desconto: R$ {orcamento_data['desconto']:.2f}" if orcamento_data['desconto'] > 0 else ""
                    desc_frete += f" | Frete: R$ {orcamento_data['frete']:.2f}" if orcamento_data['frete'] > 0 else ""
                    print(f"  ✅ Orçamento #{orcamento['id']} (APROVADO - será gerado contrato) para {cliente['nome_razao_social']}{desc_frete}")
        except Exception as e:
            print(f"  ❌ Erro ao criar orçamento: {e}")
    
    print(f"\n✅ {len(orcamentos_criados)} orçamentos criados\n")
    
    # 6. Criar Locações a partir de alguns orçamentos aprovados (para testar orçamentos não editáveis)
    print("\n📦 Criando locações (gerando contratos para alguns orçamentos aprovados)...")
    orcamentos_aprovados_sem_contrato = [o for o in orcamentos_criados if o.get("status") == "aprovado"]
    
    # Endereços de entrega em Manaus
    enderecos_entrega_manaus = [
        "Av. Djalma Batista, 1650, Chapada - Manaus/AM",
        "Av. Getúlio Vargas, 845, Centro - Manaus/AM",
        "Av. Constantino Nery, 2310, Adrianópolis - Manaus/AM",
        "Av. Torquato Tapajós, 7200, Distrito Industrial - Manaus/AM",
        "Rua 10 de Julho, 456, Centro - Manaus/AM",
        "Av. Tancredo Neves, 3500, Flores - Manaus/AM",
        "Av. Max Teixeira, 1850, Alvorada - Manaus/AM",
        "Rua Ramos Ferreira, 789, Centro - Manaus/AM",
        "Av. Paraíba, 1200, Petrópolis - Manaus/AM",
        "Av. Umberto Calderaro, 2800, Aleixo - Manaus/AM",
        "Av. Dom Pedro I, 1500, Centro - Manaus/AM",
        "Rua Recife, 234, Centro - Manaus/AM",
        "Av. Brasil, 550, Compensa - Manaus/AM",
        "Av. Autaz Mirim, 8400, Jorge Teixeira - Manaus/AM",
        "Rua 24 de Maio, 123, Centro - Manaus/AM"
    ]
    
    # Criar locações apenas para os últimos orçamentos aprovados (os que foram marcados para ter contrato)
    # Isso garante que alguns orçamentos aprovados tenham contrato (não editáveis) e outros não (editáveis)
    orcamentos_para_contrato = orcamentos_aprovados_sem_contrato[-10:] if len(orcamentos_aprovados_sem_contrato) >= 10 else orcamentos_aprovados_sem_contrato
    
    for orcamento in orcamentos_para_contrato:
        funcionario = random.choice(funcionarios_criados)
        endereco_entrega = random.choice(enderecos_entrega_manaus)
        
        try:
            response = requests.post(
                f"{API_URL}/locacoes/from-orcamento/{orcamento['id']}",
                json={"endereco_entrega": endereco_entrega},
                headers={"X-Funcionario-Username": funcionario["username"]},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                locacao = response.json()["locacao"]
                locacoes_criadas.append(locacao)
                
                # Atualizar o status do orçamento para indicar que tem contrato
                orcamento["has_locacao"] = True
                
                # Finalizar algumas locações
                if random.random() < 0.3:  # 30% de chance de finalizar
                    requests.post(
                        f"{API_URL}/locacoes/{locacao['id']}/finalizar",
                        headers={"X-Funcionario-Username": funcionario["username"]},
                        timeout=10
                    )
                    print(f"  ✅ Locação #{locacao['id']} criada e finalizada (Orçamento #{orcamento['id']} agora NÃO editável)")
                else:
                    print(f"  ✅ Locação #{locacao['id']} criada (Orçamento #{orcamento['id']} agora NÃO editável)")
            else:
                error_detail = ""
                try:
                    error_detail = response.json().get('detail', '')
                except Exception:
                    error_detail = response.text[:100]
                print(f"  ❌ Erro ao criar locação do orçamento {orcamento['id']}: {response.status_code} - {error_detail}")
        except Exception as e:
            print(f"  ❌ Erro ao criar locação: {e}")
    
    print(f"\n✅ {len(locacoes_criadas)} locações criadas\n")
    
    # Resumo final com detalhes dos cenários de teste
    print("\n" + "=" * 60)
    print("📊 RESUMO DA POPULARIZAÇÃO")
    print("=" * 60)
    print(f"👨‍💼 Funcionários: {len(funcionarios_criados)}")
    print(f"👥 Clientes: {len(clientes_criados)}")
    print(f"🔧 Equipamentos: {len(equipamentos_criados)}")
    print("   - Alguns com estoque baixo (1-2 unidades) para testar validação")
    print(f"📋 Orçamentos: {len(orcamentos_criados)}")
    
    # Contar orçamentos por status
    pendentes = len([o for o in orcamentos_criados if o.get("status") == "pendente"])
    aprovados = len([o for o in orcamentos_criados if o.get("status") == "aprovado"])
    rejeitados = len([o for o in orcamentos_criados if o.get("status") == "rejeitado"])
    aprovados_com_contrato = len([o for o in orcamentos_criados if o.get("has_locacao")])
    aprovados_sem_contrato = aprovados - aprovados_com_contrato
    
    print(f"   - Pendentes: {pendentes} (editáveis)")
    print(f"   - Aprovados sem contrato: {aprovados_sem_contrato} (editáveis)")
    print(f"   - Aprovados com contrato: {aprovados_com_contrato} (NÃO editáveis)")
    print(f"   - Rejeitados: {rejeitados} (editáveis, voltam a pendente)")
    print("   - Com desconto e/ou frete: vários para testar")
    print(f"📦 Locações: {len(locacoes_criadas)}")
    print("=" * 60)
    print("✅ Popularização concluída com sucesso!")
    print("\n🧪 CENÁRIOS DE TESTE CRIADOS:")
    print("   ✓ Orçamentos com desconto e frete variados")
    print("   ✓ Validação de estoque (equipamentos com estoque baixo)")
    print("   ✓ Orçamentos pendentes (editáveis)")
    print("   ✓ Orçamentos aprovados sem contrato (editáveis)")
    print("   ✓ Orçamentos aprovados com contrato (NÃO editáveis - botão desabilitado)")
    print("   ✓ Orçamentos rejeitados (editáveis, voltam a pendente ao editar)")
    print("\n🌐 Acesse: https://srv938431.hstgr.cloud/")


def criar_cenario_bug():
    """
    Cria o cenário específico relatado pelo usuário para reprodução do bug
    """
    print("\n" + "=" * 60)
    print("🐛 CRIANDO CENÁRIO DE REPRODUÇÃO DO BUG")
    print("=" * 60)
    
    # 1. Obter headers de autenticação
    headers = {"X-Funcionario-Username": "rloc"}
    
    # 2. Buscar ou criar Cliente Patricia Lima
    print("1. Buscando Cliente Patricia Lima...")
    cliente_id = None
    try:
        response = requests.get(f"{API_URL}/clientes/", headers=headers, timeout=10)
        if response.status_code == 200:
            clientes = response.json()
            for c in clientes:
                if "Patricia Lima" in c.get("nome_razao_social", ""):
                    cliente_id = c["id"]
                    print(f"   ✅ Cliente encontrado: {c['nome_razao_social']} (ID {cliente_id})")
                    break
    except Exception:
        pass
        
    if not cliente_id:
        print("   ⚠️ Cliente não encontrado. Criando...")
        patricia_data = {"nome": "Patricia Lima", "cpf": "012.345.678-99", "rg": "01.234.567-8", "email": "patricia.lima@email.com", "telefone": "(92) 98877-6655"}
        try:
             response = requests.post(f"{API_URL}/clientes/", json=criar_cliente_pf(patricia_data), headers=headers, timeout=10)
             if response.status_code in [200, 201]:
                 cliente_id = response.json()["id"]
                 print(f"   ✅ Cliente criado: ID {cliente_id}")
        except Exception as e:
            print(f"   ❌ Erro ao criar cliente: {e}")
            return

    # 3. Buscar Equipamentos
    print("\n2. Identificando equipamentos...")
    betoneira_id = None
    guincho_id = None
    betoneira_preco = 0
    guincho_preco = 0
    
    try:
        response = requests.get(f"{API_URL}/equipamentos/", headers=headers, timeout=10)
        if response.status_code == 200:
            equips = response.json()
            for e in equips:
                if "Betoneira 500L" in e["descricao"]:
                    betoneira_id = e["id"]
                    betoneira_preco = e.get("preco_quinzenal", 0)
                elif "Guincho Elétrico 1 Ton" in e["descricao"]:
                    guincho_id = e["id"]
                    guincho_preco = e.get("preco_quinzenal", 0)
    except Exception:
        pass

    if not betoneira_id or not guincho_id:
        print(f"   ❌ Equipamentos não encontrados")
        return

    # 4. Criar Orçamento
    print("\n3. Criando Orçamento Patricia Lima...")
    
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=17)
    
    # Calculo manual para validar
    # Quinzenal (17 dias) = 2 periodos
    sub_betoneira = 2 * betoneira_preco * 2 
    sub_guincho = 1 * guincho_preco * 2
    total_itens = sub_betoneira + sub_guincho
    
    desconto = total_itens * 0.10 # 10% de desconto (~1275)
    frete = 50.0
    total_final = total_itens - desconto + frete
    
    print(f"   💰 Total Itens: {total_itens:.2f}")
    print(f"   💰 Desconto: {desconto:.2f}")
    print(f"   💰 Total Final: {total_final:.2f}")
    
    itens_payload = [
        {
            "equipamento_id": betoneira_id,
            "quantidade": 2,
            "preco_unitario": betoneira_preco, 
            "dias": 17,
            "tipo_cobranca": "quinzenal",
            "subtotal": sub_betoneira
        },
        {
            "equipamento_id": guincho_id,
            "quantidade": 1,
            "preco_unitario": guincho_preco,
            "dias": 17,
            "tipo_cobranca": "quinzenal",
            "subtotal": sub_guincho
        }
    ]
    
    orcamento_payload = {
        "cliente_id": cliente_id,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "desconto": desconto,
        "frete": frete,
        "total_final": total_final,
        "observacoes": "Reproduction Scenario",
        "itens": itens_payload
    }
    
    try:
        response = requests.post(f"{API_URL}/orcamentos/", json=orcamento_payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            orc = response.json()
            print(f"   ✅ Orçamento criado ID {orc['id']}")
        else:
            print(f"   ❌ Erro ao criar: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    popular_dados()
    criar_cenario_bug()


