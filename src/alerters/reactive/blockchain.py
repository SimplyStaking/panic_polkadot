import logging
from typing import Optional

from src.alerts.alerts import NewReferendumAlert, \
    NewCouncilProposalAlert, NewPublicProposalAlert, \
    ValidatorSetSizeDecreasedAlert, ValidatorSetSizeIncreasedAlert
from src.channels.channel import ChannelSet
from src.utils.redis_api import RedisApi
from src.utils.types import PolkadotWrapperType


class Blockchain:
    def __init__(self, name: str, redis: Optional[RedisApi]) -> None:
        super().__init__()

        self.name = name
        self._redis = redis
        self._redis_enabled = redis is not None
        self._redis_prefix = self.name

        self._referendum_count = None
        self._public_prop_count = None
        self._council_prop_count = None
        self._validator_set_size = None

    def __str__(self) -> str:
        return self.name

    @property
    def referendum_count(self) -> int:
        return self._referendum_count

    @property
    def public_prop_count(self) -> int:
        return self._public_prop_count

    @property
    def council_prop_count(self) -> int:
        return self._council_prop_count

    @property
    def validator_set_size(self) -> int:
        return self._validator_set_size

    def status(self) -> str:
        return "referendum_count={}, public_prop_count={}, " \
               "council_prop_count={}, validator_set_size ={}" \
               "".format(self._referendum_count, self._public_prop_count,
                         self._council_prop_count, self._validator_set_size)

    def load_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, load any previously stored state
        if self._redis_enabled:
            self._referendum_count = self._redis.get_int(
                self._redis_prefix + '_referendum_count', None)
            self._public_prop_count = self._redis.get_int(
                self._redis_prefix + '_public_prop_count', None)
            self._council_prop_count = self._redis.get_int(
                self._redis_prefix + '_council_prop_count', None)
            self._validator_set_size = self._redis.get_int(
                self._redis_prefix + '_validator_set_size', None)

            logger.debug(
                'Restored %s state: _referendum_count=%s, '
                '_public_prop_count=%s, _council_prop_count=%s, '
                '_validator_set_size=%s',
                self.name, self._referendum_count, self._public_prop_count,
                self._council_prop_count, self._validator_set_size)

    def save_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, store the current state
        if self._redis_enabled:
            logger.debug(
                'Saving %s state: _referendum_count=%s, '
                '_public_prop_count=%s, _council_prop_count=%s, '
                '_validator_set_size=%s',
                self.name, self._referendum_count, self._public_prop_count,
                self._council_prop_count, self._validator_set_size)

            # Set values
            self._redis.set_multiple({
                self._redis_prefix +
                '_referendum_count': self._referendum_count,
                self._redis_prefix +
                '_public_prop_count': self._public_prop_count,
                self._redis_prefix +
                '_council_prop_count': self._council_prop_count,
                self._redis_prefix +
                '_validator_set_size': self._validator_set_size
            })

    def set_referendum_count(self, new_referendum_count: int,
                             channels: ChannelSet, logger: logging.Logger,
                             referendum_info: PolkadotWrapperType = None) \
            -> None:
        logger.debug('%s set_referendum_count: referendum_count(currently)=%s, '
                     'channels=%s', self, self.referendum_count, channels)

        if self._referendum_count not in [None, new_referendum_count] \
                and referendum_info is not None:
            end_block = int(referendum_info['end'])
            channels.alert_info(NewReferendumAlert(self.referendum_count,
                                                   end_block))
        self._referendum_count = new_referendum_count

    def set_council_prop_count(self, new_council_prop_count: int,
                               channels: ChannelSet,
                               logger: logging.Logger) -> None:
        logger.debug(
            '%s set_council_prop_count: council_prop_count(currently)=%s, '
            'channels=%s', self, self.council_prop_count, channels)

        if self._council_prop_count is None:
            self._council_prop_count = new_council_prop_count
            return

        while self._council_prop_count < new_council_prop_count:
            channels.alert_info(NewCouncilProposalAlert(
                self._council_prop_count))
            self._council_prop_count += 1

    def set_public_prop_count(self, new_public_prop_count: int,
                              channels: ChannelSet,
                              logger: logging.Logger) -> None:
        logger.debug(
            '%s set_public_prop_count: public_prop_count(currently)=%s, '
            'channels=%s', self, self.public_prop_count, channels)

        if self._public_prop_count is None:
            self._public_prop_count = new_public_prop_count
            return

        while self._public_prop_count < new_public_prop_count:
            channels.alert_info(NewPublicProposalAlert(self._public_prop_count))
            self._public_prop_count += 1

    def set_validator_set_size(self, new_validator_set_size: int,
                               channels: ChannelSet,
                               logger: logging.Logger) -> None:
        logger.debug(
            '%s set_validator_set_size: validator_set_size(currently)=%s, '
            'channels=%s', self, self.validator_set_size, channels)

        if self._validator_set_size not in [new_validator_set_size, None]:
            if self._validator_set_size < new_validator_set_size:
                channels.alert_info(ValidatorSetSizeIncreasedAlert(
                    new_validator_set_size))
            elif self._validator_set_size > new_validator_set_size:
                channels.alert_info(ValidatorSetSizeDecreasedAlert(
                    new_validator_set_size))
        self._validator_set_size = new_validator_set_size
