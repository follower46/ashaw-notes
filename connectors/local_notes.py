#!/usr/bin/python3

""" Local File Note Connector module
"""
import re
import time
from datetime import date
from shutil import copyfile
from utils.search import timestamp_to_datestring, get_search_request
from utils.configuration import load_config


config_section = 'local_notes'


def is_enabled():
    return config_section in load_config().get('base_config', 'data_backends')


def save_note(timestamp, note):
    add_local_note(timestamp, note)


def delete_note(timestamp):
    delete_local_note(timestamp)


def update_note(original_timestamp, new_timestamp, new_note):
    delete_note(original_timestamp)
    save_note(new_timestamp, new_note)


def find_notes(search_terms):
    request = get_search_request(search_terms)
    return find_local_notes(request)


# Module Specific Methods

__line_regex__ = re.compile(r'\[([^\]]+)\] (.*)')

def add_local_note(timestamp, note):
    backup_notes()
    reading_file = open(get_notes_file_location(), "r+", encoding="utf8")
    writing_file = open(get_notes_file_location(), "a+", encoding="utf8")
    if not is_header_found(reading_file, timestamp):
        write_header(writing_file, get_date_header(timestamp))
    write_line(writing_file, build_note_line(timestamp, note))
    reading_file.close()
    writing_file.close()


def delete_local_note(timestamp):
    backup_notes()
    log = open(get_notes_file_location(), "r+", encoding="utf8").readlines()
    writing_file = open(get_notes_file_location(), "w", encoding="utf8")
    for line in log:
        if line.find(build_note_line(timestamp, '')) != 0:
            writing_file.write(line)
    writing_file.close()


def find_local_notes(search_request):
    results = []

    reading_file = open(get_notes_file_location(), "r+", encoding="utf8")
    for line in reading_file:
        matching_line = True

        for term in search_request.inclusion_terms:
            if not re.search(r'\b(%s)\b' % term, line):
                matching_line = False
                break

        if not matching_line:
            continue

        for term in search_request.exclusion_terms:
            if re.search(r'\b(%s)\b' % term, line):
                matching_line = False
                break

        if not matching_line:
            continue

        timestamp, note = parse_note_line(line)

        if note:
            epoch = int(time.mktime(time.strptime(timestamp)))
            results.append((epoch, note))
    return results


def get_notes_file_location():
    config = load_config()
    return config.get(config_section, 'location')


def use_backup():
    config = load_config()
    return config.get(config_section, 'create_backup')


def backup_notes():
    if not use_backup():
        return
    destination = get_notes_file_location()
    copyfile(get_notes_file_location(), 
             "%s.bak" % get_notes_file_location())


def restore_from_backup():
    if not use_backup():
        return
    destination = get_notes_file_location()
    copyfile("%s.bak" % get_notes_file_location(), 
             get_notes_file_location())


def is_header_found(file, timestamp):
    header = get_date_header(timestamp)
    for line in file:
        if header in line:
            return True
    return False


def get_date_header(timestamp):
    return date.fromtimestamp(timestamp).isoformat()


def write_header(file, note):
    write_line(file, "==========")
    write_line(file, note)


def build_note_line(timestamp, note):
    return "[%s] %s" % (timestamp_to_datestring(timestamp), note)


def parse_note_line(notes_line):
    global __line_regex__

    line = __line_regex__.findall(notes_line)
    if line:
        return line[0][0], line[0][1]
    return None, None


def write_line(file, line):
    print(line)
    file.write(line + "\n")
