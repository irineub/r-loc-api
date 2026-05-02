from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import json
import os

from app.auth import require_master

router = APIRouter()

CONFIG_FILE = "system_config.json"


def _system_config_abs_path() -> str:
    """system_config.json na raiz do pacote r-loc-api (mesmo critério de app.auth)."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "system_config.json")

class UazapiConfig(BaseModel):
    url: str
    token: str

@router.get("/uazapi")
async def get_uazapi_config():
    if not os.path.exists(CONFIG_FILE):
        return {"url": "", "token": ""}
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("uazapi", {"url": "", "token": ""})
    except Exception as e:
        print(f"Error reading config: {e}")
        return {"url": "", "token": ""}

@router.post("/uazapi")
async def update_uazapi_config(config: UazapiConfig):
    current_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                current_config = json.load(f)
        except:
            pass
    
    current_config["uazapi"] = config.dict()
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f, indent=2)
        return {"message": "Configuração atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configuração: {str(e)}")

class TimezoneConfig(BaseModel):
    timezone: str

@router.get("/timezone")
async def get_timezone_config():
    default_tz = "America/Manaus"
    if not os.path.exists(CONFIG_FILE):
        return {"timezone": default_tz}
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return {"timezone": config.get("timezone", default_tz)}
    except Exception as e:
        print(f"Error reading config: {e}")
        return {"timezone": default_tz}

@router.post("/timezone")
async def update_timezone_config(config: TimezoneConfig):
    current_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                current_config = json.load(f)
        except:
            pass
    
    current_config["timezone"] = config.timezone
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f, indent=2)
        return {"message": "Configuração de fuso horário atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configuração: {str(e)}")

class UploadConfig(BaseModel):
    use_base64: bool
    public_url: str

@router.get("/upload")
async def get_upload_config():
    default_config = {"use_base64": True, "public_url": ""}
    if not os.path.exists(CONFIG_FILE):
        return default_config
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Tenta pegar 'upload', se não existir tenta migrar de 'ngrok' pra não perder a url, ou usa default
            up_cfg = config.get("upload")
            if up_cfg is None:
                ng_cfg = config.get("ngrok", {})
                up_cfg = {
                    "use_base64": True, # Default to True as requested
                    "public_url": ng_cfg.get("url", "")
                }
            return up_cfg
    except Exception as e:
        print(f"Error reading upload config: {e}")
        return default_config

@router.post("/upload")
async def update_upload_config(config: UploadConfig):
    current_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                current_config = json.load(f)
        except:
            pass
    
    current_config["upload"] = config.dict()
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f, indent=2)
        return {"message": "Configuração de Upload atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configuração: {str(e)}")


class AssinaturaConfig(BaseModel):
    assinatura_base64: str

@router.get("/assinatura")
async def get_assinatura_config():
    default = {"assinatura_base64": ""}
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("assinatura_locadora", default)
    except Exception as e:
        print(f"Error reading assinatura config: {e}")
        return default

class SenhaDescontoBody(BaseModel):
    senha: str


@router.post("/senha-desconto")
async def update_senha_desconto(body: SenhaDescontoBody, _: str = Depends(require_master)):
    """Persiste a senha de desconto no servidor (alinhada ao front) para validar consulta de senhas de funcionários."""
    if not body.senha or len(body.senha) < 1:
        raise HTTPException(status_code=400, detail="Senha inválida")
    cfg_api = _system_config_abs_path()
    cwd_cfg = os.path.abspath(CONFIG_FILE)
    write_path = cwd_cfg if os.path.exists(CONFIG_FILE) else cfg_api
    current_config = {}
    if os.path.exists(write_path):
        try:
            with open(write_path, "r", encoding="utf-8") as f:
                current_config = json.load(f)
        except Exception:
            pass
    current_config["senha_desconto"] = body.senha
    try:
        with open(write_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=2)
        return {"message": "Senha de desconto sincronizada no servidor"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")


@router.post("/assinatura")
async def update_assinatura_config(config: AssinaturaConfig):
    current_config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                current_config = json.load(f)
        except:
            pass

    current_config["assinatura_locadora"] = config.dict()

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(current_config, f, indent=2)
        return {"message": "Assinatura da locadora atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar assinatura: {str(e)}")
