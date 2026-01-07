from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.auth import require_master

router = APIRouter()

@router.post("/", response_model=schemas.Funcionario)
def create_funcionario(
    funcionario: schemas.FuncionarioCreate, 
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Create a new funcionario - Apenas usuários master"""
    try:
        return crud.create_funcionario(db=db, funcionario=funcionario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Funcionario])
def read_funcionarios(
    skip: int = 0, 
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get all funcionarios - Apenas usuários master"""
    funcionarios = crud.get_funcionarios(db, skip=skip, limit=limit, ativo=ativo)
    return funcionarios

@router.get("/{funcionario_id}", response_model=schemas.Funcionario)
def read_funcionario(
    funcionario_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get a specific funcionario by ID - Apenas usuários master"""
    db_funcionario = crud.get_funcionario(db, funcionario_id=funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario

@router.put("/{funcionario_id}", response_model=schemas.Funcionario)
@router.patch("/{funcionario_id}", response_model=schemas.Funcionario)
@router.post("/{funcionario_id}/update", response_model=schemas.Funcionario)
def update_funcionario(
    funcionario_id: int, 
    funcionario: schemas.FuncionarioUpdate, 
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Update a funcionario - Apenas usuários master"""
    db_funcionario = crud.update_funcionario(db, funcionario_id=funcionario_id, funcionario=funcionario)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario

@router.delete("/{funcionario_id}")
def delete_funcionario(
    funcionario_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Delete a funcionario - Apenas usuários master"""
    db_funcionario = crud.delete_funcionario(db, funcionario_id=funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return {"message": "Funcionário deletado com sucesso"}

@router.post("/login", response_model=schemas.Funcionario)
def login_funcionario(login: schemas.FuncionarioLogin, db: Session = Depends(get_db)):
    """Autentica um funcionário"""
    funcionario = crud.autenticar_funcionario(db, username=login.username, senha=login.senha)
    if funcionario is None:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    return funcionario

