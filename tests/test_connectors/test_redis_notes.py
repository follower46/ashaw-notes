""" Testing Local Notes Module
"""

import unittest
import logging
import redis
import fakeredis
from mock import MagicMock, patch, call
from ddt import ddt, data, unpack
from ashaw_notes.connectors import redis_notes
from ashaw_notes.utils.search import get_search_request


@ddt
class LocalNotesTests(unittest.TestCase):
    """Unit Testing Local Notes"""

    def setUp(self):
        """Setup for testing."""
        self.redis = fakeredis.FakeStrictRedis()
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clear data in fakeredis."""
        self.redis.flushall()

    @unpack
    @data(
        ('redis_notes', True),
        ('redis_notes, local_notes', True),
        ('local_notes', False),
    )
    @patch('ashaw_notes.utils.configuration.load_config')
    def test_is_enabled(self, string, expectation, load_config):
        """Verifies is_enabled is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, redis_notes.is_enabled())

    @patch('ashaw_notes.connectors.redis_notes.add_redis_note')
    def test_save_note(self, add_redis_note):
        """Verifies save_note is properly functioning"""
        redis_notes.save_note(12345, "test note")
        add_redis_note.assert_called_once_with(12345, "test note")

    @patch('ashaw_notes.connectors.redis_notes.delete_redis_note')
    def test_delete_note(self, delete_redis_note):
        """Verifies delete_note is properly functioning"""
        redis_notes.delete_note(12345)
        delete_redis_note.assert_called_once_with(12345)

    @patch('ashaw_notes.connectors.redis_notes.save_note')
    @patch('ashaw_notes.connectors.redis_notes.delete_redis_note')
    def test_update_note(self, delete_redis_note, save_note):
        """Verifies update_note is properly functioning"""
        redis_notes.update_note(12345, 23456, "test note")
        delete_redis_note.assert_called_once_with(12345)
        save_note.assert_called_once_with(23456, "test note")

    @patch('ashaw_notes.utils.search.get_search_request')
    @patch('ashaw_notes.connectors.redis_notes.find_redis_notes')
    def test_find_notes(self, find_redis_notes, get_search_request):
        """Verifies find_note is properly functioning"""
        redis_notes.find_notes(["test note"])
        get_search_request.assert_called_once_with(["test note"])
        find_redis_notes.assert_called_once()

    @patch('ashaw_notes.connectors.redis_notes.get_note_source_key')
    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_add_redis_note(self, get_redis_connection, get_note_source_key):
        """Verifies add_redis_note is properly functioning"""
        get_redis_connection.return_value = self.redis
        get_note_source_key.return_value = 'source_unittests'
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")

        keys = sorted(self.redis.keys())

        self.assertListEqual(
            [
                b'_keys_1373500800',
                b'day_11',
                b'hour_0',
                b'month_7',
                b'note_1373500800',
                b'source_unittests',
                b'w_#yolo',
                b'w_a',
                b'w_is',
                b'w_simple',
                b'w_test',
                b'w_this',
                b'w_today',
                b'w_yolo',
                b'weekday_3',
                b'year_2013'
            ], keys
        )
        self.assertEqual(
            b"today: this is a simple test #yolo",
            self.redis.get('note_1373500800')
        )

    @patch('ashaw_notes.connectors.redis_notes.get_note_source_key')
    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_add_redis_note_duplicate(self, get_redis_connection, get_note_source_key):
        """Verifies add_redis_note doesn't allow duplicates"""
        get_redis_connection.return_value = self.redis
        get_note_source_key.return_value = 'source_unittests'
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")
        redis_notes.add_redis_note(
            1373500800, "today: same time, different note")

        keys = sorted(self.redis.keys())

        self.assertListEqual(
            [
                b'_keys_1373500800',
                b'_keys_1373500801',
                b'day_11',
                b'hour_0',
                b'month_7',
                b'note_1373500800',
                b'note_1373500801',
                b'source_unittests',
                b'w_#yolo',
                b'w_a',
                b'w_different',
                b'w_is',
                b'w_note',
                b'w_same',
                b'w_simple',
                b'w_test',
                b'w_this',
                b'w_time',
                b'w_today',
                b'w_yolo',
                b'weekday_3',
                b'year_2013'
            ], keys
        )

        self.assertEqual(
            b"today: this is a simple test #yolo",
            self.redis.get('note_1373500800')
        )

        self.assertEqual(
            b"today: same time, different note",
            self.redis.get('note_1373500801')
        )

    @patch('ashaw_notes.connectors.redis_notes.start_watch')
    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_add_redis_note_failure(self, get_redis_connection, start_watch):
        """Verifies that notes attempt re-add on failure"""
        get_redis_connection.return_value = self.redis
        start_watch.side_effect = [
            redis.WatchError(),
            True,
        ]
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")
        self.assertEqual(
            2,
            len(start_watch.mock_calls))
        self.assertEqual(
            b"today: this is a simple test #yolo",
            self.redis.get('note_1373500800')
        )

    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_delete_redis_note_miss(self, get_redis_connection):
        """Verifies delete_redis_note handles bad timestamp properly"""
        get_redis_connection.return_value = self.redis
        redis_notes.add_redis_note(1373500800, "today: this is note 1")
        redis_notes.add_redis_note(1450794188, "today: this is note 2")
        redis_notes.delete_redis_note(1373500801)
        self.assertEqual(
            b"today: this is note 1",
            self.redis.get('note_1373500800'))
        self.assertEqual(
            b"today: this is note 2",
            self.redis.get('note_1450794188'))

    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_delete_redis_note_watched(self, get_redis_connection):
        """Verifies delete_redis_note doesn't delete on a watched timestamp"""
        get_redis_connection.return_value = self.redis
        redis_notes.add_redis_note(1373500800, "today: this is note 1")
        self.redis.set(redis_notes.get_watch_key(1373500800), 1234)
        with self.assertRaises(RuntimeWarning):
            redis_notes.delete_redis_note(1373500800)
        self.assertEqual(
            b"today: this is note 1",
            self.redis.get('note_1373500800'))

    @patch('ashaw_notes.connectors.redis_notes.get_note_source_key')
    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_delete_redis_note_hit(self, get_redis_connection, get_note_source_key):
        """Verifies delete_redis_note is properly functioning"""
        get_redis_connection.return_value = self.redis
        get_note_source_key.return_value = 'source_unittests'
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")
        redis_notes.add_redis_note(1450794188, "today: this is note 2")

        keys = sorted(self.redis.keys())

        self.assertListEqual(
            [
                b'_keys_1373500800',
                b'_keys_1450794188',
                b'day_11',
                b'day_22',
                b'hour_0',
                b'hour_14',
                b'month_12',
                b'month_7',
                b'note_1373500800',
                b'note_1450794188',
                b'source_unittests',
                b'w_#yolo',
                b'w_2',
                b'w_a',
                b'w_is',
                b'w_note',
                b'w_simple',
                b'w_test',
                b'w_this',
                b'w_today',
                b'w_yolo',
                b'weekday_1',
                b'weekday_3',
                b'year_2013',
                b'year_2015'
            ], keys
        )

        redis_notes.delete_redis_note(1373500800)
        keys.sort()

        self.assertEqual(b"set()", self.redis.get('day_11'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('day_22'))
        self.assertEqual(b"set()", self.redis.get('hour_0'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('hour_14'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('month_12'))
        self.assertEqual(b"set()", self.redis.get('month_7'))
        self.assertEqual(None, self.redis.get('note_1373500800'))
        self.assertEqual(None, self.redis.get('_keys_1373500800'))
        self.assertEqual(
            b"today: this is note 2",
            self.redis.get('note_1450794188'))
        self.assertEqual(b"set()", self.redis.get('w_#yolo'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('w_2'))
        self.assertEqual(b"set()", self.redis.get('w_a'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('w_is'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('w_note'))
        self.assertEqual(b"set()", self.redis.get('w_simple'))
        self.assertEqual(b"set()", self.redis.get('w_test'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('w_this'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('w_today'))
        self.assertEqual(b"set()", self.redis.get('w_yolo'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('weekday_1'))
        self.assertEqual(b"set()", self.redis.get('weekday_3'))
        self.assertEqual(b"set()", self.redis.get('year_2013'))
        self.assertEqual(b"{b'1450794188'}", self.redis.get('year_2015'))

    @unpack
    @data(
        (1373500800, 'note_1373500800'),
        (1450794188, 'note_1450794188'),
        ('*', 'note_*'),
    )
    def test_get_note_key(self, timestamp, expectation):
        """Verifies get_note_key is properly functioning"""
        key = redis_notes.get_note_key(timestamp)
        self.assertEqual(expectation, key)

    @unpack
    @data(
        ('test', 'w_test'),
        ('test1234', 'w_test1234'),
        ('#hashtag', 'w_#hashtag'),
        ('*', 'w_*'),
    )
    def test_get_word_key(self, word, expectation):
        """Verifies get_word_key is properly functioning"""
        key = redis_notes.get_word_key(word)
        self.assertEqual(expectation, key)

    @unpack
    @data(
        (1373500800, "a quick note", [
            'w_a',
            'w_quick',
            'w_note',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1373500800, "a a a quick note", [
            'w_a',
            'w_quick',
            'w_note',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1373500800, "special&&& characters #awesome", [
            'w_special',
            'w_characters',
            'w_awesome',
            'w_#awesome',
            'year_2013',
            'month_7',
            'day_11',
            'hour_0',
            'weekday_3']),
        (1450794188, "#yolo #sl4life #tons-of-hashtags #yolo", [
            'w_yolo',
            'w_sl4life',
            'w_tons',
            'w_of',
            'w_hashtags',
            'w_#yolo',
            'w_#sl4life',
            'w_#tons-of-hashtags',
            'year_2015',
            'month_12',
            'day_22',
            'hour_14',
            'weekday_1']),
    )
    def test_get_note_tokens(self, timestamp, note, expectation):
        """Verifies get_note_tokens is properly functioning"""
        tokens = redis_notes.get_note_tokens(timestamp, note)
        self.assertListEqual(expectation, tokens)

    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_get_common_words(self, get_redis_connection):
        """Verifies get_common_words is properly functioning"""
        get_redis_connection.return_value = self.redis
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")
        redis_notes.add_redis_note(1450794188, "today: this is note 2")

        words = sorted(redis_notes.get_common_words())

        self.assertListEqual(
            ['#yolo', '2', 'a', 'is', 'note', 'simple', 'test', 'this', 'today', 'yolo'],
            words
        )

    @patch('ashaw_notes.connectors.redis_notes.get_note_source_key')
    @patch('ashaw_notes.connectors.redis_notes.get_redis_connection')
    def test_find_redis_notes(self, get_redis_connection, get_note_source_key):
        """Verifies find_redis_notes is properly functioning"""
        get_redis_connection.return_value = self.redis
        get_note_source_key.return_value = 'source_unittests'
        redis_notes.add_redis_note(
            1373500800, "today: this is a simple test #yolo")
        redis_notes.add_redis_note(1450794188, "today: this is note 2")

        first_note = [
            (1373500800, 'today: this is a simple test #yolo')
        ]
        second_note = [
            (1450794188, 'today: this is note 2')
        ]
        both_notes = [
            (1373500800, 'today: this is a simple test #yolo'),
            (1450794188, 'today: this is note 2')
        ]

        request = get_search_request(['simple'])
        self.assertListEqual(first_note, redis_notes.find_redis_notes(request))

        request = get_search_request(['this'])
        self.assertListEqual(both_notes, redis_notes.find_redis_notes(request))

        request = get_search_request(['this', '!yolo'])
        self.assertListEqual(second_note,
                             redis_notes.find_redis_notes(request))

        request = get_search_request(['!note'])
        self.assertListEqual(first_note, redis_notes.find_redis_notes(request))

        request = get_search_request()
        self.assertListEqual(both_notes, redis_notes.find_redis_notes(request))

        request = get_search_request(['date:1450794188'])
        self.assertListEqual(second_note,
                             redis_notes.find_redis_notes(request))

        request = get_search_request(['missing'])
        self.assertListEqual(
            [(None, None)], redis_notes.find_redis_notes(request))

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_get_redis_connection(self, load_config):
        """Verifies that Redis is loaded correctly"""
        config = MagicMock()
        config.get.side_effect = [
            'myredis.server',
            4000,
            0,
            'supersecurepassword',
        ]
        load_config.return_value = config

        redis_connection = redis_notes.get_redis_connection()

        connection_kwargs = redis_connection.connection_pool.connection_kwargs
        self.assertEqual('myredis.server', connection_kwargs['host'])
        self.assertEqual(4000, connection_kwargs['port'])
        self.assertEqual(0, connection_kwargs['db'])
        self.assertEqual('supersecurepassword', connection_kwargs['password'])

        self.assertListEqual(
            config.get.mock_calls,
            [
                call('redis_notes', 'endpoint'),
                call('redis_notes', 'port'),
                call('redis_notes', 'db'),
                call('redis_notes', 'password'),
            ]
        )
