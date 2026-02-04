"""Tests for Phase 1 agent."""
import pytest
import tempfile
from pathlib import Path
from repowiki.phases.phase1 import Phase1Agent
from repowiki.core.executor import TaskExecutor


class TestPhase1Agent:
    """Test cases for Phase1Agent."""
    
    def test_phase1_agent_simple_repo(self):
        """Test Phase 1 agent with simple repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a simple repository
            (tmppath / 'main.py').write_text('print("Hello")\n' * 5)
            (tmppath / 'utils.py').write_text('def helper():\n    pass\n' * 3)
            (tmppath / 'README.md').write_text('# Test\n' * 2)
            
            # Create subdirectory
            subdir = tmppath / 'src'
            subdir.mkdir()
            (subdir / 'module.py').write_text('class Test:\n    pass\n' * 2)
            
            # Create executor with temp state dir
            state_dir = tmppath / '.repowiki'
            executor = TaskExecutor(state_dir=state_dir)
            
            # Run analysis
            agent = Phase1Agent(str(tmppath), executor)
            assert agent.get_phase() == 1
            
            results = agent.analyze()
            
            assert results['phase'] == 1
            assert results['file_count'] > 0
            assert 'summary' in results
            assert 'file_analysis' in results
    
    def test_phase1_agent_empty_repo(self):
        """Test Phase 1 agent with empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create separate directories for repo and state
            repo_dir = tmppath / 'repo'
            repo_dir.mkdir()
            state_dir = tmppath / '.repowiki'
            
            executor = TaskExecutor(state_dir=state_dir)
            
            agent = Phase1Agent(str(repo_dir), executor)
            results = agent.analyze()
            
            assert results['phase'] == 1
            assert results['file_count'] == 0
