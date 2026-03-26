from typing import Dict, Callable, Optional
import time
from core.loki_handler import get_loki_logger
from core.exceptions import RequestError

helper_logger = get_loki_logger("helper", {"app": "helper", "env": "dev"})

class Headers:
    def __init__(self, accept: str, user_agent: str, accept_language: str, authorization: Optional[str] = None) -> None:
        self.accept = accept
        self.user_agent = user_agent
        self.accept_language = accept_language
        self.authorization = authorization
    
    def build_header(self) -> Dict[str, str]:
        headers = {}
        headers["accept"] = self.accept
        headers["user-agent"] = self.user_agent
        headers["accept-language"] = self.accept_language
        headers["authorization"] = self.authorization
        
        return headers

def to_float(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def to_int(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None 

def retry(function: Callable, retries: int = 3, delay: float = 1.5):
    for attempt in range(1, retries + 1):
        try:
            result = function()
            
            if result is None:
                raise ValueError("Function returned None")
            
            return result
        except RequestError as e:
            helper_logger.error(f"Retry attempt {attempt} of {retries} because of error: {str(e)}")
            if attempt == retries:
                helper_logger.error("Retry attempts exceeded")  
                raise
            time.sleep(delay)
        
        except Exception as e:
            helper_logger.error(f"Non-retryable error: {e}")
            raise