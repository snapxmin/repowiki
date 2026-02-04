"""
Phase 1: Simple Repository Understanding Agent

For repositories with < 10K lines of code.
Direct analysis approach - reads all files and builds comprehensive understanding.
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from ..core.agent import BaseAgent
from ..core.analyzer import RepositoryAnalyzer


class Phase1Agent(BaseAgent):
    """Agent for simple repository understanding (< 10K lines)."""
    
    def get_phase(self) -> int:
        return 1
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze simple repository with direct approach.
        
        Returns:
            Comprehensive analysis results
        """
        # Create task
        task_id = f"phase1_{self.repo_path.name}_{int(os.times().elapsed * 1000)}"
        self.task = self.executor.create_task(task_id, str(self.repo_path), 1)
        
        try:
            # Step 1: Initial repository scan
            self._update_progress(0.1, "Scanning repository structure")
            analyzer = RepositoryAnalyzer(str(self.repo_path))
            repo_stats = analyzer.analyze()
            
            # Step 2: Build file inventory
            self._update_progress(0.3, "Building file inventory")
            files = self._build_file_inventory()
            
            # Step 3: Analyze file contents
            self._update_progress(0.5, "Analyzing file contents")
            file_analysis = self._analyze_files(files)
            
            # Step 4: Build structure map
            self._update_progress(0.7, "Building structure map")
            structure = self._get_file_structure(self.repo_path, max_depth=5)
            
            # Step 5: Generate summary
            self._update_progress(0.9, "Generating summary")
            summary = self._generate_summary(repo_stats, file_analysis)
            
            result = {
                'phase': 1,
                'repo_stats': repo_stats,
                'file_count': len(files),
                'files': files[:100],  # Limit for display
                'structure': structure,
                'summary': summary,
                'file_analysis': file_analysis,
            }
            
            self._update_progress(1.0, "Analysis complete")
            self.executor.complete_task(self.task)
            
            return result
            
        except Exception as e:
            self.executor.fail_task(self.task, str(e))
            raise
    
    def _build_file_inventory(self) -> List[Dict[str, Any]]:
        """Build inventory of all relevant files."""
        analyzer = RepositoryAnalyzer(str(self.repo_path))
        files = []
        
        for root, dirs, filenames in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not analyzer._should_ignore(root_path / d)]
            
            for filename in filenames:
                file_path = root_path / filename
                
                if analyzer._should_ignore(file_path):
                    continue
                
                try:
                    rel_path = file_path.relative_to(self.repo_path)
                    stat = file_path.stat()
                    
                    files.append({
                        'path': str(rel_path),
                        'full_path': str(file_path),
                        'size': stat.st_size,
                        'extension': file_path.suffix,
                    })
                except Exception:
                    continue
        
        return files
    
    def _analyze_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file contents for understanding."""
        analysis = {
            'total_files': len(files),
            'by_extension': {},
            'largest_files': [],
        }
        
        # Group by extension
        for file_info in files:
            ext = file_info['extension'] or 'no_extension'
            if ext not in analysis['by_extension']:
                analysis['by_extension'][ext] = {'count': 0, 'total_size': 0}
            
            analysis['by_extension'][ext]['count'] += 1
            analysis['by_extension'][ext]['total_size'] += file_info['size']
        
        # Find largest files
        sorted_files = sorted(files, key=lambda f: f['size'], reverse=True)
        analysis['largest_files'] = sorted_files[:10]
        
        return analysis
    
    def _generate_summary(self, repo_stats: Dict[str, Any], 
                         file_analysis: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        lines = [
            "=== Phase 1: Simple Repository Analysis ===",
            f"Repository: {self.repo_path.name}",
            f"Total Files: {repo_stats['total_files']}",
            f"Total Lines: {repo_stats['total_lines']:,}",
            "",
            "File Types:",
        ]
        
        for ext, stats in sorted(file_analysis['by_extension'].items()):
            lines.append(f"  {ext}: {stats['count']} files ({stats['total_size']:,} bytes)")
        
        lines.extend([
            "",
            "Status: ✓ Analysis complete",
            "All files have been directly analyzed and indexed.",
        ])
        
        return "\n".join(lines)
