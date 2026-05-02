from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas
from app.auth import require_master, verify_senha_desconto

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

@router.get("", response_model=schemas.PaginatedResponse[schemas.Funcionario])
@router.get("/", response_model=schemas.PaginatedResponse[schemas.Funcionario], include_in_schema=False)
def read_funcionarios(
    skip: int = 0, 
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_master)
):
    """Get all funcionarios - Apenas usuários master"""
    items, total = crud.get_funcionarios(db, skip=skip, limit=limit, ativo=ativo)
    return {"items": items, "total": total}

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

@router.post(
    "/{funcionario_id}/consultar-senha",
    response_model=schemas.FuncionarioSenhaConsultaResponse,
)
def consultar_senha_funcionario(
    funcionario_id: int,
    body: schemas.FuncionarioSenhaConsultaRequest,
    db: Session = Depends(get_db),
    _: str = Depends(require_master),
):
    """
    Retorna a última senha definida para o funcionário (texto), após validar a senha de desconto.
    Cadastros antigos sem valor guardado não podem ser recuperados.
    """
    if not verify_senha_desconto(body.senha_autorizacao):
        raise HTTPException(status_code=403, detail="Senha de autorização incorreta")
    db_funcionario = crud.get_funcionario(db, funcionario_id=funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    if not db_funcionario.senha_ultima_definida:
        return schemas.FuncionarioSenhaConsultaResponse(
            senha=None,
            message=(
                "Ainda não há senha gravada para consulta. "
                "Peça ao funcionário para fazer login uma vez com a senha atual, ou edite o cadastro e salve uma nova senha."
            ),
        )
    return schemas.FuncionarioSenhaConsultaResponse(senha=db_funcionario.senha_ultima_definida)

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

