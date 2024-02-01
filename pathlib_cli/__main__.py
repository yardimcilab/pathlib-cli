import click
import sys
from pathlib import PurePath

# Update process_paths_and_echo to handle ignore_errors properly
def process_paths_and_echo(paths, func, ignore_errors=False):
    processed_paths = paths if paths else [PurePath(line.strip()) for line in click.get_text_stream('stdin')]
    for path_str in processed_paths:
        path = PurePath(path_str)
        try:
            result = func(path)
            click.echo(result if result is not None else '')
        except Exception as e:
            if ignore_errors:
                continue
            else:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)

@click.group()
def cli():
    """ CLI tool for PurePath functionality """
    pass

def list_of_strings(lst):
    return [str(x) for x in lst]

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
def root(paths):
    """Print the root part of the paths."""
    # If no paths are provided through arguments, try reading from stdin
    if not paths:
        paths = [PurePath(line.strip()) for line in click.get_text_stream('stdin')]
    else:
        paths = [PurePath(path) for path in paths]
    
    for path in paths:
        click.echo(path.root)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
@click.option('--level', '-l', default=None, type=int, help='Specify the level of parent to print')
@click.option('--ignore-errors', is_flag=True, help='Output a blank line instead of crashing on errors')
def parents(paths, level, ignore_errors):
    """Print the parents of the paths."""
    if not paths:
        paths = [PurePath(line.strip()) for line in click.get_text_stream('stdin')]
    else:
        paths = [PurePath(path) for path in paths]

    for path in paths:
        try:
            if level is not None:
                click.echo(path.parents[level])
            else:
                # Adjusted to handle the conversion within the command
                click.echo('\t'.join([str(p) for p in path.parents]))
        except IndexError:
            if ignore_errors:
                click.echo()
            else:
                click.echo(f"Error: Specified level not found for {path}", err=True)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
def parent(paths):
    """Print the parent of the paths."""
    process_paths_and_echo(paths, lambda p: p.parent)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
def name(paths):
    """Print the name of the paths."""
    process_paths_and_echo(paths, lambda p: p.name)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
def stem(paths):
    """Print the stem of the paths."""
    process_paths_and_echo(paths, lambda p: p.stem)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
@click.option('--level', '-l', default=None, type=int)
@click.option('--ignore-errors', is_flag=True)
def suffixes(paths, level, ignore_errors):
    """Print the suffixes of the paths."""
    process_paths_and_echo(paths, lambda p: p.suffixes[level] if level is not None else '\t'.join(p.suffixes), ignore_errors=ignore_errors)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
@click.option('--ignore-errors', is_flag=True)
def suffix(paths, ignore_errors):
    """Print the suffix of the paths."""
    process_paths_and_echo(paths, lambda p: p.suffixes[0], ignore_errors=ignore_errors)

# Helper functions for specific path operations
def get_nth_prefix(file_path, n):
    parts = file_path.stem.split('.')
    if n < len(parts):
        return parts[n]
    else:
        raise ValueError(f"Level {n} out of range for {file_path}")

def get_all_prefixes(file_path):
    prefixes = file_path.name.split('.')
    return ['.'.join(prefixes[:i]) for i in range(1, len(prefixes)+1)]

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
@click.option('--level', '-l', default=None, type=int)
@click.option('--ignore-errors', is_flag=True)
def prefixes(paths, level, ignore_errors):
    """Print all prefixes of the paths or a specific level prefix."""
    def process_prefix(p):
        all_prefixes = get_all_prefixes(p)
        if level is not None:
            if level < len(all_prefixes):
                return all_prefixes[level]
            else:
                raise ValueError(f"Level {level} out of range for {p}")
        return '\n'.join(all_prefixes)
    
    process_paths_and_echo(paths, process_prefix, ignore_errors=ignore_errors)

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=False))
@click.option('--ignore-errors', is_flag=True)
def prefix(paths, ignore_errors):
    """Print the prefix of the paths."""
    process_paths_and_echo(paths, lambda p: get_nth_prefix(p, 0), ignore_errors=ignore_errors)

cli.add_command(root)
cli.add_command(parents)
cli.add_command(parent)
cli.add_command(name)
cli.add_command(stem)
cli.add_command(suffixes)
cli.add_command(suffix)
cli.add_command(prefixes)
cli.add_command(prefix)

if __name__ == '__main__':
    cli()
