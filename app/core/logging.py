import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Structured JSON logging for production."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[handler],
        force=True
    )

    # Reduce noise from third party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)