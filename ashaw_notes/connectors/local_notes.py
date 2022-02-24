#!/usr/bin/python3

""" Local File Note Connector module
"""
import re
import os
from datetime import datetime
import shutil
import ashaw_notes.utils.search
import ashaw_notes.utils.configuration
from ashaw_notes.utils.search import datestring_to_timestamp


CONFIG_SECTION = 'local_notes'


def is_enabled():
    """Checks if connector is enabled"""
    backends = ashaw_notes.utils.configuration.load_config().get('base_config',
                                                                 'data_backends')
    return CONFIG_SECTION in backends


def save_note(timestamp, note):
    """Saves note to timestamp"""
    add_local_note(timestamp, note)


def delete_note(timestamp):
    """Removes note at supplied timestamp"""
    delete_local_note(timestamp)


def update_note(original_timestamp, new_timestamp, new_note):
    """Updates note at supplied timestamp"""
    delete_note(original_timestamp)
    save_note(new_timestamp, new_note)


def find_notes(search_terms):
    """Returns all notes corresponding to supplied search object"""
    request = ashaw_notes.utils.search.get_search_request(search_terms)
    return find_local_notes(request)


def get_common_words():
    """Finds all common words in note file"""
    # not yet implemented
    return set()


# Module Specific Methods

__line_regex__ = re.compile(r'\[([^\]]+)\] (.*)')


def add_local_note(timestamp, note):
    """Inserts note into local file"""
    backup_notes()
    if os.path.isfile(get_notes_file_location()):
        reading_file = open(get_notes_file_location(), "r+", encoding="utf8")
    else:
        reading_file = None
    writing_file = open(get_notes_file_location(), "a+", encoding="utf8")
    if not is_header_found(reading_file, timestamp):
        write_header(writing_file, get_date_header(timestamp))
    write_line(writing_file, build_note_line(timestamp, note))
    if reading_file:
        reading_file.close()
    writing_file.close()


def delete_local_note(timestamp):
    """Removes note at timestamp from file"""
    backup_notes()
    log = open(get_notes_file_location(), "r+", encoding="utf8").readlines()
    writing_file = open(get_notes_file_location(), "w", encoding="utf8")
    for line in log:
        if line.find(build_note_line(timestamp, '')) != 0:
            writing_file.write(line)
    writing_file.close()


def find_local_notes(search_request):
    """Searches notes file for given request"""
    results = []

    reading_file = open(get_notes_file_location(), "r+", encoding="utf8")
    for line in reading_file:
        matching_line = True

        for term in search_request.inclusion_terms:
            if not re.search(r'(%s)\b' % term, line):
                matching_line = False
                break

        if not matching_line:
            continue

        for term in search_request.exclusion_terms:
            if re.search(r'%s' % term, line):
                matching_line = False
                break

        if not matching_line:
            continue

        timestamp, note = parse_note_line(line)
        
        if not timestamp:
            continue

        if search_request.date:
            pattern = re.compile(
                search_request.date.strftime("%a %b %d [^ ]+ %Y"))
            if not pattern.match(timestamp):
                continue

        if note:
            epoch = datestring_to_timestamp(timestamp)
            results.append((epoch, note))
    return results


def get_notes_file_location():
    """Returns the note file location from the config"""
    config = ashaw_notes.utils.configuration.load_config()
    return config.get(CONFIG_SECTION, 'location')


def use_backup():
    """Checks if local backups are enabled"""
    config = ashaw_notes.utils.configuration.load_config()
    return config.get(CONFIG_SECTION, 'create_backup')


def backup_notes():
    """Creates a local backup of the notes file"""
    if not use_backup():
        return
    if os.path.isfile(get_notes_file_location()):
        shutil.copyfile(get_notes_file_location(),
                        "%s.bak" % get_notes_file_location())


def restore_from_backup():
    """Restores previous note file"""
    if not use_backup():
        return
    shutil.copyfile("%s.bak" % get_notes_file_location(),
                    get_notes_file_location())


def is_header_found(file, timestamp):
    """Checks for header in file"""
    if not file:
        return False

    header = get_date_header(timestamp)
    for line in file:
        if "%s\n" % header == line:
            return True
    return False


def get_date_header(timestamp):
    """Builds header"""
    return ashaw_notes.utils.search.timestamp_to_datestring(timestamp, False)


def write_header(file, note):
    """Writes header to file"""
    write_line(file, "==========")
    write_line(file, note)


def build_note_line(timestamp, note):
    """Generates a note line for insertion"""
    return "[%s] %s" % (
        ashaw_notes.utils.search.timestamp_to_datestring(timestamp), note)


def parse_note_line(notes_line):
    """Rips apart note line into its timestamp and note"""
    line = __line_regex__.findall(notes_line)
    if line:
        return line[0][0], line[0][1]
    return None, None


def write_line(file, line):
    """Writes line to file"""
    file.write("%s\n" % line)
