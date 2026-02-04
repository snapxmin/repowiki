"""Tests for repository analyzer."""
import pytest
import tempfile
from pathlib import Path
from repowiki.core.analyzer import RepositoryAnalyzer


class TestRepositoryAnalyzer:
    """Test cases for RepositoryAnalyzer."""
    
    def test_analyzer_with_empty_repo(self):
        """Test analyzer with empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = RepositoryAnalyzer(tmpdir)
            stats = analyzer.analyze()
            
            assert stats['total_files'] == 0
            assert stats['total_lines'] == 0
            assert stats['phase'] == 1
    
    def test_analyzer_with_small_repo(self):
        """Test analyzer with small repository (Phase 1)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a small Python file
            test_file = tmppath / 'test.py'
            test_file.write_text('print("Hello, World!")\n' * 10)
            
            analyzer = RepositoryAnalyzer(tmpdir)
            stats = analyzer.analyze()
            
            assert stats['total_files'] == 1
            assert stats['total_lines'] == 10
            assert stats['phase'] == 1
    
    def test_analyzer_ignores_common_patterns(self):
        """Test that analyzer ignores common patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create files that should be counted
            (tmppath / 'main.py').write_text('# code\n' * 5)
            
            # Create files that should be ignored
            pycache = tmppath / '__pycache__'
            pycache.mkdir()
            (pycache / 'test.pyc').write_text('binary')
            
            analyzer = RepositoryAnalyzer(tmpdir)
            stats = analyzer.analyze()
            
            assert stats['total_files'] == 1
            assert '.py' in stats['file_types']
    
    def test_phase_detection(self):
        """Test phase detection based on line count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Test Phase 1 (< 10K lines)
            (tmppath / 'small.py').write_text('# line\n' * 100)
            analyzer = RepositoryAnalyzer(tmpdir)
            assert analyzer.analyze()['phase'] == 1
            
            # Test Phase 2 (10K-100K lines)
            (tmppath / 'medium.py').write_text('# line\n' * 15000)
            analyzer = RepositoryAnalyzer(tmpdir)
            assert analyzer.analyze()['phase'] == 2
    
    def test_file_type_tracking(self):
        """Test that file types are tracked correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            (tmppath / 'test.py').write_text('# python\n')
            (tmppath / 'test.js').write_text('// javascript\n')
            (tmppath / 'test.md').write_text('# markdown\n')
            
            analyzer = RepositoryAnalyzer(tmpdir)
            stats = analyzer.analyze()
            
            assert stats['total_files'] == 3
            assert '.py' in stats['file_types']
            assert '.js' in stats['file_types']
            assert '.md' in stats['file_types']
