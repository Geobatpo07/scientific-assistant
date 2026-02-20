"""Python code execution and sandboxing."""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PythonExecutor:
    """Safe Python code execution."""
    
    @staticmethod
    def execute_code(code: str, timeout: int = 30) -> dict:
        """Execute Python code and return output."""
        logger.info("Executing Python code")
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute code
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
                
            finally:
                # Clean up
                Path(temp_file).unlink()
                
        except subprocess.TimeoutExpired:
            logger.error("Code execution timed out")
            return {
                "success": False,
                "error": "Execution timed out",
            }
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
    
    @staticmethod
    def execute_with_context(
        code: str,
        context: dict = None,
        timeout: int = 30,
    ) -> dict:
        """Execute code with predefined context."""
        if context is None:
            context = {}
        
        # Build code with imports and context
        full_code = """
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt

# Context variables
"""
        
        for key, value in context.items():
            full_code += f"{key} = {repr(value)}\n"
        
        full_code += "\n" + code
        
        return PythonExecutor.execute_code(full_code, timeout)
