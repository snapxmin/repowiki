# RepoWiki 设计文档 (Design Document)

## 目录 (Table of Contents)

1. [项目概述](#项目概述-project-overview)
2. [系统架构](#系统架构-system-architecture)
3. [阶段设计](#阶段设计-phase-design)
4. [核心组件](#核心组件-core-components)
5. [技术实现](#技术实现-technical-implementation)
6. [数据流](#数据流-data-flow)
7. [扩展性设计](#扩展性设计-extensibility-design)

---

## 项目概述 (Project Overview)

### 1.1 目标 (Goals)

RepoWiki 旨在开发一个能够运行长程稳定复杂任务的代码库理解智能体系统，能够处理从几万到几百万行代码规模的项目，并在整个过程中保持意图不丢失，最终完成复杂的代码理解任务。

**核心目标：**
- 理解不同规模的代码仓库（从简单到复杂）
- 保持长时间运行过程中的上下文和意图
- 提供可恢复的任务执行机制
- 支持增量分析和缓存优化
- 自动选择最优分析策略

### 1.2 分阶段实现策略 (Phased Implementation Strategy)

系统采用三阶段渐进式架构设计：

| 阶段 | 代码规模 | 策略 | 特点 |
|------|----------|------|------|
| **Phase 1** | < 10,000 行 | 直接分析 | 简单直接，全量处理 |
| **Phase 2** | 10,000 - 100,000 行 | 分层分析 | 分块处理，层级缓存 |
| **Phase 3** | > 100,000 行 | 多轮分析 | 智能优先级，图结构 |

---

## 系统架构 (System Architecture)

### 2.1 总体架构图 (Overall Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface (repowiki)                 │
│                  命令行接口 - 用户交互层                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Repository Analyzer (分析器)                    │
│  • 扫描代码库                                                │
│  • 统计代码规模                                              │
│  • 自动选择Phase                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
┌────────▼──────────┐      ┌────────▼──────────┐
│  Task Executor    │      │   Agent Factory   │
│  任务执行器        │      │   智能体工厂       │
│  • 状态管理       │      │   • 选择Phase     │
│  • 进度跟踪       │      │   • 创建Agent     │
│  • 持久化        │      └────────┬──────────┘
└───────────────────┘               │
                          ┌─────────┴─────────┐
                          │                   │
                ┌─────────▼────────┐ ┌───────▼────────┐
                │   Phase Agents   │ │  Core Modules  │
                │   阶段智能体      │ │  核心模块      │
                └──────────────────┘ └────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│ Phase1Agent  │  │ Phase2Agent │  │ Phase3Agent │
│ 简单仓库      │  │ 中等仓库     │  │ 复杂仓库     │
│ 直接分析      │  │ 分层分析     │  │ 多轮分析     │
└──────────────┘  └─────────────┘  └─────────────┘
```

### 2.2 核心设计原则 (Core Design Principles)

1. **渐进式复杂度 (Progressive Complexity)**
   - 根据仓库规模自动选择策略
   - 避免过度工程化简单场景
   - 为复杂场景预留足够能力

2. **状态持久化 (State Persistence)**
   - 所有任务状态可序列化
   - 支持中断恢复
   - 进度实时保存

3. **模块化设计 (Modular Design)**
   - 松耦合组件
   - 易于扩展和测试
   - 清晰的职责分离

4. **上下文保持 (Context Preservation)**
   - 跨步骤的上下文传递
   - 智能的信息压缩
   - 关键信息优先保留

---

## 阶段设计 (Phase Design)

### 3.1 Phase 1: 简单仓库理解 (Simple Repository Understanding)

**适用范围：** < 10,000 行代码

**设计理念：**
直接、简单、全量处理。对于小型仓库，不需要复杂的优化策略，直接读取所有文件并建立完整索引。

**技术特点：**

```python
# 处理流程
1. 扫描仓库 → 2. 构建文件清单 → 3. 分析文件内容 → 4. 生成结构图 → 5. 输出摘要
```

**实现细节：**

```python
class Phase1Agent:
    """简单仓库智能体"""
    
    def analyze(self):
        # 1. 扫描仓库结构
        repo_stats = self._scan_repository()
        
        # 2. 构建完整文件清单
        files = self._build_file_inventory()
        
        # 3. 直接分析所有文件
        analysis = self._analyze_all_files(files)
        
        # 4. 构建完整结构树（深度5层）
        structure = self._build_structure_tree(depth=5)
        
        # 5. 生成摘要
        summary = self._generate_summary()
        
        return results
```

**优势：**
- ✓ 实现简单
- ✓ 运行快速
- ✓ 结果完整

**限制：**
- ✗ 不适合大型仓库
- ✗ 内存占用随文件数线性增长

---

### 3.2 Phase 2: 中等仓库理解 (Medium Repository Understanding)

**适用范围：** 10,000 - 100,000 行代码

**设计理念：**
分层处理、智能缓存、上下文管理。通过目录层级分块处理，利用缓存避免重复分析。

**技术特点：**

```python
# 处理流程
扫描 → 构建层级 → 分块分析 → 依赖映射 → 层级缓存 → 生成摘要
```

**核心创新：**

1. **分层分析 (Hierarchical Analysis)**
   ```
   Repository
   ├── package_1/          ← 作为分析单元
   │   ├── module_a/       ← 作为分析单元
   │   │   └── files...    ← 文件级分析
   │   └── module_b/
   └── package_2/
   ```

2. **智能缓存 (Intelligent Caching)**
   ```python
   # 缓存键基于路径的MD5
   cache_key = hashlib.md5(path.encode()).hexdigest()
   
   # 缓存结构
   {
       "path": "src/module",
       "analysis": {
           "file_count": 10,
           "total_size": 50000,
           "last_analyzed": "2026-02-04T..."
       }
   }
   ```

3. **依赖映射 (Dependency Mapping)**
   ```python
   dependencies = {
       "src/module_a": ["src/module_b", "src/utils"],
       "src/module_b": ["src/core"],
       "src/utils": []
   }
   ```

**实现细节：**

```python
class Phase2Agent:
    """中等仓库智能体"""
    
    def __init__(self):
        self.cache_dir = Path.home() / '.repowiki' / 'cache'
        self.context_store = {}
    
    def analyze(self):
        # 1. 构建目录层级结构
        hierarchy = self._build_hierarchy()
        
        # 2. 按目录分块分析（带缓存）
        dir_analysis = self._analyze_directories_chunked(hierarchy)
        
        # 3. 构建依赖关系图
        dependencies = self._build_dependency_map(hierarchy)
        
        # 4. 生成层级摘要
        summary = self._generate_hierarchical_summary()
        
        return results
    
    def _analyze_directories_chunked(self, hierarchy):
        """分块分析目录，使用缓存"""
        for directory in hierarchy:
            # 检查缓存
            if cached := self._get_cached_analysis(directory):
                yield cached
                continue
            
            # 分析并缓存
            analysis = self._analyze_directory(directory)
            self._cache_analysis(directory, analysis)
            yield analysis
```

**优势：**
- ✓ 支持中等规模仓库
- ✓ 缓存提高效率
- ✓ 内存占用可控

**限制：**
- ✗ 依赖关系分析较简单
- ✗ 超大仓库性能下降

---

### 3.3 Phase 3: 复杂仓库理解 (Complex Repository Understanding)

**适用范围：** > 100,000 行代码

**设计理念：**
多轮分析、智能优先级、图结构、上下文压缩。采用三轮分析策略，优先处理关键文件，构建知识图谱。

**技术特点：**

```python
# 三轮分析策略
Pass 1: 关键文件分析（README, 配置, 入口）
  ↓
Pass 2: 上下文感知分析（依赖图驱动）
  ↓
Pass 3: 全面覆盖分析（填补空白）
  ↓
知识图谱构建
```

**核心创新：**

1. **智能优先级系统 (Intelligent Prioritization)**
   ```python
   # 文件优先级计算
   priority_score = base_score + name_boost + depth_boost
   
   # 优先级规则
   FILE_PRIORITY = {
       '.py': 10,    # 源代码文件
       '.js': 10,
       '.md': 7,     # 文档
       '.json': 6,   # 配置
   }
   
   # 文件名加权
   if filename in ['README.md', 'package.json', 'setup.py']:
       priority += 5
   if filename.startswith('main.') or filename.startswith('index.'):
       priority += 3
   
   # 深度加权（根目录文件优先）
   if depth == 1: priority += 2
   elif depth == 2: priority += 1
   ```

2. **多轮分析策略 (Multi-Pass Analysis)**
   
   **Pass 1 - 关键文件分析：**
   ```python
   # 分析高优先级文件（top 50）
   for file in priority_map['high'][:50]:
       context_store[file] = {
           'priority': 'high',
           'analyzed_in_pass': 1
       }
   ```
   
   **Pass 2 - 上下文感知分析：**
   ```python
   # 基于依赖图分析中等优先级文件
   for file in priority_map['medium'][:100]:
       context_store[file] = {
           'priority': 'medium',
           'analyzed_in_pass': 2,
           'dependencies': dep_graph.get(file, [])
       }
   ```
   
   **Pass 3 - 填补空白：**
   ```python
   # 采样分析剩余文件
   remaining = [f for f in all_files if f not in analyzed_paths]
   for file in remaining[:200]:  # 采样
       context_store[file] = {
           'priority': 'low',
           'analyzed_in_pass': 3
       }
   ```

3. **知识图谱构建 (Knowledge Graph)**
   ```python
   knowledge_graph = {
       'nodes': [
           {'id': 'file1', 'type': 'source', 'priority': 'high'},
           {'id': 'file2', 'type': 'config', 'priority': 'high'},
       ],
       'edges': [
           {'from': 'file1', 'to': 'file2', 'type': 'imports'},
       ],
       'metadata': {
           'total_nodes': 350,
           'total_edges': 523,
           'coverage': {
               'pass1': 50,
               'pass2': 100,
               'pass3': 200
           }
       }
   }
   ```

**实现细节：**

```python
class Phase3Agent:
    """复杂仓库智能体"""
    
    FILE_PRIORITY = {...}  # 优先级映射
    
    def __init__(self):
        self.context_store = {}
        self.analyzed_paths = set()
    
    def analyze(self):
        # 1. 构建优先级映射
        priority_map = self._build_priority_map()
        
        # 2. Pass 1: 分析关键文件
        pass1 = self._analyze_pass_1(priority_map)
        
        # 3. 构建依赖图
        dep_graph = self._build_dependency_graph(priority_map)
        
        # 4. Pass 2: 上下文感知分析
        pass2 = self._analyze_pass_2(priority_map, dep_graph)
        
        # 5. Pass 3: 全面覆盖
        pass3 = self._analyze_pass_3(priority_map)
        
        # 6. 构建知识图谱
        knowledge_graph = self._build_knowledge_graph(
            pass1, pass2, pass3, dep_graph
        )
        
        return results
    
    def _calculate_priority_score(self, file_path):
        """计算文件优先级分数"""
        score = self.FILE_PRIORITY.get(file_path.suffix, 3)
        
        # 特殊文件名加权
        if file_path.name.lower() in ['readme.md', 'package.json']:
            score += 5
        
        # 深度加权
        depth = len(file_path.parts)
        if depth == 1: score += 2
        
        return min(score, 15)
```

**优势：**
- ✓ 支持超大规模仓库
- ✓ 智能优先级保证关键信息
- ✓ 知识图谱提供结构化理解
- ✓ 多轮策略保持上下文

**限制：**
- ✗ 实现复杂度较高
- ✗ 需要更多计算资源

---

## 核心组件 (Core Components)

### 4.1 Repository Analyzer (仓库分析器)

**职责：**
- 扫描代码库
- 统计代码规模
- 自动选择Phase

**关键方法：**

```python
class RepositoryAnalyzer:
    # 阶段阈值
    PHASE_1_THRESHOLD = 10_000
    PHASE_2_THRESHOLD = 100_000
    
    # 忽略模式
    DEFAULT_IGNORE_PATTERNS = [
        '.git/**', 'node_modules/**', '__pycache__/**', ...
    ]
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析仓库并返回统计信息
        
        Returns:
            {
                'total_files': int,
                'total_lines': int,
                'phase': int,  # 推荐的Phase
                'file_types': Dict[str, int],
                'repo_path': str
            }
        """
```

**工作流程：**

```
1. 构建忽略规则 (.gitignore + 默认规则)
   ↓
2. 遍历文件系统
   ↓
3. 过滤忽略文件
   ↓
4. 统计代码行数
   ↓
5. 分类文件类型
   ↓
6. 确定Phase
   ↓
7. 返回分析结果
```

---

### 4.2 Task Executor (任务执行器)

**职责：**
- 管理任务生命周期
- 保存/恢复任务状态
- 跟踪执行进度

**状态模型：**

```python
class TaskStatus(Enum):
    PENDING = "pending"        # 待执行
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    PAUSED = "paused"          # 暂停

@dataclass
class TaskState:
    task_id: str              # 任务ID
    repo_path: str            # 仓库路径
    phase: int                # 执行Phase
    status: TaskStatus        # 状态
    progress: float           # 进度 0.0-1.0
    current_step: str         # 当前步骤
    started_at: str           # 开始时间
    updated_at: str           # 更新时间
    completed_at: Optional[str]  # 完成时间
    error: Optional[str]      # 错误信息
    context: Dict[str, Any]   # 上下文数据
```

**持久化机制：**

```python
# 状态文件位置
~/.repowiki/tasks/{task_id}.json

# 状态文件格式
{
  "task_id": "phase1_myrepo_123456",
  "repo_path": "/path/to/repo",
  "phase": 1,
  "status": "completed",
  "progress": 1.0,
  "current_step": "Analysis complete",
  "started_at": "2026-02-04T02:30:00",
  "updated_at": "2026-02-04T02:30:30",
  "completed_at": "2026-02-04T02:30:30",
  "context": {}
}
```

**关键方法：**

```python
class TaskExecutor:
    def create_task(task_id, repo_path, phase) -> TaskState
    def save_task(task: TaskState)
    def load_task(task_id) -> TaskState
    def update_progress(task, progress, step)
    def complete_task(task)
    def fail_task(task, error)
    def pause_task(task)
    def resume_task(task)
    def list_tasks() -> List[TaskState]
```

---

### 4.3 Base Agent (基础智能体)

**职责：**
- 提供通用分析接口
- 管理进度更新
- 提供工具方法

**抽象接口：**

```python
class BaseAgent(ABC):
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """执行分析"""
        pass
    
    @abstractmethod
    def get_phase(self) -> int:
        """返回Phase编号"""
        pass
    
    def _update_progress(self, progress: float, step: str):
        """更新进度"""
        pass
    
    def _read_file_safely(self, file_path) -> Optional[str]:
        """安全读取文件"""
        pass
    
    def _get_file_structure(self, root_path, max_depth) -> Dict:
        """获取文件结构"""
        pass
```

---

## 技术实现 (Technical Implementation)

### 5.1 技术栈 (Technology Stack)

**核心依赖：**
- Python 3.8+
- click (CLI框架)
- GitPython (Git操作)
- pathspec (路径匹配)
- PyYAML (配置文件)

**可选依赖：**
- pytest (测试)
- pytest-cov (覆盖率)

### 5.2 目录结构 (Directory Structure)

```
repowiki/
├── repowiki/              # 主包
│   ├── __init__.py
│   ├── cli.py            # CLI入口
│   ├── core/             # 核心组件
│   │   ├── analyzer.py   # 仓库分析器
│   │   ├── executor.py   # 任务执行器
│   │   └── agent.py      # 基础智能体
│   ├── phases/           # 阶段实现
│   │   ├── phase1.py     # Phase 1
│   │   ├── phase2.py     # Phase 2
│   │   └── phase3.py     # Phase 3
│   └── utils/            # 工具函数
├── tests/                # 测试
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
├── examples/             # 示例
├── docs/                 # 文档
├── pyproject.toml        # 项目配置
└── README.md             # 说明文档
```

### 5.3 命令行接口 (CLI Interface)

**主要命令：**

```bash
# 分析仓库
repowiki analyze <repo_path> [options]

# 查看仓库信息
repowiki info <repo_path>

# 列出任务
repowiki tasks [--all]

# 查看版本
repowiki version
```

**使用示例：**

```bash
# 自动检测Phase并分析
$ repowiki analyze /path/to/repo

# 强制使用特定Phase
$ repowiki analyze /path/to/repo --force-phase 2

# 保存结果到文件
$ repowiki analyze /path/to/repo -o results.json

# 详细输出
$ repowiki analyze /path/to/repo -v
```

---

## 数据流 (Data Flow)

### 6.1 完整数据流图

```
用户输入
  ↓
┌─────────────────┐
│  CLI Interface  │ 解析命令行参数
└────────┬────────┘
         ↓
┌─────────────────┐
│ Analyzer.analyze()│ 扫描仓库，确定Phase
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ Phase?  │ 决策点
    └────┬────┘
         ├──→ Phase 1 → Phase1Agent.analyze()
         │      ↓
         │   直接分析所有文件
         │      ↓
         │   生成完整结果
         │
         ├──→ Phase 2 → Phase2Agent.analyze()
         │      ↓
         │   构建层级结构
         │      ↓
         │   分块分析+缓存
         │      ↓
         │   生成层级结果
         │
         └──→ Phase 3 → Phase3Agent.analyze()
                ↓
             构建优先级映射
                ↓
             三轮分析
                ↓
             构建知识图谱
                ↓
             生成综合结果
         
所有Phase汇总
  ↓
┌─────────────────┐
│ TaskExecutor    │ 保存状态和进度
└────────┬────────┘
         ↓
┌─────────────────┐
│  Output Results │ 输出结果（CLI/文件）
└─────────────────┘
```

### 6.2 状态转换图

```
TaskState 状态机：

PENDING ──→ IN_PROGRESS ──→ COMPLETED
   │            │              ↑
   │            ├──→ PAUSED ───┘
   │            │
   └────────────┴──→ FAILED
```

---

## 扩展性设计 (Extensibility Design)

### 7.1 新增Phase

```python
# 1. 创建新Agent类
class Phase4Agent(BaseAgent):
    def get_phase(self) -> int:
        return 4
    
    def analyze(self) -> Dict[str, Any]:
        # 实现新的分析策略
        pass

# 2. 更新Analyzer阈值
class RepositoryAnalyzer:
    PHASE_3_THRESHOLD = 1_000_000  # 新增
    
    def analyze(self):
        if total_lines > self.PHASE_3_THRESHOLD:
            phase = 4  # 新Phase
        ...
```

### 7.2 自定义分析器

```python
# 扩展点：自定义文件分析器
class CustomFileAnalyzer:
    def analyze_python(self, file_path):
        """Python文件深度分析"""
        # AST解析
        # 提取类、函数、导入
        pass
    
    def analyze_javascript(self, file_path):
        """JavaScript文件分析"""
        pass
```

### 7.3 插件系统（未来扩展）

```python
# 插件接口
class AnalyzerPlugin(ABC):
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """判断是否能处理该文件"""
        pass
    
    @abstractmethod
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """分析文件"""
        pass

# 注册插件
registry.register('python-ast', PythonASTPlugin())
registry.register('javascript', JavaScriptPlugin())
```

### 7.4 输出格式扩展

```python
# 当前：JSON
# 未来可扩展：
- Markdown报告
- HTML交互式视图
- PDF文档
- GraphQL API
```

---

## 性能考虑 (Performance Considerations)

### 8.1 内存优化

**Phase 1:**
- 小文件直接加载内存
- 大文件流式处理

**Phase 2:**
- 分块加载
- LRU缓存
- 按需释放

**Phase 3:**
- 采样分析
- 懒加载
- 上下文压缩

### 8.2 时间优化

| Phase | 策略 | 预期时间 |
|-------|------|---------|
| 1 | 并行读取文件 | < 10秒 |
| 2 | 分块并行+缓存 | < 60秒 |
| 3 | 多轮并行+优先级 | < 300秒 |

### 8.3 缓存策略

```python
# Phase 2/3 缓存层级
L1: 内存缓存（当前会话）
  ↓
L2: 磁盘缓存（~/.repowiki/cache）
  ↓
L3: 重新分析
```

---

## 总结 (Summary)

### 核心创新点

1. **自适应架构** - 根据仓库规模自动选择策略
2. **状态持久化** - 支持长时间运行和中断恢复
3. **多轮分析** - Phase 3的三轮策略保证质量
4. **智能优先级** - 优先处理关键文件
5. **知识图谱** - 结构化的代码理解

### 设计权衡

| 方面 | 选择 | 原因 |
|------|------|------|
| 语言 | Python | 生态丰富、开发快速 |
| 架构 | 三阶段渐进 | 平衡简单性和能力 |
| 存储 | JSON文件 | 简单、可读、可移植 |
| 缓存 | 文件系统 | 无需额外依赖 |

### 未来路线图

- [ ] 语言特定深度分析（AST解析）
- [ ] 分布式分析支持
- [ ] 增量更新机制
- [ ] 交互式UI
- [ ] 云端协作

---

**文档版本:** 1.0  
**最后更新:** 2026-02-04  
**维护者:** RepoWiki Team
