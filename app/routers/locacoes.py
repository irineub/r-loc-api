from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.models import StatusLocacao
from pydantic import BaseModel

class RecebimentoItem(BaseModel):
    equipamento_id: int
    quantidade: int

class RecebimentoParcial(BaseModel):
    itens: List[RecebimentoItem]

class LocacaoFromOrcamentoRequest(BaseModel):
    endereco_entrega: Optional[str] = None

router = APIRouter()

@router.post("/", response_model=schemas.Locacao)
def create_locacao(locacao: schemas.LocacaoCreate, db: Session = Depends(get_db)):
    """Create a new locacao"""
    try:
        return crud.create_locacao_from_orcamento(db=db, orcamento_id=locacao.orcamento_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Locacao])
def read_locacoes(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[StatusLocacao] = None,
    db: Session = Depends(get_db)
):
    """Get all locacoes with optional status filter"""
    locacoes = crud.get_locacoes(db, skip=skip, limit=limit, status=status)
    return locacoes

@router.get("/{locacao_id}", response_model=schemas.Locacao)
def read_locacao(locacao_id: int, db: Session = Depends(get_db)):
    """Get a specific locacao by ID"""
    db_locacao = crud.get_locacao(db, locacao_id=locacao_id)
    if db_locacao is None:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    return db_locacao

@router.put("/{locacao_id}", response_model=schemas.Locacao)
def update_locacao(locacao_id: int, locacao: schemas.LocacaoUpdate, db: Session = Depends(get_db)):
    """Update a locacao"""
    db_locacao = crud.update_locacao(db, locacao_id=locacao_id, locacao=locacao)
    if db_locacao is None:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    return db_locacao

@router.post("/{locacao_id}/finalizar", response_model=schemas.LocacaoResponse)
def finalizar_locacao(
    locacao_id: int, 
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Finalize a locacao"""
    try:
        db_locacao = crud.finalizar_locacao(db, locacao_id=locacao_id)
        if db_locacao is None:
            raise HTTPException(status_code=404, detail="Locação não encontrada")
        
        # Registrar log
        funcionario = None
        funcionario_username = x_funcionario_username or "rloc"
        if x_funcionario_username:
            funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
        
        # Buscar nome do cliente
        cliente = crud.get_cliente(db, db_locacao.cliente_id)
        nome_cliente = cliente.nome_razao_social if cliente else f"ID {db_locacao.cliente_id}"
        
        crud.create_log(
            db=db,
            funcionario_id=funcionario.id if funcionario else None,
            funcionario_username=funcionario_username,
            acao="finalizar_locacao",
            entidade="locacao",
            entidade_id=locacao_id,
            detalhes=f"Locação finalizada para cliente {nome_cliente}"
        )
        
        return {"locacao": db_locacao, "message": "Locação finalizada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{locacao_id}/cancelar", response_model=schemas.LocacaoResponse)
def cancelar_locacao(
    locacao_id: int, 
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Cancel a locacao"""
    try:
        db_locacao = crud.cancelar_locacao(db, locacao_id=locacao_id)
        if db_locacao is None:
            raise HTTPException(status_code=404, detail="Locação não encontrada")
        
        # Registrar log
        funcionario = None
        funcionario_username = x_funcionario_username or "rloc"
        if x_funcionario_username:
            funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
        
        # Buscar nome do cliente
        cliente = crud.get_cliente(db, db_locacao.cliente_id)
        nome_cliente = cliente.nome_razao_social if cliente else f"ID {db_locacao.cliente_id}"
        
        crud.create_log(
            db=db,
            funcionario_id=funcionario.id if funcionario else None,
            funcionario_username=funcionario_username,
            acao="cancelar_locacao",
            entidade="locacao",
            entidade_id=locacao_id,
            detalhes=f"Locação cancelada para cliente {nome_cliente}"
        )
        
        return {"locacao": db_locacao, "message": "Locação cancelada"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ativas/", response_model=List[schemas.Locacao])
def read_locacoes_ativas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all active locacoes"""
    return crud.get_locacoes(db, skip=skip, limit=limit, status=StatusLocacao.ATIVA)

@router.get("/atrasadas/", response_model=List[schemas.Locacao])
def read_locacoes_atrasadas(db: Session = Depends(get_db)):
    """Get all overdue locacoes"""
    return crud.get_locacoes_atrasadas(db)

@router.post("/from-orcamento/{orcamento_id}", response_model=schemas.LocacaoResponse)
def create_locacao_from_orcamento(
    orcamento_id: int,
    request: Optional[LocacaoFromOrcamentoRequest] = None,
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Create a locacao from an approved orcamento"""
    try:
        endereco_entrega = request.endereco_entrega if request else None
        db_locacao = crud.create_locacao_from_orcamento(db, orcamento_id=orcamento_id, endereco_entrega=endereco_entrega)
        if db_locacao is None:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado ou não aprovado")
        
        # Registrar log
        funcionario = None
        funcionario_username = x_funcionario_username or "rloc"
        if x_funcionario_username:
            funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
        
        # Buscar nome do cliente
        cliente = crud.get_cliente(db, db_locacao.cliente_id)
        nome_cliente = cliente.nome_razao_social if cliente else f"ID {db_locacao.cliente_id}"
        
        crud.create_log(
            db=db,
            funcionario_id=funcionario.id if funcionario else None,
            funcionario_username=funcionario_username,
            acao="criar_locacao",
            entidade="locacao",
            entidade_id=db_locacao.id,
            detalhes=f"Locação criada a partir do orçamento ID {orcamento_id} para cliente {nome_cliente}"
        )
        
        return {"locacao": db_locacao, "message": "Locação criada a partir do orçamento aprovado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{locacao_id}/receber", response_model=schemas.Locacao)
def receber_parcial(locacao_id: int, payload: RecebimentoParcial, db: Session = Depends(get_db)):
    try:
        locacao = crud.receber_locacao_parcial(db, locacao_id=locacao_id, itens=[i.model_dump() for i in payload.itens])
        if locacao is None:
            raise HTTPException(status_code=404, detail="Locação não encontrada")
        return locacao
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))