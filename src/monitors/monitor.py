import logging
from typing import Optional

from src.channels.channel import ChannelSet
from src.store.redis.redis_api import RedisApi
from src.utils.config_parsers.internal import InternalConfig


class Monitor:

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 internal_conf: InternalConfig) -> None:
        super().__init__()

        self._monitor_name = monitor_name
        self._channels = channels
        self._logger = logger
        self._redis = redis
        self._internal_conf = internal_conf

    @property
    def channels(self) -> ChannelSet:
        return self._channels

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def redis(self) -> RedisApi:
        return self._redis

    @property
    def redis_enabled(self) -> bool:
        return self._redis is not None

    @property
    def monitor_name(self) -> str:
        return self._monitor_name

    def status(self) -> str:
        pass

    def load_state(self) -> None:
        pass

    def save_state(self) -> None:
        pass

    def monitor(self) -> None:
        pass
