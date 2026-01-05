from fastapi import Request, Header
from typing import Optional

async def get_funcionario_username(request: Request, x_funcionario_username: Optional[str] = Header(None)) -> Optional[str]:
    """Extrai o username do funcionário do header da requisição"""
    return x_funcionario_username


