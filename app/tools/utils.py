"""Tool utilities."""

from typing import Any, Dict, List


def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Format data as ASCII table."""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create table
    lines = []
    
    # Header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        lines.append(row_line)
    
    return "\n".join(lines)


def format_list(items: List[str], numbered: bool = False) -> str:
    """Format list of items."""
    lines = []
    for i, item in enumerate(items, 1):
        if numbered:
            lines.append(f"{i}. {item}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)
