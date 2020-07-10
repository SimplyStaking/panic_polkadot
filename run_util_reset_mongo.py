import sys

from src.store.mongo.mongo_api import MongoApi
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.exceptions import InitialisationException
from src.utils.logging import create_logger


def run() -> None:
    # Check if Mongo enabled
    if not UserConf.mongo_enabled:
        raise InitialisationException('Mongo is not set up. Run the setup '
                                      'script to configure Mongo.')

    logger = create_logger(InternalConf.mongo_log_file, 'mongo',
                           InternalConf.logging_level)

    db_name = UserConf.mongo_db_name
    print('Deleting "{}" database from MongoDB.'.format(db_name))

    # Attempt to delete database
    try:
        MongoApi(
            logger, UserConf.mongo_db_name, UserConf.mongo_host,
            UserConf.mongo_port, UserConf.mongo_user, UserConf.mongo_pass
        ).drop_db()
    except Exception as e:
        sys.exit(e)

    print('Done deleting "{}" database from MongoDB.'.format(db_name))


if __name__ == '__main__':
    try:
        run()
    except InitialisationException as ie:
        sys.exit(ie)
