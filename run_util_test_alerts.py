from src.alerts.alerts import Alert
from src.alerts.alerts import AlertCode
from src.store.mongo.mongo_api import MongoApi
from src.utils.alert_utils.get_channel_set import get_full_channel_set
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.logging import DUMMY_LOGGER

if __name__ == '__main__':
    mongo = MongoApi(logger=DUMMY_LOGGER, db_name=UserConf.mongo_db_name,
                     host=UserConf.mongo_host, port=UserConf.mongo_port,
                     username=UserConf.mongo_user, password=UserConf.mongo_pass)
    channel_set = get_full_channel_set(
        channel_name='TEST', logger_general=DUMMY_LOGGER, redis=None,
        alerts_log_file=InternalConf.alerts_log_file, mongo=mongo)

    channel_set.alert_info(
        Alert(AlertCode.TestAlert, 'This is a test INFO alert.'))
    channel_set.alert_warning(
        Alert(AlertCode.TestAlert, 'This is a test WARNING alert.'))
    channel_set.alert_critical(
        Alert(AlertCode.TestAlert, 'This is a test CRITICAL alert.'))
    channel_set.alert_error(
        Alert(AlertCode.TestAlert, 'This is a test ERROR alert.'))
