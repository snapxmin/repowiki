"""Tests for task executor."""
import pytest
import tempfile
from pathlib import Path
from repowiki.core.executor import TaskExecutor, TaskStatus


class TestTaskExecutor:
    """Test cases for TaskExecutor."""
    
    def test_create_task(self):
        """Test creating a new task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            task = executor.create_task('test-task', '/tmp/repo', 1)
            
            assert task.task_id == 'test-task'
            assert task.repo_path == '/tmp/repo'
            assert task.phase == 1
            assert task.status == TaskStatus.PENDING
            assert task.progress == 0.0
    
    def test_save_and_load_task(self):
        """Test saving and loading task state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            task = executor.create_task('test-task', '/tmp/repo', 1)
            
            # Modify task
            task.progress = 0.5
            task.current_step = 'Testing'
            executor.save_task(task)
            
            # Load task
            loaded = executor.load_task('test-task')
            assert loaded is not None
            assert loaded.task_id == 'test-task'
            assert loaded.progress == 0.5
            assert loaded.current_step == 'Testing'
    
    def test_update_progress(self):
        """Test updating task progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            task = executor.create_task('test-task', '/tmp/repo', 1)
            
            executor.update_progress(task, 0.75, 'Almost done')
            
            assert task.progress == 0.75
            assert task.current_step == 'Almost done'
            assert task.status == TaskStatus.IN_PROGRESS
    
    def test_complete_task(self):
        """Test completing a task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            task = executor.create_task('test-task', '/tmp/repo', 1)
            
            executor.complete_task(task)
            
            assert task.status == TaskStatus.COMPLETED
            assert task.progress == 1.0
            assert task.completed_at is not None
    
    def test_fail_task(self):
        """Test failing a task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            task = executor.create_task('test-task', '/tmp/repo', 1)
            
            executor.fail_task(task, 'Test error')
            
            assert task.status == TaskStatus.FAILED
            assert task.error == 'Test error'
    
    def test_list_tasks(self):
        """Test listing tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = TaskExecutor(state_dir=Path(tmpdir))
            
            executor.create_task('task1', '/tmp/repo1', 1)
            executor.create_task('task2', '/tmp/repo2', 2)
            
            tasks = executor.list_tasks()
            assert len(tasks) == 2
            assert any(t.task_id == 'task1' for t in tasks)
            assert any(t.task_id == 'task2' for t in tasks)
