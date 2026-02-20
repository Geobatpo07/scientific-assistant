"""Logging configuration with Loguru."""

import sys
from pathlib import Path

from loguru import logger

from app.config import settings

# Remove default handler
logger.remove()

# Create logs directory if it doesn't exist
logs_dir = settings.PROJECT_ROOT / "logs"
logs_dir.mkdir(exist_ok=True)

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Add file handler with rotation
logger.add(
    logs_dir / "scientific_assistant_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    rotation="00:00",  # New file every day at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    enqueue=True,  # Thread-safe
)

# Add JSON file handler if LOG_FORMAT is json
if hasattr(settings, 'LOG_FORMAT') and settings.LOG_FORMAT == "json":
    logger.add(
        logs_dir / "scientific_assistant_{time:YYYY-MM-DD}.json",
        format="{message}",
        level=settings.LOG_LEVEL,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        serialize=True,  # Output as JSON
        enqueue=True,
    )


def setup_logging() -> None:
    """Setup logging configuration.
    
    Note: Loguru is auto-configured on import, but this function
    is kept for backward compatibility with existing code.
    """
    pass


def get_logger(name: str = None):
    """Get a logger instance.
    
    Args:
        name: Logger name (optional, for backward compatibility)
        
    Returns:
        Loguru logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger
