"""Structured logging configuration for Teslas.ai."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from app.config import settings


def setup_logging() -> None:
    """Configure structured logging with structlog and stdlib logging."""
    
    # Configure standard library logging
    stdlib_log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create logs directory if it doesn't exist
    logs_dir = settings.PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(logs_dir / "teslas_ai.log")
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_formatter = logging.Formatter(stdlib_log_format)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_formatter = logging.Formatter(stdlib_log_format)
    console_handler.setFormatter(console_formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer()
        )
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance with structured logging."""
    return structlog.get_logger(name)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "custom_data"):
            log_data.update(record.custom_data)  # type: ignore
        
        return json.dumps(log_data)
