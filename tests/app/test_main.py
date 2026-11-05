"""Tests for the entry point src/main.py."""

import os
import runpy
from unittest import mock

import flet as ft
import pytest

from asdf_hero.ui import theme

MAIN = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src", "main.py")


def run_script(monkeypatch, **env):
    for name in ("FLET_SERVER_IP", "FLET_SERVER_PORT"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    with mock.patch("flet.run") as run:
        namespace = runpy.run_path(MAIN, run_name="__main__")
    return run, namespace


def test_starts_the_web_server(monkeypatch):
    run, namespace = run_script(monkeypatch)

    run.assert_called_once()
    args, kwargs = run.call_args
    assert args[0].__name__ == "main"
    assert kwargs["view"] == ft.AppView.WEB_BROWSER
    assert kwargs["assets_dir"] == namespace["ASSETS_DIR"]
    assert kwargs["host"] is None
    assert kwargs["port"] == 8550


def test_server_ip_and_port_from_the_environment(monkeypatch):
    run, _ = run_script(monkeypatch, FLET_SERVER_IP="0.0.0.0", FLET_SERVER_PORT="9000")

    assert run.call_args.kwargs["host"] == "0.0.0.0"
    assert run.call_args.kwargs["port"] == 9000


def test_background_image_is_in_the_assets(monkeypatch):
    _, namespace = run_script(monkeypatch)

    path = os.path.join(namespace["ASSETS_DIR"], theme.BACKGROUND_IMAGE)
    assert os.path.isfile(path)


def test_importing_does_not_start_the_server():
    with mock.patch("flet.run") as run:
        runpy.run_path(MAIN, run_name="main")

    run.assert_not_called()
