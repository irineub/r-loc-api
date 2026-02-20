from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import json
import os

router = APIRouter()

CONFIG_FILE = "system_config.json"

class UazapiConfig(BaseModel):
    url: str
    token: str

@router.get("/config/uazapi")
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

@router.post("/config/uazapi")
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

@router.get("/config/timezone")
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

@router.post("/config/timezone")
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
