import logging
import time
import unittest
from datetime import timedelta
from time import sleep
from unittest.mock import patch

from redis import ConnectionError as RedisConnectionError, DataError, \
    AuthenticationError

from alerter.src.utils.redis_api import RedisApi
from alerter.test import TestInternalConf, TestUserConf

REDIS_RECENTLY_DOWN_FUNCTION = \
    'alerter.src.utils.redis_api.RedisApi._do_not_use_if_recently_went_down'


class TestRedisApiWithRedisOnline(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password=password)

        # Ping Redis
        try:
            redis.ping_unsafe()
        except RedisConnectionError:
            raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.namespace = 'testnamespace'
        self.password = TestUserConf.redis_password
        self.redis = RedisApi(self.logger, self.db, self.host, self.port,
                              password=self.password, namespace=self.namespace)

        # Ping Redis
        try:
            self.redis.ping_unsafe()
        except RedisConnectionError:
            self.fail('Redis is not online.')

        # Clear test database
        self.redis.delete_all_unsafe()

        self.key1 = 'key1'
        self.key2 = 'key2'
        self.key3 = 'key3'
        self.key4 = 'key4'

        self.val1 = 'val1'
        self.val1_bytes = bytes('val1', encoding='utf8')
        self.val2 = 'val2'
        self.val2_bytes = bytes('val2', encoding='utf8')
        self.val3_int = 123
        self.val4 = str(True)
        self.val4_bool = True

        self.time = timedelta(seconds=3)
        self.time_with_error_margin = timedelta(seconds=4)

        self.default_str = 'DEFAULT'
        self.default_int = 789
        self.default_bool = False

    def tearDown(self) -> None:
        self.redis.delete_all_unsafe()

    def test_set_unsafe_throws_exception_if_incorrect_password(self):
        redis_bad_pass = RedisApi(self.logger, self.db, self.host, self.port,
                                  password='incorrect password',
                                  namespace=self.namespace)

        self.redis.set_unsafe(self.key1, self.val1)  # works
        try:
            redis_bad_pass.set_unsafe(self.key1, self.val1)
            self.fail('Expected AuthenticationError to be thrown')
        except AuthenticationError:
            pass

    def test_set_unsafe_sets_the_specified_key_to_the_specified_value(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertEqual(self.redis.get_unsafe(self.key1), self.val1_bytes)

    def test_set_unsafe_throws_exception_if_invalid_type(self):
        try:
            self.redis.set_unsafe(self.key1, True)
            self.fail('Expected DataError exception to be thrown.')
        except DataError:
            pass

    def test_set_multiple_unsafe_sets_multiple_key_value_pairs(self):
        self.redis.set_multiple_unsafe({
            self.key1: self.val1,
            self.key2: self.val2
        })
        self.assertEqual(self.redis.get_unsafe(self.key1), self.val1_bytes)
        self.assertEqual(self.redis.get_unsafe(self.key2), self.val2_bytes)

    def test_set_for_unsafe_temporarily_sets_specified_key_value_pair(self):
        self.redis.set_for_unsafe(self.key1, self.val1, self.time)
        self.assertEqual(self.redis.get_unsafe(self.key1), self.val1_bytes)

        sleep(self.time_with_error_margin.seconds)
        self.assertNotEqual(self.redis.get_unsafe(self.key1), self.val1_bytes)

    def test_time_to_live_unsafe_returns_None_if_key_does_not_exist(self):
        self.redis.set(self.key1, self.val1)

        self.assertIsNone(self.redis.time_to_live_unsafe(self.key1))

    def test_time_to_live_unsafe_returns_None_if_key_does_not_have_timeout(
            self):
        self.assertIsNone(self.redis.time_to_live_unsafe(self.key1))

    def test_time_to_live_unsafe_returns_correct_timeout_if_set(self):
        self.redis.set_for_unsafe(self.key1, self.val1, self.time)

        self.assertEqual(self.time.seconds,
                         self.redis.time_to_live_unsafe(self.key1))

    def test_get_unsafe_returns_default_for_unset_key(self):
        self.assertEqual(
            self.redis.get_unsafe(self.key1, default=self.default_str),
            self.default_str)

    def test_get_unsafe_returns_set_value(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertEqual(
            self.redis.get_unsafe(self.key1, default=self.default_str),
            self.val1_bytes)

    def test_get_unsafe_returns_none_for_none_string(self):
        self.redis.set_unsafe(self.key1, 'None')
        self.assertIsNone(
            self.redis.get_unsafe(self.key1, default=self.default_str))

    def test_get_int_unsafe_returns_set_integer(self):
        self.redis.set_unsafe(self.key3, self.val3_int)
        self.assertEqual(
            self.redis.get_int_unsafe(self.key3, default=self.default_int),
            self.val3_int)

    def test_get_int_unsafe_returns_default_for_unset_key(self):
        self.assertEqual(
            self.redis.get_int_unsafe(self.key3, default=self.default_int),
            self.default_int)

    def test_get_int_unsafe_returns_default_for_non_integer_value(self):
        self.redis.set_unsafe(self.key2, self.val2)
        self.assertEqual(
            self.redis.get_int_unsafe(self.key2, default=self.default_int),
            self.default_int)

    def test_get_bool_unsafe_returns_set_boolean(self):
        self.redis.set_unsafe(self.key4, self.val4)
        self.assertEqual(
            self.redis.get_bool_unsafe(self.key4, default=self.default_bool),
            self.val4_bool)

    def test_get_bool_unsafe_returns_default_for_unset_key(self):
        self.assertEqual(
            self.redis.get_bool_unsafe(self.key4, default=self.default_bool),
            self.default_bool)

    def test_get_bool_unsafe_returns_false_for_non_boolean_value(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertFalse(
            self.redis.get_bool_unsafe(self.key1, default=self.default_bool))

    def test_exists_unsafe_returns_true_if_exists(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertTrue(self.redis.exists_unsafe(self.key1))

    def test_exists_unsafe_returns_false_if_not_exists(self):
        self.assertFalse(self.redis.exists_unsafe(self.key1))

    def test_get_keys_unsafe_returns_empty_list_if_no_keys(self):
        keys_list = self.redis.get_keys_unsafe()
        self.assertListEqual(keys_list, [])

    def test_get_keys_unsafe_returns_list_with_all_keys(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.redis.set_unsafe(self.key3, self.val3_int)

        keys_list = self.redis.get_keys_unsafe()
        self.assertSetEqual(set(keys_list), {self.key1, self.key2, self.key3})
        # Set is used just in case the keys list is unordered

    def test_get_keys_unsafe_gets_key_that_matches_specific_pattern(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.redis.set_unsafe(self.key3, self.val3_int)

        keys_list = self.redis.get_keys_unsafe(self.key1)
        self.assertListEqual(keys_list, [self.key1])

        keys_list = self.redis.get_keys_unsafe(self.key2)
        self.assertListEqual(keys_list, [self.key2])

        keys_list = self.redis.get_keys_unsafe(self.key3)
        self.assertListEqual(keys_list, [self.key3])

    def test_get_keys_unsafe_gets_only_keys_that_match_prefix_pattern(self):
        prefixed_key1 = 'aaa' + self.key1
        prefixed_key2 = 'bbb' + self.key2
        prefixed_key3 = 'aa' + self.key3
        self.redis.set_unsafe(prefixed_key1, self.val1)
        self.redis.set_unsafe(prefixed_key2, self.val2)
        self.redis.set_unsafe(prefixed_key3, self.val3_int)

        keys_list = self.redis.get_keys_unsafe('aa*')
        self.assertSetEqual(set(keys_list), {prefixed_key1, prefixed_key3})

    def test_remove_unsafe_does_nothing_if_key_does_not_exists(self):
        self.redis.remove_unsafe(self.key1)

    def test_remove_unsafe_removes_key_if_key_exists(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertTrue(self.redis.exists_unsafe(self.key1))

        self.redis.remove_unsafe(self.key1)
        self.assertFalse(self.redis.exists_unsafe(self.key1))

    def test_delete_all_unsafe_does_nothing_if_no_keys_exist(self):
        self.redis.delete_all_unsafe()

    def test_delete_all_unsafe_removes_keys_if_they_exist(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.assertTrue(self.redis.exists_unsafe(self.key1))
        self.assertTrue(self.redis.exists_unsafe(self.key2))

        self.redis.delete_all_unsafe()
        self.assertFalse(self.redis.exists_unsafe(self.key1))
        self.assertFalse(self.redis.exists_unsafe(self.key2))

    def test_set_sets_the_specified_key_to_the_specified_value(self):
        self.redis.set(self.key1, self.val1)
        self.assertEqual(self.redis.get(self.key1), self.val1_bytes)

    def test_set_returns_none_if_invalid_type(self):
        self.assertIsNone(self.redis.set(self.key1, True))

    def test_set_multiple_sets_multiple_key_value_pairs(self):
        self.redis.set_multiple({
            self.key1: self.val1,
            self.key2: self.val2
        })
        self.assertEqual(self.redis.get(self.key1), self.val1_bytes)
        self.assertEqual(self.redis.get(self.key2), self.val2_bytes)

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_set_multiple_returns_none_and_nothing_set_if_redis_down(self, _):
        self.assertIsNone(self.redis.set_multiple({
            self.key1: self.val1,
            self.key2: self.val2
        }))
        self.assertFalse(self.redis.exists_unsafe(self.key1))
        self.assertFalse(self.redis.exists_unsafe(self.key2))

    def test_set_for_temporarily_sets_specified_key_value_pair(self):
        self.redis.set_for(self.key1, self.val1, self.time)
        self.assertEqual(self.redis.get(self.key1), self.val1_bytes)

        sleep(self.time_with_error_margin.seconds)
        self.assertNotEqual(self.redis.get(self.key1), self.val1_bytes)

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_set_for_returns_none_and_nothing_set_if_redis_down(self, _):
        self.assertIsNone(self.redis.set_for(self.key1, self.val1, self.time))
        self.assertFalse(self.redis.exists_unsafe(self.key1))

    def test_time_to_live_returns_correct_timeout_when_set(self):
        self.redis.set_for(self.key1, self.val1, self.time)

        self.assertEqual(self.redis.time_to_live(self.key1), self.time.seconds)

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_time_to_live_returns_none_if_redis_down(self, _):
        self.assertIsNone(self.redis.time_to_live(self.key1))

    def test_get_returns_default_for_unset_key(self):
        self.assertEqual(self.redis.get(self.key1, default=self.default_str),
                         self.default_str)

    def test_get_returns_set_value(self):
        self.redis.set(self.key1, self.val1)
        self.assertEqual(self.redis.get(self.key1, default=self.default_str),
                         self.val1_bytes)

    def test_get_returns_none_for_none_string(self):
        self.redis.set(self.key1, 'None')
        self.assertIsNone(self.redis.get(self.key1, default=self.default_str))

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_get_returns_default_if_redis_down(self, _):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertEqual(self.redis.get(self.key1, default=self.default_str),
                         self.default_str)

    def test_get_int_returns_set_integer(self):
        self.redis.set(self.key3, self.val3_int)
        self.assertEqual(
            self.redis.get_int(self.key3, default=self.default_int),
            self.val3_int)

    def test_get_int_returns_default_for_unset_key(self):
        self.assertEqual(
            self.redis.get_int(self.key3, default=self.default_int),
            self.default_int)

    def test_get_int_returns_default_for_non_integer_value(self):
        self.redis.set(self.key2, self.val2)
        self.assertEqual(
            self.redis.get_int(self.key2, default=self.default_int),
            self.default_int)

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_get_int_returns_default_if_redis_down(self, _):
        self.redis.set_unsafe(self.key3, self.val3_int)
        self.assertEqual(
            self.redis.get_int(self.key3, default=self.default_int),
            self.default_int)

    def test_get_bool_returns_set_boolean(self):
        self.redis.set(self.key4, self.val4)
        self.assertEqual(
            self.redis.get_bool(self.key4, default=self.default_bool),
            self.val4_bool)

    def test_get_bool_returns_default_for_unset_key(self):
        self.assertEqual(
            self.redis.get_bool(self.key4, default=self.default_bool),
            self.default_bool)

    def test_get_bool_returns_false_for_non_boolean_value(self):
        self.redis.set(self.key1, self.val1)
        self.assertFalse(
            self.redis.get_bool(self.key1, default=self.default_bool))

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_get_bool_returns_default_if_redis_down(self, _):
        self.redis.set_unsafe(self.key4, self.val4)
        self.assertEqual(
            self.redis.get_bool(self.key4, default=self.default_bool),
            self.default_bool)

    def test_exists_returns_true_if_exists(self):
        self.redis.set(self.key1, self.val1)
        self.assertTrue(self.redis.exists(self.key1))

    def test_exists_returns_false_if_not_exists(self):
        self.assertFalse(self.redis.exists(self.key1))

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_exists_returns_false_if_redis_down(self, _):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertFalse(self.redis.exists(self.key1))

    def test_get_keys_returns_empty_list_if_no_keys(self):
        keys_list = self.redis.get_keys()
        self.assertListEqual(keys_list, [])

    def test_get_keys_returns_list_with_all_keys(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.redis.set_unsafe(self.key3, self.val3_int)

        keys_list = self.redis.get_keys()
        self.assertSetEqual(set(keys_list), {self.key1, self.key2, self.key3})
        # Set is used just in case the keys list is unordered

    def test_get_keys_gets_key_that_matches_specific_pattern(self):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.redis.set_unsafe(self.key3, self.val3_int)

        keys_list = self.redis.get_keys(self.key1)
        self.assertListEqual(keys_list, [self.key1])

        keys_list = self.redis.get_keys(self.key2)
        self.assertListEqual(keys_list, [self.key2])

        keys_list = self.redis.get_keys(self.key3)
        self.assertListEqual(keys_list, [self.key3])

    def test_get_keys_gets_only_keys_that_match_prefix_pattern(self):
        prefixed_key1 = 'aaa' + self.key1
        prefixed_key2 = 'bbb' + self.key2
        prefixed_key3 = 'aa' + self.key3
        self.redis.set_unsafe(prefixed_key1, self.val1)
        self.redis.set_unsafe(prefixed_key2, self.val2)
        self.redis.set_unsafe(prefixed_key3, self.val3_int)

        keys_list = self.redis.get_keys('aa*')
        self.assertSetEqual(set(keys_list), {prefixed_key1, prefixed_key3})

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_get_keys_returns_empty_set_if_redis_down(self, _):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.redis.set_unsafe(self.key3, self.val3_int)

        keys_list = self.redis.get_keys()
        self.assertSetEqual(set(keys_list), set())

    def test_remove_does_nothing_if_key_does_not_exists(self):
        self.redis.remove(self.key1)

    def test_remove_removes_key_if_key_exists(self):
        self.redis.set(self.key1, self.val1)
        self.assertTrue(self.redis.exists(self.key1))

        self.redis.remove(self.key1)
        self.assertFalse(self.redis.exists(self.key1))

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_remove_returns_none_if_redis_down(self, _):
        self.redis.set_unsafe(self.key1, self.val1)
        self.assertTrue(self.redis.exists_unsafe(self.key1))

        self.assertIsNone(self.redis.remove(self.key1))
        self.assertTrue(self.redis.exists_unsafe(self.key1))

    def test_delete_all_does_nothing_if_no_keys_exist(self):
        self.redis.delete_all()

    def test_delete_all_removes_keys_if_they_exist(self):
        self.redis.set(self.key1, self.val1)
        self.redis.set(self.key2, self.val2)
        self.assertTrue(self.redis.exists(self.key1))
        self.assertTrue(self.redis.exists(self.key2))

        self.redis.delete_all()
        self.assertFalse(self.redis.exists(self.key1))
        self.assertFalse(self.redis.exists(self.key2))

    @patch(REDIS_RECENTLY_DOWN_FUNCTION, return_value=True)
    def test_delete_all_returns_none_and_deletes_nothing_if_redis_down(self, _):
        self.redis.set_unsafe(self.key1, self.val1)
        self.redis.set_unsafe(self.key2, self.val2)
        self.assertTrue(self.redis.exists_unsafe(self.key1))
        self.assertTrue(self.redis.exists_unsafe(self.key2))

        self.assertIsNone(self.redis.delete_all())
        self.assertTrue(self.redis.exists_unsafe(self.key1))
        self.assertTrue(self.redis.exists_unsafe(self.key2))

    def test_ping_unsafe_returns_true(self):
        self.assertTrue(self.redis.ping_unsafe())


class TestRedisApiWithRedisOffline(unittest.TestCase):

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.db = TestInternalConf.redis_test_database
        self.host = 'dummyhost'
        self.port = TestUserConf.redis_port
        self.namespace = 'testnamespace'
        self.redis = RedisApi(self.logger, self.db, self.host,
                              self.port, namespace=self.namespace)

        self.key = 'key'
        self.val = 'val'
        self.time = timedelta.max

    def test_add_namespace_adds_namespace(self):
        key = 'some key'
        key_with_namespace = self.namespace + ':' + key

        self.assertEqual(key_with_namespace, self.redis._add_namespace(key))

    def test_remove_namespace_remove_namespace(self):
        key = 'some key'
        key_with_namespace = self.namespace + ':' + key

        self.assertEqual(key, self.redis._remove_namespace(key_with_namespace))

    def test_add_namespace_adds_nothing_if_already_added_namespace(self):
        key = 'some key'
        key_with_namespace = self.namespace + ':' + key

        self.assertEqual(key_with_namespace,
                         self.redis._add_namespace(key_with_namespace))

    def test_remove_namespace_removes_nothing_if_no_namespace(self):
        key = 'some key'

        self.assertEqual(key, self.redis._remove_namespace(key))

    def test_set_unsafe_throws_connection_exception(self):

        try:
            self.redis.set_unsafe(self.key, self.val)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_set_multiple_unsafe_throws_connection_exception(self):

        try:
            self.redis.set_multiple_unsafe({self.key: self.val})
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_set_for_unsafe_throws_connection_exception(self):

        try:
            self.redis.set_for_unsafe(self.key, self.val, self.time)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_time_to_live_unsafe_throws_connection_exception(self):

        try:
            self.redis.time_to_live_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_get_unsafe_throws_connection_exception(self):

        try:
            self.redis.get_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_get_int_unsafe_throws_connection_exception(self):

        try:
            self.redis.get_int_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_get_bool_unsafe_throws_connection_exception(self):

        try:
            self.redis.get_bool_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_exists_unsafe_throws_connection_exception(self):

        try:
            self.redis.exists_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_get_keys_unsafe_throws_connection_exception(self):

        try:
            self.redis.get_keys_unsafe()
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_remove_unsafe_throws_connection_exception(self):

        try:
            self.redis.remove_unsafe(self.key)
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_delete_all_unsafe_throws_connection_exception(self):

        try:
            self.redis.delete_all_unsafe()
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_set_returns_none(self):
        self.assertIsNone(self.redis.set(self.key, self.val))

    def test_set_multiple_returns_none(self):
        self.assertIsNone(self.redis.set_multiple({self.key: self.val}))

    def test_set_for_returns_none(self):
        self.assertIsNone(self.redis.set_for(self.key, self.val, self.time))

    def test_time_to_live_returns_none(self):
        self.assertIsNone(self.redis.time_to_live(self.key))

    def test_get_returns_none_if_no_default_specified(self):
        self.assertIsNone(self.redis.get(self.key))

    def test_get_returns_default_if_default_specified(self):
        default = 'default'
        self.assertEqual(self.redis.get(self.key, default=default), default)

    def test_get_int_returns_none_if_no_default_specified(self):
        self.assertIsNone(self.redis.get_int(self.key))

    def test_get_int_returns_default_if_default_specified(self):
        default = 123456
        self.assertEqual(self.redis.get_int(self.key, default=default), default)

    def test_get_bool_returns_none_if_no_default_specified(self):
        self.assertIsNone(self.redis.get_bool(self.key))

    def test_get_bool_returns_default_if_default_specified(self):
        default = True
        self.assertEqual(self.redis.get_bool(self.key, default=default),
                         default)

    def test_exists_returns_false(self):
        self.assertFalse(self.redis.exists(self.key))

    def test_exists_returns_empty_list(self):
        self.assertListEqual(self.redis.get_keys(), [])

    def test_remove_returns_none(self):
        self.assertIsNone(self.redis.remove(self.key))

    def test_delete_all_returns_none(self):
        self.assertIsNone(self.redis.delete_all())

    def test_ping_unsafe_throws_connection_exception(self):

        try:
            self.redis.ping_unsafe()
            self.fail('Expected RedisConnectionError exception to be thrown.')
        except RedisConnectionError:
            pass

    def test_second_safe_command_faster_to_throw_than_first_when_offline(self):

        start_1 = time.perf_counter()
        self.redis.set(self.key, self.val)
        elapsed_1 = time.perf_counter() - start_1

        start_2 = time.perf_counter()
        self.redis.set(self.key, self.val)
        elapsed_2 = time.perf_counter() - start_2

        # first executon is more than 10 times slower than second execution
        self.assertGreater(elapsed_1, elapsed_2 * 10)


class TestRedisNamespaceWithRedisOnline(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password)

        # Ping Redis
        try:
            redis.ping_unsafe()
        except RedisConnectionError:
            raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.password = TestUserConf.redis_password

        self.namespace1 = 'testnamespace1'
        self.namespace2 = 'testnamespace2'

        self.redis = RedisApi(
            self.logger, self.db, self.host, self.port,
            self.password, namespace=self.namespace1)
        self.same_namespace = RedisApi(
            self.logger, self.db, self.host, self.port,
            self.password, namespace=self.namespace1)
        self.different_namespace = RedisApi(
            self.logger, self.db, self.host, self.port,
            self.password, namespace=self.namespace2)

        # Ping Redis (all of above instances use same host, port, pass)
        try:
            self.redis.ping_unsafe()
        except RedisConnectionError:
            self.fail('Redis is not online.')

        # Clear test database (all of above instances use same database)
        self.redis.delete_all_unsafe()

        self.key1 = 'key1'
        self.key2 = 'key2'

        self.val1 = 'val1'
        self.val1_bytes = bytes('val1', encoding='utf8')
        self.val2 = 'val2'
        self.val2_bytes = bytes('val2', encoding='utf8')

    def tearDown(self) -> None:
        self.redis.delete_all_unsafe()
        self.different_namespace.delete_all_unsafe()

    def test_set_uses_namespace_internally(self):
        self.redis.set_unsafe(self.key1, self.val1)

        # Use raw Redis command to get, to bypass automatically-added namespace
        get_value = self.redis._redis.get(self.namespace1 + ':' + self.key1)

        self.assertEqual(get_value, self.val1_bytes)

    def test_get_uses_namespace_internally(self):
        # Use raw Redis command to set, to bypass automatically-added namespace
        self.redis._redis.set(self.namespace1 + ':' + self.key1, self.val1)

        get_value = self.redis.get_unsafe(self.key1)
        self.assertEqual(get_value, self.val1_bytes)

    def test_redis_api_with_same_namespace_has_access_to_same_store(self):
        self.redis.set_unsafe(self.key1, self.val1)

        self.assertEqual(
            self.same_namespace.get_unsafe(self.key1), self.val1_bytes)

    def test_redis_api_with_different_namespace_has_separate_store(self):
        self.redis.set_unsafe(self.key1, self.val1)

        self.assertNotEqual(
            self.different_namespace.get_unsafe(self.key1), self.val1_bytes)


class TestRedisApiLiveAndDownFeaturesWithRedisOffline(unittest.TestCase):

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.db = TestInternalConf.redis_test_database
        self.host = 'dummyhost'
        self.port = 6379
        self.live_check_time_interval = timedelta(seconds=3)
        self.live_check_time_interval_with_error_margin = timedelta(seconds=3.5)
        self.redis = RedisApi(self.logger, self.db, self.host, self.port,
                              live_check_time_interval=
                              self.live_check_time_interval)

        self.key = 'key'
        self.val = 'val'
        self.time = timedelta.max

    def test_is_live_by_default(self):
        self.assertTrue(self.redis.is_live)

    def test_set_as_live_changes_is_live_to_true(self):
        self.redis._is_live = False
        self.assertFalse(self.redis.is_live)

        self.redis._set_as_live()
        self.assertTrue(self.redis._is_live)

    def test_et_as_down_changes_is_live_to_false(self):
        self.redis._set_as_down()
        self.assertFalse(self.redis.is_live)

    def test_allowed_to_use_by_default(self):
        # noinspection PyBroadException
        try:
            self.redis._do_not_use_if_recently_went_down()
        except Exception:
            self.fail('Expected to be allowed to use Redis.')

    def test_not_allowed_to_use_if_set_as_down_and_within_time_interval(self):
        self.redis._set_as_down()
        # noinspection PyBroadException
        try:
            self.redis._do_not_use_if_recently_went_down()
            self.fail('Expected to not be allowed to use Redis.')
        except Exception:
            pass

    def test_allowed_to_use_if_set_as_down_and_within_time_interval(self):
        self.redis._set_as_down()
        sleep(self.live_check_time_interval_with_error_margin.seconds)
        # noinspection PyBroadException
        try:
            self.redis._do_not_use_if_recently_went_down()
        except Exception:
            self.fail('Expected to be allowed to use Redis.')
