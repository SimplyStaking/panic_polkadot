import logging
import unittest
from datetime import datetime, timedelta

from redis import ConnectionError as RedisConnectionError

from src.alerters.proactive.periodic import PeriodicAliveReminder
from src.channels.channel import ChannelSet
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel


class TestPeriodicWithoutRedis(unittest.TestCase):
    def setUp(self) -> None:
        self.alerter_name = 'testalerter'
        self.logger = logging.getLogger('dummy')
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)

        self.par = PeriodicAliveReminder(
            timedelta(), self.channel_set, None)

    def test_periodic_alive_reminder_sends_info_alert_if_redis_disabled(self):
        self.counter_channel.reset()  # ignore previous alerts
        self.par.send_alive_alert()
        self.assertEqual(self.counter_channel.warning_count, 0)
        self.assertEqual(self.counter_channel.critical_count, 0)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertEqual(self.counter_channel.error_count, 0)


class TestPeriodicWithRedis(unittest.TestCase):
    def setUp(self) -> None:
        self.alerter_name = 'testalerter'
        self.logger = logging.getLogger('dummy')
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)

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

        self.par = PeriodicAliveReminder(
            timedelta(), self.channel_set, self.redis)

    def test_periodic_alive_reminder_sends_info_alert_if_no_mute_key(self):
        self.counter_channel.reset()  # ignore previous alerts
        self.par.send_alive_alert()
        self.assertEqual(self.counter_channel.warning_count, 0)
        self.assertEqual(self.counter_channel.critical_count, 0)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_periodic_alive_reminder_sends_no_alert_if_mute_key_present(self):
        hours = timedelta(hours=float(1))
        until = str(datetime.now() + hours)
        key = Keys.get_alive_reminder_mute()
        self.redis.set_for(key, until, hours)
        self.counter_channel.reset()  # ignore previous alerts
        self.par.send_alive_alert()
        self.redis.remove(key)
        self.assertEqual(self.counter_channel.warning_count, 0)
        self.assertEqual(self.counter_channel.critical_count, 0)
        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.error_count, 0)
