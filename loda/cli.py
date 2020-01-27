from colorama import init as init_colorama
from pyfiglet import figlet_format
from termcolor import cprint
from . import __version__
from .exceptions import ConfigError, ScriptError, StorageError, FixtureError
from .scripting import Script
import click
import logging
import os
import sys


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--dry-run', is_flag=True)
def main(debug, dry_run):
    handler = logging.StreamHandler()
    root = logging.getLogger('loda')

    root.setLevel(debug and 'DEBUG' or 'INFO')
    root.addHandler(handler)
    logger = logging.getLogger('loda')

    if sys.stdout.isatty():
        click.echo(
            cprint(
                figlet_format('Loda'),
                'red'
            )
        )

    click.echo('Loda the Robot v%s' % __version__)
    click.echo()

    filename = os.path.join(os.getcwd(), 'script.yaml')
    script = None

    try:
        script = Script.from_file(filename)
    except ConfigError as ex:
        click.echo('Configuration error: %s' % ex.args[0])
    except FixtureError as ex:
        if debug:
            logger.exception('Fixture error: %s' % ex.args[0])
        else:
            click.echo('Fixture error: %s' % ex.args[0])

    if script is None:
        raise SystemExit(1)

    logger.debug('Running script.')

    def line_error(ex):
        logger.warn(str(ex), exc_info=debug)

    script.on('line.error', line_error)
    script.dry_run = dry_run

    try:
        script.run()
    except StorageError as ex:
        if debug:
            logger.exception(
                'Storage error running script: %s' % ex.args[0]
            )
        else:
            click.echo('Storage error running script: %s' % ex.args[0])

        raise SystemExit(1)
    except (ScriptError, FixtureError) as ex:
        if debug:
            logger.exception('Runtime error with script: %s' % ex.args[0])
        else:
            click.echo('Runtime error with script: %s' % ex.args[0])

        raise SystemExit(1)


# Strip colors if stdout is redirected
init_colorama(strip=not sys.stdout.isatty())
