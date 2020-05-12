import logging
from typing import Optional, List

from src.alerts.alerts import Alert
from src.channels.channel import Channel
from src.store.redis.redis_api import RedisApi
from src.utils.alert_utils.email_sending import EmailSender


class EmailChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi], email: EmailSender,
                 email_to: List[str]) -> None:
        super().__init__(channel_name, logger, redis)

        self._email = email
        self._email_to = email_to
        self._space = ' ' if self.channel_name != '' else ''

    def alert_info(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}INFO Alert'.format(self.channel_name,
                                                    self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_warning(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}WARNING Alert'.format(self.channel_name,
                                                       self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_critical(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}CRITICAL Alert'.format(self.channel_name,
                                                        self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)

    def alert_error(self, alert: Alert) -> None:
        for email in self._email_to:
            try:
                self._email.send_email(
                    subject='{}{}ERROR Alert'.format(self.channel_name,
                                                     self._space),
                    message=alert.message, to=email)
            except Exception as e:
                self.logger.error('Error when sending to %s: %s', email, e)
