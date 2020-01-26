from loda.cli import main
from click.testing import CliRunner
from mock import patch
from . import storage
from .helpers import getcwd
import pytest


def test_script_not_found():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    assert 'Script not found.' in output_lines[-1]


@patch('os.getcwd', getcwd('cli.invalid_yaml'))
def test_script_invalid_yaml():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    assert 'Script file syntax is invalid.' in output_lines[-1]


@patch('os.getcwd', getcwd('cli.fixture_not_found'))
def test_fixture_not_found():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    assert 'Fixture \'foo\' not found.' in output_lines[-1]

    runner = CliRunner()
    result = runner.invoke(main, '--debug')
    assert result.exit_code == 1


@patch('os.getcwd', getcwd('cli.storage_engine_not_found'))
def test_storage_engine_not_found():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    last = output_lines[-1]
    assert 'Storage engine module \'foo\' not found.' in last

    runner = CliRunner()
    result = runner.invoke(main, '--debug')
    assert result.exit_code == 1


def imp(module):
    if module == 'tests.storage':
        return storage

    if module == 'tests.actors.faulty':
        from .actors import faulty
        return faulty

    if module == 'loda.actors.dummy':
        from loda.actors import dummy
        return dummy

    if module == 'loda.storage.engines.locmem':
        from loda.storage.engines import locmem
        return locmem

    pytest.fail('Untested module import for \'%s\'' % module)


@patch('os.getcwd', getcwd('cli.storage_error'))
@patch('importlib.import_module', imp)
def test_script_error():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    last = output_lines[-1]
    assert 'Error setting value in bucket.' in last

    runner = CliRunner()
    result = runner.invoke(main, '--debug')
    assert result.exit_code == 1


@patch('os.getcwd', getcwd('cli.fixture_error'))
@patch('importlib.import_module', imp)
def test_fixture_error():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 1

    output_lines = result.output.splitlines()
    last = output_lines[-1]
    assert 'Syntax is invalid.' in last

    runner = CliRunner()
    result = runner.invoke(main, '--debug')
    assert result.exit_code == 1


@patch('os.getcwd', getcwd('cli.line_error'))
@patch('importlib.import_module', imp)
def test_line_error():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

    output_lines = result.output.splitlines()
    assert 'Error running line \'raise exception\'' in output_lines[-1]
