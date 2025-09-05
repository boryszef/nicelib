import os.path
import json

from nicelib.cli import parse_data


def test_pypi_response_parsing():
    print(__file__)
    wdir = os.path.dirname(__file__)
    pypi_sample_path = os.path.join(wdir, "samples", "pypi_sample.json")
    github_sample_path = os.path.join(wdir, "samples", "github_sample.json")
    with open(pypi_sample_path) as fp:
        pypi_data = json.load(fp)
    with open(github_sample_path) as fp:
        github_data = json.load(fp)
    output = parse_data(pypi_data, github_data)
    assert output["name"] == "platformdirs"
