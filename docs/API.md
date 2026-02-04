# RepoWiki API 参考文档 (API Reference)

## 核心模块 API

### 1. Repository Analyzer

#### `RepositoryAnalyzer`

仓库分析器，用于扫描和分析代码库。

```python
from repowiki.core.analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer(repo_path="/path/to/repo")
stats = analyzer.analyze()
```

**参数：**
- `repo_path` (str): 仓库路径

**方法：**

##### `analyze() -> Dict[str, Any]`

分析仓库并返回统计信息。

**返回值：**
```python
{
    'total_files': 150,          # 文件总数
    'total_lines': 12345,        # 代码总行数
    'phase': 2,                  # 推荐的Phase (1, 2, 或 3)
    'file_types': {              # 文件类型统计
        '.py': 100,
        '.js': 30,
        '.md': 20
    },
    'repo_path': '/path/to/repo'
}
```

##### `get_phase_description(phase: int) -> str`

获取Phase的描述文本。

**参数：**
- `phase` (int): Phase编号 (1, 2, 或 3)

**返回值：**
- str: Phase描述

**示例：**
```python
description = analyzer.get_phase_description(2)
# "Medium repository (10K-100K lines) - Hierarchical analysis with chunking"
```

---

### 2. Task Executor

#### `TaskExecutor`

任务执行器，管理分析任务的生命周期。

```python
from repowiki.core.executor import TaskExecutor

executor = TaskExecutor()
# 或指定状态目录
executor = TaskExecutor(state_dir=Path("/custom/path"))
```

**参数：**
- `state_dir` (Optional[Path]): 状态存储目录，默认为 `~/.repowiki/tasks`

**方法：**

##### `create_task(task_id: str, repo_path: str, phase: int) -> TaskState`

创建新任务。

**参数：**
- `task_id` (str): 任务唯一标识符
- `repo_path` (str): 仓库路径
- `phase` (int): 执行Phase

**返回值：**
- `TaskState`: 任务状态对象

##### `save_task(task: TaskState)`

保存任务状态到磁盘。

**参数：**
- `task` (TaskState): 任务状态对象

##### `load_task(task_id: str) -> Optional[TaskState]`

从磁盘加载任务状态。

**参数：**
- `task_id` (str): 任务ID

**返回值：**
- `Optional[TaskState]`: 任务状态对象，不存在则返回None

##### `update_progress(task: TaskState, progress: float, step: str)`

更新任务进度。

**参数：**
- `task` (TaskState): 任务对象
- `progress` (float): 进度值 (0.0 - 1.0)
- `step` (str): 当前步骤描述

##### `complete_task(task: TaskState)`

标记任务为已完成。

##### `fail_task(task: TaskState, error: str)`

标记任务为失败。

**参数：**
- `error` (str): 错误信息

##### `list_tasks() -> List[TaskState]`

列出所有任务。

**返回值：**
- `List[TaskState]`: 任务列表，按开始时间倒序排列

---

### 3. TaskState

任务状态数据类。

```python
from repowiki.core.executor import TaskState, TaskStatus

task = TaskState(
    task_id="my-task-123",
    repo_path="/path/to/repo",
    phase=1,
    status=TaskStatus.PENDING,
    progress=0.0,
    current_step="Initializing",
    started_at="2026-02-04T10:00:00",
    updated_at="2026-02-04T10:00:00"
)
```

**属性：**
- `task_id` (str): 任务ID
- `repo_path` (str): 仓库路径
- `phase` (int): Phase编号
- `status` (TaskStatus): 任务状态
- `progress` (float): 进度 (0.0-1.0)
- `current_step` (str): 当前步骤
- `started_at` (str): 开始时间 (ISO格式)
- `updated_at` (str): 更新时间
- `completed_at` (Optional[str]): 完成时间
- `error` (Optional[str]): 错误信息
- `context` (Dict[str, Any]): 上下文数据

**方法：**

##### `to_dict() -> Dict[str, Any]`

转换为字典。

##### `from_dict(data: Dict[str, Any]) -> TaskState`

从字典创建 (类方法)。

---

### 4. Base Agent

#### `BaseAgent`

所有Phase Agent的抽象基类。

```python
from repowiki.core.agent import BaseAgent

# 不能直接实例化，需要使用具体的Phase Agent
```

**抽象方法：**

