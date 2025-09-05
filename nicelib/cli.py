import re

import click
import requests
from joblib import Memory, expires_after
from packaging import version
from platformdirs import user_cache_dir
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table


APP_NAME = "nicelib"
CACHE_PATH = user_cache_dir(APP_NAME)

memory = Memory(CACHE_PATH)


@click.command()
@click.argument("module_name")
def cli(module_name):
    data = query_pypi(module_name)
    if data is None:
        render_error("Lookup failed.")
        return
    render_output(data)


def render_output(data):
    info = data["info"]
    summary = info["summary"]
    name = info["name"]
    latest_version = info["version"]
    release_count = len(data["releases"])
    python_versions = get_supported_python_versions(info["classifiers"])
    table = Table(show_header=False, box=None)
    table.add_column("key", justify="right")
    table.add_column("value", justify="left")
    table.add_row("[bright_blue]Latest version:[/bright_blue]", latest_version)
    table.add_row("[bright_blue]Number of releases:[/bright_blue]", str(release_count))
    table.add_row(
        "[bright_blue]Supported Python versions:[/bright_blue]",
        ", ".join(map(str, python_versions)),
    )
    content = Group(f"{summary}", table)
    panel = Panel(content, title=f"[bold green]{name}[/bold green]")
    Console().print(panel)


def render_error(msg):
    Console().print(f"[bold red]Error:[/] {msg}")


pattern = re.compile(r"Programming Language :: Python :: (\d+\.\d+)")


def get_supported_python_versions(classifiers):
    versions = []
    for cl in classifiers:
        match = pattern.match(cl)
        if match:
            versions.append(match.group(1))
    return sorted(map(version.parse, versions))


pypi_project_url = "https://pypi.org/pypi/{project}/json"


@memory.cache(cache_validation_callback=expires_after(days=7))
def query_pypi(module_name):
    url = pypi_project_url.format(project=module_name)
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


if __name__ == "__main__":
    cli()
