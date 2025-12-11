from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.auth import require_master

router = APIRouter()

@router.get("/", response_model=List[schemas.LogAuditoria])
def read_logs(
    skip: int = 0,
    limit: int = 100,
    funcionario_id: Optional[int] = None,
    entidade: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get all logs de auditoria - Apenas usuários master"""
    logs = crud.get_logs(db, skip=skip, limit=limit, funcionario_id=funcionario_id, entidade=entidade)
    return logs

@router.get("/{log_id}", response_model=schemas.LogAuditoria)
def read_log(
    log_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get a specific log by ID - Apenas usuários master"""
    from app import models
    log = db.query(models.LogAuditoria).filter(models.LogAuditoria.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return log

