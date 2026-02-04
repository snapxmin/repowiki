"""
Base agent class for repository understanding.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.executor import TaskExecutor, TaskState


class BaseAgent(ABC):
    """Base class for repository understanding agents."""
    
    def __init__(self, repo_path: str, executor: Optional[TaskExecutor] = None):
        """
        Initialize agent.
        
        Args:
            repo_path: Path to repository
            executor: Task executor (creates new if not provided)
        """
        self.repo_path = Path(repo_path).resolve()
        self.executor = executor or TaskExecutor()
        self.task: Optional[TaskState] = None
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the repository.
        
        Returns:
            Analysis results dictionary
        """
        pass
    
    @abstractmethod
    def get_phase(self) -> int:
        """
        Get the phase number this agent implements.
        
        Returns:
            Phase number (1, 2, or 3)
        """
        pass
    
    def _update_progress(self, progress: float, step: str):
        """Update task progress."""
        if self.task:
            self.executor.update_progress(self.task, progress, step)
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None
    
    def _get_file_structure(self, root_path: Path, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get hierarchical file structure.
        
        Args:
            root_path: Root path to analyze
            max_depth: Maximum depth to traverse
        
        Returns:
            Dictionary representing file structure
        """
        structure = {
            'name': root_path.name,
            'type': 'directory' if root_path.is_dir() else 'file',
            'path': str(root_path),
        }
        
        if root_path.is_dir() and max_depth > 0:
            children = []
            try:
                for item in sorted(root_path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    children.append(self._get_file_structure(item, max_depth - 1))
                structure['children'] = children
            except PermissionError:
                pass
        
        return structure
