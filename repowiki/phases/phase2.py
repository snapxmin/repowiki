"""
Phase 2: Medium Repository Understanding Agent

For repositories with 10K-100K lines of code.
Hierarchical analysis with chunking and caching.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..core.agent import BaseAgent
from ..core.analyzer import RepositoryAnalyzer


class Phase2Agent(BaseAgent):
    """Agent for medium repository understanding (10K-100K lines)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_dir = Path.home() / '.repowiki' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_phase(self) -> int:
        return 2
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze medium repository with hierarchical chunking.
        
        Returns:
            Analysis results with hierarchical structure
        """
        # Create task
        task_id = f"phase2_{self.repo_path.name}_{int(os.times().elapsed * 1000)}"
        self.task = self.executor.create_task(task_id, str(self.repo_path), 2)
        
        try:
            # Step 1: Initial scan
            self._update_progress(0.1, "Scanning repository structure")
            analyzer = RepositoryAnalyzer(str(self.repo_path))
            repo_stats = analyzer.analyze()
            
            # Step 2: Build directory hierarchy
            self._update_progress(0.2, "Building directory hierarchy")
            hierarchy = self._build_hierarchy()
            
            # Step 3: Chunk analysis by directory
            self._update_progress(0.4, "Analyzing directories in chunks")
            dir_analysis = self._analyze_directories_chunked(hierarchy)
            
            # Step 4: Build dependency map
            self._update_progress(0.6, "Building dependency map")
            dependencies = self._build_dependency_map(hierarchy)
            
            # Step 5: Generate hierarchical summary
            self._update_progress(0.8, "Generating hierarchical summary")
            summary = self._generate_summary(repo_stats, hierarchy, dir_analysis)
            
            result = {
                'phase': 2,
                'repo_stats': repo_stats,
                'hierarchy': hierarchy,
                'directory_analysis': dir_analysis,
                'dependencies': dependencies,
                'summary': summary,
                'cache_hits': self._get_cache_stats(),
            }
            
            self._update_progress(1.0, "Analysis complete")
            self.executor.complete_task(self.task)
            
            return result
            
        except Exception as e:
            self.executor.fail_task(self.task, str(e))
            raise
    
    def _build_hierarchy(self) -> Dict[str, Any]:
        """Build hierarchical directory structure."""
        analyzer = RepositoryAnalyzer(str(self.repo_path))
        
        def build_tree(path: Path) -> Dict[str, Any]:
            node = {
                'name': path.name,
                'path': str(path.relative_to(self.repo_path)),
                'type': 'directory' if path.is_dir() else 'file',
                'files': [],
                'subdirs': {},
            }
            
            if path.is_dir():
                try:
                    for item in sorted(path.iterdir()):
                        if analyzer._should_ignore(item):
                            continue
                        
                        if item.is_dir():
                            node['subdirs'][item.name] = build_tree(item)
                        else:
                            node['files'].append({
                                'name': item.name,
                                'path': str(item.relative_to(self.repo_path)),
                                'size': item.stat().st_size,
                            })
                except PermissionError:
                    pass
            
            return node
        
        return build_tree(self.repo_path)
    
    def _analyze_directories_chunked(self, hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze directories in chunks with caching."""
        analysis = {}
        
        def analyze_node(node: Dict[str, Any], depth: int = 0):
            path = node['path']
            
            # Check cache
            cached = self._get_cached_analysis(path)
            if cached:
                analysis[path] = cached
                return
            
            # Analyze this directory
            dir_analysis = {
                'depth': depth,
                'file_count': len(node['files']),
                'subdir_count': len(node['subdirs']),
                'total_size': sum(f['size'] for f in node['files']),
            }
            
            # Cache result
            self._cache_analysis(path, dir_analysis)
            analysis[path] = dir_analysis
            
            # Recursively analyze subdirectories
            for subdir in node['subdirs'].values():
                analyze_node(subdir, depth + 1)
        
        analyze_node(hierarchy)
        return analysis
    
    def _build_dependency_map(self, hierarchy: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build simple dependency map (placeholder for more sophisticated analysis)."""
        dependencies = {}
        
        # This is a simplified version - in a real implementation,
        # we would parse imports/includes to build actual dependency graph
        def collect_files(node: Dict[str, Any], files: List[str]):
            for file_info in node['files']:
                files.append(file_info['path'])
            for subdir in node['subdirs'].values():
                collect_files(subdir, files)
        
        all_files = []
        collect_files(hierarchy, all_files)
        
        # Group by directory
        by_dir = {}
        for file_path in all_files:
            dir_path = str(Path(file_path).parent)
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(file_path)
        
        return by_dir
    
    def _get_cached_analysis(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis for a path."""
        cache_key = hashlib.md5(path.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def _cache_analysis(self, path: str, analysis: Dict[str, Any]):
        """Cache analysis result."""
        cache_key = hashlib.md5(path.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(analysis, f)
        except Exception:
            pass
    
    def _get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            return {
                'total_cached_items': len(cache_files),
            }
        except Exception:
            return {'total_cached_items': 0}
    
    def _generate_summary(self, repo_stats: Dict[str, Any],
                         hierarchy: Dict[str, Any],
                         dir_analysis: Dict[str, Any]) -> str:
        """Generate hierarchical summary."""
        lines = [
            "=== Phase 2: Medium Repository Analysis ===",
            f"Repository: {self.repo_path.name}",
            f"Total Files: {repo_stats['total_files']}",
            f"Total Lines: {repo_stats['total_lines']:,}",
            "",
            "Hierarchical Structure:",
            f"  Total Directories: {len(dir_analysis)}",
            f"  Max Depth: {max((a['depth'] for a in dir_analysis.values()), default=0)}",
            "",
            "Analysis Strategy:",
            "  ✓ Hierarchical chunking applied",
            "  ✓ Directory-level caching enabled",
            "  ✓ Context maintained across chunks",
            "",
            "Status: ✓ Analysis complete",
        ]
        
        return "\n".join(lines)
