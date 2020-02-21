import logging
import sys

from src.alerts.alerts import Alert
from src.channels.channel import Channel


class ConsoleChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger) -> None:
        super().__init__(channel_name, logger, None)
        self._space = ' ' if self._channel_name != '' else ''

    def alert_info(self, alert: Alert) -> None:
        print('{}{}INFO - {}'.format(self._channel_name, self._space, alert))
        sys.stdout.flush()

    def alert_warning(self, alert: Alert) -> None:
        print('{}{}WARNING - {}'.format(self._channel_name, self._space, alert))
        sys.stdout.flush()

    def alert_critical(self, alert: Alert) -> None:
        print(
            '{}{}CRITICAL - {}'.format(self._channel_name, self._space, alert))
        sys.stdout.flush()

    def alert_error(self, alert: Alert) -> None:
        print('{}{}ERROR - {}'.format(self._channel_name, self._space, alert))
        sys.stdout.flush()
