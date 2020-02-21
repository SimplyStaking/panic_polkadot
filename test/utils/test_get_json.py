import logging
import unittest
from unittest.mock import patch

from src.utils.exceptions import *
from src.utils.get_json import get_polkadot_json, get_json

GET_JSON_FUNCTION = 'src.utils.get_json.get_json'
GET_FUNCTION = 'src.utils.get_json.requests.get'
LOGGER = logging.getLogger('dummy')

ENDPOINT = 'the_endpoint'
API_CALL = 'the_api_call'
PARAMS = {'websocket': 'the_websocket',
          'account_address': 'the_address'}
RESULT = 'the_result'


class TestGetJson(unittest.TestCase):
    class DummyGetReturn:
        CONTENT_BYTES = b'{"a":"b","c":1,"2":3}'
        CONTENT_DICT = {"a": "b", "c": 1, "2": 3}

        def __init__(self) -> None:
            self.content = self.CONTENT_BYTES

    @patch(GET_FUNCTION, return_value=DummyGetReturn())
    def test_get_json_accesses_content_and_parses_bytes_to_dict(self, _):
        self.assertEqual(TestGetJson.DummyGetReturn.CONTENT_DICT,
                         get_json(ENDPOINT, LOGGER, PARAMS))

    @patch(GET_FUNCTION, return_value=DummyGetReturn())
    def test_get_json_with_no_params_works_just_the_same(self, _):
        self.assertEqual(TestGetJson.DummyGetReturn.CONTENT_DICT,
                         get_json(ENDPOINT, LOGGER))


class TestGetPolkadotJson(unittest.TestCase):

    @patch(GET_JSON_FUNCTION, return_value={})
    def test_get_polka_json_error_if_api_returns_blank(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected UnexpectedApiErrorWhenReadingDataException')
        except UnexpectedApiErrorWhenReadingDataException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={
        'unexpected_key': 'unexpected_value'})
    def test_get_polka_json_error_if_api_returns_unexpected_key(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected UnexpectedApiErrorWhenReadingDataException')
        except UnexpectedApiErrorWhenReadingDataException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={'result': RESULT})
    def test_get_polka_json_result_if_api_return_has_result(self, _):
        ret = get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
        self.assertEqual(RESULT, ret)

    @patch(GET_JSON_FUNCTION, return_value={
        'error': 'Error: API call the_api_call failed.'})
    def test_get_polka_json_error_if_api_call_failed(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected ApiCallFailedException')
        except ApiCallFailedException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={
        'error': 'An API for ' + PARAMS['websocket'] +
                 ' needs to be setup before it can be queried'})
    def test_get_polka_json_error_if_api_for_ws_was_not_set_up(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected NodeWasNotConnectedToApiServerException')
        except NodeWasNotConnectedToApiServerException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={'error': 'no reply from node'})
    def test_get_polka_json_error_if_no_reply_from_node(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected ConnectionWithNodeApiLostException')
        except ConnectionWithNodeApiLostException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={'error': 'Invalid decoded address'})
    def test_get_polka_json_error_if_invalid_decoded_address(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected InvalidStashAccountAddressException')
        except InvalidStashAccountAddressException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={
        'error': "getStorage(key: StorageKey, at?: BlockHash): "
                 "StorageData:: -32603: Unknown error occured: "
                 "Client(UnknownBlock(\"State alread"})
    def test_get_polka_json_error_if_node_is_not_an_archive_node(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected NodeIsNotAnArchiveNodeException')
        except NodeIsNotAnArchiveNodeException:
            pass

    @patch(GET_JSON_FUNCTION, return_value={'error': 'some_other_error'})
    def test_get_polka_json_error_if_any_other_error(self, _):
        try:
            get_polkadot_json(ENDPOINT, PARAMS, LOGGER, API_CALL)
            self.fail('Expected UnexpectedApiCallErrorException')
        except UnexpectedApiCallErrorException:
            pass
