import logging
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, PropertyMock

from redis import ConnectionError as RedisConnectionError

from src.alerters.reactive.node import Node, NodeType
from src.alerts.alerts import FoundLiveArchiveNodeAgainAlert
from src.channels.channel import ChannelSet
from src.monitors.node import NodeMonitor
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from src.utils.exceptions import \
    NoLiveNodeConnectedWithAnApiServerException, \
    NoLiveArchiveNodeConnectedWithAnApiServerException
from src.utils.scaling import scale_to_tera
from src.utils.types import NONE
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel

GET_WEB_SOCKETS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.' \
    'get_web_sockets_connected_to_an_api'

PING_NODE_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.ping_node'

GET_SYSTEM_HEALTH_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_system_health'

GET_FINALIZED_HEAD_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_finalized_head'

GET_HEADER_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_header'

GET_BLOCK_HASH_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_block_hash'

GET_SLASH_AMOUNT_FUNCITON = \
    'src.monitors.node.PolkadotApiWrapper.get_slash_amount'

GET_SESSION_VALIDATORS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_session_validators'

GET_ERAS_STAKERS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_eras_stakers'

GET_COUNCIL_MEMBERS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_council_members'

GET_DERIVE_STAKING_VALIDATORS = \
    'src.monitors.node.PolkadotApiWrapper.get_derive_staking_validators'

GET_CURRENT_INDEX_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_current_index'

GET_AUTHORED_BLOCKS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_authored_blocks'

GET_DISABLED_VALIDATORS_FUNCTION = \
    'src.monitors.node.PolkadotApiWrapper.get_disabled_validators'

DATA_SOURCE_INDIRECT_PATH = \
    'src.monitors.node.NodeMonitor.data_source_indirect'

DATA_SOURCE_ARCHIVE_PATH = \
    'src.monitors.node.NodeMonitor.data_source_archive'


