import logging
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, PropertyMock

from redis import ConnectionError as RedisConnectionError

from src.alerters.reactive.blockchain import Blockchain
from src.alerters.reactive.node import Node, NodeType
from src.channels.channel import ChannelSet
from src.monitors.blockchain import BlockchainMonitor
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from src.utils.exceptions import NoLiveNodeConnectedWithAnApiServerException
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel

GET_WEB_SOCKETS_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.' \
    'get_web_sockets_connected_to_an_api'

PING_NODE_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.ping_node'

GET_REFERENDUM_INFO_OF_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.get_referendum_info_of'

GET_REFERENDUM_COUNT_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.get_referendum_count'

GET_COUNCIL_PROPOSAL_COUNT_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.' \
    'get_council_proposal_count'

GET_PUBLIC_PROPOSAL_COUNT_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.' \
    'get_public_proposal_count'

GET_SESSION_VALIDATORS_FUNCTION = \
    'src.monitors.blockchain.PolkadotApiWrapper.get_session_validators'

DATA_SOURCE_PATH = \
    'src.monitors.blockchain.BlockchainMonitor.data_source'


class TestBlockchainMonitorWithoutRedis(unittest.TestCase):

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.monitor_name = 'testblockchainmonitor'
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)
        self.redis = None
        self.data_sources = []
        self.polkadot_api_endpoint = 'api_endpoint'

        self.dummy_ws_url_1 = "11.22.33.11:9944"
        self.dummy_ws_url_2 = "11.22.33.12:9944"
        self.dummy_ws_url_3 = "11.22.33.13:9944"
        self.dummy_ws_url_4 = "11.22.33.14:9944"
        self.dummy_node_name_1 = "testnode1"
        self.dummy_node_name_2 = "testnode2"
        self.dummy_node_name_3 = "testnode3"
        self.dummy_node_name_4 = "testnode4"
        self.dummy_chain_name = "testchain"
        self.validator_stash_account_address = "DFJGDF8G898fdghb98dg9wetg9we00w"
        self.dummy_full_node_1 = Node(name=self.dummy_node_name_1,
                                      ws_url=self.dummy_ws_url_1,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.dummy_chain_name, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_full_node_2 = Node(name=self.dummy_node_name_2,
                                      ws_url=self.dummy_ws_url_2,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.dummy_chain_name, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_full_node_3 = Node(name=self.dummy_node_name_3,
                                      ws_url=self.dummy_ws_url_3,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.dummy_chain_name, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_validator_node_1 = Node(
            name=self.dummy_node_name_4, ws_url=self.dummy_ws_url_4,
            node_type=NodeType.VALIDATOR_FULL_NODE,
            stash_account_address=self.validator_stash_account_address,
            chain=self.dummy_chain_name, redis=None, is_archive_node=False,
            internal_conf=TestInternalConf)

        self.dummy_blockchain = Blockchain(self.dummy_chain_name, None)
        self.monitor = BlockchainMonitor(self.monitor_name,
                                         self.dummy_blockchain,
                                         self.channel_set, self.logger,
                                         self.redis, self.data_sources,
                                         self.polkadot_api_endpoint,
                                         TestInternalConf)
        self.dummy_referendum_count = 10
        self.dummy_public_prop_count = 10
        self.dummy_council_prop_count = 10
        self.dummy_validator_set_size = 120

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_chooses_an_online_full_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_validator_node_1.set_as_down(self.channel_set, self.logger)
        self.monitor.data_sources = [self.dummy_full_node_1,
                                     self.dummy_validator_node_1,
                                     self.dummy_full_node_2,
                                     self.dummy_full_node_3]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_2]
        node = self.monitor.data_source

        self.assertEqual(node.name, self.dummy_node_name_2)

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_chooses_an_online_validator_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_2.set_as_down(self.channel_set, self.logger)
        self.monitor.data_sources = [self.dummy_full_node_1,
                                     self.dummy_validator_node_1,
                                     self.dummy_full_node_2,
                                     self.dummy_full_node_3]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_4]
        node = self.monitor.data_source

        self.assertEqual(node.name, self.dummy_validator_node_1.name)

    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_raises_exception_if_no_node_is_eligible_for_choosing(
            self, mock_get_web_sockets) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_3.set_as_down(self.channel_set, self.logger)
        self.monitor.data_sources = [self.dummy_full_node_1,
                                     self.dummy_full_node_2,
                                     self.dummy_full_node_3,
                                     self.dummy_validator_node_1]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1]

        try:
            _ = self.monitor.data_source
            self.fail('Expected NoLiveNodeConnectedWithAnApiServerException'
                      ' exception to be thrown.')
        except NoLiveNodeConnectedWithAnApiServerException:
            pass

    def test_status_returns_as_expected(self) -> None:
        self.dummy_blockchain.set_referendum_count(
            self.dummy_referendum_count, self.channel_set, self.logger)
        self.dummy_blockchain.set_validator_set_size(
            self.dummy_validator_set_size, self.channel_set, self.logger)
        self.dummy_blockchain.set_public_prop_count(
            self.dummy_public_prop_count, self.channel_set, self.logger)
        self.dummy_blockchain.set_council_prop_count(
            self.dummy_council_prop_count, self.channel_set, self.logger)

        expected_output = "referendum_count={}, public_prop_count={}, " \
                          "council_prop_count={}, validator_set_size ={}" \
            .format(self.dummy_referendum_count, self.dummy_public_prop_count,
                    self.dummy_council_prop_count,
                    self.dummy_validator_set_size)
        self.assertEqual(expected_output, self.monitor.status())

    def test_check_for_new_referendums_calls_ref_setter_once_if_ref_count_None(
            self) -> None:
        self.dummy_blockchain.set_referendum_count = MagicMock(
            side_effect=self.dummy_blockchain.set_referendum_count)
        self.monitor._check_for_new_referendums(self.dummy_referendum_count)

        self.assertEqual(
            self.dummy_blockchain.set_referendum_count.call_count, 1)

    @patch(GET_REFERENDUM_INFO_OF_FUNCTION, return_value=None)
    def test_check_for_new_referendums_calls_ref_setter_5_times_if_5_new_refs(
            self, _) -> None:
        with mock.patch(DATA_SOURCE_PATH, new_callable=PropertyMock) \
                as mock_data_source:
            mock_data_source.return_value = self.dummy_full_node_1

            self.dummy_blockchain.set_referendum_count(
                self.dummy_referendum_count,
                self.channel_set,
                self.logger)
            new_referendum_count = self.dummy_referendum_count + 5

            self.dummy_blockchain.set_referendum_count = MagicMock(
                side_effect=self.dummy_blockchain.set_referendum_count)
            self.monitor._check_for_new_referendums(new_referendum_count)

            self.assertEqual(
                self.dummy_blockchain.set_referendum_count.call_count, 5)

    def test_check_for_new_referendums_calls_ref_setter_0_times_if_same_count(
            self) -> None:
        self.dummy_blockchain.set_referendum_count(self.dummy_referendum_count,
                                                   self.channel_set,
                                                   self.logger)
        new_referendum_count = self.dummy_referendum_count

        self.dummy_blockchain.set_referendum_count = MagicMock(
            side_effect=self.dummy_blockchain.set_referendum_count)
        self.monitor._check_for_new_referendums(new_referendum_count)

        self.assertEqual(
            self.dummy_blockchain.set_referendum_count.call_count, 0)

    @patch(GET_REFERENDUM_COUNT_FUNCTION)
    @patch(GET_COUNCIL_PROPOSAL_COUNT_FUNCTION)
    @patch(GET_PUBLIC_PROPOSAL_COUNT_FUNCTION)
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_sets_blockchain_state_to_retrieved_data(
            self, mock_session_val, mock_public_prop, mock_council_prop,
            mock_ref_count) -> None:
        with mock.patch(DATA_SOURCE_PATH, new_callable=PropertyMock) \
                as mock_data_source:
            mock_data_source.return_value = self.dummy_full_node_1
            mock_session_val.return_value = ['7DG7fdgfd', 'dgtdFG884']
            mock_public_prop.return_value = self.dummy_public_prop_count
            mock_council_prop.return_value = self.dummy_council_prop_count
            mock_ref_count.return_value = self.dummy_referendum_count
            self.monitor.last_data_source_used = self.dummy_full_node_1

            self.monitor.monitor()
            self.assertEqual(self.dummy_blockchain.referendum_count,
                             self.dummy_referendum_count)
            self.assertEqual(self.dummy_blockchain.public_prop_count,
                             self.dummy_public_prop_count)
            self.assertEqual(self.dummy_blockchain.council_prop_count,
                             self.dummy_council_prop_count)
            self.assertEqual(self.dummy_blockchain.validator_set_size,
                             2)

    @patch(GET_REFERENDUM_COUNT_FUNCTION, return_value=0)
    @patch(GET_COUNCIL_PROPOSAL_COUNT_FUNCTION, return_value=0)
    @patch(GET_PUBLIC_PROPOSAL_COUNT_FUNCTION, return_value=0)
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_sets_API_as_up_if_entire_data_obtained_successfully(
            self, _1, _2, _3, _4) -> None:
        with mock.patch(DATA_SOURCE_PATH, new_callable=PropertyMock) \
                as mock_data_source:
            mock_data_source.return_value = self.dummy_full_node_1
            self.monitor.last_data_source_used = self.dummy_full_node_1

            self.monitor.monitor()
            self.assertFalse(self.monitor.data_wrapper.is_api_down)

    @patch(GET_REFERENDUM_COUNT_FUNCTION, return_value=0)
    @patch(GET_COUNCIL_PROPOSAL_COUNT_FUNCTION, return_value=0)
    @patch(GET_PUBLIC_PROPOSAL_COUNT_FUNCTION, return_value=0)
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_connects_data_source_with_api_if_entire_data_obtained_successfully(
            self, _1, _2, _3, _4) -> None:
        with mock.patch(DATA_SOURCE_PATH, new_callable=PropertyMock) \
                as mock_data_source:
            mock_data_source.return_value = self.dummy_full_node_1
            self.monitor.last_data_source_used = self.dummy_full_node_1
            self.monitor.last_data_source_used.disconnect_from_api(
                self.channel_set, self.logger)
            self.assertFalse(self.monitor.last_data_source_used.is_connected_to_api_server)
            self.monitor.monitor()
            self.assertTrue(self.monitor.last_data_source_used.is_connected_to_api_server)


