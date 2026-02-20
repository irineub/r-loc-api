from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app import models, schemas
from app.models import StatusOrcamento, StatusLocacao
from app.models import Equipamento, StatusOrcamento
from app.schemas import EquipamentoCreate, EquipamentoUpdate
from typing import Dict
from app.utils import get_current_time

# Cliente CRUD
def get_cliente(db: Session, cliente_id: int):
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

def get_clientes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cliente).offset(skip).limit(limit).all()

def create_cliente(db: Session, cliente: schemas.ClienteCreate):
    cliente_data = cliente.dict()
    cliente_data["data_cadastro"] = get_current_time()
    db_cliente = models.Cliente(**cliente_data)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def update_cliente(db: Session, cliente_id: int, cliente: schemas.ClienteUpdate):
    db_cliente = get_cliente(db, cliente_id)
    if db_cliente:
        update_data = cliente.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cliente, field, value)
        db.commit()
        db.refresh(db_cliente)
    return db_cliente

def delete_cliente(db: Session, cliente_id: int):
    db_cliente = get_cliente(db, cliente_id)
    if db_cliente:
        db.delete(db_cliente)
        db.commit()
    return db_cliente

# Equipamento CRUD
def get_equipamento(db: Session, equipamento_id: int):
    return db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()

def get_equipamentos(db: Session, skip: int = 0, limit: int = 100):
    equipamentos = db.query(models.Equipamento).offset(skip).limit(limit).all()
    return equipamentos

def create_equipamento(db: Session, equipamento: schemas.EquipamentoCreate):
    db_equipamento = models.Equipamento(**equipamento.dict())
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)
    return db_equipamento

def update_equipamento(db: Session, equipamento_id: int, equipamento: schemas.EquipamentoUpdate):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if db_equipamento:
        for key, value in equipamento.dict(exclude_unset=True).items():
            setattr(db_equipamento, key, value)
        db.commit()
        db.refresh(db_equipamento)
    return db_equipamento

def delete_equipamento(db: Session, equipamento_id: int):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if db_equipamento:
        db.delete(db_equipamento)
        db.commit()
    return db_equipamento

def update_equipamento_stock(db: Session, equipamento_id: int, quantidade_alugada: int):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if db_equipamento:
        db_equipamento.estoque_alugado += quantidade_alugada
        db.commit()
        db.refresh(db_equipamento)
    return db_equipamento

def alugar_equipamento(db: Session, equipamento_id: int, quantidade: int):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise ValueError("Equipamento não encontrado")
    
    estoque_disponivel = db_equipamento.estoque - db_equipamento.estoque_alugado
    if estoque_disponivel < quantidade:
        raise ValueError(f"Estoque insuficiente. Disponível: {estoque_disponivel}, Solicitado: {quantidade}")
    
    db_equipamento.estoque_alugado += quantidade
    db.commit()
    db.refresh(db_equipamento)
    return db_equipamento

def devolver_equipamento(db: Session, equipamento_id: int, quantidade: int):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise ValueError("Equipamento não encontrado")
    
    if db_equipamento.estoque_alugado < quantidade:
        raise ValueError(f"Quantidade a devolver ({quantidade}) maior que quantidade alugada ({db_equipamento.estoque_alugado})")
    
    db_equipamento.estoque_alugado -= quantidade
    db.commit()
    db.refresh(db_equipamento)
    return db_equipamento

# Orcamento CRUD
def get_orcamento(db: Session, orcamento_id: int):
    return db.query(models.Orcamento).options(joinedload(models.Orcamento.locacao)).filter(models.Orcamento.id == orcamento_id).first()

def get_orcamentos(db: Session, skip: int = 0, limit: int = 100, cliente_id: Optional[int] = None):
    query = db.query(models.Orcamento)
    if cliente_id:
        query = query.filter(models.Orcamento.cliente_id == cliente_id)
    return query.offset(skip).limit(limit).all()

def get_orcamentos_aprovados(db: Session, skip: int = 0, limit: int = 100):
    """Get only approved orcamentos from database"""
    return db.query(models.Orcamento).filter(
        models.Orcamento.status == "aprovado"
    ).offset(skip).limit(limit).all()

