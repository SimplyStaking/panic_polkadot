from alerter.src.alerting.alert_utils.get_channel_set import \
    get_full_channel_set
from alerter.src.alerting.alerts.alerts import Alert
from alerter.src.utils.config_parsers.internal_parsed import InternalConf
from alerter.src.utils.logging import DUMMY_LOGGER

if __name__ == '__main__':
    channel_set = get_full_channel_set(
        channel_name='TEST', logger_general=DUMMY_LOGGER, redis=None,
        alerts_log_file=InternalConf.alerts_log_file)

    channel_set.alert_info(Alert('This is a test info alert.'))
    channel_set.alert_warning(Alert('This is a test warning alert.'))
    channel_set.alert_critical(Alert('This is a test critical alert.'))
    channel_set.alert_error(Alert('This is a test error alert.'))
