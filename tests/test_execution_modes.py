"""Tests for ExecutionMode system (FAST vs FULL modes).

Tests verify:
1. Mode configuration correctness
2. Agent selection based on mode
3. RAG parameter enforcement
4. API integration
5. Mode switching behavior
"""

import pytest
from unittest.mock import Mock, patch

from app.config import ExecutionMode, ModeConfig, get_settings
from app.agents.graph import TeslasAIOrchestrator
from app.agents.states import ResearchContext
from app.assistant import Assistant
from app.api.schemas import ResearchRequest


class TestExecutionModeConfig:
    """Test ExecutionMode enum and ModeConfig class."""
    
    def test_execution_mode_enum(self):
        """Test ExecutionMode enum values."""
        assert ExecutionMode.FAST == "fast"
        assert ExecutionMode.FULL == "full"
        assert len(ExecutionMode) == 2
    
    def test_agent_config_fast_mode(self):
        """Test agent configuration for FAST mode."""
        config = ModeConfig.get_agent_config(ExecutionMode.FAST)
        
        # FAST mode should disable reviewer and memory
        assert config["reviewer"] is False
        assert config["memory"] is False
        assert config["data_scientist"] is False
        
        # Writer should always be enabled
        assert config["writer"] is True
        
        # Optional agents should be marked as such
        assert config["planner"] == "optional"
        assert config["mathematician"] == "optional"
    
    def test_agent_config_full_mode(self):
        """Test agent configuration for FULL mode."""
        config = ModeConfig.get_agent_config(ExecutionMode.FULL)
        
        # FULL mode should enable all agents
        assert config["planner"] is True
        assert config["mathematician"] is True
        assert config["numerical"] is True
        assert config["data_scientist"] is True
        assert config["literature"] is True
        assert config["reviewer"] is True
        assert config["writer"] is True
        assert config["memory"] is True
    
    def test_rag_config_fast_mode(self):
        """Test RAG configuration for FAST mode."""
        config = ModeConfig.get_rag_config(ExecutionMode.FAST)
        
        assert config["faiss_top_k"] == 15
        assert config["final_chunks"] == 3
        assert config["rerank_enabled"] is True
        assert config["context_compression"] is True
        assert config["web_search_enabled"] is False
    
    def test_rag_config_full_mode(self):
        """Test RAG configuration for FULL mode."""
        config = ModeConfig.get_rag_config(ExecutionMode.FULL)
        
        assert config["faiss_top_k"] == 30
        assert config["final_chunks"] == 5
        assert config["rerank_enabled"] is True
        assert config["context_compression"] is True
        assert config["web_search_enabled"] is True
    
    def test_llm_config_fast_mode(self):
        """Test LLM configuration for FAST mode."""
        config = ModeConfig.get_llm_config(ExecutionMode.FAST)
        
        assert config["temperature"] == 0.1
        assert config["max_tokens"] == 2000
        assert config["timeout"] == 120
    
    def test_llm_config_full_mode(self):
        """Test LLM configuration for FULL mode."""
        config = ModeConfig.get_llm_config(ExecutionMode.FULL)
        
        assert config["temperature"] == 0.3
        assert config["max_tokens"] == 4000
        assert config["timeout"] == 300
    
    def test_iteration_config_fast_mode(self):
        """Test iteration limits for FAST mode."""
        config = ModeConfig.get_iteration_config(ExecutionMode.FAST)
        
        assert config["max_iterations"] == 3
        assert config["max_agent_calls"] == 5
    
    def test_iteration_config_full_mode(self):
        """Test iteration limits for FULL mode."""
        config = ModeConfig.get_iteration_config(ExecutionMode.FULL)
        
        assert config["max_iterations"] == 10
        assert config["max_agent_calls"] == 20
    
    def test_is_agent_enabled_fast_mode(self):
        """Test agent enabled check for FAST mode."""
        # Disabled agents
        assert ModeConfig.is_agent_enabled(ExecutionMode.FAST, "reviewer") is False
        assert ModeConfig.is_agent_enabled(ExecutionMode.FAST, "memory") is False
        
        # Enabled agents
        assert ModeConfig.is_agent_enabled(ExecutionMode.FAST, "writer") is True
        
        # Optional agents return False (caller must decide)
        assert ModeConfig.is_agent_enabled(ExecutionMode.FAST, "planner") is False
    
    def test_is_agent_optional(self):
        """Test agent optional check."""
        assert ModeConfig.is_agent_optional(ExecutionMode.FAST, "planner") is True
        assert ModeConfig.is_agent_optional(ExecutionMode.FAST, "mathematician") is True
        assert ModeConfig.is_agent_optional(ExecutionMode.FAST, "reviewer") is False
        assert ModeConfig.is_agent_optional(ExecutionMode.FULL, "planner") is False


