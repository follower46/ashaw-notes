#!/usr/bin/python3
""" QuickNote Script
    Data input script for adding new notes
"""

import re
import time
import readline
import sys
import os

from ashaw_notes.utils.plugin_manager import PluginManager


def run_quicknote(sys_args):
    """Main quicknote method"""
    add_parent_modules(sys_args)
    modules = import_connectors()
    setup_auto_complete(modules)
    write_note(take_note(), modules)


def add_parent_modules(sys_args):
    """Adds parent modules to import"""
    script_path = os.path.abspath(os.path.dirname(sys_args))
    parent_path = os.path.dirname(script_path)
    parent_parent_path = os.path.dirname(parent_path)
    sys.path.append(parent_parent_path)


def import_connectors():
    """Dynamic imports"""
    import ashaw_notes.utils.configuration
    return ashaw_notes.utils.configuration.get_connection_modules()


def setup_auto_complete(modules):
    """Builds up Completer"""
    words = set()
    for module in modules:
        words = words | module.get_common_words()
    completer = Completer(list(words))
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.complete)


def write_note(note, modules):
    """Builds out note"""
    timestamp = int(time.time())
    print("writing %s" % timestamp)
    note = process_note(note)

    for module in modules:
        module.save_note(timestamp, note)


def take_note():
    """Gets note from user"""
    return input("note: ")


def process_note(note):
    """Builds out note"""
    if PluginManager().bypass_today(note):
        return note
    return "today: " + note


class Completer:
    """Auto completion class"""
    def __init__(self, words):
        self.words = words
        self.prefix = None
        self.matching_words = []
    def complete(self, prefix, index):
        """Auto completion method"""
        if prefix != self.prefix:
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
        try:
            return self.matching_words[index] + " "
        except IndexError:
            return None


if __name__ == '__main__':
    run_quicknote(sys.argv[0])
