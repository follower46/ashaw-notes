#!/usr/bin/python3
import re
import time
from utils.configuration import load_config
from datetime import date
from redis_connector import get_redis_connection

__notes__ = None
__line_regex__ = re.compile(r'\[([^\]]+)\] (.*)')



''' Imports and loads up notes file
'''
def load_notes():
    global __notes__
    config = load_config()

    __notes__ = {}
    with open(config.get('notes_file', 'location')) as file:
        for line in file:
            timestamp, parsed_line = parse_notes_line(line)
            if parsed_line:
                epoch = int(time.mktime(time.strptime(timestamp)))
                __notes__[epoch] = parsed_line


def parse_notes_line(notes_line):
    global __line_regex__

    line = __line_regex__.findall(notes_line)
    if line:

        return line[0][0], line[0][1]
    return None, None


def import_notes():
    global __notes__

    redis = get_redis_connection()
    i = 0;
    for timestamp in sorted(__notes__):
        line = __notes__[timestamp]

        if redis.exists(get_note_key(timestamp)):
            print("%s: Skipping %s (keys already exist)" % (i, timestamp))
            i += 1
            continue

        print("%s: Adding %s" % (i, timestamp))
        add_redis_note(timestamp, line)

        i += 1


def add_redis_note(timestamp, note):
    redis = get_redis_connection()
    tokens = get_note_tokens(timestamp, note)

    print("    Adding %s tokens" % len(tokens))
    # Add search indices
    for token in tokens:
        redis.sadd(token, timestamp)
    
    # Add notes
    print("    Adding %s note" % timestamp)
    redis.set(get_note_key(timestamp), note)


def get_notes_file_location():
    config = load_config()
    return config.get('notes_file', 'location')


def export_notes(export_path=None):
    if not export_path:
        export_path = get_notes_file_location()

    redis = get_redis_connection()
    note_keys = redis.keys(get_note_key("*"))
    note_keys.sort()

    with open(export_path, 'w+') as file:
        previous_date = None
        for note_key in note_keys:
            current_date = get_date_header(get_timestamp(note_key))
            if previous_date != current_date:
                write_header(file, current_date)
                previous_date = current_date


            note = redis.get(note_key)
            write_line(file, get_note_line(note_key))


def get_date_header(timestamp):
    return date.fromtimestamp(timestamp).isoformat()


def write_header(file, note):
    write_line(file, "==========")
    write_line(file, note)


def write_line(file, line):
    print(line)
    file.write(line + "\n")


def delete_note(timestamp):
    # delete local note line
    #line = __notes__[timestamp]

    # delete remote line
    redis = get_redis_connection()

    if not redis.exists(get_note_key(timestamp)):
        return

    line = redis.get(get_note_key(timestamp)).decode('utf-8')
    tokens = get_note_tokens(timestamp, line)

    print("Deleting %s" % timestamp)
    print("    Deleting %s tokens" % len(tokens))
    # Add search indices
    for token in tokens:
        redis.srem(token, timestamp)
    
    # Add notes
    print("    Deleting %s note" % timestamp)
    redis.delete(get_note_key(timestamp))


def get_note_line(note_key):
    return build_note_line(get_timestamp(note_key), get_redis_connection().get(note_key).decode('utf-8'))


def build_note_line(timestamp, note):
    return "[%s] %s" % (time.asctime(time.localtime(timestamp)), note)


def get_time(note_key):
    return time.localtime(get_timestamp(note_key))


def get_timestamp(note_key):
    return int(note_key[len(get_note_key('')):])


def get_note_key(timestamp):
    return "note_%s" % timestamp


def get_note_tokens(timestamp, line):
    tokens = []
    parts = re.findall(r'(\w+)', line)
    for part in parts:
        tokens.append("w_%s" % part.lower())

    note_time = time.gmtime(timestamp)
    tokens.append("year_%s" % note_time.tm_year)
    tokens.append("month_%s" % note_time.tm_mon)
    tokens.append("day_%s" % note_time.tm_mday)
    tokens.append("hour_%s" % note_time.tm_hour)
    tokens.append("weekday_%s" % note_time.tm_wday)
    return tokens

if __name__ == '__main__':
    #load_notes()
    #delete_note(1498842351)
    #delete_note(1498842274)
    #import_notes()
    export_notes()
    pass
