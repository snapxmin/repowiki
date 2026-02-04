"""
Repository analyzer that determines repository complexity and selects appropriate phase.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import git
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


class RepositoryAnalyzer:
    """Analyzes repository to determine appropriate processing phase."""
    
    # Phase thresholds based on total lines of code
    PHASE_1_THRESHOLD = 10_000  # Simple repos
    PHASE_2_THRESHOLD = 100_000  # Medium repos
    # Above PHASE_2_THRESHOLD: Complex repos
    
    # Common ignore patterns
    DEFAULT_IGNORE_PATTERNS = [
        '.git/**',
        'node_modules/**',
        'venv/**',
        'env/**',
        '__pycache__/**',
        '*.pyc',
        'dist/**',
        'build/**',
        '.tox/**',
        'coverage/**',
        '.pytest_cache/**',
        '*.min.js',
        '*.min.css',
        'vendor/**',
    ]
    
    def __init__(self, repo_path: str):
        """
        Initialize repository analyzer.
        
        Args:
            repo_path: Path to the repository to analyze
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self.ignore_spec = self._build_ignore_spec()
    
    def _build_ignore_spec(self) -> PathSpec:
        """Build PathSpec for files to ignore."""
        patterns = self.DEFAULT_IGNORE_PATTERNS.copy()
        
        # Try to read .gitignore
        gitignore_path = self.repo_path / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass  # Ignore errors reading .gitignore
        
        return PathSpec.from_lines(GitWildMatchPattern, patterns)
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        try:
            rel_path = file_path.relative_to(self.repo_path)
            return self.ignore_spec.match_file(str(rel_path))
        except (ValueError, Exception):
            return True
    
    def _count_lines_in_file(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze repository to determine complexity.
        
        Returns:
            Dictionary with analysis results including:
            - total_files: Number of code files
            - total_lines: Total lines of code
            - phase: Recommended phase (1, 2, or 3)
            - file_types: Count of files by extension
        """
        total_lines = 0
        total_files = 0
        file_types = {}
        
        # Walk through all files
        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                
                if self._should_ignore(file_path):
                    continue
                
                # Count lines
                lines = self._count_lines_in_file(file_path)
                if lines > 0:
                    total_lines += lines
                    total_files += 1
                    
                    # Track file types
                    ext = file_path.suffix.lower() or 'no_extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        # Determine phase
        if total_lines <= self.PHASE_1_THRESHOLD:
            phase = 1
        elif total_lines <= self.PHASE_2_THRESHOLD:
            phase = 2
        else:
            phase = 3
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'phase': phase,
            'file_types': file_types,
            'repo_path': str(self.repo_path),
        }
    
    def get_phase_description(self, phase: int) -> str:
        """Get description of a phase."""
        descriptions = {
            1: "Simple repository (< 10K lines) - Direct analysis",
            2: "Medium repository (10K-100K lines) - Hierarchical analysis with chunking",
            3: "Complex repository (> 100K lines) - Distributed analysis with advanced context management",
        }
        return descriptions.get(phase, "Unknown phase")