def create_orcamento(db: Session, orcamento: schemas.OrcamentoCreate):
    # Agrupar quantidades por equipamento
    equipamentos_quantidades = {}
    for item in orcamento.itens:
        equipamento_id = item.equipamento_id
        if equipamento_id not in equipamentos_quantidades:
            equipamentos_quantidades[equipamento_id] = 0
        equipamentos_quantidades[equipamento_id] += item.quantidade
    
    # Verificar se todos os equipamentos existem
    equipamentos_db = {}
    for equipamento_id in equipamentos_quantidades.keys():
        db_equipamento = get_equipamento(db, equipamento_id)
        if not db_equipamento:
            raise ValueError(f"Equipamento ID {equipamento_id} não encontrado")
        equipamentos_db[equipamento_id] = db_equipamento
    
    # Validar estoque ANTES de criar qualquer coisa (primeira validação)
    for equipamento_id, quantidade_total in equipamentos_quantidades.items():
        db_equipamento = equipamentos_db[equipamento_id]
        estoque_disponivel = db_equipamento.estoque - db_equipamento.estoque_alugado
        
        if estoque_disponivel <= 0:
            raise ValueError(
                f"Equipamento '{db_equipamento.descricao}' não possui estoque disponível. "
                f"Estoque total: {db_equipamento.estoque}, Alugado: {db_equipamento.estoque_alugado}, Disponível: {estoque_disponivel}"
            )
        
        if quantidade_total > estoque_disponivel:
            raise ValueError(
                f"Estoque insuficiente para o equipamento '{db_equipamento.descricao}'. "
                f"Disponível: {estoque_disponivel}, Solicitado: {quantidade_total}"
            )
    
    # Criar orçamento
    orcamento_data = orcamento.dict(exclude={'itens'})
    orcamento_data["data_criacao"] = get_current_time()
    db_orcamento = models.Orcamento(**orcamento_data)
    db.add(db_orcamento)
    db.flush()  # Flush para obter o ID sem commit
    
    # Criar itens e reservar estoque (com validação final antes de reservar)
    for item in orcamento.itens:
        # Revalidar estoque ANTES de reservar (evita race condition)
        db_equipamento = db.query(models.Equipamento).filter(
            models.Equipamento.id == item.equipamento_id
        ).with_for_update().first()  # Lock pessimista para evitar race condition
        
        if not db_equipamento:
            db.rollback()
            raise ValueError(f"Equipamento ID {item.equipamento_id} não encontrado durante a reserva")
        
        estoque_disponivel_atual = db_equipamento.estoque - db_equipamento.estoque_alugado
        
        if estoque_disponivel_atual < item.quantidade:
            db.rollback()
            raise ValueError(
                f"Estoque insuficiente para o equipamento '{db_equipamento.descricao}' durante a reserva. "
                f"Disponível: {estoque_disponivel_atual}, Solicitado: {item.quantidade}. "
                f"O estoque pode ter sido reservado por outro orçamento."
            )
        
        # Criar item
        db_item = models.ItemOrcamento(**item.dict(), orcamento_id=db_orcamento.id)
        db.add(db_item)
        
        # Reservar estoque (incrementar estoque_alugado)
        db_equipamento.estoque_alugado += item.quantidade
    
    # Commit final (tudo ou nada)
    db.commit()
    db.refresh(db_orcamento)
    return db_orcamento

