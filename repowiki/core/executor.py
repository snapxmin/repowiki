"""
Task execution engine with state persistence and progress tracking.
"""
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class TaskState:
    """State of a running task."""
    task_id: str
    repo_path: str
    phase: int
    status: TaskStatus
    progress: float  # 0.0 to 1.0
    current_step: str
    started_at: str
    updated_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskState':
        """Create from dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
        return cls(**data)


class TaskExecutor:
    """Manages task execution with persistence and resumability."""
    
    def __init__(self, state_dir: Optional[Path] = None):
        """
        Initialize task executor.
        
        Args:
            state_dir: Directory to store task state (default: .repowiki in user home)
        """
        if state_dir is None:
            state_dir = Path.home() / '.repowiki' / 'tasks'
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_task: Optional[TaskState] = None
    
    def _get_task_file(self, task_id: str) -> Path:
        """Get path to task state file."""
        return self.state_dir / f"{task_id}.json"
    
    def create_task(self, task_id: str, repo_path: str, phase: int) -> TaskState:
        """
        Create a new task.
        
        Args:
            task_id: Unique identifier for the task
            repo_path: Path to repository
            phase: Processing phase (1, 2, or 3)
        
        Returns:
            Created task state
        """
        now = datetime.now().isoformat()
        task = TaskState(
            task_id=task_id,
            repo_path=repo_path,
            phase=phase,
            status=TaskStatus.PENDING,
            progress=0.0,
            current_step="Initialized",
            started_at=now,
            updated_at=now,
        )
        self.save_task(task)
        return task
    
    def save_task(self, task: TaskState):
        """Save task state to disk."""
        task.updated_at = datetime.now().isoformat()
        task_file = self._get_task_file(task.task_id)
        
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)
    
    def load_task(self, task_id: str) -> Optional[TaskState]:
        """Load task state from disk."""
        task_file = self._get_task_file(task_id)
        
        if not task_file.exists():
            return None
        
        try:
            with open(task_file, 'r') as f:
                data = json.load(f)
            return TaskState.from_dict(data)
        except Exception:
            return None
    
    def list_tasks(self) -> List[TaskState]:
        """List all tasks."""
        tasks = []
        for task_file in self.state_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    data = json.load(f)
                tasks.append(TaskState.from_dict(data))
            except Exception:
                continue
        return sorted(tasks, key=lambda t: t.started_at, reverse=True)
    
    def update_progress(self, task: TaskState, progress: float, step: str):
        """Update task progress."""
        task.progress = min(1.0, max(0.0, progress))
        task.current_step = step
        task.status = TaskStatus.IN_PROGRESS
        self.save_task(task)
    
    def complete_task(self, task: TaskState):
        """Mark task as completed."""
        task.status = TaskStatus.COMPLETED
        task.progress = 1.0
        task.completed_at = datetime.now().isoformat()
        self.save_task(task)
    
    def fail_task(self, task: TaskState, error: str):
        """Mark task as failed."""
        task.status = TaskStatus.FAILED
        task.error = error
        self.save_task(task)
    
    def pause_task(self, task: TaskState):
        """Pause task execution."""
        task.status = TaskStatus.PAUSED
        self.save_task(task)
    
    def resume_task(self, task: TaskState):
        """Resume paused task."""
        if task.status == TaskStatus.PAUSED:
            task.status = TaskStatus.IN_PROGRESS
            self.save_task(task)
