from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.auth import require_master

router = APIRouter()

def _to_local_naive(dt, timezone_str: str):
    """
    Converte um datetime (possivelmente tz-aware UTC/outro) para datetime naive
    no fuso horário configurado, para comparar com os registros armazenados
    como naive local no banco.
    """
    if dt is None:
        return None
    try:
        # Se for tz-aware, converter para o fuso local e remover tzinfo
        if dt.tzinfo is not None:
            try:
                from zoneinfo import ZoneInfo
                local_tz = ZoneInfo(timezone_str)
            except Exception:
                import pytz
                local_tz = pytz.timezone(timezone_str)
            dt = dt.astimezone(local_tz)
            return dt.replace(tzinfo=None)
        return dt
    except Exception:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

@router.get("", response_model=List[schemas.LogAuditoria])
@router.get("/", response_model=List[schemas.LogAuditoria], include_in_schema=False)
def read_logs(
    skip: int = 0,
    limit: int = 100,
    funcionario_id: Optional[int] = None,
    entidade: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get all logs de auditoria - Apenas usuários master"""
    from datetime import datetime
    from app.utils import get_configured_timezone

    timezone_str = get_configured_timezone()

    data_inicio = None
    data_fim = None

    if start_date:
        try:
            parsed = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            data_inicio = _to_local_naive(parsed, timezone_str)
        except ValueError:
            pass

    if end_date:
        try:
            parsed = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            data_fim = _to_local_naive(parsed, timezone_str)
        except ValueError:
            pass

    logs = crud.get_logs(
        db,
        skip=skip,
        limit=limit,
        funcionario_id=funcionario_id,
        entidade=entidade,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
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