def update_orcamento(db: Session, orcamento_id: int, orcamento: schemas.OrcamentoUpdate):
    db_orcamento = get_orcamento(db, orcamento_id)
    if db_orcamento:
        update_data = orcamento.dict(exclude_unset=True, exclude={'itens', 'status'})
        for field, value in update_data.items():
            setattr(db_orcamento, field, value)
        
        old_status = db_orcamento.status
        
        # Se estava rejeitado e está editando, voltar para pendente
        # Mas só se não tiver locação gerada
        if db_orcamento.status == models.StatusOrcamento.REJEITADO and db_orcamento.locacao is None:
            db_orcamento.status = models.StatusOrcamento.PENDENTE
        
        # Atualizar status se fornecido explicitamente
        if orcamento.status is not None:
            db_orcamento.status = orcamento.status
            
        # Determinar se houve reativação (REJEITADO -> outra coisa)
        # Se foi reativado e NÃO vamos mexer nos itens (abaixo), precisamos reservar o estoque dos itens existentes
        is_reactivated = (old_status == models.StatusOrcamento.REJEITADO and 
                          db_orcamento.status != models.StatusOrcamento.REJEITADO)
        
        has_new_items = 'itens' in orcamento.dict(exclude_unset=True) and orcamento.itens is not None
        
        if is_reactivated and not has_new_items:
             # Re-reservar estoque dos itens existentes
             for item in db_orcamento.itens:
                 db_equipamento = get_equipamento(db, item.equipamento_id)
                 if db_equipamento:
                     # Verificar disponibilidade antes de reservar
                     estoque_disponivel = db_equipamento.estoque - db_equipamento.estoque_alugado
                     if estoque_disponivel < item.quantidade:
                         raise ValueError(f"Estoque insuficiente ao reativar orçamento para {db_equipamento.descricao}")
                     
                     db_equipamento.estoque_alugado += item.quantidade
        
        # Atualizar itens se fornecidos
        if 'itens' in orcamento.dict(exclude_unset=True) and orcamento.itens is not None:
            # Buscar itens antigos antes de deletar para liberar estoque
            itens_antigos = db.query(models.ItemOrcamento).filter(
                models.ItemOrcamento.orcamento_id == orcamento_id
            ).all()
            
            # Calcular quantidades dos itens antigos por equipamento
            equipamentos_antigos_quantidades = {}
            for item_antigo in itens_antigos:
                equipamento_id = item_antigo.equipamento_id
                if equipamento_id not in equipamentos_antigos_quantidades:
                    equipamentos_antigos_quantidades[equipamento_id] = 0
                equipamentos_antigos_quantidades[equipamento_id] += item_antigo.quantidade
            
            # Calcular quantidades dos novos itens
            equipamentos_quantidades = {}
            for item in orcamento.itens:
                equipamento_id = item.equipamento_id
                if equipamento_id not in equipamentos_quantidades:
                    equipamentos_quantidades[equipamento_id] = 0
                equipamentos_quantidades[equipamento_id] += item.quantidade
            
            # Validar estoque ANTES de liberar os itens antigos
            # Precisamos considerar que os itens antigos já estão reservados e serão liberados
            for equipamento_id, quantidade_total in equipamentos_quantidades.items():
                db_equipamento = get_equipamento(db, equipamento_id)
                if not db_equipamento:
                    raise ValueError(f"Equipamento ID {equipamento_id} não encontrado")
                
                # Calcular estoque disponível considerando que os itens antigos serão liberados
                quantidade_antiga = equipamentos_antigos_quantidades.get(equipamento_id, 0)
                # O estoque disponível atual + a quantidade que será liberada dos itens antigos
                estoque_disponivel_atual = db_equipamento.estoque - db_equipamento.estoque_alugado
                estoque_disponivel_apos_liberacao = estoque_disponivel_atual + quantidade_antiga
                
                # Validar se há estoque disponível após liberar os itens antigos
                if estoque_disponivel_apos_liberacao <= 0:
                    raise ValueError(
                        f"Equipamento '{db_equipamento.descricao}' não possui estoque disponível. "
                        f"Estoque total: {db_equipamento.estoque}, Alugado: {db_equipamento.estoque_alugado}, "
                        f"Disponível atual: {estoque_disponivel_atual}, Após liberar itens antigos: {estoque_disponivel_apos_liberacao}"
                    )
                
                if quantidade_total > estoque_disponivel_apos_liberacao:
                    raise ValueError(
                        f"Estoque insuficiente para o equipamento '{db_equipamento.descricao}'. "
                        f"Disponível após liberar itens antigos: {estoque_disponivel_apos_liberacao}, Solicitado: {quantidade_total}"
                    )
            
            # Agora sim, liberar estoque dos itens antigos (só se não tiver locação gerada E não estava rejeitado)
            # Se estava rejeitado, o estoque já foi liberado quando foi rejeitado
            if db_orcamento.locacao is None and db_orcamento.status != models.StatusOrcamento.REJEITADO:
                for item_antigo in itens_antigos:
                    db_equipamento = get_equipamento(db, item_antigo.equipamento_id)
                    if db_equipamento:
                        # Liberar o estoque que estava reservado para este item
                        db_equipamento.estoque_alugado = max(0, db_equipamento.estoque_alugado - item_antigo.quantidade)
            
            # Deletar itens antigos
            db.query(models.ItemOrcamento).filter(
                models.ItemOrcamento.orcamento_id == orcamento_id
            ).delete()
            
            # Criar novos itens e reservar estoque (só se não tiver locação gerada)
            for item in orcamento.itens:
                db_item = models.ItemOrcamento(**item.dict(), orcamento_id=orcamento_id)
                db.add(db_item)
                
                # Reservar estoque para o novo item (só se não tiver locação gerada)
                if db_orcamento.locacao is None:
                    db_equipamento = get_equipamento(db, item.equipamento_id)
                    if db_equipamento:
                        db_equipamento.estoque_alugado += item.quantidade
        
        db.commit()
        db.refresh(db_orcamento)
    return db_orcamento

