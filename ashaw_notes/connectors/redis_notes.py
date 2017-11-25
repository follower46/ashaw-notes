#!/usr/bin/python3

""" Redis Note Connector module
"""
import re
import time
import redis
import uuid
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
    logger.debug("Building search request")
    request = ashaw_notes.utils.search.get_search_request(search_terms)
    logger.debug("Calling find_redis_notes")
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
    note_key = get_note_key(timestamp)
    watch_key = get_watch_key(timestamp)
    if redis_connection.exists(note_key) or redis_connection.exists(watch_key):
        # no duplicates are allowed
        # add a little bit to the timestamp and try again
        logger.warning("%s already exists, " \
                    "adding 1 to timestamp and trying note " \
                    "\"%s\" again", timestamp, note)
        return add_redis_note(timestamp + 1, note)

    with redis_connection.pipeline() as pipe:
        try:
            start_watch(watch_key, pipe)

            tokens = get_note_tokens(timestamp, note)
            logger.debug("Adding %s tokens", len(tokens))
            for token in tokens:
                add_note_token(pipe, token, timestamp)

            # add source token
            add_note_token(pipe, get_note_source_key(), timestamp)

            logger.debug("Adding %s note", timestamp)
            pipe.set(get_note_key(timestamp), note)

            # Run pipe commands
            pipe.execute()

            # Clear out watch key
            redis_connection.delete(watch_key)
        except redis.WatchError:
            # Redis has updated against the watch variable
            logger.error("Watch failed on %s - \"%s\". " \
                            "Attemping insert again.", watch_key, note)
            add_redis_note(timestamp, note)


def add_note_token(pipe, token, timestamp):
    """Adds note token to redis pipe"""
    pipe.sadd(token, timestamp)


def delete_redis_note(timestamp):
    """Removes a note from redis"""
    redis_connection = get_redis_connection()
    note_key = get_note_key(timestamp)
    watch_key = get_watch_key(timestamp)

    if not redis_connection.exists(note_key):
        logger.warning("Attempted to delete non-existing note: %s", timestamp)
        return

    if redis_connection.exists(watch_key):
        logger.error("Existing opperation on %s", watch_key)
        raise RuntimeWarning("%s was found! Update against %s in progress", watch_key, timestamp)

    with redis_connection.pipeline() as pipe:
        start_watch(watch_key, pipe)
        # get current notes tokens
        note = pipe.get(get_note_key(timestamp)).decode('utf-8')
        tokens = get_note_tokens(timestamp, note)
        sources = pipe.keys("source_*")
        # Return pipe to multi mode
        pipe.multi()

        logger.debug("Deleting %s tokens", len(tokens))
        for token in tokens:
            pipe.srem(token, timestamp)

        logger.debug("Deleting %s note", timestamp)
        pipe.delete(get_note_key(timestamp))

        logger.debug("Deleting %s note source", timestamp)
        for source in sources:
            pipe.srem(source, timestamp)

        # Run pipe commands
        pipe.execute()

        # Clear out watch key
        redis_connection.delete(watch_key)


def get_watch_key(timestamp):
    """Generates watch keyname for note"""
    return "watch_%s" % timestamp


def get_note_key(timestamp):
    """Generates redis keyname for note"""
    return "note_%s" % timestamp


def get_note_source_key():
    """Generates redis source keyname for note"""
    config = ashaw_notes.utils.configuration.load_config()
    source = config.get(CONFIG_SECTION, 'note_source')
    return "source_%s" % source


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


def start_watch(watch_key, pipe):
    """Adds watch to redis pipe"""
    # Create watch key
    get_redis_connection().set(watch_key, uuid.uuid4())
    # Start the watch
    pipe.watch(watch_key)


def find_redis_notes(search_request):
    """Finds all notes related to the request"""
    logger.debug("Finding notes")
    redis_connection = get_redis_connection()
    timestamps = set([])

    required_keys = []
    excluded_keys = []

    logger.debug("Building Redis Keys")
    if search_request.inclusion_terms:
        required_keys += [get_word_key(term)
                          for term in search_request.inclusion_terms]
    if search_request.exclusion_terms:
        excluded_keys += [get_word_key(term)
                          for term in search_request.exclusion_terms]

    if search_request.date:
        logger.debug("Building Redis Keys: Date")
        date_keys = get_date_keys(
            search_request.date.timestamp()
        )
        required_keys += [
            date_keys[0],  # year
            date_keys[1],  # month
            date_keys[2],  # day
        ]

    logger.debug("Getting Timestamps")
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
        logger.debug("Excluding Timestamps")
        timestamps = timestamps.difference(
            redis_connection.sunion(excluded_keys))

    logger.debug("Sorting timestamps")
    timestamps = sorted([int(timestamp.decode('utf-8'))
                         for timestamp in timestamps])

    if not timestamps:
        return [(None, None)]

    logger.debug("Getting Notes")
    notes = redis_connection.mget(
        [get_note_key(timestamp) for timestamp in timestamps])
    logger.debug("Decoding Notes")
    notes = [note.decode('utf-8') for note in notes]
    logger.debug("Zipping Notes")
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
