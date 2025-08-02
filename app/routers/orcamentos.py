from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.models import StatusOrcamento

router = APIRouter()

@router.post("/", response_model=schemas.Orcamento)
def create_orcamento(orcamento: schemas.OrcamentoCreate, db: Session = Depends(get_db)):
    """Create a new orcamento"""
    return crud.create_orcamento(db=db, orcamento=orcamento)

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
def update_orcamento(orcamento_id: int, orcamento: schemas.OrcamentoUpdate, db: Session = Depends(get_db)):
    """Update an orcamento"""
    db_orcamento = crud.update_orcamento(db, orcamento_id=orcamento_id, orcamento=orcamento)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return db_orcamento

@router.post("/{orcamento_id}/aprovar", response_model=schemas.OrcamentoResponse)
def aprovar_orcamento(orcamento_id: int, db: Session = Depends(get_db)):
    """Approve an orcamento"""
    db_orcamento = crud.aprovar_orcamento(db, orcamento_id=orcamento_id)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return {"orcamento": db_orcamento, "message": "Orçamento aprovado com sucesso"}

@router.post("/{orcamento_id}/rejeitar", response_model=schemas.OrcamentoResponse)
def rejeitar_orcamento(orcamento_id: int, db: Session = Depends(get_db)):
    """Reject an orcamento"""
    db_orcamento = crud.rejeitar_orcamento(db, orcamento_id=orcamento_id)
    if db_orcamento is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
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