"""Advanced Loguru features demonstration."""

from app.utils.logger import get_logger, logger

print("=" * 80)
print("Loguru Advanced Features Demo")
print("=" * 80)

# 1. Basic usage
print("\n1. Basic logging levels")
print("-" * 80)
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
logger.critical("This is critical!")

# 2. Structured logging with context
print("\n2. Structured logging")
print("-" * 80)
logger.info("User logged in", username="alice", ip="192.168.1.1")
logger.info("Processing started", task_id=12345, items=150)

# 3. Binding context to logger
print("\n3. Context binding")
print("-" * 80)
request_logger = logger.bind(request_id="abc-123", user_id=42)
request_logger.info("Processing user request")
request_logger.info("Request completed successfully")

# 4. Exception handling
print("\n4. Exception handling")
print("-" * 80)
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.exception("Division by zero occurred")

try:
    data = {"key": "value"}
    value = data["missing_key"]
except KeyError as e:
    logger.error("Key not found: {}", e)

# 5. Using logger with names
print("\n5. Named loggers")
print("-" * 80)
api_logger = get_logger("api")
db_logger = get_logger("database")
cache_logger = get_logger("cache")

api_logger.info("API endpoint called: /users/123")
db_logger.info("Query executed", duration_ms=45)
cache_logger.info("Cache hit", key="user:123")

# 6. Lazy evaluation for expensive operations
print("\n6. Lazy evaluation (performance)")
print("-" * 80)

def expensive_computation():
    """Simulates an expensive operation."""
    import time
    time.sleep(0.001)
    return "Expensive result"

# This won't call expensive_computation() because level is INFO
logger.opt(lazy=True).debug("Debug with expensive: {result}", result=expensive_computation)
logger.info("This is INFO level - expensive computation skipped above!")

# 7. Catch decorator
print("\n7. Catch decorator for automatic exception logging")
print("-" * 80)

@logger.catch
def risky_function():
    """Function that might fail."""
    numbers = [1, 2, 3]
    return numbers[10]  # Will raise IndexError

try:
    risky_function()
except IndexError:
    logger.info("Exception was caught and logged automatically!")

# 8. Record extra information
print("\n8. Recording extra metadata")
print("-" * 80)
logger.bind(
    environment="production",
    version="0.2.0",
    host="server-01"
).info("Application started")

# 9. Formatting options
print("\n9. Custom formatting in messages")
print("-" * 80)
items = ["apple", "banana", "cherry"]
logger.info("Processing {} items: {}", len(items), items)

user = {"name": "John", "age": 30}
logger.info("User data: {user}", user=user)

# 10. Performance metrics
print("\n10. Performance logging")
print("-" * 80)
import time

start_time = time.time()
time.sleep(0.1)  # Simulate work
duration = time.time() - start_time

logger.info("Operation completed", duration_ms=round(duration * 1000, 2))

# 11. Conditional logging
print("\n11. Conditional logging")
print("-" * 80)
debug_mode = False

if debug_mode:
    logger.debug("Debug information (only when debug_mode=True)")

logger.info("Info message (always shown)")

# 12. Multiple contexts
print("\n12. Chaining contexts")
print("-" * 80)
with_request = logger.bind(request_id="req-456")
with_user = with_request.bind(user_id=789)
with_session = with_user.bind(session_id="sess-xyz")

with_session.info("Complex context logging")

print("\n" + "=" * 80)
print("✅ Demo completed! Check logs/scientific_assistant_*.log for output")
print("=" * 80)
