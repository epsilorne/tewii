import click

from tewii.core import init_project


@click.group(add_help_option=False)
@click.help_option("--help", "-h", help="Show this message and exit")
def main():
    """
    TODO: add a good description here
    """
    # Intentionally empty, since interaction is primarily through commands
    pass


@main.command(help="Create an empty project")
@click.argument("name", help="The name of the project")
def init(name: str) -> None:
    try:
        click.echo(init_project(name))
    except Exception as e:
        # TODO: make better
        click.secho(f"{e}")
