import json
import logging
import os
import requests
from datetime import datetime, timezone
from threading import Thread

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        return json.dumps(log_entry, default=str, ensure_ascii=False)

class LokiHandler(logging.Handler):
    def __init__(self, loki_url, labels):
        super().__init__()
        self.loki_url = loki_url
        self.labels = labels

    def emit(self, record):
        log_entry = self.format(record)
        stream = {**self.labels, "level": record.levelname.lower(),"logger": record.name}
        payload = {
            "streams": [
                {
                    "stream": stream,
                    "values": [
                        [str(int(datetime.now(timezone.utc).timestamp() * 1e9)), log_entry, ]
                    ],
                }
            ]
        }
        Thread(target=self._send_log, args=(payload,)).start()

    def _send_log(self, payload):
        try:
            response = requests.post(
                f"{self.loki_url}/loki/api/v1/push",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=2,
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to push log to Loki: {e}")


def get_loki_logger(name: str, labels: dict[str, str]) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    logger.propagate = False

    if any(isinstance(handler, LokiHandler) for handler in logger.handlers):
        return logger

    formatter = JsonFormatter()
    loki_handler = LokiHandler(
        loki_url=os.getenv("LOKI_URL", "http://localhost:3100"),
        labels=labels,
    )
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)
    return logger