def aprovar_orcamento(db: Session, orcamento_id: int):
    db_orcamento = get_orcamento(db, orcamento_id)
    if db_orcamento and db_orcamento.status == StatusOrcamento.PENDENTE:
        db_orcamento.status = StatusOrcamento.APROVADO
        db.commit()
        db.refresh(db_orcamento)
    return db_orcamento

def rejeitar_orcamento(db: Session, orcamento_id: int):
    db_orcamento = get_orcamento(db, orcamento_id)
    if db_orcamento and db_orcamento.status == StatusOrcamento.PENDENTE:
        # Liberar estoque dos itens do orçamento rejeitado (só se não tiver locação gerada)
        if db_orcamento.locacao is None:
            for item in db_orcamento.itens:
                db_equipamento = get_equipamento(db, item.equipamento_id)
                if db_equipamento:
                    # Liberar o estoque que estava reservado para este item
                    db_equipamento.estoque_alugado = max(0, db_equipamento.estoque_alugado - item.quantidade)
        
        db_orcamento.status = StatusOrcamento.REJEITADO
        db_orcamento.data_rejeicao = get_current_time()  # Salvar data de rejeição
        db.commit()
        db.refresh(db_orcamento)
    return db_orcamento

def limpar_orcamentos_rejeitados(db: Session, dias: int = 30):
    """Deleta orçamentos rejeitados que foram rejeitados há mais de X dias"""
    data_limite = get_current_time() - timedelta(days=dias)
    
    # Buscar orçamentos rejeitados há mais de X dias
    orcamentos_rejeitados = db.query(models.Orcamento).filter(
        and_(
            models.Orcamento.status == StatusOrcamento.REJEITADO,
            models.Orcamento.data_rejeicao.isnot(None),
            models.Orcamento.data_rejeicao < data_limite,
            models.Orcamento.locacao == None  # Só deletar se não tiver locação gerada
        )
    ).all()
    
    quantidade_deletados = 0
    for orcamento in orcamentos_rejeitados:
        # Deletar itens do orçamento primeiro
        db.query(models.ItemOrcamento).filter(
            models.ItemOrcamento.orcamento_id == orcamento.id
        ).delete()
        
        # Deletar o orçamento
        db.delete(orcamento)
        quantidade_deletados += 1
    
    db.commit()
    return quantidade_deletados

# Locacao CRUD
def get_locacao(db: Session, locacao_id: int):
    return db.query(models.Locacao).options(
        joinedload(models.Locacao.cliente),
        joinedload(models.Locacao.orcamento),
        joinedload(models.Locacao.itens).joinedload(models.ItemLocacao.equipamento)
    ).filter(models.Locacao.id == locacao_id).first()

