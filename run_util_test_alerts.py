from src.utils.alert_utils.get_channel_set import get_full_channel_set
from src.alerts.alerts import Alert
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.logging import DUMMY_LOGGER
from src.utils.mongo_api import MongoApi

if __name__ == '__main__':
    mongo = MongoApi(logger=DUMMY_LOGGER, db_name=UserConf.mongo_db_name,
                     host=UserConf.mongo_host, port=UserConf.mongo_port,
                     username=UserConf.mongo_user, password=UserConf.mongo_pass)
    channel_set = get_full_channel_set(
        channel_name='TEST', logger_general=DUMMY_LOGGER, redis=None,
        alerts_log_file=InternalConf.alerts_log_file, mongo=mongo)

    channel_set.alert_info(Alert('This is a test info alert.'))
    channel_set.alert_warning(Alert('This is a test warning alert.'))
    channel_set.alert_critical(Alert('This is a test critical alert.'))
    channel_set.alert_error(Alert('This is a test error alert.'))
