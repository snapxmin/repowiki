"""
Command-line interface for RepoWiki.
"""
import click
import json
from pathlib import Path
from .core.analyzer import RepositoryAnalyzer
from .core.executor import TaskExecutor
from .phases.phase1 import Phase1Agent
from .phases.phase2 import Phase2Agent
from .phases.phase3 import Phase3Agent


@click.group()
@click.version_option(version='0.1.0')
def main():
    """RepoWiki - A phased agent system for understanding repositories."""
    pass


@main.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--force-phase', type=click.Choice(['1', '2', '3']), 
              help='Force a specific phase instead of auto-detection')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file for analysis results (JSON)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Verbose output')
def analyze(repo_path, force_phase, output, verbose):
    """
    Analyze a repository and generate understanding.
    
    REPO_PATH: Path to the repository to analyze
    """
    click.echo(f"Analyzing repository: {repo_path}")
    click.echo()
    
    try:
        # Determine phase
        analyzer = RepositoryAnalyzer(repo_path)
        stats = analyzer.analyze()
        
        if force_phase:
            phase = int(force_phase)
            click.echo(f"Forcing Phase {phase} (user specified)")
        else:
            phase = stats['phase']
            click.echo(f"Auto-detected Phase {phase}")
        
        click.echo(f"  {analyzer.get_phase_description(phase)}")
        click.echo()
        
        # Select and run appropriate agent
        executor = TaskExecutor()
        
        if phase == 1:
            agent = Phase1Agent(repo_path, executor)
        elif phase == 2:
            agent = Phase2Agent(repo_path, executor)
        else:
            agent = Phase3Agent(repo_path, executor)
        
        click.echo("Starting analysis...")
        results = agent.analyze()
        
        # Display summary
        click.echo()
        click.echo(results['summary'])
        
        # Save results if requested
        if output:
            output_path = Path(output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo()
            click.echo(f"Results saved to: {output_path}")
        
        # Show task info
        if verbose and agent.task:
            click.echo()
            click.echo(f"Task ID: {agent.task.task_id}")
            click.echo(f"Status: {agent.task.status.value}")
            click.echo(f"Progress: {agent.task.progress * 100:.1f}%")
        
        click.echo()
        click.secho("✓ Analysis completed successfully!", fg='green', bold=True)
        
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        raise click.Abort()


@main.command()
@click.argument('repo_path', type=click.Path(exists=True))
def info(repo_path):
    """
    Show repository information and recommended phase.
    
    REPO_PATH: Path to the repository to analyze
    """
    try:
        analyzer = RepositoryAnalyzer(repo_path)
        stats = analyzer.analyze()
        
        click.echo("Repository Information:")
        click.echo(f"  Path: {stats['repo_path']}")
        click.echo(f"  Total Files: {stats['total_files']}")
        click.echo(f"  Total Lines: {stats['total_lines']:,}")
        click.echo()
        click.echo(f"Recommended Phase: {stats['phase']}")
        click.echo(f"  {analyzer.get_phase_description(stats['phase'])}")
        click.echo()
        
        if stats['file_types']:
            click.echo("File Types:")
            for ext, count in sorted(stats['file_types'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10]:
                click.echo(f"  {ext}: {count}")
        
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        raise click.Abort()


@main.command()
@click.option('--all', '-a', is_flag=True, help='Show all tasks')
def tasks(all):
    """List analysis tasks."""
    executor = TaskExecutor()
    task_list = executor.list_tasks()
    
    if not task_list:
        click.echo("No tasks found.")
        return
    
    click.echo(f"Found {len(task_list)} task(s):")
    click.echo()
    
    for task in task_list[:10 if not all else None]:
        status_color = {
            'completed': 'green',
            'in_progress': 'yellow',
            'failed': 'red',
            'pending': 'blue',
            'paused': 'cyan',
        }.get(task.status.value, 'white')
        
        click.echo(f"Task: {task.task_id}")
        click.echo(f"  Repository: {task.repo_path}")
        click.echo(f"  Phase: {task.phase}")
        click.secho(f"  Status: {task.status.value}", fg=status_color)
        click.echo(f"  Progress: {task.progress * 100:.1f}%")
        click.echo(f"  Current Step: {task.current_step}")
        click.echo(f"  Started: {task.started_at}")
        if task.completed_at:
            click.echo(f"  Completed: {task.completed_at}")
        if task.error:
            click.secho(f"  Error: {task.error}", fg='red')
        click.echo()


@main.command()
def version():
    """Show version information."""
    click.echo("RepoWiki v0.1.0")
    click.echo("A phased agent system for understanding repositories")


if __name__ == '__main__':
    main()
