"""Tests for Teslas.ai agents."""

import pytest

from app.agents.planner import PlannerAgent
from app.agents.mathematician import MathematicalAnalystAgent
from app.agents.states import ResearchContext


@pytest.fixture
def research_context():
    """Create test research context."""
    return ResearchContext(main_query="Solve x^2 + 2x + 1 = 0")


def test_planner_agent():
    """Test planner agent."""
    planner = PlannerAgent()
    context = planner.plan("What is the derivative of x^2?")
    
    assert context.main_query == "What is the derivative of x^2?"
    assert context.research_plan is not None
    assert "planner" in context.execution_path


def test_mathematician_agent(research_context):
    """Test mathematical analyst agent."""
    mathematician = MathematicalAnalystAgent()
    context = mathematician.analyze(research_context.main_query, research_context)
    
    assert len(context.mathematical_insights) > 0
    assert "mathematician" in context.execution_path


def test_research_context():
    """Test research context."""
    context = ResearchContext(main_query="Test query")
    
    assert context.main_query == "Test query"
    assert len(context.execution_path) == 0
    assert len(context.errors) == 0
