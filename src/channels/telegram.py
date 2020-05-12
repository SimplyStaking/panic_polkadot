import logging
from typing import Optional

from src.alerts.alerts import Alert, ProblemWithTelegramBot
from src.channels.channel import Channel, ChannelSet
from src.store.redis.redis_api import RedisApi
from src.utils.alert_utils.telegram_bot_api import TelegramBotApi


class TelegramChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi], telegram_bot: TelegramBotApi,
                 backup_channels: ChannelSet) -> None:
        super().__init__(channel_name, logger, redis)

        self._telegram_bot = telegram_bot
        self._backup_channels = backup_channels
        self._space = ' ' if self.channel_name != '' else ''

    def _alert(self, alert: Alert, subject: str) -> None:
        if self._telegram_bot is not None:
            telegram_ret = self._telegram_bot.send_message(
                '*{}*: `{}`'.format(subject, alert))
            self._logger.debug("alert: telegram_ret: %s", telegram_ret)
            if telegram_ret['ok']:
                self._logger.info('Sent telegram alert.')
            else:
                self._backup_channels.alert_error(
                    ProblemWithTelegramBot(telegram_ret['description']))
        else:
            self._logger.warning('Telegram bot alerts are disabled.')

    def alert_info(self, alert: Alert) -> None:
        self._alert(alert=alert,
                    subject='{}{}INFO'.format(self.channel_name, self._space))

    def alert_warning(self, alert: Alert) -> None:
        self._alert(alert=alert,
                    subject='{}{}WARNING'.format(self.channel_name,
                                                 self._space))

    def alert_critical(self, alert: Alert) -> None:
        self._alert(alert=alert,
                    subject='{}{}CRITICAL'.format(self.channel_name,
                                                  self._space))

    def alert_error(self, alert: Alert) -> None:
        self._alert(alert=alert,
                    subject='{}{}ERROR'.format(self.channel_name, self._space))
