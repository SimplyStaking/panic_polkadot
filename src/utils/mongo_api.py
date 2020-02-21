import logging
from datetime import timedelta
from typing import Dict, List, Optional

from pymongo import MongoClient
from pymongo.results import InsertOneResult, InsertManyResult

from src.utils.timing import TimedTaskLimiter


class MongoApi:
    def __init__(self, logger: logging.Logger, db_name: str,
                 host: str = 'localhost', port: int = 27017,
                 username: str = '', password: str = '',
                 live_check_time_interval: timedelta = timedelta(seconds=60),
                 timeout_ms: int = 10000) \
            -> None:
        self._logger = logger
        self._db_name = db_name
        if password == '':
            self._client = MongoClient(
                host=host, port=port, connectTimeoutMS=timeout_ms,
                socketTimeoutMS=timeout_ms, serverSelectionTimeoutMS=timeout_ms)
        else:
            self._client = MongoClient(
                host=host, port=port, connectTimeoutMS=timeout_ms,
                socketTimeoutMS=timeout_ms, serverSelectionTimeoutMS=timeout_ms,
                username=username, password=password)

        # The live check limiter means that we don't wait for connection
        # errors to occur to be able to continue, thus speeding everything up
        self._live_check_limiter = TimedTaskLimiter(live_check_time_interval)
        self._is_live = True  # This is necessary to initialise the variable
        self._set_as_live()

        self._logger.info('Mongo initialised.')

    @property
    def _db(self):
        return self._client[self._db_name]

    @property
    def is_live(self) -> bool:
        return self._is_live

    def _set_as_live(self) -> None:
        if not self._is_live:
            self._logger.info('Mongo is now accessible again.')
        self._is_live = True

    def _set_as_down(self) -> None:
        # If Mongo is live or if we can check whether it is live (because the
        # live check time interval has passed), reset the live check limiter
        # so that usage of Mongo is skipped for as long as the time interval
        if self._is_live or self._live_check_limiter.can_do_task():
            self._live_check_limiter.did_task()
            self._logger.warning('Mongo is unusable for some reason. Stopping '
                                 'usage temporarily to improve performance.')
        self._is_live = False

    def _do_not_use_if_recently_went_down(self) -> bool:
        # If Mongo is not live and cannot check if it is live (by using it)
        # then stop the function called from happening by returning True
        return not self._is_live and not self._live_check_limiter.can_do_task()

    def insert_one(self, collection: str, document: Dict) \
            -> Optional[InsertOneResult]:
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self._db[collection].insert_one(document)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Mongo error in insert_one: %s', e)
            self._set_as_down()
            raise e

    def insert_many(self, collection: str, documents: List[Dict]) \
            -> Optional[InsertManyResult]:
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self._db[collection].insert_many(documents)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Mongo error in insert_many: %s', e)
            self._set_as_down()
            raise e

    def get_all(self, collection: str) -> Optional[List[Dict]]:
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = list(self._db[collection].find({}))
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Mongo error in drop_collection: %s', e)
            self._set_as_down()
            raise e

    def drop_collection(self, collection: str) -> Optional[Dict]:
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self._db.drop_collection(collection)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Mongo error in drop_collection: %s', e)
            self._set_as_down()
            raise e

    def drop_db(self) -> None:
        try:
            if self._do_not_use_if_recently_went_down():
                return None
            ret = self._client.drop_database(self._db.name)
            self._set_as_live()
            return ret
        except Exception as e:
            self._logger.error('Mongo error in drop_db: %s', e)
            self._set_as_down()
            raise e

    def ping_unsafe(self):
        return self._db.command('ping')

    def ping_auth(self, username: str, password: str):
        return self._db.authenticate(username, password, "admin")
