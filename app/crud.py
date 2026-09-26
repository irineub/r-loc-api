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
    query = db.query(models.Cliente).order_by(models.Cliente.id.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

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
    query = db.query(models.Equipamento).order_by(models.Equipamento.id.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def create_equipamento(db: Session, equipamento: schemas.EquipamentoCreate):
    db_equipamento = models.Equipamento(**equipamento.dict())
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)
    return db_equipamento

def update_equipamento(db: Session, equipamento_id: int, equipamento: schemas.EquipamentoUpdate, is_master: bool = False):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if db_equipamento:
        update_data = equipamento.dict(exclude_unset=True)
        
        if db_equipamento.estoque_alugado > 0:
            # Se for master, permite editar estoque E também preços
            allowed_fields = {'estoque', 'preco_diaria', 'preco_semanal', 'preco_quinzenal', 'preco_mensal'} if is_master else {'estoque'}
            
            for key in update_data.keys():
                if key not in allowed_fields and update_data[key] is not None and update_data[key] != getattr(db_equipamento, key):
                    raise ValueError(f"Não é possível alterar o campo '{key}' pois o equipamento está em uso.")

        if 'estoque' in update_data and update_data['estoque'] is not None and update_data['estoque'] < db_equipamento.estoque_alugado:
            raise ValueError(
                f"Não é possível reduzir o estoque abaixo da quantidade em uso ({db_equipamento.estoque_alugado})."
            )
        for key, value in update_data.items():
            setattr(db_equipamento, key, value)
        db.commit()
        db.refresh(db_equipamento)
    return db_equipamento

def delete_equipamento(db: Session, equipamento_id: int):
    db_equipamento = db.query(models.Equipamento).filter(models.Equipamento.id == equipamento_id).first()
    if db_equipamento:
        # Check if equipamento has associated items in locacoes or orcamentos
        from app.models import ItemLocacao, ItemOrcamento
        has_locacao = db.query(ItemLocacao).filter(ItemLocacao.equipamento_id == equipamento_id).first()
        has_orcamento = db.query(ItemOrcamento).filter(ItemOrcamento.equipamento_id == equipamento_id).first()
        if has_locacao or has_orcamento:
            raise ValueError("Não é possível excluir este equipamento pois ele possui histórico de locações ou orçamentos vinculados.")
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
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.funcionario),
        joinedload(models.Orcamento.itens).joinedload(models.ItemOrcamento.equipamento),
        joinedload(models.Orcamento.locacao),
    ).filter(models.Orcamento.id == orcamento_id).first()

