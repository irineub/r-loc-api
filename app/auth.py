"""
Módulo de autenticação e autorização
"""
import hashlib
import hmac
import json
import os
from fastapi import HTTPException, Header
from typing import Optional


def _system_config_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "system_config.json")


def _read_senha_desconto_from_config_file() -> Optional[str]:
    candidates = (
        _system_config_path(),
        os.path.join(os.getcwd(), "system_config.json"),
    )
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            s = data.get("senha_desconto")
            if isinstance(s, str) and s:
                return s
        except Exception:
            continue
    return None


def get_expected_senha_desconto() -> str:
    """
    Mesma senha usada no front para desconto > 10% (padrão 0609).
    Ordem: variável de ambiente SENHA_DESCONTO, depois system_config.json (gravado ao alterar a senha no app),
    depois o padrão 0609.
    """
    env = os.environ.get("SENHA_DESCONTO")
    if env:
        return env
    from_file = _read_senha_desconto_from_config_file()
    if from_file:
        return from_file
    return "0609"


def verify_senha_desconto(senha: Optional[str]) -> bool:
    """Valida a senha de autorização (desconto) de forma resistente a timing em comprimentos iguais de digest."""
    if not senha:
        return False
    expected = get_expected_senha_desconto()
    a = hashlib.sha256(senha.encode()).hexdigest()
    b = hashlib.sha256(expected.encode()).hexdigest()
    return hmac.compare_digest(a, b)

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


