from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.models import StatusOrcamento

router = APIRouter()

@router.post("/", response_model=schemas.Orcamento)
def create_orcamento(
    orcamento: schemas.OrcamentoCreate, 
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Create a new orcamento"""
    db_orcamento = crud.create_orcamento(db=db, orcamento=orcamento)
    
    # Registrar log
    funcionario = None
    funcionario_username = x_funcionario_username or "rloc"
    if x_funcionario_username:
        funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
    
    # Buscar nome do cliente
    cliente = crud.get_cliente(db, orcamento.cliente_id)
    nome_cliente = cliente.nome_razao_social if cliente else f"ID {orcamento.cliente_id}"
    
    crud.create_log(
        db=db,
        funcionario_id=funcionario.id if funcionario else None,
        funcionario_username=funcionario_username,
        acao="criar_orcamento",
        entidade="orcamento",
        entidade_id=db_orcamento.id,
        detalhes=f"Orçamento criado para cliente {nome_cliente}"
    )
    
    return db_orcamento

@router.get("/", response_model=List[schemas.Orcamento])
def read_orcamentos(
    skip: int = 0, 
    limit: int = 100, 
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all orcamentos with optional cliente filter"""
    orcamentos = crud.get_orcamentos(db, skip=skip, limit=limit, cliente_id=cliente_id)
    return orcamentos

@router.get("/{orcamento_id}", response_model=schemas.Orcamento)
def read_orcamento(orcamento_id: int, db: Session = Depends(get_db)):
    """Get a specific orcamento by ID"""
    db_orcamento = crud.get_orcamento(db, orcamento_id=orcamento_id)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return db_orcamento

@router.put("/{orcamento_id}", response_model=schemas.Orcamento)
@router.patch("/{orcamento_id}", response_model=schemas.Orcamento)
@router.post("/{orcamento_id}/update", response_model=schemas.Orcamento)
def update_orcamento(orcamento_id: int, orcamento: schemas.OrcamentoUpdate, db: Session = Depends(get_db)):
    """Update an orcamento"""
    db_orcamento = crud.update_orcamento(db, orcamento_id=orcamento_id, orcamento=orcamento)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return db_orcamento

@router.post("/{orcamento_id}/aprovar", response_model=schemas.OrcamentoResponse)
def aprovar_orcamento(
    orcamento_id: int, 
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Approve an orcamento"""
    db_orcamento = crud.aprovar_orcamento(db, orcamento_id=orcamento_id)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # Registrar log
    funcionario = None
    funcionario_username = x_funcionario_username or "rloc"
    if x_funcionario_username:
        funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
    
    # Buscar nome do cliente
    cliente = crud.get_cliente(db, db_orcamento.cliente_id)
    nome_cliente = cliente.nome_razao_social if cliente else f"ID {db_orcamento.cliente_id}"
    
    crud.create_log(
        db=db,
        funcionario_id=funcionario.id if funcionario else None,
        funcionario_username=funcionario_username,
        acao="aprovar_orcamento",
        entidade="orcamento",
        entidade_id=orcamento_id,
        detalhes=f"Orçamento aprovado para cliente {nome_cliente}"
    )
    
    return {"orcamento": db_orcamento, "message": "Orçamento aprovado com sucesso"}

@router.post("/{orcamento_id}/rejeitar", response_model=schemas.OrcamentoResponse)
def rejeitar_orcamento(
    orcamento_id: int, 
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    """Reject an orcamento"""
    db_orcamento = crud.rejeitar_orcamento(db, orcamento_id=orcamento_id)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # Registrar log
    funcionario = None
    funcionario_username = x_funcionario_username or "rloc"
    if x_funcionario_username:
        funcionario = crud.get_funcionario_by_username(db, x_funcionario_username)
    
    # Buscar nome do cliente
    cliente = crud.get_cliente(db, db_orcamento.cliente_id)
    nome_cliente = cliente.nome_razao_social if cliente else f"ID {db_orcamento.cliente_id}"
    
    crud.create_log(
        db=db,
        funcionario_id=funcionario.id if funcionario else None,
        funcionario_username=funcionario_username,
        acao="rejeitar_orcamento",
        entidade="orcamento",
        entidade_id=orcamento_id,
        detalhes=f"Orçamento rejeitado para cliente {nome_cliente}"
    )
    
    return {"orcamento": db_orcamento, "message": "Orçamento rejeitado"}

@router.get("/pendentes/", response_model=List[schemas.Orcamento])
def read_orcamentos_pendentes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all pending orcamentos"""
    orcamentos = crud.get_orcamentos(db, skip=skip, limit=limit)
    return [orc for orc in orcamentos if orc.status == StatusOrcamento.PENDENTE]

@router.get("/aprovados/", response_model=List[schemas.Orcamento])
def read_orcamentos_aprovados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all approved orcamentos"""
    return crud.get_orcamentos_aprovados(db, skip=skip, limit=limit) 