# noinspection PyUnresolvedReferences
class TestNodeMonitorWithoutRedis(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger('dummy')
        self.monitor_name = 'testnodemonitor'
        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)
        self.node_monitor_max_catch_up_blocks = \
            TestInternalConf.node_monitor_max_catch_up_blocks
        self.redis = None
        self.archive_alerts_disabled = False
        self.data_sources = []
        self.polkadot_api_endpoint = 'api_endpoint'
        self.chain = 'testchain'

        self.full_node_name = 'testfullnode'
        self.full_node_ws_url = '123.123.123.11:9944'
        self.full_node = Node(self.full_node_name, self.full_node_ws_url,
                              NodeType.NON_VALIDATOR_FULL_NODE, '', self.chain,
                              None, True, TestInternalConf)
        self.full_node_monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.full_node,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)

        self.validator_name = 'testvalidator'
        self.validator_ws_url = '13.13.14.11:9944'
        self.validator_stash_account_address = "DFJGDF8G898fdghb98dg9wetg9we00w"
        self.validator = Node(self.validator_name, self.validator_ws_url,
                              NodeType.VALIDATOR_FULL_NODE,
                              self.validator_stash_account_address, self.chain,
                              None, True, TestInternalConf)
        self.validator_monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.validator,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)

        self.dummy_session_index = 60
        self.dummy_last_height_checked = 1000
        self.dummy_height_to_check = 1000
        self.dummy_bonded_balance = scale_to_tera(5)
        self.dummy_auth_index = 10
        self.dummy_no_of_peers = 100
        self.dummy_active = True
        self.dummy_council_member = True
        self.dummy_elected = True
        self.dummy_disabled = True
        self.dummy_no_of_blocks_authored = 10
        self.dummy_finalized_block_height = 34535
        self.dummy_ws_url_1 = "11.22.33.11:9944"
        self.dummy_ws_url_2 = "11.22.33.12:9944"
        self.dummy_ws_url_3 = "11.22.33.13:9944"
        self.dummy_ws_url_4 = "11.22.33.14:9944"
        self.dummy_ws_url_5 = "11.22.33.15:9944"
        self.dummy_node_name_1 = "testnode1"
        self.dummy_node_name_2 = "testnode2"
        self.dummy_node_name_3 = "testnode3"
        self.dummy_node_name_4 = "testnode4"
        self.dummy_node_name_5 = "testnode5"
        self.dummy_full_node_1 = Node(name=self.dummy_node_name_1,
                                      ws_url=self.dummy_ws_url_1,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.chain, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_full_node_2 = Node(name=self.dummy_node_name_2,
                                      ws_url=self.dummy_ws_url_2,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.chain, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_full_node_3 = Node(name=self.dummy_node_name_3,
                                      ws_url=self.dummy_ws_url_3,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.chain, redis=None,
                                      is_archive_node=True,
                                      internal_conf=TestInternalConf)
        self.dummy_full_node_4 = Node(name=self.dummy_node_name_5,
                                      ws_url=self.dummy_ws_url_5,
                                      node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                      stash_account_address='',
                                      chain=self.chain, redis=None,
                                      is_archive_node=False,
                                      internal_conf=TestInternalConf)
        self.dummy_validator_node_1 = Node(
            name=self.dummy_node_name_4, ws_url=self.dummy_ws_url_4,
            node_type=NodeType.VALIDATOR_FULL_NODE,
            stash_account_address=self.validator_stash_account_address,
            chain=self.chain, redis=None, is_archive_node=True,
            internal_conf=TestInternalConf)

    def test_indirect_monitoring_data_sources_field_set_correctly(self) -> None:
        self.data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2,
            self.dummy_full_node_3, self.dummy_full_node_4,
            self.dummy_validator_node_1
        ]
        test_monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.validator,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)

        self.assertEqual(test_monitor.indirect_monitoring_data_sources,
                         self.data_sources)

    def test_archive_monitoring_data_sources_field_set_correctly(self) -> None:
        self.data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2,
            self.dummy_full_node_3, self.dummy_full_node_4,
            self.dummy_validator_node_1
        ]
        test_monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.validator,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)
        expected_result = [self.dummy_full_node_1, self.dummy_full_node_2,
                           self.dummy_full_node_3, self.dummy_validator_node_1]

        self.assertEqual(test_monitor.archive_monitoring_data_sources,
                         expected_result)

    def test_is_catching_up_false_by_default(self) -> None:
        self.assertFalse(self.validator_monitor.is_catching_up())

    def test_is_indirect_monitoring_disabled_true_if_no_data_sources(
            self) -> None:
        self.assertTrue(self.validator_monitor.indirect_monitoring_disabled)

    def test_is_indirect_monitoring_disabled_false_if_data_sources_given(
            self) -> None:
        self.data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2
        ]
        test_monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.validator,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)

        self.assertFalse(test_monitor.indirect_monitoring_disabled)

    def test_session_index_NONE_by_default(self) -> None:
        self.assertEqual(NONE, self.validator_monitor.session_index)

    def test_last_height_checked_NONE_by_default(self) -> None:
        self.assertEqual(NONE, self.validator_monitor.last_height_checked)

    def test_no_live_archive_node_alert_sent_false_by_default(self) -> None:
        self.assertFalse(self.validator_monitor.no_live_archive_node_alert_sent)

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_chooses_an_online_full_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_validator_node_1.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._indirect_monitoring_data_sources = [
            self.dummy_full_node_1, self.dummy_validator_node_1,
            self.dummy_full_node_2, self.dummy_full_node_3]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_2]
        node = self.validator_monitor.data_source_indirect

        self.assertEqual(node.name, self.dummy_node_name_2)

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_chooses_an_online_validator_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_2.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._indirect_monitoring_data_sources = [
            self.dummy_full_node_1, self.dummy_validator_node_1,
            self.dummy_full_node_2, self.dummy_full_node_3]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_4]
        node = self.validator_monitor.data_source_indirect

        self.assertEqual(node.name, self.dummy_node_name_4)

    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_indirect_raises_exception_if_no_node_is_eligible_for_choosing(
            self, mock_get_web_sockets) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_3.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._indirect_monitoring_data_sources = [
            self.dummy_full_node_1,
            self.dummy_full_node_2,
            self.dummy_full_node_3,
            self.dummy_validator_node_1]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1]

        try:
            _ = self.validator_monitor.data_source_indirect
            self.fail('Expected NoLiveNodeConnectedWithAnApiServerException'
                      ' exception to be thrown.')
        except NoLiveNodeConnectedWithAnApiServerException:
            pass

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_archive_chooses_an_online_archive_full_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_3.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._archive_monitoring_data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2,
            self.dummy_full_node_3, self.dummy_validator_node_1,
            self.dummy_full_node_4]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_5]
        node = self.validator_monitor.data_source_archive

        self.assertEqual(node.name, self.dummy_node_name_5)

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_archive_chooses_an_online_archive_validator_node_connected_to_the_API(
            self, mock_get_web_sockets, _) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_3.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_2.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._archive_monitoring_data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2,
            self.dummy_full_node_3, self.dummy_validator_node_1,
            self.dummy_full_node_4]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_4,
                                             self.dummy_ws_url_5]
        node = self.validator_monitor.data_source_archive

        self.assertEqual(node.name, self.dummy_node_name_4)

    @patch(GET_WEB_SOCKETS_FUNCTION)
    def test_data_source_archive_raises_exception_if_no_archive_node_is_eligible_for_choosing(
            self, mock_get_web_sockets) -> None:
        self.dummy_full_node_1.set_as_down(self.channel_set, self.logger)
        self.dummy_full_node_3.set_as_down(self.channel_set, self.logger)
        self.dummy_validator_node_1.set_as_down(self.channel_set, self.logger)
        self.validator_monitor._archive_monitoring_data_sources = [
            self.dummy_full_node_1, self.dummy_full_node_2,
            self.dummy_full_node_3, self.dummy_validator_node_1]
        mock_get_web_sockets.return_value = [self.dummy_ws_url_1,
                                             self.dummy_ws_url_5]

        try:
            _ = self.validator_monitor.data_source_archive
            self.fail('Expected '
                      'NoLiveArchiveNodeConnectedWithAnApiServerException'
                      ' exception to be thrown.')
        except NoLiveArchiveNodeConnectedWithAnApiServerException:
            pass

    def test_status_returns_as_expected_for_validator_monitor(self) -> None:
        self.validator_monitor._session_index = self.dummy_session_index
        self.validator_monitor._last_height_checked = \
            self.dummy_last_height_checked
        self.validator._bonded_balance = self.dummy_bonded_balance
        self.validator._no_of_peers = self.dummy_no_of_peers
        self.validator._active = self.dummy_active
        self.validator._council_member = self.dummy_council_member
        self.validator._elected = self.dummy_elected
        self.validator._disabled = self.dummy_disabled
        self.validator._no_of_blocks_authored = \
            self.dummy_no_of_blocks_authored
        self.validator._finalized_block_height = \
            self.dummy_finalized_block_height

        expected_output = "bonded_balance={}, is_syncing=False, " \
                          "no_of_peers={}, active={}, council_member={}, " \
                          "elected={}, disabled={}, " \
                          "no_of_blocks_authored={}, " \
                          "finalized_block_height={}, session_index={}, " \
                          "last_height_checked={}".format(
            self.dummy_bonded_balance, self.dummy_no_of_peers,
            self.dummy_active, self.dummy_council_member,
            self.dummy_elected, self.dummy_disabled,
            self.dummy_no_of_blocks_authored,
            self.dummy_finalized_block_height,
            self.dummy_session_index,
            self.dummy_last_height_checked)
        self.assertEqual(expected_output, self.validator_monitor.status())

    def test_status_returns_as_expected_for_full_node_monitor(self) -> None:
        self.full_node._no_of_peers = self.dummy_no_of_peers
        self.full_node._finalized_block_height = \
            self.dummy_finalized_block_height

        expected_output = "bonded_balance={}, is_syncing=False, " \
                          "no_of_peers={}, active={}, council_member={}, " \
                          "elected={}, disabled={}, " \
                          "no_of_blocks_authored={}, " \
                          "finalized_block_height={}".format(
            None, self.dummy_no_of_peers, None, None,
            None, None, 0, self.dummy_finalized_block_height)
        self.assertEqual(expected_output, self.full_node_monitor.status())

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_SYSTEM_HEALTH_FUNCTION,
           return_value={"isSyncing": True, "peers": 92,
                         "shouldHavePeers": True})
    @patch(GET_FINALIZED_HEAD_FUNCTION,
           return_value={"0x42ebf471c67fe6dd8a5b535ad2596513e9e54d"})
    @patch(GET_HEADER_FUNCTION,
           return_value={"digest": {
               "logs": ["0x064241424",
                        "0x05424c64ec57d9d0b3fb0a9f46146e517bf310d82cd3448e"]},
               "extrinsicsRoot": "0xffb51f954a94",
               "number": "523686",
               "parentHash": "0x0d676112b55cb14b200a94da",
               "stateRoot": "0xbdbdf6d9b93945e42e0beac"})
    def test_monitor_direct_sets_node_state_to_retrieved_data(
            self, _1, _2, _3, _4) -> None:
        self.validator_monitor.monitor_direct()

        self.assertFalse(self.validator.is_down)
        self.assertTrue(self.validator.is_syncing)
        self.assertEqual(self.validator.no_of_peers, 92)
        self.assertEqual(self.validator.finalized_block_height, 523686)

    @patch(PING_NODE_FUNCTION, return_value=None)
    @patch(GET_SYSTEM_HEALTH_FUNCTION,
           return_value={"isSyncing": True, "peers": 92,
                         "shouldHavePeers": True})
    @patch(GET_FINALIZED_HEAD_FUNCTION,
           return_value={"0x42ebf471c67fe6dd8a5b535ad2596513e9e54d"})
    @patch(GET_HEADER_FUNCTION,
           return_value={"digest": {
               "logs": ["0x064241424",
                        "0x05424c64ec57d9d0b3fb0a9f46146e517bf310d82cd3448e"]},
               "extrinsicsRoot": "0xffb51f954a94",
               "number": "523686",
               "parentHash": "0x0d676112b55cb14b200a94da",
               "stateRoot": "0xbdbdf6d9b93945e42e0beac"})
    def test_monitor_direct_sets_API_as_up_if_monitoring_successful(
            self, _1, _2, _3, _4) -> None:
        self.validator_monitor.monitor_direct()

        self.assertFalse(self.validator_monitor.data_wrapper.is_api_down)

    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=50)
    def test_check_for_slashing_calls_node_slash_function_amount_greater_than_0(
            self, _1, _2) -> None:
        self.validator_monitor.node.slash = MagicMock(
            side_effect=self.validator_monitor.node.slash)
        self.validator_monitor._check_for_slashing(self.dummy_height_to_check,
                                                   self.dummy_full_node_1)

        self.assertEqual(self.validator_monitor.node.slash.call_count, 1)

    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    def test_check_for_slashing_does_not_call_node_slash_function_amount_0(
            self, _1, _2) -> None:
        self.validator_monitor.node.slash = MagicMock(
            side_effect=self.validator_monitor.node.slash)
        self.validator_monitor._check_for_slashing(self.dummy_height_to_check,
                                                   self.dummy_full_node_1)

        self.assertEqual(self.validator_monitor.node.slash.call_count, 0)

    def test_check_for_new_session_sets_and_does_not_modify_node_state_first_time_round(
            self) -> None:
        self.validator_monitor.node.set_time_of_last_block(
            10.3, self.channel_set, self.logger)
        self.validator_monitor.node._no_of_blocks_authored = \
            self.dummy_no_of_blocks_authored
        last_time_did_task = \
            self.validator_monitor.node.blocks_authored_alert_limiter. \
                last_time_that_did_task
        self.validator_monitor.node.set_is_authoring(
            False, self.channel_set, self.logger)
        self.validator_monitor.node.set_time_of_last_block_check_activity(
            34.4, self.channel_set, self.logger)

        self.validator_monitor._check_for_new_session(self.dummy_session_index)

        self.assertEqual(self.validator_monitor.session_index,
                         self.dummy_session_index)
        self.assertEqual(10.3, self.validator_monitor.node._time_of_last_block)
        self.assertEqual(self.dummy_no_of_blocks_authored,
                         self.validator_monitor.node._no_of_blocks_authored)
        self.assertEqual(
            last_time_did_task, self.validator_monitor.node.
                blocks_authored_alert_limiter.last_time_that_did_task)
        self.assertFalse(self.validator_monitor.node.is_authoring)
        self.assertEqual(34.4, self.validator_monitor.node.
                         _time_of_last_block_check_activity)

    def test_check_for_new_session_sets_and_modifies_node_state_if_new_session(
            self) -> None:
        self.validator_monitor._session_index = self.dummy_session_index - 1
        self.validator_monitor.node.set_time_of_last_block(
            10.3, self.channel_set, self.logger)
        self.validator_monitor.node._no_of_blocks_authored = \
            self.dummy_no_of_blocks_authored
        last_time_did_task = \
            self.validator_monitor.node.blocks_authored_alert_limiter. \
                last_time_that_did_task
        self.validator_monitor.node.set_is_authoring(
            False, self.channel_set, self.logger)
        self.validator_monitor.node.set_time_of_last_block_check_activity(
            34.4, self.channel_set, self.logger)

        self.validator_monitor._check_for_new_session(self.dummy_session_index)

        self.assertEqual(self.validator_monitor.session_index,
                         self.dummy_session_index)
        self.assertEqual(NONE, self.validator_monitor.node._time_of_last_block)
        self.assertEqual(0, self.validator_monitor.node._no_of_blocks_authored)
        self.assertNotEqual(
            last_time_did_task, self.validator_monitor.node.
                blocks_authored_alert_limiter.last_time_that_did_task)
        self.assertTrue(self.validator_monitor.node.is_authoring)
        self.assertEqual(NONE, self.validator_monitor.node.
                         _time_of_last_block_check_activity)

    def test_check_for_new_session_does_nothing_if_same_session(
            self) -> None:
        self.validator_monitor._session_index = self.dummy_session_index
        self.validator_monitor.node.set_time_of_last_block(
            10.3, self.channel_set, self.logger)
        self.validator_monitor.node._no_of_blocks_authored = \
            self.dummy_no_of_blocks_authored
        last_time_did_task = \
            self.validator_monitor.node.blocks_authored_alert_limiter. \
                last_time_that_did_task
        self.validator_monitor.node.set_is_authoring(
            False, self.channel_set, self.logger)
        self.validator_monitor.node.set_time_of_last_block_check_activity(
            34.4, self.channel_set, self.logger)

        self.validator_monitor._check_for_new_session(self.dummy_session_index)

        self.assertEqual(self.validator_monitor.session_index,
                         self.dummy_session_index)
        self.assertEqual(10.3, self.validator_monitor.node._time_of_last_block)
        self.assertEqual(self.dummy_no_of_blocks_authored,
                         self.validator_monitor.node._no_of_blocks_authored)
        self.assertEqual(
            last_time_did_task, self.validator_monitor.node.
                blocks_authored_alert_limiter.last_time_that_did_task)
        self.assertFalse(self.validator_monitor.node.is_authoring)
        self.assertEqual(34.4, self.validator_monitor.node.
                         _time_of_last_block_check_activity)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_sets_API_up_when_validator_indirect_monitoring_succesfull(
            self, _1, _2, _3, _4, _5, _6, _7) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor.monitor_indirect()
            self.assertFalse(self.validator_monitor.data_wrapper.is_api_down)

    def test_monitor_indirect_full_node_sets_values_as_expected(self) -> None:
        self.full_node_monitor.monitor_indirect()

        self.assertEqual(self.full_node_monitor.session_index, NONE)
        self.assertEqual(self.full_node_monitor.node.bonded_balance, 0)
        self.assertFalse(self.full_node_monitor.node.is_active)
        self.assertFalse(self.full_node_monitor.node.is_disabled)
        self.assertFalse(self.full_node_monitor.node.is_elected)
        self.assertFalse(self.full_node_monitor.node.is_council_member)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_active_true_if_validator_stash_in_set(
            self, mock_session_val, _1, _2, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = [
                self.validator.stash_account_address, 'DHGBDG8dsgh']

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertTrue(self.validator_monitor.node.is_active)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_active_false_if_validator_stash_not_in_set(
            self, mock_session_val, _1, _2, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = ['DHGBDG8dsgh']

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertFalse(self.validator_monitor.node.is_active)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_auth_index_correctly_if_validator_active(
            self, mock_session_val, _1, _2, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = [
                'DHGBDG8dsgh', self.validator.stash_account_address,
                'HDGFBDB898ds8dfh']

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(self.validator.auth_index, 1)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_does_not_set_auth_index_if_validator_inactive(
            self, mock_session_val, _1, _2, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = ['DHGBDG8dsgh']

            self.validator.set_active(True, self.channel_set, self.logger)
            self.validator.set_auth_index(self.dummy_auth_index, self.logger)
            self.validator.set_active(False, self.channel_set, self.logger)

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(self.dummy_auth_index,
                             self.validator_monitor.node.auth_index)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION)
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_disabled_true_if_validator_in_disabled_list(
            self, mock_session_val, _1, _2, _3, _4, _5, mock_disabled_val) \
            -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = [
                'HDGFVBSHFD7sf', self.validator.stash_account_address,
                'DHSBFH8sdss']
            mock_disabled_val.return_value = [1, 2, 3, 454]

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertTrue(self.validator_monitor.node.is_disabled)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION)
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_disabled_false_if_validator_in_disabled_list(
            self, mock_session_val, _1, _2, _3, _4, _5, mock_disabled_val) \
            -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_session_val.return_value = [
                'HDGFVBSHFD7sf', self.validator.stash_account_address,
                'DHSBFH8sdss']
            mock_disabled_val.return_value = [2, 3, 454]

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertFalse(self.validator_monitor.node.is_disabled)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS)
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_sets_elected_true_if_validator_in_elected_list(
            self, _1, _2, _3, mock_elected, _5, _6, _7) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_elected.return_value = {
                'validators': [],
                'nextElected': [
                    'sdgdsgJSNFNJ', 'HDHGF8dgfh',
                    self.validator.stash_account_address],
            }
            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertTrue(self.validator_monitor.node.is_elected)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS)
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_sets_elected_false_if_validator_not_in_elected_list(
            self, _1, _2, _3, mock_elected, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_elected.return_value = {
                'validators': [],
                'nextElected': ['sdgdsgJSNFNJ', 'HDHGF8dgfh'],
            }
            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertFalse(self.validator_monitor.node.is_elected)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION)
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_sets_council_member_true_if_validator_in_council_list(
            self, _1, _2, mock_council_mem, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_council_mem.return_value = [
                'sdgdsgJSNFNJ', 'HDHGF8dgfh',
                self.validator.stash_account_address]

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertTrue(self.validator_monitor.node.is_council_member)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION)
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_sets_council_member_false_if_validator_not_in_council_list(
            self, _1, _2, mock_council_mem, _3, _4, _5, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_council_mem.return_value = ['sdgdsgJSNFNJ', 'HDHGF8dgfh']

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertFalse(self.validator_monitor.node.is_council_member)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_sets_validator_blocks_authored_to_retrieved_val_if_validator_active(
            self, mock_session_val, _2, _3, _4, _5, mock_authored_blocks,
            _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_authored_blocks.return_value = \
                self.dummy_no_of_blocks_authored
            mock_session_val.return_value = [
                self.validator.stash_account_address]

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(self.validator_monitor.node.no_of_blocks_authored,
                             self.dummy_no_of_blocks_authored)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION)
    def test_monitor_indirect_validator_does_not_set_validator_blocks_authored_if_validator_not_active(
            self, _1, _2, _3, _4, _5, mock_authored_blocks, _6) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            mock_authored_blocks.return_value = \
                self.dummy_no_of_blocks_authored

            self.validator_monitor._archive_alerts_disabled = True
            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(self.validator_monitor.node.no_of_blocks_authored,
                             0)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_calls_monitor_archive_if_not_disabled(
            self, _1, _2, _3, _4, _5, _6, _7) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.validator_monitor._monitor_archive_state = MagicMock()

            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(
                self.validator_monitor._monitor_archive_state.call_count, 1)

    @patch(GET_DISABLED_VALIDATORS_FUNCTION, return_value=[])
    @patch(GET_AUTHORED_BLOCKS_FUNCTION, return_value=0)
    @patch(GET_CURRENT_INDEX_FUNCTION, return_value=45)
    @patch(GET_DERIVE_STAKING_VALIDATORS, return_value={
        'validators': [],
        'nextElected': [],
    })
    @patch(GET_COUNCIL_MEMBERS_FUNCTION, return_value=[])
    @patch(GET_ERAS_STAKERS_FUNCTION,
           return_value={"total": 0, "own": 0, "others": []})
    @patch(GET_SESSION_VALIDATORS_FUNCTION, return_value=[])
    def test_monitor_indirect_validator_does_not_call_monitor_archive_if_disabled(
            self, _1, _2, _3, _4, _5, _6, _7) -> None:
        with mock.patch(DATA_SOURCE_INDIRECT_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.validator_monitor._monitor_archive_state = MagicMock()
            self.validator_monitor._archive_alerts_disabled = True

            self.validator_monitor._monitor_indirect_validator()
            self.assertEqual(
                self.validator_monitor._monitor_archive_state.call_count, 0)

    # In the following tests, last_height_checked = LHC,
    # height_to_check = LHTC

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_state_0_calls_to_check_for_slashing_if_HTC_less_than_LHC(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.dummy_full_node_1.update_finalized_block_height(
                self.dummy_finalized_block_height, self.logger,
                self.channel_set)
            self.validator_monitor._last_height_checked = \
                self.dummy_finalized_block_height
            self.validator_monitor._check_for_slashing = MagicMock(
                side_effect=self.validator_monitor._check_for_slashing)

            self.validator_monitor._monitor_archive_state()
            self.assertEqual(
                self.validator_monitor._check_for_slashing.call_count, 0)
            self.assertEqual(self.validator_monitor.last_height_checked,
                             self.dummy_finalized_block_height)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_calls_check_for_slashing_once_if_monitor_is_catching_up(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1

            # To make the monitor catch up
            archive_node_height = self.dummy_finalized_block_height + 600

            self.dummy_full_node_1.update_finalized_block_height(
                archive_node_height, self.logger, self.channel_set)
            self.validator_monitor._last_height_checked = \
                self.dummy_finalized_block_height
            self.validator_monitor._check_for_slashing = MagicMock(
                side_effect=self.validator_monitor._check_for_slashing)

            self.validator_monitor._monitor_archive_state()
            self.assertEqual(
                self.validator_monitor._check_for_slashing.call_count, 1)
            self.assertEqual(self.validator_monitor.last_height_checked, 34635)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_calls_check_for_slashing_once_if_monitor_is_not_catching_up(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.dummy_full_node_1.update_finalized_block_height(
                self.dummy_finalized_block_height, self.logger,
                self.channel_set)
            self.validator_monitor._check_for_slashing = MagicMock(
                side_effect=self.validator_monitor._check_for_slashing)

            self.validator_monitor._monitor_archive_state()
            self.assertEqual(
                self.validator_monitor._check_for_slashing.call_count, 1)
            self.assertEqual(self.validator_monitor.last_height_checked,
                             self.dummy_finalized_block_height)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_sets_catching_up_true_if_more_than_2_blocks_late(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1

            # To make the monitor catch up
            archive_node_height = self.dummy_finalized_block_height + 4

            self.dummy_full_node_1.update_finalized_block_height(
                archive_node_height, self.logger, self.channel_set)
            self.validator_monitor._last_height_checked = \
                self.dummy_finalized_block_height
            self.validator_monitor._monitor_archive_state()

            self.assertTrue(self.validator_monitor._monitor_is_catching_up)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_sets_catching_up_false_if_less_than_2_blocks_late(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.dummy_full_node_1.update_finalized_block_height(
                self.dummy_finalized_block_height, self.logger,
                self.channel_set)
            self.validator_monitor._monitor_archive_state()

            self.assertFalse(self.validator_monitor._monitor_is_catching_up)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_sets_catching_up_false_if_2_blocks_late(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1
            self.dummy_full_node_1.update_finalized_block_height(
                self.dummy_finalized_block_height, self.logger,
                self.channel_set)
            self.validator_monitor._last_height_checked = \
                self.dummy_finalized_block_height - 3
            self.validator_monitor._monitor_archive_state()

            self.assertFalse(self.validator_monitor._monitor_is_catching_up)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_raises_info_alert_if_monitoring_round_successful_and_error_alert_sent(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1

            self.validator_monitor._no_live_archive_node_alert_sent = True
            self.validator_monitor._monitor_archive_state()

            self.assertEqual(self.counter_channel.info_count, 1)
            self.assertFalse(
                self.validator_monitor._no_live_archive_node_alert_sent)
            self.assertIsInstance(self.counter_channel.latest_alert,
                                  FoundLiveArchiveNodeAgainAlert)

    @patch(GET_SLASH_AMOUNT_FUNCITON, return_value=0)
    @patch(GET_BLOCK_HASH_FUNCTION, return_value=None)
    def test_monitor_archive_no_alerts_if_monitoring_round_successful_error_alert_not_sent_previously(
            self, _1, _2) -> None:
        with mock.patch(DATA_SOURCE_ARCHIVE_PATH, new_callable=PropertyMock) \
                as mock_data_source_indirect:
            mock_data_source_indirect.return_value = self.dummy_full_node_1

            self.validator_monitor._monitor_archive_state()

            self.assertTrue(self.counter_channel.no_alerts())
            self.assertFalse(
                self.validator_monitor._no_live_archive_node_alert_sent)


class TestNodeMonitorWithRedis(unittest.TestCase):
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
        self.monitor_name = 'testnodemonitor'
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

        self.node_monitor_max_catch_up_blocks = \
            TestInternalConf.node_monitor_max_catch_up_blocks
        self.node = None
        self.archive_alerts_disabled = False
        self.data_sources = []
        self.polkadot_api_endpoint = 'api_endpoint'
        self.monitor = NodeMonitor(
            self.monitor_name, self.channel_set, self.logger,
            self.node_monitor_max_catch_up_blocks, self.redis, self.node,
            self.archive_alerts_disabled, self.data_sources,
            self.polkadot_api_endpoint, TestInternalConf)

        self.dummy_session_index = 60
        self.dummy_last_height_checked = 1000

        self.redis_alive_key_timeout = \
            TestInternalConf.redis_node_monitor_alive_key_timeout

    def test_load_state_changes_nothing_if_nothing_saved(self) -> None:
        self.monitor.load_state()

        self.assertEqual(NONE, self.monitor._session_index)
        self.assertEqual(NONE, self.monitor._last_height_checked)

    def test_load_state_sets_values_to_saved_values(self) -> None:
        # Set Redis values manually
        key_si = Keys.get_node_monitor_session_index(self.monitor_name)
        key_lh = Keys.get_node_monitor_last_height_checked(self.monitor_name)
        self.redis.set_unsafe(key_si, self.dummy_session_index)
        self.redis.set_unsafe(key_lh, self.dummy_last_height_checked)

        # Load the values from Redis
        self.monitor.load_state()

        # Assert
        self.assertEqual(self.dummy_session_index, self.monitor.session_index)
        self.assertEqual(self.dummy_last_height_checked,
                         self.monitor.last_height_checked)

    def test_save_state_sets_values_to_current_values_and_stores_alive_key_temp(
            self) -> None:
        # Set monitor values manually
        self.monitor._session_index = self.dummy_session_index
        self.monitor._last_height_checked = self.dummy_last_height_checked

        # Save the values to Redis
        self.monitor.save_state()

        key_si = Keys.get_node_monitor_session_index(self.monitor_name)
        key_lh = Keys.get_node_monitor_last_height_checked(self.monitor_name)

        # Get last update, and its timeout in Redis
        last_update = self.redis.get(key_lh)
        timeout = self.redis.time_to_live(key_lh)

        # Assert
        self.assertEqual(self.dummy_session_index, self.redis.get_int(key_si))
        self.assertEqual(self.dummy_last_height_checked,
                         self.redis.get_int(key_lh))
        self.assertIsNotNone(last_update)
        self.assertEqual(timeout, self.redis_alive_key_timeout)