def get_locacoes(db: Session, skip: int = 0, limit: int = 100, status: Optional[StatusLocacao] = None):
    query = db.query(models.Locacao)
    if status:
        query = query.filter(models.Locacao.status == status)
    return query.options(
        joinedload(models.Locacao.cliente),
        joinedload(models.Locacao.orcamento),
        joinedload(models.Locacao.itens).joinedload(models.ItemLocacao.equipamento)
    ).offset(skip).limit(limit).all()

def create_locacao_from_orcamento(db: Session, orcamento_id: int, endereco_entrega: Optional[str] = None):
    # Buscar o orçamento
    orcamento = db.query(models.Orcamento).filter(models.Orcamento.id == orcamento_id).first()
    if not orcamento:
        raise ValueError("Orçamento não encontrado")
    
    if orcamento.status != StatusOrcamento.APROVADO:
        raise ValueError("Apenas orçamentos aprovados podem gerar locações")
    
    # Verificar se já existe uma locação para este orçamento
    existing_locacao = db.query(models.Locacao).filter(models.Locacao.orcamento_id == orcamento_id).first()
    if existing_locacao:
        raise ValueError("Já existe uma locação para este orçamento")
    
    # Criar a locação
    locacao_data = {
        "orcamento_id": orcamento_id,
        "cliente_id": orcamento.cliente_id,
        "data_inicio": orcamento.data_inicio,
        "data_fim": orcamento.data_fim,
        "total_final": orcamento.total_final,
        "status": "ativa",
        "endereco_entrega": endereco_entrega,
        "data_criacao": get_current_time()
    }
    
    db_locacao = models.Locacao(**locacao_data)
    db.add(db_locacao)
    db.flush() # Flush para obter o ID sem commit
    db.refresh(db_locacao)
    
    # Criar itens da locação baseados nos itens do orçamento
    for item_orcamento in orcamento.itens:
        equipamento = get_equipamento(db, item_orcamento.equipamento_id)
        if not equipamento:
            db.rollback()
            raise ValueError(f"Equipamento {item_orcamento.equipamento_id} não encontrado")
        
        # Verificar disponibilidade
        estoque_disponivel = equipamento.estoque - equipamento.estoque_alugado
        # Nota: Como o orçamento já reservou o estoque, tecnicamente o estoque_disponivel conta com essa reserva.
        # Se o item do orçamento está reservado, ele está em estoque_alugado.
        # Então se fizermos estoque - estoque_alugado, a quantidade do nosso item JÁ está subtraída?
        # Sim. Se o orçamento reservou 5, estoque 10 -> alugado 5 -> disponivel 5.
        # Mas para ESTA locação, queremos usar aqueles 5 reservados.
        # Então a validação abaixo iria falhar se tentássemos alugar mais do que o restante.
        # MAS, estamos convertendo O PRÓPRIO orçamento.
        # Então a validação abaixo está incorreta se bloquear.
        # Se 'estoque_disponivel' é o que sobra ALÉM da nossa reserva, então OK verificar se é < 0?
        # Não. A verificação correta seria: (estoque - (estoque_alugado - item.quantidade)) < item.quantidade
        # Ou simplesmente confiar na reserva do orçamento.
        # REMOVENDO VALIDAÇÃO REDUNDANTE QUE PODE FALHAR FALSAMENTE
        # (Já que o orçamento aprovado garante a reserva)
        
        if estoque_disponivel < 0: # Apenas sanidade grave
             db.rollback()
             raise ValueError(f"Estoque inconsistente para {equipamento.descricao}")
        
        # Criar item da locação
        item_locacao_data = {
            "locacao_id": db_locacao.id,
            "equipamento_id": item_orcamento.equipamento_id,
            "quantidade": item_orcamento.quantidade,
            "quantidade_devolvida": 0,
            "preco_unitario": item_orcamento.preco_unitario,
            "dias": item_orcamento.dias,
            "subtotal": item_orcamento.subtotal,
            "data_inicio": item_orcamento.data_inicio,
            "data_fim": item_orcamento.data_fim
        }
        
        db_item_locacao = models.ItemLocacao(**item_locacao_data)
        db.add(db_item_locacao)
        
        # O estoque já foi reservado quando o orçamento foi criado/aprovado.
    
    db.commit()
    return db_locacao

def update_locacao(db: Session, locacao_id: int, locacao: schemas.LocacaoUpdate):
    db_locacao = get_locacao(db, locacao_id)
    if db_locacao:
        update_data = locacao.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_locacao, field, value)
        db.commit()
        db.refresh(db_locacao)
    return db_locacao

def finalizar_locacao(db: Session, locacao_id: int):
    """Finaliza uma locação e devolve os equipamentos ao estoque"""
    locacao = get_locacao(db, locacao_id=locacao_id)
    if not locacao:
        raise ValueError("Locação não encontrada")
    
    if locacao.status != StatusLocacao.ATIVA:
        raise ValueError("Apenas locações ativas podem ser finalizadas")
    
    # Estoque sustenta a locação. Se finalizar, devolver tudo que não foi devolvido ainda.
    for item in locacao.itens:
        pendente = item.quantidade - (item.quantidade_devolvida or 0)
        if pendente > 0:
            db_equipamento = get_equipamento(db, item.equipamento_id)
            if db_equipamento:
                # Devolve ao estoque (decrementa alugado)
                db_equipamento.estoque_alugado = max(0, db_equipamento.estoque_alugado - pendente)
            # Atualiza item como devolvido
            item.quantidade_devolvida = item.quantidade

    locacao.status = StatusLocacao.FINALIZADA
    locacao.data_devolucao = get_current_time()
    
    db.commit()
    return locacao

def cancelar_locacao(db: Session, locacao_id: int):
    """Cancela uma locação e devolve os equipamentos ao estoque"""
    locacao = get_locacao(db, locacao_id=locacao_id)
    if not locacao:
        raise ValueError("Locação não encontrada")
    
    if locacao.status != StatusLocacao.ATIVA:
        raise ValueError("Apenas locações ativas podem ser canceladas")
    
    # Estoque deve ser ajustado separadamente caso haja devolução -> CORREÇÃO: Liberar o estoque reservado.
    for item in locacao.itens:
        pendente = item.quantidade - (item.quantidade_devolvida or 0)
        if pendente > 0:
            db_equipamento = get_equipamento(db, item.equipamento_id)
            if db_equipamento:
                # Devolve ao estoque (decrementa alugado)
                db_equipamento.estoque_alugado = max(0, db_equipamento.estoque_alugado - pendente)
    
    locacao.status = StatusLocacao.CANCELADA
    
    db.commit()
    return locacao

def receber_locacao_parcial(db: Session, locacao_id: int, itens: list[Dict[str, int]]):
    locacao = get_locacao(db, locacao_id=locacao_id)
    if not locacao:
        raise ValueError("Locação não encontrada")

    # Mapear itens por equipamento_id para acesso rápido
    equipamento_id_to_qtd = {i["equipamento_id"]: i["quantidade"] for i in itens}

    for item in locacao.itens:
        if item.equipamento_id in equipamento_id_to_qtd:
            qtd_dev = equipamento_id_to_qtd[item.equipamento_id]
            if qtd_dev <= 0:
                continue
            pendente = max(0, item.quantidade - (item.quantidade_devolvida or 0))
            devolver = min(qtd_dev, pendente)
            if devolver <= 0:
                continue
            equipamento = get_equipamento(db, item.equipamento_id)
            if equipamento:
                equipamento.estoque_alugado = max(0, equipamento.estoque_alugado - devolver)
            item.quantidade_devolvida = (item.quantidade_devolvida or 0) + devolver

    db.commit()
    db.refresh(locacao)
    return locacao

# Utility functions
def calcular_dias(data_inicio: datetime, data_fim: datetime) -> int:
    """Calculate the number of days between two dates"""
    return (data_fim - data_inicio).days

