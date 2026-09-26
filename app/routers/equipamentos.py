from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("", response_model=schemas.PaginatedResponse[schemas.Equipamento])
@router.get("/", response_model=schemas.PaginatedResponse[schemas.Equipamento], include_in_schema=False)
def read_equipamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = crud.get_equipamentos(db, skip=skip, limit=limit)
    return {"items": items, "total": total}

@router.get("/{equipamento_id}", response_model=schemas.Equipamento)
def read_equipamento(equipamento_id: int, db: Session = Depends(get_db)):
    equipamento = crud.get_equipamento(db, equipamento_id=equipamento_id)
    if equipamento is None:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return equipamento

@router.post("/", response_model=schemas.Equipamento)
def create_equipamento(equipamento: schemas.EquipamentoCreate, db: Session = Depends(get_db)):
    return crud.create_equipamento(db=db, equipamento=equipamento)

@router.put("/{equipamento_id}", response_model=schemas.Equipamento)
@router.patch("/{equipamento_id}", response_model=schemas.Equipamento)
@router.post("/{equipamento_id}/update", response_model=schemas.Equipamento)
def update_equipamento(equipamento_id: int, equipamento: schemas.EquipamentoUpdate, is_master: bool = False, db: Session = Depends(get_db)):
    try:
        db_equipamento = crud.update_equipamento(db, equipamento_id=equipamento_id, equipamento=equipamento, is_master=is_master)
        if db_equipamento is None:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        return db_equipamento
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{equipamento_id}")
def delete_equipamento(equipamento_id: int, db: Session = Depends(get_db)):
    try:
        success = crud.delete_equipamento(db, equipamento_id=equipamento_id)
        if not success:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        return {"message": "Equipamento excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{equipamento_id}/alocacoes", response_model=schemas.EquipamentoAlocacoesResponse)
def read_equipamento_alocacoes(equipamento_id: int, db: Session = Depends(get_db)):
    resultado = crud.get_equipamento_alocacoes(db, equipamento_id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return resultado

@router.post("/{equipamento_id}/corrigir-estoque", response_model=schemas.Equipamento)
def corrigir_estoque_equipamento(
    equipamento_id: int,
    payload: schemas.CorrigirEstoqueRequest,
    db: Session = Depends(get_db),
    x_funcionario_username: Optional[str] = Header(None)
):
    equipamento = crud.corrigir_estoque_equipamento(
        db,
        equipamento_id=equipamento_id,
        estoque=payload.estoque,
        recalcular_alugado=payload.recalcular_alugado,
        estoque_alugado=payload.estoque_alugado,
    )
    if equipamento is None:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")

    funcionario_username = x_funcionario_username or "rloc"
    funcionario = crud.get_funcionario_by_username(db, funcionario_username) if x_funcionario_username else None
    motivo = payload.motivo or "correção manual"
    crud.create_log(
        db=db,
        funcionario_id=funcionario.id if funcionario else None,
        funcionario_username=funcionario_username,
        acao="corrigir_estoque",
        entidade="equipamento",
        entidade_id=equipamento_id,
        detalhes=(
            f"Estoque físico={equipamento.estoque}, alugado={equipamento.estoque_alugado} "
            f"(recalcular={payload.recalcular_alugado}). Motivo: {motivo}"
        ),
    )
    return equipamento

@router.post("/recalcular-estoque")
def recalcular_estoque(db: Session = Depends(get_db)):
    crud.recalcular_estoque_alugado(db)
    return {"message": "Estoque alugado recalculado a partir dos contratos e orçamentos aprovados"}

@router.post("/{equipamento_id}/alugar")
def alugar_equipamento(equipamento_id: int, quantidade: int, db: Session = Depends(get_db)):
    try:
        equipamento = crud.alugar_equipamento(db, equipamento_id=equipamento_id, quantidade=quantidade)
        if equipamento is None:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        return {"message": f"{quantidade} unidades alugadas com sucesso", "equipamento": equipamento}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{equipamento_id}/devolver")
def devolver_equipamento(equipamento_id: int, quantidade: int, db: Session = Depends(get_db)):
    try:
        equipamento = crud.devolver_equipamento(db, equipamento_id=equipamento_id, quantidade=quantidade)
        if equipamento is None:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        return {"message": f"{quantidade} unidades devolvidas com sucesso", "equipamento": equipamento}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 