#!/usr/bin/python3
""" Notes Switchboard
    All actions are executed from this base file
"""

import click
import ashaw_notes.scripts.quicknote
import ashaw_notes.scripts.migration
import ashaw_notes.gui.main

@click.group()
def cli():
    """Basic Click CLI"""
    pass

@click.command()
def gui():
    """Opens up the Notes QT Gui"""
    ashaw_notes.gui.main.run()

@click.command()
@click.option('--note', default=None, help='A note to add')
@click.option('--backend', default="all", help='A backend to add the note to')
def quicknote(note, backend):
    """Adds a note"""
    ashaw_notes.scripts.quicknote.run()

@click.command()
@click.argument('source')
@click.argument('target')
def migrate(source, target):
    """Migrates notes from one backend to another"""
    ashaw_notes.scripts.migration.run(source, target)

cli.add_command(gui)
cli.add_command(quicknote)
cli.add_command(migrate)

if __name__ == '__main__':
    cli()
