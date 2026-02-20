"""LaTeX generation and equation handling."""

from typing import Optional


class LaTeXGenerator:
    """Generate LaTeX equations and documents."""
    
    @staticmethod
    def create_document(title: str, content: str, author: str = "Teslas.ai") -> str:
        """Create a complete LaTeX document."""
        latex = f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}

\\title{{{title}}}
\\author{{{author}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\tableofcontents

{content}

\\end{{document}}
"""
        return latex
    
    @staticmethod
    def equation(expr: str, label: Optional[str] = None) -> str:
        """Format equation in LaTeX."""
        if label:
            return f"\\begin{{equation}}\\label{{{label}}}\n{expr}\n\\end{{equation}}"
        else:
            return f"\\begin{{equation*}}\n{expr}\n\\end{{equation*}}"
    
    @staticmethod
    def inline_equation(expr: str) -> str:
        """Format inline equation."""
        return f"${expr}$"
    
    @staticmethod
    def matrix(data: list, brackets: str = "pmatrix") -> str:
        """Create LaTeX matrix."""
        rows = []
        for row in data:
            rows.append(" & ".join(str(x) for x in row))
        
        matrix_str = " \\\\ ".join(rows)
        return f"\\begin{{{brackets}}}\n{matrix_str}\n\\end{{{brackets}}}"
    
    @staticmethod
    def fraction(numerator: str, denominator: str) -> str:
        """Create fraction."""
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    
    @staticmethod
    def section(title: str, content: str) -> str:
        """Create LaTeX section."""
        return f"\\section{{{title}}}\n\n{content}\n"
    
    @staticmethod
    def subsection(title: str, content: str) -> str:
        """Create LaTeX subsection."""
        return f"\\subsection{{{title}}}\n\n{content}\n"
