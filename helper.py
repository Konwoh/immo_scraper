from typing import Dict

class Headers:
    def __init__(self, accept, user_agent, accept_language) -> None:
        self.accept = accept
        self.user_agent = user_agent
        self.accept_language = accept_language
    
    def build_header(self) -> Dict[str, str]:
        headers = {}
        headers["accept"] = self.accept
        headers["user-agent"] = self.user_agent
        headers["accept-language"] = self.accept_language
        
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