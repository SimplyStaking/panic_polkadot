import logging

from src.alerts.alerts import Alert
from src.channels.channel import Channel


class DummyException(Exception):
    pass


class CounterChannel(Channel):

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__('counter_channel', logger, redis=None)
        self.info_count = 0
        self.warning_count = 0
        self.critical_count = 0
        self.error_count = 0
        self.latest_alert = None

    def reset(self) -> None:
        self.info_count = 0
        self.warning_count = 0
        self.critical_count = 0
        self.error_count = 0
        self.latest_alert = None

    def alert_info(self, alert: Alert) -> None:
        self.info_count += 1
        self.latest_alert = alert

    def alert_warning(self, alert: Alert) -> None:
        self.warning_count += 1
        self.latest_alert = alert

    def alert_critical(self, alert: Alert) -> None:
        self.critical_count += 1
        self.latest_alert = alert

    def alert_error(self, alert: Alert) -> None:
        self.error_count += 1
        self.latest_alert = alert

    def no_alerts(self):
        return self.info_count == 0 and self.warning_count == 0 and \
               self.critical_count == 0 and self.error_count == 0
