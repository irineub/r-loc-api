from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas, crud

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardResumo)
@router.get("/dashboard/", response_model=schemas.DashboardResumo, include_in_schema=False)
def dashboard_resumo(db: Session = Depends(get_db)):
    return crud.get_dashboard_resumo(db)

@router.get("/orcamentos", response_model=List[schemas.Orcamento])
@router.get("/orcamentos/", response_model=List[schemas.Orcamento], include_in_schema=False)
def relatorio_orcamentos(
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    funcionario_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Orcamento)
    if data_inicio:
        query = query.filter(models.Orcamento.data_criacao >= data_inicio)
    if data_fim:
        query = query.filter(models.Orcamento.data_criacao <= data_fim)
    if funcionario_id:
        query = query.filter(models.Orcamento.funcionario_id == funcionario_id)
    return query.order_by(models.Orcamento.data_criacao.desc()).all()

@router.get("/locacoes", response_model=List[schemas.Locacao])
@router.get("/locacoes/", response_model=List[schemas.Locacao], include_in_schema=False)
def relatorio_locacoes(
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    funcionario_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Locacao)
    if data_inicio:
        query = query.filter(models.Locacao.data_criacao >= data_inicio)
    if data_fim:
        query = query.filter(models.Locacao.data_criacao <= data_fim)
    if funcionario_id:
        query = query.filter(models.Locacao.funcionario_id == funcionario_id)
    return query.order_by(models.Locacao.data_criacao.desc()).all()

@router.get("/clientes", response_model=List[schemas.Cliente])
@router.get("/clientes/", response_model=List[schemas.Cliente], include_in_schema=False)
def relatorio_clientes(
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Cliente)
    if data_inicio:
        query = query.filter(models.Cliente.data_cadastro >= data_inicio)
    if data_fim:
        query = query.filter(models.Cliente.data_cadastro <= data_fim)
    return query.order_by(models.Cliente.data_cadastro.desc()).all()

@router.get("/equipamentos", response_model=List[schemas.Equipamento])
@router.get("/equipamentos/", response_model=List[schemas.Equipamento], include_in_schema=False)
def relatorio_equipamentos(
    db: Session = Depends(get_db)
):
    # Equipamentos generally don't have a creation date to filter by in this context
    # so we just return all
    return db.query(models.Equipamento).all()