##### `analyze() -> Dict[str, Any]`

执行仓库分析 (子类必须实现)。

##### `get_phase() -> int`

返回Phase编号 (子类必须实现)。

**工具方法：**

##### `_update_progress(progress: float, step: str)`

更新任务进度。

##### `_read_file_safely(file_path: Path) -> Optional[str]`

安全读取文件内容。

##### `_get_file_structure(root_path: Path, max_depth: int) -> Dict`

获取文件层级结构。

---

### 5. Phase Agents

#### `Phase1Agent`

简单仓库分析智能体 (< 10K 行)。

```python
from repowiki.phases.phase1 import Phase1Agent

agent = Phase1Agent(repo_path="/path/to/repo")
results = agent.analyze()
```

**返回值示例：**
```python
{
    'phase': 1,
    'repo_stats': {...},
    'file_count': 25,
    'files': [...],           # 文件列表 (最多100个)
    'structure': {...},       # 目录结构树
    'summary': "...",         # 文本摘要
    'file_analysis': {...}    # 文件分析结果
}
```

#### `Phase2Agent`

中等仓库分析智能体 (10K-100K 行)。

```python
from repowiki.phases.phase2 import Phase2Agent

agent = Phase2Agent(repo_path="/path/to/repo")
results = agent.analyze()
```

**返回值示例：**
```python
{
    'phase': 2,
    'repo_stats': {...},
    'hierarchy': {...},           # 层级结构
    'directory_analysis': {...},  # 目录级分析
    'dependencies': {...},        # 依赖映射
    'summary': "...",
    'cache_hits': {...}          # 缓存统计
}
```

#### `Phase3Agent`

复杂仓库分析智能体 (> 100K 行)。

```python
from repowiki.phases.phase3 import Phase3Agent

agent = Phase3Agent(repo_path="/path/to/repo")
results = agent.analyze()
```

**返回值示例：**
```python
{
    'phase': 3,
    'repo_stats': {...},
    'priority_map': {           # 优先级映射
        'high': [...],          # 高优先级文件
        'medium': [...],        # 中优先级文件
        'low': [...],           # 低优先级文件
        'file_scores': {...}    # 文件分数映射
    },
    'dependency_graph': {...},  # 依赖图
    'knowledge_graph': {        # 知识图谱
        'total_nodes': 350,
        'total_edges': 523,
        'coverage': {...}
    },
    'analysis_passes': {        # 多轮分析结果
        'pass1': {...},
        'pass2': {...},
        'pass3': {...}
    },
    'summary': "...",
    'context_preserved': 350    # 保留的上下文数量
}
```

---

## CLI 命令参考

### `repowiki analyze`

分析仓库。

```bash
repowiki analyze <repo_path> [OPTIONS]
```

**参数：**
- `repo_path`: 仓库路径 (必需)

**选项：**
- `--force-phase {1,2,3}`: 强制使用指定Phase
- `-o, --output PATH`: 保存结果到JSON文件
- `-v, --verbose`: 详细输出
- `--help`: 显示帮助信息

**示例：**
```bash
# 自动检测Phase
repowiki analyze /path/to/repo

# 强制Phase 2
repowiki analyze /path/to/repo --force-phase 2

# 保存结果
repowiki analyze /path/to/repo -o result.json

# 详细模式
repowiki analyze /path/to/repo -v
```

### `repowiki info`

显示仓库信息和推荐Phase。

```bash
repowiki info <repo_path>
```

**参数：**
- `repo_path`: 仓库路径 (必需)

**示例：**
```bash
repowiki info /path/to/repo
```

**输出示例：**
```
Repository Information:
  Path: /path/to/repo
  Total Files: 150
  Total Lines: 45,678

Recommended Phase: 2
  Medium repository (10K-100K lines) - Hierarchical analysis with chunking

File Types:
  .py: 100
  .js: 30
  .md: 20
```

### `repowiki tasks`

列出分析任务。

```bash
repowiki tasks [OPTIONS]
```

**选项：**
- `-a, --all`: 显示所有任务 (默认显示最近10个)

**示例：**
```bash
# 显示最近任务
repowiki tasks

# 显示所有任务
repowiki tasks --all
```

### `repowiki version`

显示版本信息。

```bash
repowiki version
```

---

## 编程接口示例

### 完整分析流程

