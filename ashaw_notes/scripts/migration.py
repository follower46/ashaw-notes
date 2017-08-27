#!/usr/bin/python3
""" Migration Script
    A data migration script for importing/transferring data on backends
"""

import sys
from ashaw_notes.utils.connection_manager import ConnectionManager
from ashaw_notes.utils.search import timestamp_to_datestring


def run(source_name, target_name):
    """Main script method"""
    if not source_name:
        print("Source Connector Module is required")
        return
    source = ConnectionManager().load_connector(source_name)

    if not target_name:
        print("Target Connector Module is required")
        return
    target = ConnectionManager().load_connector(target_name)

    migrate_notes(source, target)


def migrate_notes(source, target):
    """Migrations notes from source connector to target connector"""
    notes = source.find_notes([])
    count = 1
    for timestamp, note in notes:
        print(
            "%s/%s - [%s] %s" %
            (count,
             len(notes),
             timestamp_to_datestring(timestamp),
             note))
        target.save_note(timestamp, note)
        count += 1
