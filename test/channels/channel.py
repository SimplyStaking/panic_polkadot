import logging
import unittest

from src.alerts.alerts import Alert, AlertCode, SeverityCode
from src.channels.channel import ChannelSet
from test import TestInternalConfSomeAlertsDisabled
from test.test_helpers import CounterChannel


class TestChannelSet(unittest.TestCase):

    def setUp(self) -> None:
        self.alerter_name = 'testalerter'
        self.logger = logging.getLogger('dummy')
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet(
            [self.counter_channel], TestInternalConfSomeAlertsDisabled)

        self.dummy_alert = Alert(AlertCode.TestAlert, 'dummy')
        self.severities_map_bkp = \
            TestInternalConfSomeAlertsDisabled.severities_enabled_map.copy()
        self.alerts_map_bkp = \
            TestInternalConfSomeAlertsDisabled.alerts_enabled_map.copy()

    @staticmethod
    def enable_severity(severity: SeverityCode):
        TestInternalConfSomeAlertsDisabled.severities_enabled_map[
            severity.name] = True

    @staticmethod
    def disable_severity(severity: SeverityCode):
        TestInternalConfSomeAlertsDisabled.severities_enabled_map[
            severity.name] = False

    @staticmethod
    def enable_alert(alert: AlertCode):
        TestInternalConfSomeAlertsDisabled.alerts_enabled_map[alert.name] = True

    @staticmethod
    def disable_alert(alert: AlertCode):
        TestInternalConfSomeAlertsDisabled.alerts_enabled_map[
            alert.name] = False

    def tearDown(self) -> None:
        self.counter_channel.reset()  # ignore previous alerts
        TestInternalConfSomeAlertsDisabled.severities_enabled_map = \
            self.severities_map_bkp
        TestInternalConfSomeAlertsDisabled.alerts_enabled_map = \
            self.alerts_map_bkp

    def test_info_severity_disabled_from_config(self):
        # As set in test_internal_config_alerts, info is disabled by default
        self.channel_set.alert_info(self.dummy_alert)
        self.assertEqual(self.counter_channel.info_count, 0)

    def test_warning_severity_disabled_from_config(self):
        # As set in test_internal_config_alerts, warning is disabled by default
        self.channel_set.alert_warning(self.dummy_alert)
        self.assertEqual(self.counter_channel.warning_count, 0)

    def test_critical_severity_enabled_from_config(self):
        # As set in test_internal_config_alerts, critical is enabled by default
        self.channel_set.alert_critical(self.dummy_alert)
        self.assertEqual(self.counter_channel.critical_count, 1)

    def test_error_severity_enabled_from_config(self):
        # As set in test_internal_config_alerts, error is enabled by default
        self.channel_set.alert_error(self.dummy_alert)
        self.assertEqual(self.counter_channel.error_count, 1)

    def test_info_severity_does_not_work_if_disabled(self):
        self.disable_severity(SeverityCode.INFO)
        self.channel_set.alert_info(self.dummy_alert)
        self.assertEqual(self.counter_channel.info_count, 0)

    def test_warning_severity_does_not_work_if_disabled(self):
        self.disable_severity(SeverityCode.WARNING)
        self.channel_set.alert_warning(self.dummy_alert)
        self.assertEqual(self.counter_channel.warning_count, 0)

    def test_critical_severity_does_not_work_if_disabled(self):
        self.disable_severity(SeverityCode.CRITICAL)
        self.channel_set.alert_critical(self.dummy_alert)
        self.assertEqual(self.counter_channel.critical_count, 0)

    def test_error_severity_does_not_work_if_disabled(self):
        self.disable_severity(SeverityCode.ERROR)
        self.channel_set.alert_error(self.dummy_alert)
        self.assertEqual(self.counter_channel.error_count, 0)

    def test_info_severity_works_if_enabled(self):
        self.enable_severity(SeverityCode.INFO)
        self.channel_set.alert_info(self.dummy_alert)
        self.assertEqual(self.counter_channel.info_count, 1)

    def test_warning_severity_works_if_enabled(self):
        self.enable_severity(SeverityCode.WARNING)
        self.channel_set.alert_warning(self.dummy_alert)
        self.assertEqual(self.counter_channel.warning_count, 1)

    def test_critical_severity_works_if_enabled(self):
        self.enable_severity(SeverityCode.CRITICAL)
        self.channel_set.alert_critical(self.dummy_alert)
        self.assertEqual(self.counter_channel.critical_count, 1)

    def test_error_severity_works_if_enabled(self):
        self.enable_severity(SeverityCode.ERROR)
        self.channel_set.alert_error(self.dummy_alert)
        self.assertEqual(self.counter_channel.error_count, 1)

    def test_alert_works_if_severity_and_alert_enabled_in_config(self):
        # As set in test_internal_config_alerts,
        # - info, warning are disabled by default
        # - critical, error are enabled by default
        # - test alert code is enabled by default
        self.channel_set.alert_info(self.dummy_alert)
        self.channel_set.alert_warning(self.dummy_alert)
        self.channel_set.alert_critical(self.dummy_alert)
        self.channel_set.alert_error(self.dummy_alert)

        self.assertEqual(self.counter_channel.info_count, 0)
        self.assertEqual(self.counter_channel.warning_count, 0)
        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertEqual(self.counter_channel.error_count, 1)

    def test_alert_does_not_work_on_any_severity_if_disabled(self):
        self.disable_alert(self.dummy_alert.alert_code)

        self.channel_set.alert_info(self.dummy_alert)
        self.channel_set.alert_warning(self.dummy_alert)
        self.channel_set.alert_critical(self.dummy_alert)
        self.channel_set.alert_error(self.dummy_alert)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_alert_works_on_any_severity_if_enabled(self):
        self.enable_severity(SeverityCode.INFO)
        self.enable_severity(SeverityCode.WARNING)
        self.enable_severity(SeverityCode.CRITICAL)
        self.enable_severity(SeverityCode.ERROR)
        self.enable_alert(self.dummy_alert.alert_code)

        self.channel_set.alert_info(self.dummy_alert)
        self.channel_set.alert_warning(self.dummy_alert)
        self.channel_set.alert_critical(self.dummy_alert)
        self.channel_set.alert_error(self.dummy_alert)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertEqual(self.counter_channel.error_count, 1)