```python
from repowiki.core.analyzer import RepositoryAnalyzer
from repowiki.core.executor import TaskExecutor
from repowiki.phases.phase1 import Phase1Agent
from repowiki.phases.phase2 import Phase2Agent
from repowiki.phases.phase3 import Phase3Agent

# 1. 分析仓库，确定Phase
analyzer = RepositoryAnalyzer("/path/to/repo")
stats = analyzer.analyze()
phase = stats['phase']

print(f"Detected Phase: {phase}")
print(f"Description: {analyzer.get_phase_description(phase)}")

# 2. 创建任务执行器
executor = TaskExecutor()

# 3. 选择并运行适当的Agent
if phase == 1:
    agent = Phase1Agent("/path/to/repo", executor)
elif phase == 2:
    agent = Phase2Agent("/path/to/repo", executor)
else:
    agent = Phase3Agent("/path/to/repo", executor)

# 4. 执行分析
results = agent.analyze()

# 5. 处理结果
print(results['summary'])

# 6. 保存结果
import json
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

### 恢复中断的任务

```python
from repowiki.core.executor import TaskExecutor, TaskStatus

executor = TaskExecutor()

# 列出所有任务
tasks = executor.list_tasks()

# 查找暂停或失败的任务
for task in tasks:
    if task.status in [TaskStatus.PAUSED, TaskStatus.FAILED]:
        print(f"Found incomplete task: {task.task_id}")
        print(f"  Progress: {task.progress * 100:.1f}%")
        print(f"  Last step: {task.current_step}")
        
        # 可以选择恢复任务
        # executor.resume_task(task)
```

### 自定义进度回调

```python
from repowiki.phases.phase2 import Phase2Agent
from repowiki.core.executor import TaskExecutor

class CustomExecutor(TaskExecutor):
    def update_progress(self, task, progress, step):
        super().update_progress(task, progress, step)
        # 自定义回调
        print(f"Progress: {progress*100:.0f}% - {step}")

executor = CustomExecutor()
agent = Phase2Agent("/path/to/repo", executor)
results = agent.analyze()
```

---

## 数据结构参考

### 分析结果结构

所有Phase的结果都包含以下基本字段：

```python
{
    'phase': int,              # Phase编号 (1, 2, 或 3)
    'repo_stats': {
        'total_files': int,
        'total_lines': int,
        'phase': int,
        'file_types': Dict[str, int],
        'repo_path': str
    },
    'summary': str,            # 文本摘要
    # ... Phase特定的其他字段
}
```

### 文件结构树

```python
{
    'name': 'dirname',
    'type': 'directory' | 'file',
    'path': 'relative/path',
    'children': [...]  # 仅目录有此字段
}
```

### 依赖图结构

```python
{
    'file_path_1': ['dependency_1', 'dependency_2'],
    'file_path_2': ['dependency_3'],
    ...
}
```

### 知识图谱结构

```python
{
    'total_nodes': int,
    'total_edges': int,
    'high_priority_nodes': int,
    'coverage': {
        'pass1': int,  # Pass 1 分析的文件数
        'pass2': int,  # Pass 2 分析的文件数
        'pass3': int,  # Pass 3 分析的文件数
        'total': int   # 总分析文件数
    }
}
```

---

## 错误处理

### 常见错误

#### `ValueError: Repository path does not exist`

仓库路径不存在。

**解决方案：**
```python
from pathlib import Path

repo_path = Path("/path/to/repo")
if not repo_path.exists():
    print("Repository does not exist!")
```

#### 任务执行失败

检查任务错误信息：

```python
executor = TaskExecutor()
task = executor.load_task("task_id")
if task and task.error:
    print(f"Error: {task.error}")
```

---

## 性能建议

### 大型仓库优化

1. **使用Phase 3** 的智能优先级
2. **启用缓存** (Phase 2/3 自动启用)
3. **限制分析深度**

```python
# Phase 3 已内置优先级系统
agent = Phase3Agent("/large/repo")
results = agent.analyze()
# 只分析最重要的文件
```

### 内存管理

对于超大仓库，考虑分批处理：

```python
# Phase 3 使用采样策略
# 只分析 top 50 (Pass 1) + 100 (Pass 2) + 200 (Pass 3)
# 而不是全部文件
```

---

**API版本:** 1.0  
**最后更新:** 2026-02-04
