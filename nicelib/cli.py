import locale
import re
from collections import OrderedDict
from datetime import datetime, timezone
from urllib.parse import urlparse

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
locale.setlocale(locale.LC_ALL, "")


@click.command()
@click.argument("module_name")
def cli(module_name):
    data = query_pypi(module_name)
    if data is None:
        render_error("Lookup failed.")
        return
    source = get_source_info(data)
    if source is None:
        render_error("Source not on github - not supported.")
        return
    output = parse_data(data, source)
    render_output(output)


def parse_data(pypi_data, repo_data):
    info = pypi_data["info"]
    python_versions = get_supported_python_versions(info["classifiers"])
    updated_at = datetime.strptime(
        repo_data["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    return OrderedDict(
        [
            ("name", info["name"]),
            ("summary", info["summary"]),
            ("Latest version", info["version"]),
            ("Number of releases", str(len(pypi_data["releases"]))),
            ("Supported Python versions", ", ".join(map(str, python_versions))),
            ("Most recent commit", updated_at.strftime("%x")),
            ("Starred", str(repo_data["stargazers_count"])),
            ("Watchers", str(repo_data["subscribers_count"])),
        ]
    )


def render_output(data):
    name = data.pop("name")
    summary = data.pop("summary")
    table = Table(show_header=False, box=None)
    table.add_column("key", justify="right")
    table.add_column("value", justify="left")
    for key, value in data.items():
        table.add_row(f"[bright_blue]{key}:[/bright_blue]", value)
    content = Group(f"{summary}", table)
    panel = Panel(content, title=f"[bold green]{name}[/bold green]")
    Console().print(panel)


def render_error(msg):
    Console().print(f"[bold red]Error:[/] {msg}")


python_version_pattern = re.compile(r"Programming Language :: Python :: (\d+\.\d+)")


def get_supported_python_versions(classifiers):
    versions = []
    for cl in classifiers:
        match = python_version_pattern.match(cl)
        if match:
            versions.append(match.group(1))
    return sorted(map(version.parse, versions))


github_project_pattern = re.compile(r"github\.com\/([A-Za-z0-9_-]+)\/([A-Za-z0-9_-]+)")


def get_source_info(pypi_data):
    url = pypi_data["info"]["project_urls"]["Source"]
    netloc = urlparse(url).netloc
    if netloc != "github.com":
        return None
    match = github_project_pattern.search(url)
    if match is None:
        return None
    owner = match.group(1)
    project = match.group(2)
    return query_github(owner, project)


pypi_project_url = "https://pypi.org/pypi/{project}/json"


@memory.cache(cache_validation_callback=expires_after(days=7))
def query_pypi(module_name):
    url = pypi_project_url.format(project=module_name)
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


github_project_url = "https://api.github.com/repos/{owner}/{repo}"


@memory.cache(cache_validation_callback=expires_after(days=7))
def query_github(owner, project):
    url = github_project_url.format(owner=owner, repo=project)
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


if __name__ == "__main__":
    cli()
