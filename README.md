# RepoWiki

A phased agent system for understanding repositories of varying complexity - from simple projects to massive codebases with millions of lines of code.

## Overview

RepoWiki implements a three-phase approach to repository analysis, automatically selecting the appropriate strategy based on repository size:

- **Phase 1** (< 10K lines): Simple repositories - Direct analysis of all files
- **Phase 2** (10K-100K lines): Medium repositories - Hierarchical analysis with chunking and caching
- **Phase 3** (> 100K lines): Complex repositories - Multi-pass analysis with intelligent prioritization and context preservation

## Features

### Phase 1: Simple Repository Understanding
- Direct file-by-file analysis
- Complete content indexing
- Fast processing for small projects
- Simple dependency tracking

### Phase 2: Medium Repository Understanding  
- Hierarchical directory-based chunking
- Intelligent caching mechanism
- Context-aware analysis
- Resumable task execution
- Optimized for medium-sized codebases

### Phase 3: Complex Repository Understanding
- Multi-pass analysis strategy (3 passes)
- Intelligent file prioritization system
- Dependency graph construction
- Knowledge graph generation
- Advanced context compression
- Designed for large-scale projects

## Installation

```bash
pip install -e .
```

## Usage

### Analyze a Repository

```bash
# Auto-detect phase and analyze
repowiki analyze /path/to/repo

# Force a specific phase
repowiki analyze /path/to/repo --force-phase 2

# Save results to file
repowiki analyze /path/to/repo -o results.json

# Verbose output
repowiki analyze /path/to/repo -v
```

### Get Repository Information

```bash
repowiki info /path/to/repo
```

### List Analysis Tasks

```bash
# List recent tasks
repowiki tasks

# List all tasks
repowiki tasks --all
```

## Architecture

The system is built with modularity and extensibility in mind:

```
repowiki/
├── core/           # Core components
│   ├── analyzer.py    # Repository analysis and phase detection
│   ├── agent.py       # Base agent class
│   └── executor.py    # Task execution and state management
├── phases/         # Phase implementations
│   ├── phase1.py      # Simple repository agent
│   ├── phase2.py      # Medium repository agent
│   └── phase3.py      # Complex repository agent
└── utils/          # Utility functions
```

### Key Components

1. **RepositoryAnalyzer**: Scans repositories and determines complexity
2. **TaskExecutor**: Manages task execution with state persistence
3. **Phase Agents**: Specialized agents for different complexity levels
4. **Context Management**: Preserves intent across analysis passes

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Test Coverage

```bash
pytest --cov=repowiki --cov-report=html
```

## Examples

### Example 1: Analyze a Simple Python Project

```bash
repowiki analyze my-simple-project/
```

Output:
```
=== Phase 1: Simple Repository Analysis ===
Repository: my-simple-project
Total Files: 15
Total Lines: 1,234

File Types:
  .py: 10 files (45,678 bytes)
  .md: 3 files (12,345 bytes)
  .txt: 2 files (1,234 bytes)

Status: ✓ Analysis complete
```

### Example 2: Analyze a Medium Project

```bash
repowiki analyze medium-webapp/ --force-phase 2 -o analysis.json
```

### Example 3: Check Repository Info Before Analysis

```bash
repowiki info /path/to/large/repo
```

## Roadmap

- [x] Phase 1: Simple repository understanding
- [x] Phase 2: Medium repository understanding  
- [x] Phase 3: Complex repository understanding
- [ ] Export to multiple formats (Markdown, HTML, PDF)
- [ ] Interactive UI for exploring analysis results
- [ ] Plugin system for custom analyzers
- [ ] Language-specific deep analysis
- [ ] Integration with popular IDEs

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
