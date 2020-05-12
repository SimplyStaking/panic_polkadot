from datetime import timedelta
from time import sleep
from typing import Optional

from src.alerts.alerts import AlerterAliveAlert
from src.channels.channel import ChannelSet
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys


class PeriodicAliveReminder:

    def __init__(self, interval: timedelta, channel_set: ChannelSet,
                 redis: Optional[RedisApi]):
        self._interval = interval
        self._channel_set = channel_set
        self._redis = redis
        self._redis_enabled = redis is not None

    def start(self):
        while True:
            sleep(self._interval.total_seconds())
            self.send_alive_alert()

    def send_alive_alert(self) -> None:
        # If it is not the case that Redis is enabled and the reminder is muted,
        # inform the node operator that the alerter is still running.
        if not (self._redis_enabled and
                self._redis.exists(Keys.get_alive_reminder_mute())):
            self._channel_set.alert_info(AlerterAliveAlert())
