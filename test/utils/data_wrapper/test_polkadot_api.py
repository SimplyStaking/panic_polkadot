import logging
import unittest
from typing import Dict
from unittest.mock import patch

from src.channels.channel import ChannelSet
from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from test.test_helpers import CounterChannel

GET_POLKADOT_JSON_FUNCTION = \
    'src.utils.data_wrapper.polkadot_api.get_polkadot_json'


def api_mock_generator(expected_endpoint: str, expected_params: Dict,
                       expected_api_call: str):
    def api_mock(endpoint: str, params: Dict, _, api_call: str = ''):
        return (endpoint == expected_endpoint and
                params == expected_params and
                api_call == expected_api_call)

    return api_mock


class TestPolkadotApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ws_url = 'the_ws'
        cls.api_endpoint = 'the_api'
        cls.block_hash = 'the_block_hash'
        cls.acc_addr = 'the_account_address'
        cls.validator_id = "the_validator_id"
        cls.block_no = 1
        cls.referendum_index = 2
        cls.session_index = 3
        cls.auth_index = 4

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.wrapper = PolkadotApiWrapper(self.logger, self.api_endpoint)

        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel])

        self.params = {'websocket': self.ws_url}

    def test_api_endpoint_returns_api_endpoint(self):
        self.assertEqual(self.api_endpoint, self.wrapper.api_endpoint)

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_block_hash(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/rpc/chain/getBlockHash'
        self.params['block_number'] = self.block_no
        api_call = 'chain/getBlockHash'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(
            self.wrapper.get_block_hash(self.ws_url, self.block_no))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_finalized_head(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/rpc/chain/getFinalizedHead'
        api_call = 'chain/getFinalizedHead'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_finalized_head(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_header(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/rpc/chain/getHeader'
        self.params['hash'] = self.block_hash
        api_call = 'chain/getHeader'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_header(self.ws_url, self.block_hash))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_system_chain(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/rpc/system/chain'
        api_call = 'system/chain'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_system_chain(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_system_health(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/rpc/system/health'
        api_call = 'system/health'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_system_health(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_council_members(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/council/members'
        api_call = 'council/members'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_council_members(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_council_proposal_count(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/council/proposalCount'
        api_call = 'council/proposalCount'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_council_proposal_count(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_public_proposal_count(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/democracy/publicPropCount'
        api_call = 'democracy/publicPropCount'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_public_proposal_count(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_referendum_count(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/democracy/referendumCount'
        api_call = 'democracy/referendumCount'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_referendum_count(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_referendum_info_of(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/democracy/referendumInfoOf'
        api_call = 'democracy/referendumInfoOf'
        self.params['referendum_index'] = self.referendum_index
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_referendum_info_of(
            self.ws_url, self.referendum_index))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_authored_block(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/imOnline/authoredBlocks'
        self.params['validator_id'] = self.validator_id
        self.params['session_index'] = self.session_index
        api_call = 'imOnline/authoredBlocks'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_authored_blocks(
            self.ws_url, self.session_index, self.validator_id))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_received_heartbeats(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/imOnline/receivedHeartbeats'
        self.params['session_index'] = self.session_index
        self.params['auth_index'] = self.auth_index
        api_call = 'imOnline/receivedHeartbeats'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_received_heartbeats(
            self.ws_url, self.session_index, self.auth_index))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_current_index(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/session/currentIndex'
        api_call = 'session/currentIndex'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_current_index(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_disabled_validators(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/session/disabledValidators'
        api_call = 'session/disabledValidators'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_disabled_validators(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_session_validators(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/session/validators'
        api_call = 'session/validators'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_session_validators(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_current_elected(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/staking/currentElected'
        api_call = 'staking/currentElected'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_current_elected(self.ws_url))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_stakers(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/staking/stakers'
        self.params['account_address'] = self.acc_addr
        api_call = 'staking/stakers'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(
            self.wrapper.get_stakers(self.ws_url, self.acc_addr))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_events(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/query/system/events'
        self.params['block_hash'] = self.block_hash
        api_call = 'system/events'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_events(self.ws_url, self.block_hash))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_slash_amount(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/custom/getSlashAmount'
        self.params['block_hash'] = self.block_hash
        self.params['account_address'] = self.acc_addr
        api_call = 'custom/getSlashAmount'
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_slash_amount(
            self.ws_url, self.block_hash, self.acc_addr))

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_get_web_sockets_connected_to_an_api(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/getConnectionsList'
        api_call = ''
        mock.api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.get_web_sockets_connected_to_an_api())

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_ping_api(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/pingApi'
        self.params = {}
        api_call = ''
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.ping_api())

    @patch(GET_POLKADOT_JSON_FUNCTION)
    def test_ping_node(self, mock):
        # Set up mock
        endpoint = self.api_endpoint + '/api/pingNode'
        api_call = ''
        mock.side_effect = api_mock_generator(endpoint, self.params, api_call)

        self.assertTrue(self.wrapper.ping_node(self.ws_url))

    def test_set_api_as_down_produces_alert_if_api_not_down(self):
        # By default, API not down

        # First time round, error alert is produced
        self.counter_channel.reset()
        self.wrapper.set_api_as_down("", self.channel_set)
        self.assertEqual(1, self.counter_channel.error_count)

        # Second time round, API is already down, so no alerts
        self.counter_channel.reset()
        self.wrapper.set_api_as_down("", self.channel_set)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_api_as_up_produces_alert_if_api_is_down(self):
        # By default, API not down

        # First time round, no alert is produced
        self.counter_channel.reset()
        self.wrapper.set_api_as_up("", self.channel_set)
        self.assertTrue(self.counter_channel.no_alerts())

        # In between, we set the api as down
        self.wrapper.set_api_as_down("", self.channel_set)

        # API is now down, so info alert is produced
        self.counter_channel.reset()
        self.wrapper.set_api_as_up("", self.channel_set)
        self.assertEqual(1, self.counter_channel.info_count)
