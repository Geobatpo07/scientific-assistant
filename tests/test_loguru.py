"""Test script to verify Loguru integration."""

from app.utils.logger import get_logger

# Test basic logging
logger = get_logger(__name__)

print("Testing Loguru integration...")
print("=" * 70)

# Test different log levels
logger.debug("This is a DEBUG message")
logger.info("This is an INFO message")
logger.warning("This is a WARNING message")
logger.error("This is an ERROR message")

# Test with context
logger.info("User action", user="john_doe", action="login")

# Test exception logging
try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("An error occurred during division")

# Test logger with name binding
named_logger = get_logger("my_module")
named_logger.info("Message from named logger")

print("=" * 70)
print("✅ Loguru integration test completed!")
print("Check the logs/ directory for log files.")