def calcular_subtotal(quantidade: int, preco_unitario: float, dias: int) -> float:
    """Calculate the subtotal for an item"""
    return quantidade * preco_unitario * dias

def get_locacoes_atrasadas(db: Session):
    """Get all overdue locacoes"""
    hoje = get_current_time()
    return db.query(models.Locacao).filter(
        and_(
            models.Locacao.status == StatusLocacao.ATIVA,
            models.Locacao.data_fim < hoje
        )
    ).all()

# Funcionario CRUD
def get_funcionario(db: Session, funcionario_id: int):
    return db.query(models.Funcionario).filter(models.Funcionario.id == funcionario_id).first()

def get_funcionario_by_username(db: Session, username: str):
    return db.query(models.Funcionario).filter(models.Funcionario.username == username).first()

def get_funcionarios(db: Session, skip: int = 0, limit: int = 100, ativo: Optional[bool] = None):
    query = db.query(models.Funcionario)
    if ativo is not None:
        query = query.filter(models.Funcionario.ativo == ativo)
    return query.offset(skip).limit(limit).all()

def create_funcionario(db: Session, funcionario: schemas.FuncionarioCreate):
    # Verificar se username já existe
    existing = get_funcionario_by_username(db, funcionario.username)
    if existing:
        raise ValueError("Username já existe")
    
    senha_hash = models.Funcionario.hash_senha(funcionario.senha)
    db_funcionario = models.Funcionario(
        username=funcionario.username,
        senha_hash=senha_hash,
        nome=funcionario.nome,
        ativo=funcionario.ativo,
        data_cadastro=get_current_time()
    )
    db.add(db_funcionario)
    db.commit()
    db.refresh(db_funcionario)
    return db_funcionario

def update_funcionario(db: Session, funcionario_id: int, funcionario: schemas.FuncionarioUpdate):
    db_funcionario = get_funcionario(db, funcionario_id)
    if db_funcionario:
        update_data = funcionario.dict(exclude_unset=True)
        if 'senha' in update_data:
            update_data['senha_hash'] = models.Funcionario.hash_senha(update_data.pop('senha'))
        for field, value in update_data.items():
            setattr(db_funcionario, field, value)
        db.commit()
        db.refresh(db_funcionario)
    return db_funcionario

def delete_funcionario(db: Session, funcionario_id: int):
    db_funcionario = get_funcionario(db, funcionario_id)
    if db_funcionario:
        db.delete(db_funcionario)
        db.commit()
    return db_funcionario

def autenticar_funcionario(db: Session, username: str, senha: str):
    """Autentica um funcionário e retorna o funcionário se válido"""
    funcionario = get_funcionario_by_username(db, username)
    if not funcionario:
        return None
    if not funcionario.ativo:
        return None
    if funcionario.verificar_senha(senha):
        return funcionario
    return None

# LogAuditoria CRUD
def create_log(db: Session, funcionario_id: Optional[int], funcionario_username: Optional[str], 
               acao: str, entidade: str, entidade_id: Optional[int] = None, detalhes: Optional[str] = None):
    """Cria um log de auditoria"""
    log = models.LogAuditoria(
        funcionario_id=funcionario_id,
        funcionario_username=funcionario_username,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhes=detalhes,
        data_hora=get_current_time()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs(db: Session, skip: int = 0, limit: int = 100, 
             funcionario_id: Optional[int] = None, entidade: Optional[str] = None,
             data_inicio: Optional[datetime] = None, data_fim: Optional[datetime] = None):
    """Busca logs de auditoria com filtros opcionais"""
    query = db.query(models.LogAuditoria)
    if funcionario_id:
        query = query.filter(models.LogAuditoria.funcionario_id == funcionario_id)
    if entidade:
        query = query.filter(models.LogAuditoria.entidade == entidade)
    if data_inicio:
        query = query.filter(models.LogAuditoria.data_hora >= data_inicio)
    if data_fim:
        query = query.filter(models.LogAuditoria.data_hora <= data_fim)
        
    return query.order_by(models.LogAuditoria.data_hora.desc()).offset(skip).limit(limit).all() 