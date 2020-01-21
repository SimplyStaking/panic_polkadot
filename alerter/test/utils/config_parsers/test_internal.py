import unittest

from alerter.src.utils.config_parsers.internal import InternalConfig


class TestInternalConfig(unittest.TestCase):

    def test_internal_config_values_loaded_successfully(self) -> None:
        InternalConfig('alerter/test/test_internal_config.ini')
