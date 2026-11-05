"""requirements-dev.txt has the same packages as pyproject.toml."""

import pathlib

import pytest
from packaging.requirements import Requirement

tomllib = pytest.importorskip("tomllib")  # Python 3.11+

ROOT = pathlib.Path(__file__).resolve().parent.parent


def requirements_file():
    lines = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
    return [Requirement(line) for line in map(str.strip, lines) if line and not line.startswith("#")]


def pyproject_requirements():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    extras = project["optional-dependencies"]
    specs = project["dependencies"] + [spec for group in extras.values() for spec in group]
    return [Requirement(spec) for spec in specs]


def test_every_pyproject_package_is_in_requirements_dev():
    by_name = {req.name: req for req in requirements_file()}

    for req in pyproject_requirements():
        assert req.name in by_name, req
        assert by_name[req.name].specifier == req.specifier, req
        assert req.extras <= by_name[req.name].extras, req


def test_no_extra_packages_in_requirements_dev():
    names = {req.name for req in pyproject_requirements()}

    assert {req.name for req in requirements_file()} <= names


def test_run_test_and_build_tools():
    flet = {req.name: req for req in requirements_file()}["flet"]

    assert flet.extras == {"web", "cli"}  # web server + `flet build`
    assert {"pytest", "pytest-cov"} <= {req.name for req in requirements_file()}
