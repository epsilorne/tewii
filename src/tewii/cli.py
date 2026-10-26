import sys
import click

from tewii.core import edit_project, init_project


@click.group(add_help_option=False)
@click.help_option("--help", "-h", help="Show this message and exit")
def main():
    """
    Tewii: A seamless Markdown to LaTeX & PDF experience
    """
    # Intentionally empty, since interaction is primarily through commands
    pass


@main.command(help="Create an empty project")
@click.argument("name", help="The name of the project")
def init(name: str) -> None:
    try:
        click.echo(init_project(name))
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", file=sys.stderr)


@main.command(help="Edit an existing project")
@click.argument("name", help="The name of the project")
def edit(name: str) -> None:
    try:
        click.echo(edit_project(name))
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", file=sys.stderr)
