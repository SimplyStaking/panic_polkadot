import logging
import unittest

from redis import ConnectionError as RedisConnectionError

from alerter.src.alerting.alerts.alerts import *
from alerter.src.alerting.channels.channel import ChannelSet
from alerter.src.blockchain.blockchain import Blockchain
from alerter.src.utils.redis_api import RedisApi
from alerter.test import TestInternalConf, TestUserConf
from alerter.test.test_helpers import CounterChannel


class TestBlockchainWithoutRedis(unittest.TestCase):

    def setUp(self) -> None:
        self.blockchain_name = 'testblockchain'
        self.logger = logging.getLogger('dummy')

        self.blockchain = Blockchain(name=self.blockchain_name, redis=None)

        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])

        self.dummy_referendum_count, self.dummy_public_prop_count, \
        self.dummy_council_prop_count = 10, 10, 10
        self.dummy_validator_set_size = 120
        self.dummy_referendum_info = {'end': '8568'}

    def test_str_returns_blockchain_name(self) -> None:
        self.assertEqual(self.blockchain_name, str(self.blockchain))

    def test_referendum_count_None_by_default(self) -> None:
        self.assertIsNone(self.blockchain.referendum_count)

    def test_public_prop_count_None_by_default(self) -> None:
        self.assertIsNone(self.blockchain.public_prop_count)

    def test_council_prop_count_None_by_default(self) -> None:
        self.assertIsNone(self.blockchain.council_prop_count)

    def test_validator_set_size_None_by_default(self) -> None:
        self.assertIsNone(self.blockchain.validator_set_size)

    def test_status_returns_as_expected(self) -> None:
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)
        self.blockchain.set_public_prop_count(self.dummy_public_prop_count,
                                              self.channel_set, self.logger)
        self.blockchain.set_council_prop_count(self.dummy_council_prop_count,
                                               self.channel_set, self.logger)
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)

        self.assertEqual(self.blockchain.status(),
                         "referendum_count={}, public_prop_count={}, "
                         "council_prop_count={}, validator_set_size ={}"
                         .format(self.dummy_referendum_count,
                                 self.dummy_public_prop_count,
                                 self.dummy_council_prop_count,
                                 self.dummy_validator_set_size))

    def test_set_referendum_count_raises_no_alerts_first_time_round(
            self) -> None:
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.referendum_count,
                         self.dummy_referendum_count)

    def test_set_referendum_count_raises_no_alerts_if_same_referendum_count(
            self) -> None:
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.referendum_count,
                         self.dummy_referendum_count)

    def test_set_referendum_count_raises_no_alerts_if_new_referendum_expired(
            self) -> None:
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)
        new_referendum_count = self.dummy_referendum_count + 1
        self.blockchain.set_referendum_count(
            new_referendum_count, self.channel_set, self.logger, None)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.referendum_count, new_referendum_count)

    def test_set_referendum_count_info_alert_if_new_referendum_not_expired(
            self) -> None:
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)
        new_referendum_count = self.dummy_referendum_count + 1
        self.blockchain.set_referendum_count(
            new_referendum_count, self.channel_set, self.logger,
            self.dummy_referendum_info)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NewReferendumAlert)
        self.assertEqual(self.blockchain.referendum_count, new_referendum_count)

    def test_set_public_prop_count_raises_no_alerts_first_time_round(
            self) -> None:
        self.blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.public_prop_count,
                         self.dummy_public_prop_count)

    def test_set_public_prop_count_raises_no_alerts_if_same_count(self) -> None:
        self.blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)
        self.blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.public_prop_count,
                         self.dummy_public_prop_count)

    def test_set_public_prop_count_1_info_alert_if_increase_by_1(self) -> None:
        self.blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)
        new_public_prop_count = self.dummy_public_prop_count + 1
        self.blockchain.set_public_prop_count(
            new_public_prop_count, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NewPublicProposalAlert)
        self.assertEqual(self.blockchain.public_prop_count,
                         new_public_prop_count)

    def test_set_public_prop_count_2_info_alerts_if_increase_by_2(self) -> None:
        self.blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)
        new_public_prop_count = self.dummy_public_prop_count + 2
        self.blockchain.set_public_prop_count(
            new_public_prop_count, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 2)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NewPublicProposalAlert)
        self.assertEqual(self.blockchain.public_prop_count,
                         new_public_prop_count)

    def test_set_council_prop_count_raises_no_alerts_first_time_round(
            self) -> None:
        self.blockchain.set_council_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.council_prop_count,
                         self.dummy_council_prop_count)

    def test_set_council_prop_count_raises_no_alerts_if_same_count(
            self) -> None:
        self.blockchain.set_council_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)
        self.blockchain.set_public_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.council_prop_count,
                         self.dummy_council_prop_count)

    def test_set_council_prop_count_info_alert_if_increase_by_1(self) -> None:
        self.blockchain.set_council_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)
        new_council_prop_count = self.dummy_council_prop_count + 1
        self.blockchain.set_council_prop_count(
            new_council_prop_count, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NewCouncilProposalAlert)
        self.assertEqual(self.blockchain.council_prop_count,
                         new_council_prop_count)

    def test_set_council_prop_count_info_alert_if_increase_by_2(self) -> None:
        self.blockchain.set_council_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)
        new_council_prop_count = self.dummy_council_prop_count + 2
        self.blockchain.set_council_prop_count(
            new_council_prop_count, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 2)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NewCouncilProposalAlert)
        self.assertEqual(self.blockchain.council_prop_count,
                         new_council_prop_count)

    def test_set_validator_set_size_no_alerts_first_time_round(self) -> None:
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.validator_set_size,
                         self.dummy_validator_set_size)

    def test_set_validator_set_size_no_alerts_if_same_size(self) -> None:
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.blockchain.validator_set_size,
                         self.dummy_validator_set_size)

    def test_set_validator_set_size_info_alert_if_size_decreased(self) -> None:
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)
        new_validator_set_size = self.dummy_validator_set_size - 2
        self.blockchain.set_validator_set_size(new_validator_set_size,
                                               self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorSetSizeDecreasedAlert)
        self.assertEqual(self.blockchain.validator_set_size,
                         new_validator_set_size)

    def test_set_validator_set_size_info_alert_if_size_increased(self) -> None:
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)
        new_validator_set_size = self.dummy_validator_set_size + 2
        self.blockchain.set_validator_set_size(new_validator_set_size,
                                               self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorSetSizeIncreasedAlert)
        self.assertEqual(self.blockchain.validator_set_size,
                         new_validator_set_size)


class TestBlockchainWithRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password)

        try:
            redis.ping_unsafe()
        except RedisConnectionError:
            raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.blockchain_name = 'testblockchain'
        self.redis_prefix = self.blockchain_name
        self.logger = logging.getLogger('dummy')
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])

        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.password = TestUserConf.redis_password
        self.redis = RedisApi(self.logger, self.db, self.host,
                              self.port, self.password)
        self.redis.delete_all_unsafe()

        try:
            self.redis.ping_unsafe()
        except RedisConnectionError:
            self.fail('Redis is not online.')

        self.blockchain = Blockchain(self.blockchain_name, self.redis)
        self.dummy_referendum_count = 10
        self.dummy_council_prop_count = 10
        self.dummy_public_prop_count = 10
        self.dummy_validator_set_size = 120

    def test_load_state_changes_nothing_if_nothing_saved(self):
        self.blockchain.load_state(self.logger)

        self.assertIsNone(self.blockchain.validator_set_size)
        self.assertIsNone(self.blockchain.public_prop_count)
        self.assertIsNone(self.blockchain.council_prop_count)
        self.assertIsNone(self.blockchain.validator_set_size)

    def test_load_state_sets_values_to_saved_values(self):
        # Set Redis values manually
        self.redis.set_unsafe(self.redis_prefix + '_referendum_count',
                              self.dummy_referendum_count)
        self.redis.set_unsafe(self.redis_prefix + '_public_prop_count',
                              self.dummy_public_prop_count)
        self.redis.set_unsafe(self.redis_prefix + '_council_prop_count',
                              self.dummy_council_prop_count)
        self.redis.set_unsafe(self.redis_prefix + '_validator_set_size',
                              self.dummy_validator_set_size)

        # Load the Redis values
        self.blockchain.load_state(self.logger)

        # Assert
        self.assertEqual(self.blockchain.referendum_count,
                         self.dummy_referendum_count)
        self.assertEqual(self.blockchain.public_prop_count,
                         self.dummy_public_prop_count)
        self.assertEqual(self.blockchain.council_prop_count,
                         self.dummy_council_prop_count)
        self.assertEqual(self.blockchain.validator_set_size,
                         self.dummy_validator_set_size)

    def test_save_state_sets_values_to_current_values(self):
        # Set blockchain values manually
        self.blockchain.set_referendum_count(self.dummy_referendum_count,
                                             self.channel_set, self.logger)
        self.blockchain.set_council_prop_count(self.dummy_council_prop_count,
                                               self.channel_set, self.logger)
        self.blockchain.set_public_prop_count(self.dummy_public_prop_count,
                                              self.channel_set, self.logger)
        self.blockchain.set_validator_set_size(self.dummy_validator_set_size,
                                               self.channel_set, self.logger)

        # Save the values to Redis
        self.blockchain.save_state(self.logger)

        # Assert
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix + '_referendum_count'),
            self.dummy_referendum_count)
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix + '_public_prop_count'),
            self.dummy_public_prop_count)
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix +
                                      '_council_prop_count'),
            self.dummy_council_prop_count)
        self.assertEqual(
            self.redis.get_int_unsafe(self.redis_prefix +
                                      '_validator_set_size'),
            self.dummy_validator_set_size)
