"""Reviewer Agent - Scientific quality review with anti-hallucination validation."""

from typing import Optional
import numpy as np
import sympy as sp

from app.agents.states import ResearchContext
from app.llm.ollama import get_llm
from app.llm.prompts import AgentRole, get_system_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReviewerAgent:
    """Review and critique research for quality."""
    
    def __init__(self):
        """Initialize reviewer agent."""
        self.llm = get_llm(temperature=0.2)
        self.system_prompt = get_system_prompt(AgentRole.REVIEWER)
    
    def review(self, context: ResearchContext) -> ResearchContext:
        """Review all research conducted with anti-hallucination validation."""
        logger.info("Conducting scientific review with anti-hallucination checks...")
        
        try:
            # Run anti-hallucination checks (before LLM review)
            math_issues = self._validate_mathematics(context)
            numerical_issues = self._validate_numerical_results(context)
            consistency_issues = self._validate_consistency(context)
            data_science_issues = self._validate_data_science(context)
            
            logger.info(
                "Validation results",
                math_issues=len(math_issues),
                numerical_issues=len(numerical_issues),
                consistency_issues=len(consistency_issues),
                data_science_issues=len(data_science_issues),
            )
            
            # Compile research summary with findings
            research_summary = self._compile_summary(context)
            
            # Generate review prompt with validation findings
            review_prompt = f"""{self.system_prompt}

Research Summary:
{research_summary}

Pre-validation Findings:
- Mathematical errors: {len(math_issues)}
- Numerical stability issues: {len(numerical_issues)}
- Consistency problems: {len(consistency_issues)}
- Data science concerns: {len(data_science_issues)}

Critical Issues to Address:
{self._format_issues(math_issues + numerical_issues + consistency_issues + data_science_issues)}

Please provide a rigorous scientific review addressing the above issues:
1. Mathematical correctness check (verify equations are parseable and meaningful)
2. Numerical validity assessment (check for NaN, Inf, unrealistic values)
3. Identification of assumptions (list all implicit assumptions)
4. Potential errors or issues (especially related to the pre-validation findings)
5. Suggestions for improvement (how to strengthen weak areas)
6. Reproducibility assessment (can someone else reproduce this?)

Be constructive but thorough."""
            
            # Get review from LLM (ChatOllama)
            review_text = ""
            try:
                llm_resp = self.llm.invoke(review_prompt)
                review_text = getattr(llm_resp, "content", str(llm_resp))
            except Exception as llm_err:
                logger.warning(f"LLM review invocation failed: {llm_err}")
                review_text = "Review unavailable from LLM; proceeding with validator findings and suggestions."
            
            # Extract critique and improvements
            criticisms = self._extract_criticisms(review_text)
            improvements = self._extract_improvements(review_text)
            
            # Add validation findings to criticisms
            criticisms.extend(math_issues)
            criticisms.extend(numerical_issues)
            criticisms.extend(consistency_issues)
            criticisms.extend(data_science_issues)
            
            context.criticisms.extend(criticisms)
            context.improvements.extend(improvements)
            context.execution_path.append("reviewer")
            
            logger.info(f"Review completed: {len(criticisms)} total issues identified")
            
        except Exception as e:
            logger.error(f"Review error: {str(e)}")
            context.errors.append(f"Review failed: {str(e)}")
        
        return context
    
    @staticmethod
    def _validate_mathematics(context: ResearchContext) -> list:
        """Validate mathematical correctness using SymPy with advanced applied math checks.
        
        Checks for:
        - Hallucinated/trivial equations
        - Unparseable expressions
        - Proofs that are too short or use logical shortcuts
        - Vague mathematical insights
        - Advanced mathematics validity:
          * Convergence and limits
          * Boundary conditions
          * Domain restrictions
          * Stability analysis
          * Approximation quality
        """
        issues = []
        
        # Check for hallucinated equations
        for eq in context.final_equations:
            try:
                # Try to parse as sympy expression
                parsed = sp.sympify(eq, strict=False)
                parsed_str = str(parsed)
                
                # Check if equation is too simple/trivial
                if parsed_str in ["0", "1", "True", "False", "nan", "oo"]:
                    issues.append(f"❌ HALLUCI: Trivial equation: {eq}")
                
                # Check for malformed expressions
                if "nan" in parsed_str.lower() or "oo" in parsed_str:
                    issues.append(f"❌ HALLUCI: Invalid equation (NaN/Inf): {eq}")
                    
                # Check for overly complex expressions that may be noise
                if len(eq) > 200:
                    issues.append(f"⚠ Equation suspiciously complex (possible noise): {eq[:80]}...")
                
                # Advanced: Check for common mathematical errors
                # Detect division by potentially zero terms
                if "/" in eq or "1/(" in eq:
                    try:
                        # Extract denominators and check for zero risk
                        if "x=0" in eq or "(0)" in eq or "divide" in eq.lower():
                            issues.append(
                                f"⚠ Equation {eq[:60]}... may have division by zero issues"
                            )
                    except:
                        pass
                
                # Check for negative values under square roots
                if "sqrt(" in eq.lower() or "**0.5" in eq:
                    if "-" in eq and "sqrt" in eq.lower():
                        issues.append(
                            f"⚠ Equation {eq[:60]}... may have sqrt of negative (check domain)"
                        )
                
                # Check for logarithm domain issues
                if "log(" in eq.lower() or "ln(" in eq.lower():
                    # Log needs positive argument
                    issues.append(
                        f"⚠ Logarithm in equation {eq[:60]}... - verify argument is positive"
                    )
                    
            except Exception:
                issues.append(f"❌ HALLUCI: Unparseable equation (not valid math): {eq}")
        
        # Validate mathematical proofs
        for proof_name, proof_text in context.mathematical_proofs.items():
            word_count = len(proof_text.split())
            
            # Check proof length (too short = likely hallucination or stub)
            if word_count < 10 and word_count > 0:
                issues.append(f"❌ HALLUCI: Proof for '{proof_name}' too short ({word_count} words)")
            
            # Check for common logical shortcuts (skipping steps)
            fallacy_markers = [
                "obviously", "clearly", "trivially", "it's obvious",
                "as anyone can see", "without loss of generality",
                "by inspection", "by observation",
            ]
            if any(marker in proof_text.lower() for marker in fallacy_markers):
                issues.append(
                    f"⚠ Proof for '{proof_name}' uses shortcuts without justification"
                )
            
            # Check for vague language
            if proof_text.count("approximately") > 2 or proof_text.count("roughly") > 2:
                issues.append(f"⚠ Proof for '{proof_name}' lacks precision")
            
            # Advanced: Check for convergence discussion (if limits/series involved)
            has_series = any(
                kw in proof_text.lower()
                for kw in ["series", "sum", "infinite", "converge", "limit"]
            )
            if has_series and "converge" not in proof_text.lower():
                issues.append(
                    f"⚠ Proof for '{proof_name}' mentions series/limits but lacks convergence analysis"
                )
            
            # Advanced: Check for boundary condition discussion
            has_boundary_ops = any(
                kw in proof_text.lower()
                for kw in ["boundary", "pde", "differential", "integral", "equation"]
            )
            if has_boundary_ops and "boundary" not in proof_text.lower():
                issues.append(
                    f"⚠ Proof for '{proof_name}' involves DEs/integrals but lacks boundary condition specification"
                )
            
            # Advanced: Check for stability/uniqueness discussion
            has_stability_keywords = any(
                kw in proof_text.lower()
                for kw in ["stability", "well-posed", "uniqueness", "existence"]
            )
            if "differential" in proof_text.lower() and not has_stability_keywords:
                issues.append(
                    f"⚠ Proof for '{proof_name}' discusses DEs but lacks well-posedness/stability discussion"
                )
            
            # Advanced: Check for approximation error bounds
            has_approximation = any(
                kw in proof_text.lower()
                for kw in ["approximation", "approximate", "error", "accuracy"]
            )
            if has_approximation and "error" not in proof_text.lower():
                issues.append(
                    f"⚠ Proof for '{proof_name}' uses approximation but lacks error bound analysis"
                )
        
        # Check mathematical insights for vagueness and depth
        for insight in context.mathematical_insights:
            if len(insight) < 15:
                issues.append(f"⚠ Mathematical insight too vague: '{insight}'")
            
            # Check for circular/empty insights
            if insight.lower() in ["yes", "no", "maybe", "true", "false"]:
                issues.append(f"❌ HALLUCI: Empty mathematical insight: '{insight}'")
            
            # Advanced: Check for missing justification in optimization
            if any(kw in insight.lower() for kw in ["optimal", "maximum", "minimum", "extremum"]):
                if "lagrange" not in insight.lower() and "derivative" not in insight.lower():
                    if "condition" not in insight.lower():
                        issues.append(
                            f"⚠ Optimization claim '{insight}' lacks mention of optimality conditions"
                        )
            
            # Advanced: Check for missing constraint discussion
            if "constraint" in insight.lower():
                if len(insight.split()) < 15:
                    issues.append(
                        f"⚠ Constraint-based insight '{insight}' lacks sufficient explanation"
                    )
            
            # Advanced: Check for eigenvalue/matrix property claims
            if any(kw in insight.lower() for kw in ["eigenvalue", "eigenvector", "matrix", "diagonal"]):
                if "symmetric" not in insight.lower() and "positive" not in insight.lower():
                    issues.append(
                        f"⚠ Matrix property insight '{insight}' lacks specification of matrix type"
                    )
        
        # Advanced: Check for transform (Fourier, Laplace) validity
        for analysis in context.data_analysis:
            if any(kw in analysis.lower() for kw in ["fourier", "laplace", "transform", "spectrum"]):
                # Check for periodicity/causality discussion
                if "fourier" in analysis.lower():
                    if "periodic" not in analysis.lower() and "frequency" not in analysis.lower():
                        issues.append(
                            "⚠ Fourier analysis mentioned but lacks periodicity or frequency domain discussion"
                        )
                
                if "laplace" in analysis.lower():
                    if "causal" not in analysis.lower() and "convergence" not in analysis.lower():
                        issues.append(
                            "⚠ Laplace transform used but lacks causality or ROC discussion"
                        )
        
        # Advanced: Check for normalization/scaling issues
        has_normalization = any(
            kw in " ".join(context.mathematical_insights).lower()
            for kw in ["norm", "normalize", "scale", "standardize"]
        )
        
        if context.numerical_results and not has_normalization:
            # Check if results have vastly different scales
            vals = []
            for v in context.numerical_results.values():
                if isinstance(v, (int, float)):
                    vals.append(float(v))
            
            if len(vals) > 2:
                finite_vals = [v for v in vals if np.isfinite(v) and v != 0]
                if finite_vals:
                    val_range = max(np.abs(finite_vals)) / min(np.abs(finite_vals)) if min(np.abs(finite_vals)) > 0 else np.inf
                    if val_range > 1e6:
                        issues.append(
                            f"⚠ Results span {val_range:.2e} orders of magnitude - normalization recommended"
                        )
        
        return issues
    
    @staticmethod
    def _validate_numerical_results(context: ResearchContext) -> list:
        """Validate numerical results for stability, NaN, Inf, and convergence issues."""
        issues = []
        
        # Track statistics for pattern analysis
        result_values = []
        
        for result_name, result_value in context.numerical_results.items():
            try:
                # Handle different numeric types
                if isinstance(result_value, (int, float)):
                    val = float(result_value)
                    result_values.append((result_name, val))
                elif isinstance(result_value, list) and result_value:
                    try:
                        val = float(result_value[0])
                        result_values.append((result_name, val))
                    except (ValueError, TypeError):
                        pass
                elif isinstance(result_value, np.ndarray):
                    # Check array stability
                    arr = np.asarray(result_value, dtype=float)
                    if np.any(np.isnan(arr)):
                        issues.append(f"❌ CRITICAL: NaN in array '{result_name}'")
                    elif np.any(np.isinf(arr)):
                        issues.append(f"❌ CRITICAL: Infinity in array '{result_name}'")
                    else:
                        # Check condition number for matrices
                        if arr.ndim == 2:
                            try:
                                cond_number = np.linalg.cond(arr)
                                if cond_number > 1e10:
                                    issues.append(
                                        f"⚠ Array '{result_name}' is ill-conditioned (κ={cond_number:.2e})"
                                    )
                            except np.linalg.LinAlgError:
                                issues.append(f"⚠ Matrix '{result_name}' is singular or near-singular")
                
            except (ValueError, TypeError):
                # Skip non-numeric results
                pass
        
        # Analyze numerical result patterns
        if result_values:
            vals = np.array([v for _, v in result_values])
            
            for result_name, val in result_values:
                # Check for NaN
                if np.isnan(val):
                    issues.append(f"❌ CRITICAL: NaN in '{result_name}'")
                
                # Check for Inf
                elif np.isinf(val):
                    issues.append(f"❌ CRITICAL: Infinity in '{result_name}'")
                
                # Check for unrealistic magnitude (likely hallucination)
                elif abs(val) > 1e15:
                    issues.append(
                        f"❌ HALLUCI: Value unrealistically large: {result_name} = {val:.2e}"
                    )
                
                # Check for very small values (underflow)
                elif 0 < abs(val) < 1e-15 and result_name not in ["tolerance", "epsilon", "threshold"]:
                    issues.append(
                        f"⚠ Value suspiciously small (underflow): {result_name} = {val:.2e}"
                    )
                
                # Check for subnormal numbers (very small positive values)
                elif 0 < abs(val) < np.finfo(float).tiny:
                    issues.append(
                        f"⚠ Subnormal number detected in '{result_name}' = {val:.2e}"
                    )
            
            # Check for numerical stability across results
            finite_vals = vals[np.isfinite(vals)]
            if len(finite_vals) > 1:
                # Check for extreme value spread (ill-scaled results)
                val_range = np.ptp(finite_vals)
                val_max = np.max(np.abs(finite_vals))
                if val_max > 0:
                    relative_range = val_range / val_max
                    if relative_range > 1e10:
                        issues.append(
                            f"⚠ Results have extreme value spread (range/max = {relative_range:.2e})"
                        )
                
                # Check for loss of significance (many similar values)
                unique_ratio = len(np.unique(finite_vals)) / len(finite_vals)
                if unique_ratio < 0.3 and len(finite_vals) > 5:
                    issues.append(
                        f"⚠ Results may suffer from loss of significance ({unique_ratio*100:.0f}% unique)"
                    )
        
        # Validate numerical code for stability patterns
        for i, code_snippet in enumerate(context.numerical_code):
            # Check if code looks incomplete
            if len(code_snippet) > 50 and code_snippet.count("\n") < 2:
                if code_snippet.count("=") < 1:
                    issues.append(f"⚠ Code snippet {i} may be incomplete")
            
            # Check for dangerous patterns
            if "eval(" in code_snippet or "exec(" in code_snippet:
                issues.append(f"⚠ Code snippet {i} uses unsafe eval/exec")
            
            # Check for potential numerical instability patterns
            stability_warnings = [
                ("pow(", "exponential operations may overflow"),
                ("divide", "division by small numbers can be unstable"),
                ("/", "check denominators aren't near zero"),
                ("sqrt", "ensure argument is non-negative"),
                ("log", "logarithm of non-positive numbers causes NaN"),
            ]
            
            for pattern, warning in stability_warnings:
                if pattern in code_snippet.lower():
                    if "assert" not in code_snippet and "check" not in code_snippet.lower():
                        issues.append(f"⚠ Code snippet {i}: {warning} (no guard detected)")
        
        return issues
    
    @staticmethod
    def _validate_consistency(context: ResearchContext) -> list:
        """Cross-validate mathematical and numerical results for consistency."""
        issues = []
        
        # Check if equations and insights align
        if context.final_equations and context.mathematical_insights:
            eq_tokens = sum(len(e.split()) for e in context.final_equations)
            insight_tokens = sum(len(i.split()) for i in context.mathematical_insights)
            
            # If many equations but no insights, missing explanation
            if eq_tokens > 20 and insight_tokens < 10:
                issues.append(
                    "⚠ Many equations ({}) but few insights ({}) - missing explanation".format(
                        len(context.final_equations), len(context.mathematical_insights)
                    )
                )
            
            # If many insights but no equations, claims lack backing
            if insight_tokens > 30 and eq_tokens < 10:
                issues.append(
                    "⚠ Many insights ({}) but few equations ({}) - claims need math backing".format(
                        len(context.mathematical_insights), len(context.final_equations)
                    )
                )
        
        # Check if proofs and insights align
        if context.mathematical_proofs and not context.mathematical_insights:
            if len(context.mathematical_proofs) > 2:
                issues.append("⚠ Multiple proofs but no mathematical insights - analysis incomplete")
        
        # Check for repetitive insights (hallucination pattern)
        if len(context.mathematical_insights) > 2:
            unique_insights = len(set(context.mathematical_insights))
            if unique_insights < len(context.mathematical_insights) * 0.6:
                issues.append(
                    f"❌ HALLUCI: Insights are {(1 - unique_insights/len(context.mathematical_insights))*100:.0f}% "
                    f"repetitive - limited analysis"
                )
        
        # Check if numerical results relate to equations
        if context.numerical_results and context.final_equations:
            result_keys_count = len(context.numerical_results)
            eq_count = len(context.final_equations)
            
            # If many results but few equations, or vice versa
            if result_keys_count > 5 and eq_count < 2:
                issues.append(
                    "⚠ Many numerical results ({}) but few equations ({}) - may be unrelated".format(
                        result_keys_count, eq_count
                    )
                )
        
        # Check for empty/stub results
        empty_count = sum(
            1 for v in context.numerical_results.values()
            if v is None or v == "" or v == [] or v == {}
        )
        if empty_count > 0 and len(context.numerical_results) > 0:
            issues.append(
                f"⚠ {empty_count}/{len(context.numerical_results)} numerical results are empty"
            )
        
        return issues
    
    @staticmethod
    def _validate_data_science(context: ResearchContext) -> list:
        """Validate data science methodology and analysis quality.
        
        Checks for:
        - Sample size adequacy
        - Statistical significance awareness
        - Overfitting patterns
        - Missing data handling
        - Feature engineering validity
        - Model evaluation rigor
        """
        issues = []
        
        # Validate data analysis results
        for i, analysis in enumerate(context.data_analysis):
            if not analysis or len(analysis) < 20:
                issues.append(f"⚠ Data analysis result {i} appears incomplete or vague")
            
            # Check for statistical rigor keywords
            has_stats = any(
                keyword in analysis.lower()
                for keyword in ["statistic", "p-value", "confidence", "significant", "test"]
            )
            
            # Check for causation/correlation confusion
            if "cause" in analysis.lower() or "caused" in analysis.lower():
                if "correlation" in analysis.lower() or "relationship" in analysis.lower():
                    if "experiment" not in analysis.lower() and "control" not in analysis.lower():
                        issues.append(
                            f"⚠ Analysis {i} mentions causation but lacks experimental design justification"
                        )
            
            # Check for overfitting red flags
            if "fit" in analysis.lower() or "model" in analysis.lower():
                if "overfit" not in analysis.lower() and "validation" not in analysis.lower():
                    if "test" not in analysis.lower() and "train" not in analysis.lower():
                        issues.append(
                            f"⚠ Analysis {i} discusses modeling without mentioning train/test split or validation"
                        )
            
            # Check for missing value handling
            if "data" in analysis.lower() and "missing" not in analysis.lower():
                if "null" not in analysis.lower() and "nan" not in analysis.lower():
                    issues.append(
                        f"⚠ Analysis {i} processes data but doesn't mention handling of missing values"
                    )
        
        # Check data analysis depth vs other sections
        data_analysis_tokens = sum(len(a.split()) for a in context.data_analysis)
        math_tokens = sum(len(i.split()) for i in context.mathematical_insights)
        
        if context.data_analysis and data_analysis_tokens < 20 and len(context.data_analysis) > 1:
            issues.append(
                "❌ HALLUCI: Data analysis is superficial (avg < 10 words per analysis)"
            )
        
        # Check for unsubstantiated claims about data
        for analysis in context.data_analysis:
            vague_claims = [
                "very", "really", "quite", "seems to",
                "appears to", "might be", "could be",
            ]
            
            # Count vague language
            vague_count = sum(
                1 for claim in vague_claims if claim in analysis.lower()
            )
            
            if vague_count > 3 and len(analysis.split()) > 30:
                issues.append(
                    f"⚠ Analysis uses vague language ({vague_count} instances) instead of concrete metrics"
                )
        
        # Check for feature engineering validity
        if len(context.data_analysis) > 2:
            feature_keywords = ["feature", "variable", "attribute", "dimension", "column"]
            has_feature_discussion = any(
                any(kw in a.lower() for kw in feature_keywords)
                for a in context.data_analysis
            )
            
            if not has_feature_discussion and len(context.numerical_results) > 5:
                issues.append(
                    "⚠ Analysis has many numerical results but no discussion of feature engineering"
                )
        
        # Check model evaluation rigor
        for analysis in context.data_analysis:
            if "model" in analysis.lower() or "algorithm" in analysis.lower():
                evaluation_keywords = [
                    "accuracy", "precision", "recall", "f1", "auc", "rmse",
                    "mae", "r2", "confusion matrix", "roc",
                ]
                
                has_evaluation = any(kw in analysis.lower() for kw in evaluation_keywords)
                
                if not has_evaluation:
                    issues.append(
                        "⚠ Model/algorithm mentioned but no quantitative evaluation metrics provided"
                    )
        
        # Check for dataset size awareness
        has_size_mention = any(
            keyword in " ".join(context.data_analysis).lower()
            for keyword in ["samples", "observations", "rows", "size", "n=", "sample size"]
        )
        
        if context.data_analysis and not has_size_mention:
            if len(context.numerical_results) > 0:
                issues.append(
                    "⚠ Data analysis lacks mention of sample size (critical for statistical validity)"
                )
        
        # Check for bias/fairness awareness in ML context
        ml_keywords = ["machine learning", "classification", "regression", "prediction", "cluster"]
        has_ml = any(
            any(kw in a.lower() for kw in ml_keywords)
            for a in context.data_analysis
        )
        
        if has_ml:
            bias_keywords = ["bias", "fairness", "confound", "selection", "imbalance"]
            has_bias_check = any(
                any(kw in a.lower() for kw in bias_keywords)
                for a in context.data_analysis
            )
            
            if not has_bias_check:
                issues.append(
                    "⚠ Machine learning analysis lacks discussion of bias, fairness, or confounding"
                )
        
        return issues
    
    
    @staticmethod
    def _format_issues(issues: list) -> str:
        """Format validation issues for inclusion in LLM prompt."""
        if not issues:
            return "✓ No major issues detected in pre-validation."
        
        # Limit to top issues
        critical = [i for i in issues if "❌" in i]
        warnings = [i for i in issues if "⚠" in i]
        
        formatted = []
        if critical:
            formatted.append("CRITICAL ISSUES:")
            formatted.extend(critical[:5])
        if warnings:
            formatted.append("WARNINGS:")
            formatted.extend(warnings[:5])
        
        return "\n".join(formatted)
    
    @staticmethod
    def _compile_summary(context: ResearchContext) -> str:
        """Compile research summary for review."""
        summary = f"""Query: {context.main_query}

Mathematical Insights: {len(context.mathematical_insights)} items
- {context.mathematical_insights[:2] if context.mathematical_insights else 'None'}

Mathematical Proofs: {len(context.mathematical_proofs)} items
- {list(context.mathematical_proofs.keys())[:2] if context.mathematical_proofs else 'None'}

Final Equations: {len(context.final_equations)} items
- {context.final_equations[:1] if context.final_equations else 'None'}

Numerical Results: {len(context.numerical_results)} items
- Sample: {list(context.numerical_results.items())[:2] if context.numerical_results else 'None'}

Data Analysis Results: {len(context.data_analysis)} items

Literature Sources: {len(context.literature_sources)} references

Execution Path: {' -> '.join(context.execution_path)}

Errors Encountered: {len(context.errors)}
{context.errors[:2] if context.errors else 'None'}
"""
        return summary
    
    @staticmethod
    def _extract_criticisms(text: str) -> list:
        """Extract criticisms from review."""
        criticisms = []
        lines = text.split('\n')
        
        criticism_keywords = [
            "error", "issue", "problem", "concern", "incorrect",
            "missing", "incomplete", "inaccurate", "flaw", "weakness",
            "invalid", "wrong", "mistake", "gap", "limitation",
        ]
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in criticism_keywords):
                if line and len(line) > 10 and not line.startswith("http"):
                    criticisms.append(line)
        
        return criticisms[:15]
    
    @staticmethod
    def _extract_improvements(text: str) -> list:
        """Extract improvement suggestions."""
        improvements = []
        lines = text.split('\n')
        
        improvement_keywords = [
            "suggest", "recommend", "improve", "enhance", "could",
            "should", "consider", "try", "strengthen", "better",
            "refine", "extend", "expand", "add", "include",
        ]
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in improvement_keywords):
                if line and len(line) > 10 and not line.startswith("http"):
                    improvements.append(line)
        
        return improvements[:10]
