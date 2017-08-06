#!/usr/bin/python3

""" Redis Note Connector module
"""
import configparser
import re
import redis
import time
from datetime import date
from utils.search import timestamp_to_datestring, get_search_request


def save_note(timestamp, note):
    add_redis_note(timestamp, note)


def delete_note(timestamp):
    delete_redis_note(timestamp)


def update_note(original_timestamp, new_timestamp, new_note):
    delete_note(original_timestamp)
    save_note(new_timestamp, new_note)


def find_notes(search_terms):
    request = get_search_request(search_terms)
    return find_redis_notes(request)


# Module Specific Methods

__redis__ = None # reduces the number of simultaneous redis connections

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


def delete_redis_note(timestamp):
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


def get_note_key(timestamp):
    return "note_%s" % timestamp


def get_word_key(word):
    return "w_%s" % word.lower()


def get_note_tokens(timestamp, line):
    tokens = []
    parts = re.findall(r'(\w+)', line)
    for part in parts:
        tokens.append(get_word_key(part.lower()))

    note_time = time.gmtime(timestamp)
    tokens.append("year_%s" % note_time.tm_year)
    tokens.append("month_%s" % note_time.tm_mon)
    tokens.append("day_%s" % note_time.tm_mday)
    tokens.append("hour_%s" % note_time.tm_hour)
    tokens.append("weekday_%s" % note_time.tm_wday)
    return tokens


def get_common_words():
    redis = get_redis_connection()
    words = redis.keys(get_word_key("*"))
    return [word[2:].decode('utf-8') for word in words]


def find_redis_notes(search_request):
    redis = get_redis_connection()
    timestamps = set([])

    if search_request.inclusion_terms:
        timestamps = redis.sinter([get_word_key(term) for term in search_request.inclusion_terms])
        if search_request.exclusion_terms:
            timestamps = timestamps.difference(redis.sunion([get_word_key(term) for term in search_request.exclusion_terms]))
    elif search_request.exclusion_terms:
        timestamps = set([key[len(get_note_key('')):] for key in set(redis.keys(get_note_key("*")))])
        exclusion_timestamps = redis.sunion([get_word_key(term) for term in search_request.exclusion_terms])

        timestamps = timestamps.difference(exclusion_timestamps)
    else:
        timestamps = [key[len(get_note_key('')):] for key in set(redis.keys(get_note_key("*")))]

    timestamps = [int(timestamp.decode('utf-8')) for timestamp in timestamps]
    timestamps.sort()

    notes = redis.mget([get_note_key(timestamp) for timestamp in timestamps])
    notes = [note.decode('utf-8') for note in notes]
    return list(zip(timestamps, notes))


def get_redis_connection():
    global __redis__

    config = configparser.ConfigParser()
    config.read('notes.config')

    if not __redis__:
        __redis__ = redis.StrictRedis(
            host=config.get('redis_server', 'endpoint'), 
            port=config.get('redis_server', 'port'), 
            db=config.get('redis_server', 'db'),
            password=config.get('redis_server', 'password')
        )

    return __redis__
