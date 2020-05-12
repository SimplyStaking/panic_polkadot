import logging
from datetime import datetime
from typing import Optional

from src.alerts.alerts import Alert, ProblemWithMongo
from src.channels.channel import Channel, ChannelSet
from src.store.mongo.mongo_api import MongoApi
from src.store.redis.redis_api import RedisApi


class MongoChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 redis: Optional[RedisApi], mongo: MongoApi,
                 mongo_collection_name: str,
                 backup_channels: ChannelSet) -> None:
        super().__init__(channel_name, logger, redis)

        self._mongo = mongo
        self._mongo_coll = mongo_collection_name
        self._backup_channels = backup_channels

    def _alert(self, alert: Alert, severity: str) -> None:
        try:
            ret = self._mongo.insert_one(self._mongo_coll, {
                'origin': self.channel_name,
                'severity': severity,
                'message': alert.message,
                'timestamp': datetime.now().timestamp()
            })
            # TODO: add checks around 'ret', if necessary
        except Exception as e:
            self._backup_channels.alert_error(ProblemWithMongo(e))

    def alert_info(self, alert: Alert) -> None:
        self._alert(alert=alert, severity='INFO')

    def alert_warning(self, alert: Alert) -> None:
        self._alert(alert=alert, severity='WARNING')

    def alert_critical(self, alert: Alert) -> None:
        self._alert(alert=alert, severity='CRITICAL')

    def alert_error(self, alert: Alert) -> None:
        self._alert(alert=alert, severity='ERROR')