class TestBlockchainMonitorWithRedis(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Same as in setUp(), to avoid running all tests if Redis is offline

        logger = logging.getLogger('dummy')
        db = TestInternalConf.redis_test_database
        host = TestUserConf.redis_host
        port = TestUserConf.redis_port
        password = TestUserConf.redis_password
        redis = RedisApi(logger, db, host, port, password)

        try:
            redis.ping_unsafe()
        except RedisConnectionError:
            raise Exception('Redis is not online.')

    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.monitor_name = 'testblockchainmonitor'
        self.blockchain_name = 'testblockchain'
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)

        self.db = TestInternalConf.redis_test_database
        self.host = TestUserConf.redis_host
        self.port = TestUserConf.redis_port
        self.password = TestUserConf.redis_password
        self.redis = RedisApi(self.logger, self.db, self.host,
                              self.port, self.password)
        self.redis.delete_all_unsafe()

        try:
            self.redis.ping_unsafe()
        except RedisConnectionError:
            self.fail('Redis is not online.')

        self.data_sources = []
        self.blockchain = Blockchain(self.blockchain_name, self.redis)
        self.polkadot_api_endpoint = 'api_endpoint'
        self.monitor = BlockchainMonitor(self.monitor_name, self.blockchain,
                                         self.channel_set, self.logger,
                                         self.redis, self.data_sources,
                                         self.polkadot_api_endpoint,
                                         TestInternalConf)

        self.redis_alive_key_timeout = \
            TestInternalConf.redis_blockchain_monitor_alive_key_timeout
        self.alive_key_timeout = \
            TestInternalConf.redis_blockchain_monitor_alive_key_timeout

    def test_save_state_saves_alive_key_temporarily(self):
        self.monitor.save_state()

        key = Keys.get_blockchain_monitor_alive(self.monitor_name)
        last_update = self.redis.get(key)
        timeout = self.redis.time_to_live(key)

        self.assertIsNotNone(last_update)
        self.assertEqual(timeout, self.alive_key_timeout)
