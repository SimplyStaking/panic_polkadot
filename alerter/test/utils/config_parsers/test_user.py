import unittest

from alerter.src.utils.config_parsers.user import UserConfig


class TestUserConfig(unittest.TestCase):

    def test_user_config_values_loaded_successfully(self) -> None:
        UserConfig('alerter/test/test_user_config_main.ini',
                   'alerter/test/test_user_config_nodes.ini',
                   'alerter/test/test_user_config_repos.ini')
