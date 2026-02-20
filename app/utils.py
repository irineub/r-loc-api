
import json
import os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older python versions if pytz is available
    from pytz import timezone as ZoneInfo

CONFIG_FILE = "system_config.json"

def get_configured_timezone() -> str:
    """Retorna a string do fuso horário configurado"""
    timezone_str = "America/Manaus"
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                timezone_str = config.get("timezone", "America/Manaus")
        except:
            pass
    return timezone_str

def get_current_time() -> datetime:
    """Retorna a data e hora atual no fuso horário configurado"""
    timezone_str = get_configured_timezone()
    try:
        return datetime.now(ZoneInfo(timezone_str))
    except Exception as e:
        print(f"Erro ao obter hora no fuso {timezone_str}: {e}")
        return datetime.now()
