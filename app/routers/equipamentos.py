from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Equipamento])
def read_equipamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipamentos = crud.get_equipamentos(db, skip=skip, limit=limit)
    return equipamentos

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
def update_equipamento(equipamento_id: int, equipamento: schemas.EquipamentoUpdate, db: Session = Depends(get_db)):
    try:
        db_equipamento = crud.update_equipamento(db, equipamento_id=equipamento_id, equipamento=equipamento)
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