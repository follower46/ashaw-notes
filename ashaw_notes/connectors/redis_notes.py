#!/usr/bin/python3

""" Redis Note Connector module
"""
import re
import time
import redis
import ashaw_notes.utils.search
import ashaw_notes.utils.configuration


CONFIG_SECTION = 'redis_notes'
logger = ashaw_notes.utils.configuration.get_logger()


def is_enabled():
    """Checks if connector is enabled"""
    backends = ashaw_notes.utils.configuration.load_config().get('base_config',
                                                                 'data_backends')
    return CONFIG_SECTION in backends


def save_note(timestamp, note):
    """Saves note to timestamp"""
    add_redis_note(timestamp, note)


def delete_note(timestamp):
    """Removes note at supplied timestamp"""
    delete_redis_note(timestamp)


def update_note(original_timestamp, new_timestamp, new_note):
    """Updates note at supplied timestamp"""
    delete_note(original_timestamp)
    save_note(new_timestamp, new_note)


def find_notes(search_terms):
    """Returns all notes corresponding to supplied search object"""
    request = ashaw_notes.utils.search.get_search_request(search_terms)
    return find_redis_notes(request)


def get_common_words():
    """Finds all common words in Redis"""
    redis_connection = get_redis_connection()
    words = redis_connection.keys(get_word_key("*"))
    return set([word[2:].decode('utf-8') for word in words])


# Module Specific Methods

__redis__ = None  # reduces the number of simultaneous redis connections


def add_redis_note(timestamp, note):
    """Adds a note to redis"""
    redis_connection = get_redis_connection()
    tokens = get_note_tokens(timestamp, note)

    logger.debug("Adding %s tokens" % len(tokens))

    # Add search indices
    for token in tokens:
        redis_connection.sadd(token, timestamp)

    # Add notes
    logger.debug("Adding %s note" % timestamp)
    redis_connection.set(get_note_key(timestamp), note)


def delete_redis_note(timestamp):
    """Removes a note from redis"""
    redis_connection = get_redis_connection()

    if not redis_connection.exists(get_note_key(timestamp)):
        return

    line = redis_connection.get(get_note_key(timestamp)).decode('utf-8')
    tokens = get_note_tokens(timestamp, line)

    logger.debug("Deleting %s" % timestamp)
    logger.debug("Deleting %s tokens" % len(tokens))
    # Remove search indices
    for token in tokens:
        redis_connection.srem(token, timestamp)

    # Remove notes
    logger.debug("Deleting %s note" % timestamp)
    redis_connection.delete(get_note_key(timestamp))


def get_note_key(timestamp):
    """Generates redis keyname for note"""
    return "note_%s" % timestamp


def get_word_key(word):
    """Generates redis keyname for word"""
    return "w_%s" % word.lower()


def get_date_keys(timestamp):
    """Generates redis keysnames for timestamp"""
    note_time = time.gmtime(timestamp)
    return [
        "year_%s" % note_time.tm_year,
        "month_%s" % note_time.tm_mon,
        "day_%s" % note_time.tm_mday,
        "hour_%s" % note_time.tm_hour,
        "weekday_%s" % note_time.tm_wday,
    ]


def get_note_tokens(timestamp, line):
    """Generates a list of tokens for a supplied note"""
    tokens = []
    parts = re.findall(r'(\w+)', line)
    for part in parts:
        token = get_word_key(part.lower())
        if token not in tokens:
            tokens.append(get_word_key(part.lower()))

    parts = re.findall(r'(#[A-z0-9-_]+)', line)
    for part in parts:
        token = get_word_key(part.lower())
        if token not in tokens:
            tokens.append(get_word_key(part.lower()))

    tokens += get_date_keys(timestamp)
    return tokens


def find_redis_notes(search_request):
    """Finds all notes related to the request"""
    redis_connection = get_redis_connection()
    timestamps = set([])

    required_keys = []
    excluded_keys = []

    if search_request.inclusion_terms:
        required_keys += [get_word_key(term)
                          for term in search_request.inclusion_terms]
    if search_request.exclusion_terms:
        excluded_keys += [get_word_key(term)
                          for term in search_request.exclusion_terms]

    if search_request.date:
        date_keys = get_date_keys(
            search_request.date.timestamp()
        )
        required_keys += [
            date_keys[0],  # year
            date_keys[1],  # month
            date_keys[2],  # day
        ]

    if required_keys:
        # filter against required note keys
        timestamps = redis_connection.sinter(required_keys)
    else:
        # filter against all notes if none are required
        timestamps = set(
            [key[len(get_note_key('')):]
             for key in set(redis_connection.keys(get_note_key("*")))]
        )

    if timestamps and excluded_keys:
        timestamps = timestamps.difference(
            redis_connection.sunion(excluded_keys))

    timestamps = sorted([int(timestamp.decode('utf-8'))
                         for timestamp in timestamps])

    if not timestamps:
        return [(None, None)]

    notes = redis_connection.mget(
        [get_note_key(timestamp) for timestamp in timestamps])
    notes = [note.decode('utf-8') for note in notes]
    return list(zip(timestamps, notes))


def get_redis_connection():
    """Returns a common redis connection"""
    global __redis__

    config = ashaw_notes.utils.configuration.load_config()

    if not __redis__:
        __redis__ = redis.StrictRedis(
            host=config.get(CONFIG_SECTION, 'endpoint'),
            port=config.get(CONFIG_SECTION, 'port'),
            db=config.get(CONFIG_SECTION, 'db'),
            password=config.get(CONFIG_SECTION, 'password')
        )

    return __redis__
