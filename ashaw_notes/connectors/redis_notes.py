#!/usr/bin/python3

""" Redis Note Connector module
"""
import re
import time
import redis
import uuid
import ashaw_notes.utils.search
import ashaw_notes.utils.configuration


class RedisNotes:

    config_section = 'redis_notes'
    logger = ashaw_notes.utils.configuration.get_logger()
    redis_connection = None  # reduces the number of simultaneous redis connections

    def is_enabled(self):
        """Checks if connector is enabled"""
        backends = ashaw_notes\
            .utils.configuration\
            .load_config()\
            .get('base_config', 'data_backends')
        return self.config_section in backends

    def save_note(self, timestamp, note):
        """Saves note to timestamp"""
        self.add_redis_note(timestamp, note)

    def delete_note(self, timestamp):
        """Removes note at supplied timestamp"""
        self.delete_redis_note(timestamp)

    def update_note(self, original_timestamp, new_timestamp, new_note):
        """Updates note at supplied timestamp"""
        self.delete_note(original_timestamp)
        self.save_note(new_timestamp, new_note)

    def find_notes(self, search_terms):
        """Returns all notes corresponding to supplied search object"""
        self.logger.debug("Building search request")
        request = ashaw_notes.utils.search.get_search_request(search_terms)
        self.logger.debug("Calling find_redis_notes")
        return self.find_redis_notes(request)

    def get_common_words(self):
        """Finds all common words in Redis"""
        redis_connection = self.get_redis_connection()
        words = redis_connection.keys(self.get_word_key("*"))
        return set([word[2:].decode('utf-8') for word in words])

    def add_redis_note(self, timestamp, note):
        """Adds a note to redis"""
        redis_connection = self.get_redis_connection()
        note_key = self.get_note_key(timestamp)
        watch_key = self.get_watch_key(timestamp)
        if redis_connection.exists(note_key) or redis_connection.exists(watch_key):
            # no duplicates are allowed
            # add a little bit to the timestamp and try again
            self.logger.warning("%s already exists, " \
                        "adding 1 to timestamp and trying note " \
                        "\"%s\" again", timestamp, note)
            return self.add_redis_note(timestamp + 1, note)

        with redis_connection.pipeline() as pipe:
            try:
                self.start_watch(watch_key, pipe)

                tokens = self.get_note_tokens(timestamp, note)
                self.logger.debug("Adding %s tokens", len(tokens))
                for token in tokens:
                    self.add_note_token(pipe, token, timestamp)

                # add source token
                self.add_note_token(pipe, self.get_note_source_key(), timestamp)

                self.logger.debug("Adding %s note", timestamp)
                pipe.set(self.get_note_key(timestamp), note)

                # Run pipe commands
                pipe.execute()

                # Clear out watch key
                redis_connection.delete(watch_key)
            except redis.WatchError:
                # Redis has updated against the watch variable
                self.logger.error("Watch failed on %s - \"%s\". " \
                                "Attemping insert again.", watch_key, note)
                self.add_redis_note(timestamp, note)

    @staticmethod
    def add_note_token(pipe, token, timestamp):
        """Adds note token to redis pipe"""
        pipe.sadd(token, timestamp)

    def delete_redis_note(self, timestamp):
        """Removes a note from redis"""
        redis_connection = self.get_redis_connection()
        note_key = self.get_note_key(timestamp)
        watch_key = self.get_watch_key(timestamp)

        if not redis_connection.exists(note_key):
            self.logger.warning("Attempted to delete non-existing note: %s", timestamp)
            return

        if redis_connection.exists(watch_key):
            self.logger.error("Existing opperation on %s", watch_key)
            raise RuntimeWarning("%s was found! Update against %s in progress", watch_key, timestamp)

        with redis_connection.pipeline() as pipe:
            self.start_watch(watch_key, pipe)
            # get current notes tokens
            note = pipe.get(self.get_note_key(timestamp)).decode('utf-8')
            tokens = self.get_note_tokens(timestamp, note)
            sources = pipe.keys("source_*")
            # Return pipe to multi mode
            pipe.multi()

            self.logger.debug("Deleting %s tokens", len(tokens))
            for token in tokens:
                pipe.srem(token, timestamp)

            self.logger.debug("Deleting %s note", timestamp)
            pipe.delete(self.get_note_key(timestamp))

            self.logger.debug("Deleting %s note source", timestamp)
            for source in sources:
                pipe.srem(source, timestamp)

            # Run pipe commands
            pipe.execute()

            # Clear out watch key
            redis_connection.delete(watch_key)

    @staticmethod
    def get_watch_key(timestamp):
        """Generates watch keyname for note"""
        return "watch_%s" % timestamp

    @staticmethod
    def get_note_key(timestamp):
        """Generates redis keyname for note"""
        return "note_%s" % timestamp

    def get_note_source_key(self):
        """Generates redis source keyname for note"""
        config = ashaw_notes.utils.configuration.load_config()
        source = config.get(self.config_section, 'note_source')
        return "source_%s" % source

    @staticmethod
    def get_word_key(word):
        """Generates redis keyname for word"""
        return "w_%s" % word.lower()

    @staticmethod
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

    def get_note_tokens(self, timestamp, line):
        """Generates a list of tokens for a supplied note"""
        tokens = []
        parts = re.findall(r'(\w+)', line)
        for part in parts:
            token = self.get_word_key(part.lower())
            if token not in tokens:
                tokens.append(self.get_word_key(part.lower()))

        parts = re.findall(r'(#[A-z0-9-_]+)', line)
        for part in parts:
            token = self.get_word_key(part.lower())
            if token not in tokens:
                tokens.append(self.get_word_key(part.lower()))

        tokens += self.get_date_keys(timestamp)
        return tokens

    def start_watch(self, watch_key, pipe):
        """Adds watch to redis pipe"""
        # Create watch key
        self.get_redis_connection().set(watch_key, uuid.uuid4())
        # Start the watch
        pipe.watch(watch_key)

    def find_redis_notes(self, search_request):
        """Finds all notes related to the request"""
        self.logger.debug("Finding notes")
        redis_connection = self.get_redis_connection()

        required_keys = []
        excluded_keys = []

        self.logger.debug("Building Redis Keys")
        if search_request.inclusion_terms:
            required_keys += [self.get_word_key(term)
                              for term in search_request.inclusion_terms]
        if search_request.exclusion_terms:
            excluded_keys += [self.get_word_key(term)
                              for term in search_request.exclusion_terms]

        if search_request.date:
            self.logger.debug("Building Redis Keys: Date")
            date_keys = self.get_date_keys(
                search_request.date.timestamp()
            )
            required_keys += [
                date_keys[0],  # year
                date_keys[1],  # month
                date_keys[2],  # day
            ]

        self.logger.debug("Getting Timestamps")
        if required_keys:
            # filter against required note keys
            timestamps = redis_connection.sinter(required_keys)
        else:
            # filter against all notes if none are required
            timestamps = set(
                [key[len(self.get_note_key('')):]
                 for key in set(redis_connection.keys(self.get_note_key("*")))]
            )

        if timestamps and excluded_keys:
            self.logger.debug("Excluding Timestamps")
            timestamps = timestamps.difference(
                redis_connection.sunion(excluded_keys))

        self.logger.debug("Sorting timestamps")
        timestamps = sorted([int(timestamp.decode('utf-8'))
                             for timestamp in timestamps])

        if not timestamps:
            return [(None, None)]

        self.logger.debug("Getting Notes")
        notes = redis_connection.mget(
            [self.get_note_key(timestamp) for timestamp in timestamps])
        self.logger.debug("Decoding Notes")
        notes = [note.decode('utf-8') for note in notes]
        self.logger.debug("Zipping Notes")
        return list(zip(timestamps, notes))

    def get_redis_connection(self):
        """Returns a common redis connection"""
        config = ashaw_notes.utils.configuration.load_config()

        if not self.redis_connection:
            redis_connection = redis.StrictRedis(
                host=config.get(self.config_section, 'endpoint'),
                port=config.get(self.config_section, 'port'),
                db=config.get(self.config_section, 'db'),
                password=config.get(self.config_section, 'password')
            )

        return redis_connection
