"""
Example demonstrating RepoWiki's phased analysis approach.

This script creates example repositories of different sizes and
analyzes them to demonstrate the automatic phase selection.
"""
import tempfile
import json
from pathlib import Path
from repowiki.core.analyzer import RepositoryAnalyzer
from repowiki.phases.phase1 import Phase1Agent
from repowiki.phases.phase2 import Phase2Agent
from repowiki.phases.phase3 import Phase3Agent


def create_simple_repo(path: Path):
    """Create a simple repository (< 10K lines)."""
    # Create a basic Python project
    (path / 'main.py').write_text('''#!/usr/bin/env python3
"""Main application entry point."""
import sys
from utils import helper

def main():
    """Main function."""
    print("Hello from simple repo!")
    helper.do_something()

if __name__ == "__main__":
    main()
''' * 10)  # ~130 lines
    
    (path / 'utils.py').write_text('''"""Utility functions."""

def helper():
    """Helper function."""
    pass

def do_something():
    """Do something useful."""
    return True
''' * 20)  # ~180 lines
    
    (path / 'README.md').write_text('''# Simple Project

This is a simple example project.

## Features
- Feature 1
- Feature 2
- Feature 3
''')


def create_medium_repo(path: Path):
    """Create a medium repository (10K-100K lines)."""
    # Create multiple modules
    for i in range(100):
        module_dir = path / f'module_{i}'
        module_dir.mkdir(exist_ok=True)
        
        (module_dir / '__init__.py').write_text(f'"""Module {i}."""\n')
        (module_dir / 'core.py').write_text(f'''"""Core functionality for module {i}."""

class Module{i}:
    """Main class for module {i}."""
    
    def __init__(self):
        self.name = "module_{i}"
        self.version = "1.0.0"
    
    def process(self, data):
        """Process data."""
        return data
    
    def validate(self, data):
        """Validate data."""
        return True
''' * 10)  # ~1600 lines per module = ~160K total (will be Phase 2)


def create_complex_repo(path: Path):
    """Create a complex repository (> 100K lines)."""
    # Create many modules with deep hierarchy
    for i in range(300):
        module_dir = path / f'package_{i // 30}' / f'module_{i}'
        module_dir.mkdir(parents=True, exist_ok=True)
        
        (module_dir / '__init__.py').write_text(f'"""Module {i}."""\n')
        (module_dir / 'implementation.py').write_text(f'''"""Implementation for module {i}."""

class Implementation{i}:
    """Implementation class {i}."""
    
    def __init__(self):
        self.id = {i}
        self.data = []
    
    def method1(self):
        """Method 1."""
        pass
    
    def method2(self):
        """Method 2."""
        pass
    
    def method3(self):
        """Method 3."""
        pass
''' * 20)  # ~4K lines per module = ~1.2M total (Phase 3)


def analyze_example(name: str, create_func, expected_phase: int):
    """Analyze an example repository."""
    print(f"\n{'='*70}")
    print(f"Example: {name}")
    print('='*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / 'repo'
        repo_path.mkdir()
        
        # Create repository
        print(f"Creating {name.lower()}...")
        create_func(repo_path)
        
        # Analyze
        print("Analyzing repository...")
        analyzer = RepositoryAnalyzer(str(repo_path))
        stats = analyzer.analyze()
        
        print(f"\nRepository Stats:")
        print(f"  Total Files: {stats['total_files']}")
        print(f"  Total Lines: {stats['total_lines']:,}")
        print(f"  Detected Phase: {stats['phase']}")
        print(f"  Description: {analyzer.get_phase_description(stats['phase'])}")
        
        assert stats['phase'] == expected_phase, \
            f"Expected phase {expected_phase}, got {stats['phase']}"
        
        # Run appropriate agent
        print(f"\nRunning Phase {stats['phase']} analysis...")
        
        if stats['phase'] == 1:
            agent = Phase1Agent(str(repo_path))
        elif stats['phase'] == 2:
            agent = Phase2Agent(str(repo_path))
        else:
            agent = Phase3Agent(str(repo_path))
        
        results = agent.analyze()
        
        # Display summary
        print("\n" + results['summary'])
        
        return results


def main():
    """Run all examples."""
    print("RepoWiki Phase Analysis Examples")
    print("=" * 70)
    
    # Example 1: Simple Repository
    analyze_example(
        "Simple Repository",
        create_simple_repo,
        expected_phase=1
    )
    
    # Example 2: Medium Repository
    analyze_example(
        "Medium Repository",
        create_medium_repo,
        expected_phase=2
    )
    
    # Example 3: Complex Repository
    analyze_example(
        "Complex Repository",
        create_complex_repo,
        expected_phase=3
    )
    
    print(f"\n{'='*70}")
    print("✓ All examples completed successfully!")
    print('='*70)


if __name__ == '__main__':
    main()
