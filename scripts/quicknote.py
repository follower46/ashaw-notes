#!/usr/bin/python3

import re
import time
import readline
import importlib
import ashaw_notes.utils.configuration

import ashaw_notes.connectors.redis_notes as redis_notes
import ashaw_notes.connectors.local_notes as local_notes

noPrefix_regex = re.compile(r'^todo(ne\[[0-9]*\])?:|^(s)?lunch$|^cal:')


def import_connectors():
    """Dynamic imports"""
    modules = []
    module_names = ashaw_notes.utils.configuration.load_config().get('base_config', 'data_backends')
    for module_name in [name.strip() for name in module_names.split(',')]:
        modules.append(importlib.import_module("connectors.%s" % module_name))
    return modules


def setup_auto_complete():
    """Builds up Completer"""
    completer = Completer(redis_notes.get_common_words())
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.complete)


def write_note(note):
    """Builds out note"""
    timestamp = int(time.time())
    print("writing %s" % timestamp)
    note = process_note(note)

    redis_notes.save_note(timestamp, note)
    local_notes.save_note(timestamp, note)


def process_note(note):
    """Builds out note"""
    if noPrefix_regex.match(note):
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
    import_connectors()
    setup_auto_complete()
    write_note(input("note: "))