class TestOrchestratorModeAware:
    """Test orchestrator respects execution modes."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return TeslasAIOrchestrator()
    
    @pytest.fixture
    def mock_agents(self, orchestrator):
        """Mock all agent methods."""
        with patch.object(orchestrator.planner, 'plan') as mock_plan, \
             patch.object(orchestrator.mathematician, 'analyze') as mock_math, \
             patch.object(orchestrator.numerical, 'simulate') as mock_num, \
             patch.object(orchestrator.data_scientist, 'analyze') as mock_data, \
             patch.object(orchestrator.literature, 'research') as mock_lit, \
             patch.object(orchestrator.reviewer, 'review') as mock_review, \
             patch.object(orchestrator.writer, 'write') as mock_write, \
             patch.object(orchestrator.memory, 'curate') as mock_memory:
            
            # Configure mocks to return context
            def return_context(query_or_context, context=None):
                ctx = context if context is not None else query_or_context
                if isinstance(ctx, str):
                    ctx = ResearchContext(main_query=ctx)
                return ctx
            
            mock_plan.side_effect = return_context
            mock_math.side_effect = return_context
            mock_num.side_effect = return_context
            mock_data.side_effect = return_context
            mock_lit.side_effect = return_context
            mock_review.side_effect = return_context
            mock_write.side_effect = return_context
            mock_memory.side_effect = return_context
            
            yield {
                'planner': mock_plan,
                'mathematician': mock_math,
                'numerical': mock_num,
                'data_scientist': mock_data,
                'literature': mock_lit,
                'reviewer': mock_review,
                'writer': mock_write,
                'memory': mock_memory,
            }
    
    def test_fast_mode_skips_reviewer_and_memory(self, orchestrator, mock_agents):
        """Test FAST mode skips reviewer and memory agents."""
        result = orchestrator.run_research("test query", mode=ExecutionMode.FAST)
        
        # Reviewer and memory should not be called in FAST mode
        assert mock_agents['reviewer'].call_count == 0
        assert mock_agents['memory'].call_count == 0
        
        # Writer should always be called
        assert mock_agents['writer'].call_count == 1
        
        # Check metadata
        assert result.metadata['execution_mode'] == 'fast'
    
    def test_full_mode_runs_all_agents(self, orchestrator, mock_agents):
        """Test FULL mode attempts to run all relevant agents."""
        # Create a research plan that requires all analyses
        plan_result = ResearchContext(main_query="test query")
        plan_result.research_plan = Mock()
        plan_result.research_plan.required_analyses = ["mathematical", "numerical", "data", "literature"]
        
        mock_agents['planner'].return_value = plan_result
        
        result = orchestrator.run_research("test query", mode=ExecutionMode.FULL)
        
        # In FULL mode, all agents should be called (if required by plan)
        assert mock_agents['planner'].call_count == 1
        assert mock_agents['reviewer'].call_count == 1
        assert mock_agents['writer'].call_count == 1
        assert mock_agents['memory'].call_count == 1
        
        # Check metadata
        assert result.metadata['execution_mode'] == 'full'
    
    def test_fast_mode_respects_agent_call_limit(self, orchestrator, mock_agents):
        """Test FAST mode stops at agent call limit."""
        # Create plan requiring all analyses
        plan_result = ResearchContext(main_query="test query")
        plan_result.research_plan = Mock()
        plan_result.research_plan.required_analyses = ["mathematical", "numerical", "data", "literature"]
        
        mock_agents['planner'].return_value = plan_result
        
        result = orchestrator.run_research("test query", mode=ExecutionMode.FAST)
        
        # FAST mode has max_agent_calls=5, should not exceed
        total_calls = sum(mock.call_count for mock in mock_agents.values())
        assert total_calls <= 5
        
        # Check metadata
        assert result.metadata.get('agent_calls', 0) <= 5
    
    def test_selective_mode_with_fast_params(self, orchestrator, mock_agents):
        """Test selective agents with FAST mode parameters."""
        result = orchestrator.run_research_selective(
            "test query",
            agents=["mathematician", "writer"],
            mode=ExecutionMode.FAST
        )
        
        # Only specified agents should be called
        assert mock_agents['mathematician'].call_count == 1
        assert mock_agents['writer'].call_count == 1
        
        # Others should not be called
        assert mock_agents['reviewer'].call_count == 0
        assert mock_agents['memory'].call_count == 0
        
        # Check metadata
        assert result.metadata['execution_mode'] == 'fast'
        assert result.metadata['selective_agents'] == ["mathematician", "writer"]


class TestAssistantModeSupport:
    """Test Assistant class mode support."""
    
    @pytest.fixture
    def assistant(self):
        """Create assistant instance."""
        return Assistant()
    
    @patch('app.assistant.create_orchestrator')
    def test_assistant_passes_mode_to_orchestrator(self, mock_create_orch, assistant):
        """Test Assistant passes mode to orchestrator."""
        mock_orchestrator = Mock()
        mock_create_orch.return_value = mock_orchestrator
        
        # Recreate assistant to use mock
        assistant._orchestrator = mock_orchestrator
        
        # Call with FAST mode
        assistant.research("test query", mode=ExecutionMode.FAST)
        mock_orchestrator.run_research.assert_called_once_with("test query", ExecutionMode.FAST)
        
        # Call with FULL mode
        assistant.research("test query 2", mode=ExecutionMode.FULL)
        mock_orchestrator.run_research.assert_called_with("test query 2", ExecutionMode.FULL)
    
    @patch('app.assistant.create_orchestrator')
    def test_assistant_default_mode_is_fast(self, mock_create_orch, assistant):
        """Test Assistant defaults to FAST mode."""
        mock_orchestrator = Mock()
        mock_create_orch.return_value = mock_orchestrator
        assistant._orchestrator = mock_orchestrator
        
        # Call without mode parameter
        assistant.research("test query")
        
        # Should default to FAST
        mock_orchestrator.run_research.assert_called_once_with("test query", ExecutionMode.FAST)


class TestAPISchemas:
    """Test API schemas support execution modes."""
    
    def test_research_request_default_mode(self):
        """Test ResearchRequest defaults to FAST mode."""
        request = ResearchRequest(query="test query")
        
        assert request.mode == ExecutionMode.FAST
        assert request.query == "test query"
    
    def test_research_request_accepts_fast_mode(self):
        """Test ResearchRequest accepts FAST mode string."""
        request = ResearchRequest(query="test query", mode="fast")
        
        assert request.mode == ExecutionMode.FAST
    
    def test_research_request_accepts_full_mode(self):
        """Test ResearchRequest accepts FULL mode string."""
        request = ResearchRequest(query="test query", mode="full")
        
        assert request.mode == ExecutionMode.FULL
    
    def test_research_request_with_enum(self):
        """Test ResearchRequest accepts ExecutionMode enum."""
        request = ResearchRequest(query="test query", mode=ExecutionMode.FULL)
        
        assert request.mode == ExecutionMode.FULL


class TestRAGModeAware:
    """Test RAG chain respects execution modes."""
    
    @pytest.fixture
    def mock_rag_chain(self):
        """Create mock RAG chain."""
        from app.rag.chains import RAGChain
        
        with patch.object(RAGChain, '__init__', return_value=None):
            chain = RAGChain()
            chain.llm = Mock()
            chain.vector_store = Mock()
            chain.retriever = Mock()
            chain.context_engineer = Mock()
            
            # Mock methods
            chain.context_engineer.normalize_query.return_value = "normalized query"
            chain.context_engineer.compress_context_batch.return_value = ["compressed1", "compressed2"]
            chain.retriever.retrieve_with_metadata.return_value = [
                {"content": "doc1", "source": "source1"},
                {"content": "doc2", "source": "source2"},
            ]
            chain.llm.invoke.return_value = Mock(content="LLM response")
            
            return chain
    
    def test_fast_mode_uses_correct_k_values(self, mock_rag_chain):
        """Test FAST mode uses correct retrieval parameters."""
        result = mock_rag_chain.retrieve_and_generate(
            "test query",
            mode=ExecutionMode.FAST
        )
        
        # Should use FAST mode k=15
        mock_rag_chain.retriever.retrieve_with_metadata.assert_called_once_with(
            "normalized query", k=15
        )
        
        # Result should include mode
        assert result['mode'] == 'fast'
    
    def test_full_mode_uses_correct_k_values(self, mock_rag_chain):
        """Test FULL mode uses correct retrieval parameters."""
        result = mock_rag_chain.retrieve_and_generate(
            "test query",
            mode=ExecutionMode.FULL
        )
        
        # Should use FULL mode k=30
        mock_rag_chain.retriever.retrieve_with_metadata.assert_called_once_with(
            "normalized query", k=30
        )
        
        # Result should include mode
        assert result['mode'] == 'full'


class TestModeSwitching:
    """Test switching between modes works correctly."""
    
    @patch('app.assistant.create_orchestrator')
    def test_switch_modes_between_requests(self, mock_create_orch):
        """Test switching modes between consecutive requests."""
        assistant = Assistant()
        mock_orchestrator = Mock()
        mock_create_orch.return_value = mock_orchestrator
        assistant._orchestrator = mock_orchestrator
        
        # First request: FAST
        assistant.research("query 1", mode=ExecutionMode.FAST)
        assert mock_orchestrator.run_research.call_args[0][1] == ExecutionMode.FAST
        
        # Second request: FULL
        assistant.research("query 2", mode=ExecutionMode.FULL)
        assert mock_orchestrator.run_research.call_args[0][1] == ExecutionMode.FULL
        
        # Third request: back to FAST
        assistant.research("query 3", mode=ExecutionMode.FAST)
        assert mock_orchestrator.run_research.call_args[0][1] == ExecutionMode.FAST


class TestModeConfiguration:
    """Test mode configuration consistency."""
    
    def test_fast_mode_is_faster_than_full(self):
        """Test FAST mode has lower resource limits than FULL."""
        fast_rag = ModeConfig.get_rag_config(ExecutionMode.FAST)
        full_rag = ModeConfig.get_rag_config(ExecutionMode.FULL)
        
        assert fast_rag["faiss_top_k"] < full_rag["faiss_top_k"]
        assert fast_rag["final_chunks"] < full_rag["final_chunks"]
        
        fast_iter = ModeConfig.get_iteration_config(ExecutionMode.FAST)
        full_iter = ModeConfig.get_iteration_config(ExecutionMode.FULL)
        
        assert fast_iter["max_iterations"] < full_iter["max_iterations"]
        assert fast_iter["max_agent_calls"] < full_iter["max_agent_calls"]
        
        fast_llm = ModeConfig.get_llm_config(ExecutionMode.FAST)
        full_llm = ModeConfig.get_llm_config(ExecutionMode.FULL)
        
        assert fast_llm["temperature"] < full_llm["temperature"]
        assert fast_llm["max_tokens"] < full_llm["max_tokens"]
    
    def test_all_modes_have_complete_config(self):
        """Test all modes have complete configuration."""
        for mode in ExecutionMode:
            # All configs should exist
            agent_config = ModeConfig.get_agent_config(mode)
            rag_config = ModeConfig.get_rag_config(mode)
            llm_config = ModeConfig.get_llm_config(mode)
            iter_config = ModeConfig.get_iteration_config(mode)
            
            # Agent config should have all agents
            required_agents = ["planner", "mathematician", "numerical", 
                             "data_scientist", "literature", "reviewer", 
                             "writer", "memory"]
            for agent in required_agents:
                assert agent in agent_config
            
            # RAG config should have all parameters
            assert "faiss_top_k" in rag_config
            assert "final_chunks" in rag_config
            assert "rerank_enabled" in rag_config
            
            # LLM config should have all parameters
            assert "temperature" in llm_config
            assert "max_tokens" in llm_config
            assert "timeout" in llm_config
            
            # Iteration config should have all parameters
            assert "max_iterations" in iter_config
            assert "max_agent_calls" in iter_config


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
