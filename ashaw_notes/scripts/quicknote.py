#!/usr/bin/python3

import re
import time
import readline
import importlib
import sys
import os


__regex__ = re.compile(r'^todo(ne\[[0-9]*\])?:|^(s)?lunch$|^cal:')


def add_parent_modules(sys_args):
    """Adds parent modules to import"""
    script_path = os.path.abspath(os.path.dirname(sys_args))
    parent_path = os.path.dirname(script_path)
    parent_parent_path = os.path.dirname(parent_path)
    sys.path.append(parent_parent_path)

def import_connectors():
    """Dynamic imports"""
    import ashaw_notes.utils.configuration

    modules = []
    module_names = ashaw_notes.utils.configuration.load_config().get('base_config', 'data_backends')
    for module_name in [name.strip() for name in module_names.split(',')]:
        modules.append(importlib.import_module("ashaw_notes.connectors.%s" % module_name))
    return modules


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


def process_note(note):
    """Builds out note"""
    if __regex__.match(note):
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
    add_parent_modules(sys.argv[0])
    imported_modules = import_connectors()
    setup_auto_complete(imported_modules)
    write_note(input("note: "), imported_modules)