def get_orcamentos(db: Session, skip: int = 0, limit: int = 100, cliente_id: Optional[int] = None):
    base = db.query(models.Orcamento)
    if cliente_id:
        base = base.filter(models.Orcamento.cliente_id == cliente_id)
    total = base.count()
    items = (
        base.options(
            joinedload(models.Orcamento.cliente),
            joinedload(models.Orcamento.funcionario),
            joinedload(models.Orcamento.itens).joinedload(models.ItemOrcamento.equipamento),
        )
        .order_by(models.Orcamento.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total

def get_orcamentos_pendentes(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(models.Orcamento).filter(models.Orcamento.status == StatusOrcamento.PENDENTE)
    total = query.count()
    items = (
        query.options(
            joinedload(models.Orcamento.cliente),
            joinedload(models.Orcamento.funcionario),
            joinedload(models.Orcamento.itens).joinedload(models.ItemOrcamento.equipamento),
        )
        .order_by(models.Orcamento.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total

def get_orcamentos_aprovados(db: Session, skip: int = 0, limit: int = 100):
    """Get only approved orcamentos from database"""
    query = db.query(models.Orcamento).filter(models.Orcamento.status == "aprovado").order_by(models.Orcamento.id.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def _agrupar_quantidades_por_equipamento(itens) -> Dict[int, int]:
    agrupado: Dict[int, int] = {}
    for item in itens:
        equipamento_id = item.equipamento_id
        agrupado[equipamento_id] = agrupado.get(equipamento_id, 0) + item.quantidade
    return agrupado


def _orcamento_reserva_estoque(status, locacao) -> bool:
    """Somente orçamento aprovado e ainda sem contrato ocupa estoque."""
    return status == StatusOrcamento.APROVADO and locacao is None


def _liberar_estoque_itens(db: Session, itens):
    for item in itens:
        db_equipamento = get_equipamento(db, item.equipamento_id)
        if db_equipamento:
            db_equipamento.estoque_alugado = max(0, db_equipamento.estoque_alugado - item.quantidade)


def _reservar_estoque_itens(db: Session, itens, contexto: str = "reservar estoque"):
    agrupado = _agrupar_quantidades_por_equipamento(itens)
    faltando = []
    equipamentos_locked = {}

    for equipamento_id, quantidade_total in agrupado.items():
        db_equipamento = db.query(models.Equipamento).filter(
            models.Equipamento.id == equipamento_id
        ).with_for_update().first()

        if not db_equipamento:
            db.rollback()
            raise ValueError(f"Equipamento ID {equipamento_id} não encontrado ao {contexto}")

        estoque_disponivel = db_equipamento.estoque - db_equipamento.estoque_alugado
        if estoque_disponivel < quantidade_total:
            faltando.append(
                f"'{db_equipamento.descricao}': disponível {estoque_disponivel}, solicitado {quantidade_total}"
            )
        equipamentos_locked[equipamento_id] = (db_equipamento, quantidade_total)

    if faltando:
        db.rollback()
        raise ValueError(
            "Estoque insuficiente para aprovar o orçamento. "
            "Ajuste as quantidades e tente novamente. " + "; ".join(faltando)
        )

    for db_equipamento, quantidade_total in equipamentos_locked.values():
        db_equipamento.estoque_alugado += quantidade_total


def _validar_estoque_disponivel(db: Session, itens, extra_liberar: Optional[Dict[int, int]] = None):
    """Valida contra estoque físico já alugado/reservado (locações + orçamentos aprovados)."""
    extra_liberar = extra_liberar or {}
    agrupado = _agrupar_quantidades_por_equipamento(itens)
    for equipamento_id, quantidade_total in agrupado.items():
        db_equipamento = get_equipamento(db, equipamento_id)
        if not db_equipamento:
            raise ValueError(f"Equipamento ID {equipamento_id} não encontrado")
        disponivel = db_equipamento.estoque - db_equipamento.estoque_alugado + extra_liberar.get(equipamento_id, 0)
        if quantidade_total > disponivel:
            raise ValueError(
                f"Estoque insuficiente para o equipamento '{db_equipamento.descricao}'. "
                f"Disponível: {disponivel}, Solicitado: {quantidade_total}"
            )


def recalcular_estoque_alugado(db: Session):
    """Recalcula estoque_alugado a partir de locações ativas/atrasadas e orçamentos aprovados sem contrato."""
    from sqlalchemy import func

    equipamentos = db.query(models.Equipamento).all()
    for eq in equipamentos:
        locacao_qtd = db.query(
            func.coalesce(func.sum(models.ItemLocacao.quantidade - models.ItemLocacao.quantidade_devolvida), 0)
        ).join(models.Locacao).filter(
            models.ItemLocacao.equipamento_id == eq.id,
            models.Locacao.status.in_([StatusLocacao.ATIVA, StatusLocacao.ATRASADA]),
        ).scalar()

        orcamento_qtd = db.query(
            func.coalesce(func.sum(models.ItemOrcamento.quantidade), 0)
        ).join(models.Orcamento).outerjoin(
            models.Locacao, models.Locacao.orcamento_id == models.Orcamento.id
        ).filter(
            models.ItemOrcamento.equipamento_id == eq.id,
            models.Orcamento.status == StatusOrcamento.APROVADO,
            models.Locacao.id.is_(None),
        ).scalar()

        eq.estoque_alugado = int(locacao_qtd or 0) + int(orcamento_qtd or 0)
    db.commit()


def _quantidade_alugada_equipamento(db: Session, equipamento_id: int) -> int:
    from sqlalchemy import func

    locacao_qtd = db.query(
        func.coalesce(
            func.sum(
                models.ItemLocacao.quantidade - func.coalesce(models.ItemLocacao.quantidade_devolvida, 0)
            ),
            0,
        )
    ).join(models.Locacao).filter(
        models.ItemLocacao.equipamento_id == equipamento_id,
        models.Locacao.status.in_([StatusLocacao.ATIVA, StatusLocacao.ATRASADA]),
    ).scalar()

    orcamento_qtd = db.query(
        func.coalesce(func.sum(models.ItemOrcamento.quantidade), 0)
    ).join(models.Orcamento).outerjoin(
        models.Locacao, models.Locacao.orcamento_id == models.Orcamento.id
    ).filter(
        models.ItemOrcamento.equipamento_id == equipamento_id,
        models.Orcamento.status == StatusOrcamento.APROVADO,
        models.Locacao.id.is_(None),
    ).scalar()

    return int(locacao_qtd or 0) + int(orcamento_qtd or 0)


def get_equipamento_alocacoes(db: Session, equipamento_id: int):
    db_equipamento = get_equipamento(db, equipamento_id)
    if not db_equipamento:
        return None

    alocacoes = []

    itens_locacao = (
        db.query(models.ItemLocacao)
        .join(models.Locacao)
        .options(
            joinedload(models.ItemLocacao.locacao).joinedload(models.Locacao.cliente),
        )
        .filter(
            models.ItemLocacao.equipamento_id == equipamento_id,
            models.Locacao.status.in_([StatusLocacao.ATIVA, StatusLocacao.ATRASADA]),
        )
        .all()
    )
    for item in itens_locacao:
        pendente = item.quantidade - (item.quantidade_devolvida or 0)
        if pendente <= 0:
            continue
        locacao = item.locacao
        alocacoes.append({
            "tipo": "locacao",
            "id": locacao.id,
            "cliente_id": locacao.cliente_id,
            "cliente_nome": locacao.cliente.nome_razao_social if locacao.cliente else None,
            "quantidade": item.quantidade,
            "quantidade_pendente": pendente,
            "status": locacao.status.value if hasattr(locacao.status, "value") else str(locacao.status),
            "data_inicio": locacao.data_inicio,
            "data_fim": locacao.data_fim,
        })

    itens_orcamento = (
        db.query(models.ItemOrcamento)
        .join(models.Orcamento)
        .outerjoin(models.Locacao, models.Locacao.orcamento_id == models.Orcamento.id)
        .options(
            joinedload(models.ItemOrcamento.orcamento).joinedload(models.Orcamento.cliente),
        )
        .filter(
            models.ItemOrcamento.equipamento_id == equipamento_id,
            models.Orcamento.status == StatusOrcamento.APROVADO,
            models.Locacao.id.is_(None),
        )
        .all()
    )
    for item in itens_orcamento:
        orcamento = item.orcamento
        alocacoes.append({
            "tipo": "orcamento",
            "id": orcamento.id,
            "cliente_id": orcamento.cliente_id,
            "cliente_nome": orcamento.cliente.nome_razao_social if orcamento.cliente else None,
            "quantidade": item.quantidade,
            "quantidade_pendente": item.quantidade,
            "status": orcamento.status.value if hasattr(orcamento.status, "value") else str(orcamento.status),
            "data_inicio": orcamento.data_inicio,
            "data_fim": orcamento.data_fim,
        })

    return {
        "equipamento_id": db_equipamento.id,
        "descricao": db_equipamento.descricao,
        "estoque": db_equipamento.estoque,
        "estoque_alugado": db_equipamento.estoque_alugado,
        "estoque_disponivel": db_equipamento.estoque - db_equipamento.estoque_alugado,
        "alocacoes": alocacoes,
    }


def corrigir_estoque_equipamento(
    db: Session,
    equipamento_id: int,
    estoque: int,
    recalcular_alugado: bool = True,
    estoque_alugado: Optional[int] = None,
):
    db_equipamento = get_equipamento(db, equipamento_id)
    if not db_equipamento:
        return None

    db_equipamento.estoque = estoque
    if recalcular_alugado:
        db_equipamento.estoque_alugado = _quantidade_alugada_equipamento(db, equipamento_id)
    elif estoque_alugado is not None:
        db_equipamento.estoque_alugado = estoque_alugado

    db.commit()
    db.refresh(db_equipamento)
    return db_equipamento


def get_dashboard_resumo(db: Session):
    from sqlalchemy import func, desc

    totais = {
        "clientes": db.query(func.count(models.Cliente.id)).scalar() or 0,
        "equipamentos": db.query(func.count(models.Equipamento.id)).scalar() or 0,
        "orcamentos": db.query(func.count(models.Orcamento.id)).scalar() or 0,
        "locacoes_ativas": db.query(func.count(models.Locacao.id)).filter(
            models.Locacao.status.in_([StatusLocacao.ATIVA, StatusLocacao.ATRASADA])
        ).scalar() or 0,
    }

    orcamentos_pendentes = (
        db.query(models.Orcamento)
        .options(
            joinedload(models.Orcamento.cliente),
            joinedload(models.Orcamento.funcionario),
            joinedload(models.Orcamento.itens).joinedload(models.ItemOrcamento.equipamento),
        )
        .filter(models.Orcamento.status == StatusOrcamento.PENDENTE)
        .order_by(models.Orcamento.id.desc())
        .limit(8)
        .all()
    )

    locacoes_ativas = (
        db.query(models.Locacao)
        .options(
            joinedload(models.Locacao.cliente),
            joinedload(models.Locacao.itens).joinedload(models.ItemLocacao.equipamento),
        )
        .filter(models.Locacao.status.in_([StatusLocacao.ATIVA, StatusLocacao.ATRASADA]))
        .order_by(models.Locacao.id.desc())
        .all()
    )

    top_eq_rows = (
        db.query(
            models.Equipamento.descricao,
            func.coalesce(func.sum(models.ItemLocacao.quantidade), 0).label("totalLocacoes"),
            func.coalesce(func.sum(models.ItemLocacao.dias), 0).label("totalDias"),
        )
        .join(models.ItemLocacao, models.ItemLocacao.equipamento_id == models.Equipamento.id)
        .join(models.Locacao, models.Locacao.id == models.ItemLocacao.locacao_id)
        .filter(models.Locacao.status != StatusLocacao.CANCELADA)
        .group_by(models.Equipamento.id, models.Equipamento.descricao)
        .order_by(desc("totalLocacoes"))
        .limit(5)
        .all()
    )
    top_equipamentos = [
        {"nome": row.descricao, "totalLocacoes": int(row.totalLocacoes or 0), "totalDias": int(row.totalDias or 0)}
        for row in top_eq_rows
    ]

    top_cli_rows = (
        db.query(
            models.Cliente.nome_razao_social,
            func.count(models.Locacao.id).label("totalLocacoes"),
            func.coalesce(func.sum(models.Locacao.total_final), 0).label("totalValor"),
        )
        .join(models.Locacao, models.Locacao.cliente_id == models.Cliente.id)
        .filter(models.Locacao.status != StatusLocacao.CANCELADA)
        .group_by(models.Cliente.id, models.Cliente.nome_razao_social)
        .order_by(desc("totalValor"))
        .limit(5)
        .all()
    )
    top_clientes = [
        {
            "nome": row.nome_razao_social,
            "totalLocacoes": int(row.totalLocacoes or 0),
            "totalValor": float(row.totalValor or 0),
        }
        for row in top_cli_rows
    ]

    locacoes_faturamento = db.query(
        models.Locacao.id,
        models.Locacao.data_criacao,
        models.Locacao.status,
        models.Locacao.total_final,
        models.Locacao.cliente_id,
    ).all()

    return {
        "totais": totais,
        "orcamentos_pendentes": orcamentos_pendentes,
        "locacoes_ativas": locacoes_ativas,
        "top_equipamentos": top_equipamentos,
        "top_clientes": top_clientes,
        "locacoes_faturamento": [
            {
                "id": row.id,
                "data_criacao": row.data_criacao,
                "status": row.status,
                "total_final": row.total_final,
                "cliente_id": row.cliente_id,
            }
            for row in locacoes_faturamento
        ],
    }


def create_orcamento(db: Session, orcamento: schemas.OrcamentoCreate):
    equipamentos_quantidades = _agrupar_quantidades_por_equipamento(orcamento.itens)

    for equipamento_id in equipamentos_quantidades.keys():
        if not get_equipamento(db, equipamento_id):
            raise ValueError(f"Equipamento ID {equipamento_id} não encontrado")

    # Orçamento pendente não ocupa estoque. A validação impede só quantidade acima do estoque físico atual.
    _validar_estoque_disponivel(db, orcamento.itens)

    orcamento_data = orcamento.dict(exclude={'itens'})
    orcamento_data["data_criacao"] = get_current_time()
    db_orcamento = models.Orcamento(**orcamento_data)
    db.add(db_orcamento)
    db.flush()

    for item in orcamento.itens:
        db.add(models.ItemOrcamento(**item.dict(), orcamento_id=db_orcamento.id))

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
        tinha_reserva = _orcamento_reserva_estoque(old_status, db_orcamento.locacao)

        # Se estava rejeitado e está editando, voltar para pendente
        if db_orcamento.status == models.StatusOrcamento.REJEITADO and db_orcamento.locacao is None:
            db_orcamento.status = models.StatusOrcamento.PENDENTE

        if orcamento.status is not None:
            db_orcamento.status = orcamento.status

        has_new_items = 'itens' in orcamento.dict(exclude_unset=True) and orcamento.itens is not None
        tera_reserva = _orcamento_reserva_estoque(db_orcamento.status, db_orcamento.locacao)

        if has_new_items:
            itens_antigos = db.query(models.ItemOrcamento).filter(
                models.ItemOrcamento.orcamento_id == orcamento_id
            ).all()

            extra_liberar = {}
            if tinha_reserva:
                extra_liberar = _agrupar_quantidades_por_equipamento(itens_antigos)

            _validar_estoque_disponivel(db, orcamento.itens, extra_liberar=extra_liberar)

            if tinha_reserva:
                _liberar_estoque_itens(db, itens_antigos)

            db.query(models.ItemOrcamento).filter(
                models.ItemOrcamento.orcamento_id == orcamento_id
            ).delete()

            for item in orcamento.itens:
                db.add(models.ItemOrcamento(**item.dict(), orcamento_id=orcamento_id))

            db.flush()

            if tera_reserva:
                _reservar_estoque_itens(db, orcamento.itens, contexto="atualizar orçamento aprovado")
        elif tera_reserva and not tinha_reserva:
            _reservar_estoque_itens(db, db_orcamento.itens, contexto="ativar reserva do orçamento")

        db.commit()
        db.refresh(db_orcamento)
    return db_orcamento

def aprovar_orcamento(db: Session, orcamento_id: int):
    db_orcamento = get_orcamento(db, orcamento_id)
    if db_orcamento and db_orcamento.status == StatusOrcamento.PENDENTE:
        if not db_orcamento.itens:
            raise ValueError("Não é possível aprovar um orçamento sem itens.")
        # Reserva efetiva só na aprovação, com lock para não aprovar acima do estoque.
        _reservar_estoque_itens(db, db_orcamento.itens, contexto="aprovar orçamento")
        db_orcamento.status = StatusOrcamento.APROVADO
        db.commit()
        db.refresh(db_orcamento)
    return db_orcamento

def rejeitar_orcamento(db: Session, orcamento_id: int):
    db_orcamento = get_orcamento(db, orcamento_id)
    if db_orcamento and db_orcamento.status == StatusOrcamento.PENDENTE:
        # Pendente não ocupa estoque; não há reserva para liberar.
        db_orcamento.status = StatusOrcamento.REJEITADO
        db_orcamento.data_rejeicao = get_current_time()
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
        joinedload(models.Locacao.funcionario),
        joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.cliente),
        joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.funcionario),
        joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.itens).joinedload(
            models.ItemOrcamento.equipamento
        ),
        joinedload(models.Locacao.itens).joinedload(models.ItemLocacao.equipamento),
    ).filter(models.Locacao.id == locacao_id).first()

def get_locacoes(db: Session, skip: int = 0, limit: int = 100, status: Optional[StatusLocacao] = None):
    base = db.query(models.Locacao)
    if status:
        base = base.filter(models.Locacao.status == status)
    total = base.count()
    items = (
        base.options(
            joinedload(models.Locacao.cliente),
            joinedload(models.Locacao.funcionario),
            joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.cliente),
            joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.funcionario),
            joinedload(models.Locacao.orcamento).joinedload(models.Orcamento.itens).joinedload(
                models.ItemOrcamento.equipamento
            ),
            joinedload(models.Locacao.itens).joinedload(models.ItemLocacao.equipamento),
        )
        .order_by(models.Locacao.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total

def create_locacao_from_orcamento(db: Session, orcamento_id: int, endereco_entrega: Optional[str] = None, funcionario_id: Optional[int] = None):
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
        "desconto": orcamento.desconto,
        "desconto_percentual": orcamento.desconto_percentual,
        "frete": orcamento.frete,
        "total_final": orcamento.total_final,
        "status": "ativa",
        "endereco_entrega": endereco_entrega,
        "data_criacao": get_current_time(),
        "funcionario_id": funcionario_id
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
        
        # O estoque já foi reservado na aprovação do orçamento.
        estoque_disponivel = equipamento.estoque - equipamento.estoque_alugado
        if estoque_disponivel < 0:
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

def renovar_locacao(db: Session, locacao_id: int, request: schemas.RenovarLocacaoRequest, funcionario_id: Optional[int] = None):
    # 1. Obter locação antiga
    old_locacao = get_locacao(db, locacao_id)
    if not old_locacao:
        raise ValueError("Locação não encontrada")
    
    if old_locacao.status == StatusLocacao.CANCELADA:
        raise ValueError("Não é possível renovar uma locação cancelada")
        
    # 2. Finalizar locação antiga se ainda estiver ativa ou atrasada.
    if old_locacao.status in [StatusLocacao.ATIVA, StatusLocacao.ATRASADA]:
        old_locacao = finalizar_locacao(db, locacao_id)
        
    # 3. Mapear as novas datas e preços por equipamento do request
    item_requests = {item.equipamento_id: item for item in request.itens}
    
    # Mantém o histórico da cadeia de renovações usando a locação original (sempre aponta para a "raiz" ou para a imediatamente anterior)
    # Vamos apontar para a locação imediatamente anterior
    original_id_to_link = locacao_id
    
    # 4. Construir nova locação
    locacao_data = {
        "orcamento_id": old_locacao.orcamento_id,
        "cliente_id": old_locacao.cliente_id,
        "data_inicio": request.data_inicio,
        "data_fim": request.data_fim,
        "desconto": request.desconto,
        "desconto_percentual": request.desconto_percentual,
        "frete": request.frete,
        "total_final": 0.0,
        "status": StatusLocacao.ATIVA,
        "endereco_entrega": old_locacao.endereco_entrega,
        "data_criacao": get_current_time(),
        "funcionario_id": funcionario_id,
        "locacao_original_id": original_id_to_link
    }
    
    db_nova_locacao = models.Locacao(**locacao_data)
    db.add(db_nova_locacao)
    db.flush()
    db.refresh(db_nova_locacao)
    
    total_final = 0.0
    
    # 5. Criar novos itens
    for req_item in request.itens:
        equipamento = get_equipamento(db, req_item.equipamento_id)
        if not equipamento:
            continue
            
        data_fim_item = req_item.data_fim or request.data_fim
        preco_unit = req_item.preco_unitario or equipamento.preco_diaria
        
        dias = max(1, calcular_dias(request.data_inicio, data_fim_item))
        
        # O backend recalcula o subtotal para fins de segurança, caso a cobranca não seja diária
        # Tentamos extrair o fator caso o preço unit seja estritamente igual a tabela mensal, quinzenal ou semanal
        base_periodo = 30
        if preco_unit == equipamento.preco_diaria:
             base_periodo = 1
        elif preco_unit == equipamento.preco_semanal:
             base_periodo = 7
        elif preco_unit == equipamento.preco_quinzenal:
             base_periodo = 15
             
        import math
        fator = math.ceil(dias / base_periodo)
        
        subtotal = round(preco_unit * fator * req_item.quantidade, 2)
        
        # Verificar disponibilidade
        estoque_disponivel = equipamento.estoque - equipamento.estoque_alugado
        if estoque_disponivel < req_item.quantidade:
             db.rollback()
             raise ValueError(f"Estoque insuficiente para {equipamento.descricao} durante renovação.")
             
        item_locacao_data = {
            "locacao_id": db_nova_locacao.id,
            "equipamento_id": req_item.equipamento_id,
            "quantidade": req_item.quantidade,
            "quantidade_devolvida": 0,
            "preco_unitario": preco_unit,
            "dias": dias,
            "subtotal": subtotal,
            "data_inicio": request.data_inicio,
            "data_fim": data_fim_item
        }
        
        db_item_locacao = models.ItemLocacao(**item_locacao_data)
        db.add(db_item_locacao)
        
        # Reservar estoque
        equipamento.estoque_alugado += req_item.quantidade
        
        total_final += subtotal
        
    total_frete = request.frete or 0.0
    db_nova_locacao.total_final = total_final - (request.desconto or 0.0) + total_frete
    db.commit()
    db.refresh(db_nova_locacao)
    
    return db_nova_locacao

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
    query = db.query(models.Funcionario).order_by(models.Funcionario.id.desc())
    if ativo is not None:
        query = query.filter(models.Funcionario.ativo == ativo)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def create_funcionario(db: Session, funcionario: schemas.FuncionarioCreate):
    # Verificar se username já existe
    existing = get_funcionario_by_username(db, funcionario.username)
    if existing:
        raise ValueError("Username já existe")
    
    senha_hash = models.Funcionario.hash_senha(funcionario.senha)
    db_funcionario = models.Funcionario(
        username=funcionario.username,
        senha_hash=senha_hash,
        senha_ultima_definida=funcionario.senha,
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
            plain = update_data.pop('senha')
            update_data['senha_hash'] = models.Funcionario.hash_senha(plain)
            update_data['senha_ultima_definida'] = plain
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
        # Grava texto da última senha válida no login (cadastros antigos + sincroniza após trocas feitas fora do formulário)
        if getattr(funcionario, "senha_ultima_definida", None) != senha:
            funcionario.senha_ultima_definida = senha
            db.add(funcionario)
            db.commit()
            db.refresh(funcionario)
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
        
    total = query.count()
    items = query.order_by(models.LogAuditoria.data_hora.desc()).offset(skip).limit(limit).all() 
    return items, total