#!/usr/bin/python3

import re
import time
import readline
import importlib

import connectors.redis_notes as redis_notes
import connectors.local_notes as local_notes

noPrefix_regex = re.compile('^todo(ne\[[0-9]*\])?:|^(s)?lunch$|^cal:')


def import_connectors():
    #importlib.import_module("matplotlib.text")
    pass


def write_note(note):
    timestamp = int(time.time())
    print("writing %s" % timestamp)
    note = process_note(note)

    redis_notes.save_note(timestamp, note)
    local_notes.save_note(timestamp, note)


def process_note(note):
    if noPrefix_regex.match(note):
        return note
    return "today: " + note


class Completer:
    def __init__(self, words):
        self.words = words
        self.prefix = None
    def complete(self, prefix, index):
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

    try:
        completer = Completer(redis_notes.get_common_words())

        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
    except:
        pass

    write_note(input("note: "))
