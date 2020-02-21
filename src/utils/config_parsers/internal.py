import configparser
import sys
from datetime import timedelta

from src.utils.config_parsers.config_parser import ConfigParser


class InternalConfig(ConfigParser):
    # Use internal_parsed.py rather than creating a new instance of this class
    def __init__(self, config_file_path: str) -> None:
        super().__init__([config_file_path])

        cp = configparser.ConfigParser()
        cp.read(config_file_path)

        # [logging]
        section = cp['logging']
        self.logging_level = section['logging_level']

        self.telegram_commands_general_log_file = section[
            'telegram_commands_general_log_file']
        self.github_monitor_general_log_file_template = section[
            'github_monitor_general_log_file_template']
        self.node_monitor_general_log_file_template = section[
            'node_monitor_general_log_file_template']
        self.blockchain_monitor_general_log_file_template = section[
            'blockchain_monitor_general_log_file_template']

        self.alerts_log_file = section['alerts_log_file']
        self.redis_log_file = section['redis_log_file']
        self.mongo_log_file = section['mongo_log_file']
        self.general_log_file = section['general_log_file']

        # [twilio]
        section = cp['twilio']
        self.twiml_instructions_url = section['twiml_instructions_url']

        # [mongo]
        section = cp['mongo']
        self.mongo_coll_alerts_prefix = section['coll_alerts_prefix']

        # [redis]
        section = cp['redis']
        self.redis_database = int(section['redis_database'])
        self.redis_test_database = int(section['redis_test_database'])

        self.redis_twilio_snooze_key = section['redis_twilio_snooze_key']
        self.redis_github_releases_key_prefix = section[
            'redis_github_releases_key_prefix']
        self.redis_node_monitor_alive_key_prefix = section[
            'redis_node_monitor_alive_key_prefix']
        self.redis_node_monitor_session_index_key_prefix = section[
            'redis_node_monitor_session_index_key_prefix']
        self.redis_node_monitor_last_height_checked_key_prefix = section[
            'redis_node_monitor_last_height_checked_key_prefix']
        self.redis_blockchain_monitor_alive_key_prefix = section[
            'redis_blockchain_monitor_alive_key_prefix']
        self.redis_periodic_alive_reminder_mute_key = \
            section['redis_periodic_alive_reminder_mute_key']

        self.redis_twilio_snooze_key_default_hours = timedelta(hours=float(
            section['redis_twilio_snooze_key_default_hours']))
        self.redis_periodic_alive_reminder_mute_key_default_hours = timedelta(
            hours=float(section['redis_periodic_alive_reminder_mute_key_'
                                'default_hours']))

        self.redis_node_monitor_alive_key_timeout = int(
            section['redis_node_monitor_alive_key_timeout'])
        self.redis_node_monitor_last_height_key_timeout = int(
            section['redis_node_monitor_last_height_key_timeout'])
        self.redis_blockchain_monitor_alive_key_timeout = int(
            section['redis_blockchain_monitor_alive_key_timeout'])

        # [monitoring_periods]
        section = cp['monitoring_periods']
        self.node_monitor_period_seconds = int(
            section['node_monitor_period_seconds'])
        self.node_monitor_max_catch_up_blocks = int(
            section['node_monitor_max_catch_up_blocks'])
        self.blockchain_monitor_period_seconds = int(
            section['blockchain_monitor_period_seconds'])
        self.github_monitor_period_seconds = int(
            section['github_monitor_period_seconds'])

        # [alert_intervals_and_limits]
        section = cp['alert_intervals_and_limits']
        self.downtime_alert_time_interval = timedelta(seconds=int(
            section['downtime_alert_interval_seconds']))
        self.validator_peer_danger_boundary = int(
            section['validator_peer_danger_boundary'])
        self.validator_peer_safe_boundary = int(
            section['validator_peer_safe_boundary'])
        self._check_if_peer_safe_and_danger_boundaries_are_valid()
        self.full_node_peer_danger_boundary = int(
            section['full_node_peer_danger_boundary'])
        self.max_time_alert_between_blocks_authored = timedelta(seconds=int(
            section['max_time_alert_between_blocks_authored']))
        self.github_error_interval_seconds = timedelta(seconds=int(
            section['github_error_interval_seconds']))
        self.no_change_in_height_interval_seconds = int(
            section['no_change_in_height_interval_seconds'])
        self.no_change_in_height_first_warning_seconds = int(
            section['no_change_in_height_first_warning_seconds'])
        self.change_in_bonded_balance_threshold = int(
            section['change_in_bonded_balance_threshold'])
        self._check_if_block_height_warning_and_interval_are_valid()

        # [links]
        section = cp['links']
        self.validators_polkascan_link = section['validators_polkascan_link']
        self.validators_polkastats_link = section['validators_polkastats_link']

        self.block_polkascan_link_prefix = section[
            'block_polkascan_link_prefix']
        self.block_boka_network_link_prefix = section[
            'block_boka_network_link_prefix']
        self.block_subscan_link_prefix = section['block_subscan_link_prefix']

        self.tx_polkascan_link_prefix = section['tx_polkascan_link_prefix']

        self.github_releases_template = section['github_releases_template']

    # Safe boundary must be greater than danger boundary at all times for
    # correct execution
    def _peer_safe_and_danger_boundaries_are_valid(self) -> bool:
        return self.validator_peer_safe_boundary > \
               self.validator_peer_danger_boundary > 0

    def _check_if_peer_safe_and_danger_boundaries_are_valid(self):
        if not self._peer_safe_and_danger_boundaries_are_valid():
            print("validator_peer_safe_boundary must be STRICTLY GREATER than "
                  "validator_peer_danger_boundary for correct execution."
                  "\nPlease do the necessary modifications in the "
                  "config/internal_config.ini file and restart the alerter.")
            sys.exit(-1)

    # The warning value must be less than the interval value at all times for
    # correct execution
    def _block_height_warning_and_interval_values_valid(self) -> bool:
        return self.no_change_in_height_interval_seconds > \
               self.no_change_in_height_first_warning_seconds > 0

    def _check_if_block_height_warning_and_interval_are_valid(self):
        if not self._block_height_warning_and_interval_values_valid():
            print(
                "no_change_in_height_interval_seconds must be STRICTLY GREATER "
                "than no_change_in_height_first_warning_seconds for correct "
                "execution.\nPlease do the necessary modifications in the "
                "config/internal_config.ini file and restart the alerter.")
            sys.exit(-1)
