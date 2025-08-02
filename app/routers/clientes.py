from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Cliente)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """Create a new cliente"""
    return crud.create_cliente(db=db, cliente=cliente)

@router.get("/", response_model=List[schemas.Cliente])
def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all clientes"""
    clientes = crud.get_clientes(db, skip=skip, limit=limit)
    return clientes

@router.get("/{cliente_id}", response_model=schemas.Cliente)
def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Get a specific cliente by ID"""
    db_cliente = crud.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@router.put("/{cliente_id}", response_model=schemas.Cliente)
def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    """Update a cliente"""
    db_cliente = crud.update_cliente(db, cliente_id=cliente_id, cliente=cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Delete a cliente"""
    db_cliente = crud.delete_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": "Cliente deletado com sucesso"} 