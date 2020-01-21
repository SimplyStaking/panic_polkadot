import configparser
import sys
from datetime import timedelta

from alerter.src.utils.config_parsers.config_parser import ConfigParser


def to_bool(bool_str: str) -> bool:
    return bool_str.lower() in ['true', 'yes', 'y']


class NodeConfig:

    def __init__(self, node_name: str, node_ws_url: str,
                 node_is_validator: bool, is_archive_node: bool,
                 include_in_node_monitor: bool,
                 include_in_blockchain_monitor: bool,
                 stash_account_address: str) -> None:
        self._check_if_stash_account_address_is_valid(node_is_validator,
                                                      stash_account_address)
        self.node_name = node_name
        self.node_ws_url = node_ws_url
        self.node_is_validator = node_is_validator
        self.is_archive_node = is_archive_node
        self.include_in_node_monitor = include_in_node_monitor
        self.include_in_blockchain_monitor = include_in_blockchain_monitor
        self.stash_account_address = stash_account_address

    # This method marks a stash account address valid if the stash account
    # address is non-empty for validators, and empty for full nodes.
    @staticmethod
    def _stash_account_address_is_valid(node_is_validator: bool,
                                        stash_account_address: str) \
            -> bool:
        if not stash_account_address and node_is_validator is False:
            return True
        elif stash_account_address and node_is_validator is True:
            return True
        else:
            return False

    def _check_if_stash_account_address_is_valid(self, node_is_validator: bool,
                                                 stash_account_address: str):
        if not self._stash_account_address_is_valid(node_is_validator,
                                                    stash_account_address):
            print(
                "stash_account_address must be non empty for validators "
                "and empty for full nodes.\nPlease do the necessary "
                "modifications in the config/user_config_nodes.ini file and "
                "restart the alerter.")
            sys.exit(-1)


class RepoConfig:
    def __init__(self, repo_name: str, repo_page: str,
                 include_in_github_monitor: bool) -> None:
        self.repo_name = repo_name
        self.repo_page = repo_page
        self.include_in_github_monitor = include_in_github_monitor


class UserConfig(ConfigParser):
    # Use user_parsed.py rather than creating a new instance of this class
    def __init__(self, alerting_config_file_path: str,
                 nodes_config_file_path: str,
                 repos_config_file_path: str) -> None:
        super().__init__([alerting_config_file_path,
                          nodes_config_file_path,
                          repos_config_file_path])

        cp = configparser.ConfigParser()
        cp.read(alerting_config_file_path)
        cp.read(nodes_config_file_path)
        cp.read(repos_config_file_path)

        # ------------------------ Main Config

        # [general]
        self.unique_alerter_identifier = cp['general'][
            'unique_alerter_identifier']

        # [telegram_alerts]
        self.telegram_alerts_enabled = to_bool(cp['telegram_alerts']['enabled'])
        self.telegram_alerts_bot_token = cp['telegram_alerts']['bot_token']
        self.telegram_alerts_bot_chat_id = cp['telegram_alerts']['bot_chat_id']

        # [email_alerts]
        self.email_alerts_enabled = to_bool(cp['email_alerts']['enabled'])
        self.email_smtp = cp['email_alerts']['smtp']
        self.email_from = cp['email_alerts']['from']
        self.email_to = cp['email_alerts']['to'].split(';')
        # email_to is a semicolon-separated list of email addresses
        self.email_user = cp['email_alerts']['user']
        self.email_pass = cp['email_alerts']['pass']

        # [twilio_alerts]
        self.twilio_alerts_enabled = to_bool(cp['twilio_alerts']['enabled'])
        self.twilio_account_sid = cp['twilio_alerts']['account_sid']
        self.twilio_auth_token = cp['twilio_alerts']['auth_token']
        self.twilio_phone_number = cp['twilio_alerts']['twilio_phone_number']
        self.twilio_dial_numbers = cp['twilio_alerts'][
            'phone_numbers_to_dial'].split(';')
        # twilio_dial_numbers is a semicolon-separated list of phone numbers

        # [telegram_commands]
        self.telegram_cmds_enabled = to_bool(cp['telegram_commands']['enabled'])
        self.telegram_cmds_bot_token = cp['telegram_commands']['bot_token']
        self.telegram_cmds_bot_chat_id = cp['telegram_commands']['bot_chat_id']

        # [redis]
        self.redis_enabled = to_bool(cp['redis']['enabled'])
        self.redis_host = cp['redis']['host']
        self.redis_port = cp['redis']['port']
        self.redis_password = cp['redis']['password']

        # [periodic_alive_reminder]
        self.periodic_alive_reminder_enabled = to_bool(
            cp['periodic_alive_reminder']['enabled'])
        self.interval_seconds = timedelta(
            seconds=int(cp['periodic_alive_reminder']['interval_seconds'])) \
            if self.periodic_alive_reminder_enabled else None
        self.email_enabled = to_bool(
            cp['periodic_alive_reminder']['email_enabled']) \
            if self.periodic_alive_reminder_enabled else None
        self.telegram_enabled = to_bool(
            cp['periodic_alive_reminder']['telegram_enabled']) \
            if self.periodic_alive_reminder_enabled else None

        # [api]
        self.polkadot_api_endpoint = cp['api']['polkadot_api_endpoint']

        # ------------------------ Nodes Config

        # [node_...]
        sections = [cp[k] for k in cp.keys() if k.startswith('node_')]
        self.all_nodes = []
        for section in sections:
            self.all_nodes.append(
                NodeConfig(
                    section['node_name'], section['node_ws_url'],
                    section['node_is_validator'].lower() == 'true',
                    section['is_archive_node'].lower() == 'true',
                    section['include_in_node_monitor'].lower() == 'true',
                    section['include_in_blockchain_monitor'].lower() == 'true',
                    section['stash_account_address']
                ))

        self.filtered_nodes = [n for n in self.all_nodes
                               if n.include_in_node_monitor
                               or n.include_in_blockchain_monitor]

        # ------------------------ Repos Config

        # [repo_...]
        sections = [cp[k] for k in cp.keys() if k.startswith('repo_')]
        self.all_repos = []
        for section in sections:
            self.all_repos.append(
                RepoConfig(
                    section['repo_name'], section['repo_page'],
                    section['include_in_github_monitor'].lower() == 'true'
                ))

        self.filtered_repos = [r for r in self.all_repos
                               if r.include_in_github_monitor]
