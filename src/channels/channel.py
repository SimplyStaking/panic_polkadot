import logging
from typing import Optional, List

from src.alerts.alerts import Alert, SeverityCode
from src.store.redis.redis_api import RedisApi
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf


class Channel:

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi]) -> None:
        self._channel_name = channel_name
        self._logger = logger
        self._redis = redis

    def alert_info(self, alert: Alert) -> None:
        pass

    def alert_warning(self, alert: Alert) -> None:
        pass

    def alert_critical(self, alert: Alert) -> None:
        pass

    def alert_error(self, alert: Alert) -> None:
        pass

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def redis(self) -> RedisApi:
        return self._redis

    @property
    def redis_enabled(self) -> bool:
        return self._redis is not None


class ChannelSet:

    def __init__(self, channels: List[Channel],
                 internal_conf: InternalConfig = InternalConf) -> None:
        # self._channels is not set to channels to disallow adding more
        # channels to the set by appending to the channels list directly
        self._channels = []
        for c in channels:
            self.add_channel(c)

        self.internal_conf = internal_conf

    def enabled_channels_list(self) -> str:
        return ', '.join([type(c).__name__ for c in self._channels]) \
            if len(self._channels) > 0 else 'None'

    def add_channel(self, channel: Channel) -> None:
        self._channels.append(channel)

    def should_alert(self, alert: Alert, severity: SeverityCode):
        try:
            # Returns true if alert is enabled
            alert = alert.alert_code.name
            severity = severity.name
            alerts_map = self.internal_conf.alerts_enabled_map
            severities_map = self.internal_conf.severities_enabled_map
            if alert in alerts_map and not alerts_map[alert]:
                return False  # Alert is disabled
            elif severity in severities_map and not severities_map[severity]:
                return False  # Severity is disabled
            else:
                return True  # If not in map, default to "should alert"
        except Exception:
            return True  # If any exception, default to "should alert"

    def unsafe_alert_info(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_info(alert)

    def unsafe_alert_warning(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_warning(alert)

    def unsafe_alert_critical(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_critical(alert)

    def unsafe_alert_error(self, alert: Alert) -> None:
        for a in self._channels:
            a.alert_error(alert)

    def alert_info(self, alert: Alert) -> None:
        if self.should_alert(alert, SeverityCode.INFO):
            for c in self._channels:
                try:
                    c.alert_info(alert)
                except Exception as e:
                    c.logger.error('Error in alert_info of %s (%s): %s',
                                   type(c).__name__, c.channel_name, e)

    def alert_warning(self, alert: Alert) -> None:
        if self.should_alert(alert, SeverityCode.WARNING):
            for c in self._channels:
                try:
                    c.alert_warning(alert)
                except Exception as e:
                    c.logger.error('Error in alert_warning of %s (%s): %s',
                                   type(c).__name__, c.channel_name, e)

    def alert_critical(self, alert: Alert) -> None:
        if self.should_alert(alert, SeverityCode.CRITICAL):
            for c in self._channels:
                try:
                    c.alert_critical(alert)
                except Exception as e:
                    c.logger.error('Error in alert_critical of %s (%s): %s',
                                   type(c).__name__, c.channel_name, e)

    def alert_error(self, alert: Alert) -> None:
        if self.should_alert(alert, SeverityCode.ERROR):
            for c in self._channels:
                try:
                    c.alert_error(alert)
                except Exception as e:
                    c.logger.error('Error in alert_error of %s (%s): %s',
                                   type(c).__name__, c.channel_name, e)
