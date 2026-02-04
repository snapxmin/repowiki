#!/usr/bin/env python3
"""Quick demonstration of RepoWiki capabilities."""

from repowiki.core.analyzer import RepositoryAnalyzer
from repowiki.phases.phase1 import Phase1Agent

def main():
    """Run a quick demo on the repowiki repository itself."""
    print("=" * 70)
    print("RepoWiki Quick Demonstration")
    print("=" * 70)
    print()
    
    # Analyze the repowiki repository itself
    repo_path = "/home/runner/work/repowiki/repowiki"
    
    print(f"Analyzing: {repo_path}")
    print()
    
    # Step 1: Repository Analysis
    print("Step 1: Repository Analysis")
    print("-" * 70)
    analyzer = RepositoryAnalyzer(repo_path)
    stats = analyzer.analyze()
    
    print(f"Total Files: {stats['total_files']}")
    print(f"Total Lines: {stats['total_lines']:,}")
    print(f"Detected Phase: {stats['phase']}")
    print(f"Description: {analyzer.get_phase_description(stats['phase'])}")
    print()
    
    print("File Type Distribution:")
    for ext, count in sorted(stats['file_types'].items(), 
                            key=lambda x: x[1], reverse=True):
        print(f"  {ext:15s}: {count:3d} files")
    print()
    
    # Step 2: Run Phase 1 Analysis
    print("Step 2: Running Phase 1 Analysis")
    print("-" * 70)
    agent = Phase1Agent(repo_path)
    results = agent.analyze()
    
    # Display summary
    print(results['summary'])
    print()
    
    # Step 3: Show Analysis Details
    print("Step 3: Analysis Details")
    print("-" * 70)
    file_analysis = results['file_analysis']
    print(f"Files analyzed: {file_analysis['total_files']}")
    print(f"File types: {len(file_analysis['by_extension'])}")
    print()
    
    print("Largest files:")
    for i, file_info in enumerate(file_analysis['largest_files'][:5], 1):
        size_kb = file_info['size'] / 1024
        print(f"  {i}. {file_info['path']:40s} ({size_kb:.1f} KB)")
    print()
    
    print("=" * 70)
    print("✓ Demonstration Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
