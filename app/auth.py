"""
Módulo de autenticação e autorização
"""
from fastapi import HTTPException, Header
from typing import Optional

def is_master_user(username: Optional[str]) -> bool:
    """Verifica se o usuário é master (rloc ou tem .master no username)"""
    if not username:
        return False
    return username == "rloc" or ".master" in username

def get_current_user(x_funcionario_username: Optional[str] = Header(None)) -> str:
    """Extrai o username do header ou retorna 'rloc' como padrão"""
    return x_funcionario_username or "rloc"

def require_master(x_funcionario_username: Optional[str] = Header(None)):
    """Dependency que verifica se o usuário tem permissão master"""
    username = get_current_user(x_funcionario_username)
    if not is_master_user(username):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas usuários master podem acessar esta funcionalidade."
        )
    return username


