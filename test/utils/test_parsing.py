import unittest

from src.utils.parsing import parse_int_from_string


class TestParsing(unittest.TestCase):

    def test_parse_int_from_str_returns_as_expected_when_given_hex_val_non_0(
            self) -> None:
        self.assertEqual(15, parse_int_from_string("0xF"))

    def test_parse_int_from_str_returns_as_expected_when_given_hex_val_0(
            self) -> None:
        self.assertEqual(0, parse_int_from_string("0x0"))

    def test_parse_int_from_str_returns_as_expected_when_given_val_non_0(
            self) -> None:
        self.assertEqual(4546, parse_int_from_string("4546"))

    def test_parse_int_from_str_returns_as_expected_when_given_val_0(
            self) -> None:
        self.assertEqual(0, parse_int_from_string("0"))
