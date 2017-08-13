#!/usr/bin/python3
""" Migration Script
    A data migration script for importing/transferring data on backends
"""

import sys
import os


def add_parent_modules(sys_args):
    """Adds parent modules to import"""
    script_path = os.path.abspath(os.path.dirname(sys_args))
    parent_path = os.path.dirname(script_path)
    parent_parent_path = os.path.dirname(parent_path)
    sys.path.append(parent_parent_path)


def run_migrations(sys_argv):
    """Main script method"""
    from ashaw_notes.utils.connection_manager import ConnectionManager
    if len(sys_argv) < 2:
        print("Source Connector Module is required")
        return
    source = ConnectionManager().load_connector(sys_argv[1])

    if len(sys_argv) < 3:
        print("Target Connector Module is required")
        return
    target = ConnectionManager().load_connector(sys_argv[2])

    migrate_notes(source, target)


def migrate_notes(source, target):
    """Migrations notes from source connector to target connector"""
    notes = source.find_notes([])
    count = 1
    for timestamp, note in notes:
        print("%s/%s - %s %s" % (count, len(notes), timestamp, note))
        target.save_note(timestamp, note)
        count += 1

if __name__ == '__main__':
    add_parent_modules(sys.argv[0])
    run_migrations(sys.argv)
