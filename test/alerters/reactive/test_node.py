import logging
import unittest
from datetime import timedelta
from time import sleep

from redis import ConnectionError as RedisConnectionError

from src.alerters.reactive.node import Node, NodeType
from src.alerts.alerts import *
from src.channels.channel import ChannelSet
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from src.utils.scaling import scale_to_tera
from src.utils.types import NONE
from test import TestInternalConf, TestUserConf
from test.test_helpers import CounterChannel, DummyException


class TestNodeWithoutRedis(unittest.TestCase):
    ERROR_MARGIN = timedelta(seconds=1)

    def setUp(self) -> None:
        self.node_name = 'testnode'
        self.logger = logging.getLogger('dummy')

        self.downtime_alert_time_interval = \
            TestInternalConf.downtime_alert_time_interval
        self.downtime_alert_time_interval_with_error_margin = \
            self.downtime_alert_time_interval + self.ERROR_MARGIN

        self.max_time_alert_between_blocks_authored = \
            TestInternalConf.max_time_alert_between_blocks_authored
        self.max_time_alert_between_blocks_authored_with_error = \
            self.max_time_alert_between_blocks_authored + self.ERROR_MARGIN

        self.no_change_in_height_interval_seconds = \
            timedelta(seconds=int(
                TestInternalConf.no_change_in_height_interval_seconds))
        self.no_change_in_height_interval_seconds_with_error = \
            self.no_change_in_height_interval_seconds + self.ERROR_MARGIN

        self.no_change_in_height_first_warning_seconds = \
            timedelta(seconds=int(
                TestInternalConf.no_change_in_height_first_warning_seconds))
        self.no_change_in_height_first_warning_seconds_with_error = \
            self.no_change_in_height_first_warning_seconds + self.ERROR_MARGIN

        self.bonded_balance_threshold = \
            scale_to_tera(TestInternalConf.change_in_bonded_balance_threshold)

        self.validator_peer_danger_boundary = \
            TestInternalConf.validator_peer_danger_boundary
        self.validator_peer_safe_boundary = \
            TestInternalConf.validator_peer_safe_boundary
        self.full_node_peer_danger_boundary = \
            TestInternalConf.full_node_peer_danger_boundary

        self.full_node = Node(name=self.node_name, ws_url=None,
                              node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                              stash_account_address='', chain='', redis=None,
                              is_archive_node=True,
                              internal_conf=TestInternalConf)

        self.validator = Node(name=self.node_name, ws_url=None,
                              node_type=NodeType.VALIDATOR_FULL_NODE,
                              stash_account_address='', chain='', redis=None,
                              is_archive_node=True,
                              internal_conf=TestInternalConf)

        self.counter_channel = CounterChannel(self.logger)
        self.channel_set = ChannelSet([self.counter_channel], TestInternalConf)

        self.dummy_exception = DummyException()
        self.dummy_bonded_balance = scale_to_tera(5)
        self.dummy_no_of_peers = 100
        self.dummy_active = True
        self.dummy_council_member = True
        self.dummy_elected = True
        self.dummy_disabled = True
        self.dummy_no_of_blocks_authored = 10
        self.dummy_finalized_block_height = 34535
        self.dummy_session_index = 200
        self.dummy_era_index = 50
        self.dummy_auth_index = 10
        self.dummy_slash_amount = 45.4

        self.full_node_no_of_peers_less_than_danger_boundary = \
            self.full_node_peer_danger_boundary - 2
        self.full_node_no_of_peers_greater_than_danger_boundary = \
            self.full_node_peer_danger_boundary + 2
        self.validator_no_of_peers_less_than_danger_boundary = \
            self.validator_peer_danger_boundary - 2
        self.validator_no_of_peers_greater_than_danger_boundary = \
            self.validator_peer_danger_boundary + 2
        self.validator_no_of_peers_less_than_safe_boundary = \
            self.validator_peer_safe_boundary - 2
        self.validator_no_of_peers_greater_than_safe_boundary = \
            self.validator_peer_safe_boundary + 2

    def test_str_returns_name_of_node(self) -> None:
        self.assertEqual(str(self.validator), self.node_name)

    def test_is_validator_true_if_is_validator(self) -> None:
        self.assertTrue(self.validator.is_validator)

    def test_is_validator_false_if_not_validator(self) -> None:
        self.assertFalse(self.full_node.is_validator)

    def test_is_down_false_by_default(self) -> None:
        self.assertFalse(self.validator.is_down)

    def test_is_down_true_when_went_down_not_none(self) -> None:
        self.validator._went_down_at = datetime.now().timestamp()
        self.assertTrue(self.validator.is_down)

    def test_is_active_none_by_default(self) -> None:
        self.assertIsNone(self.validator.is_active)

    def test_is_elected_none_by_default(self) -> None:
        self.assertIsNone(self.validator.is_elected)

    def test_is_disabled_none_by_default(self) -> None:
        self.assertIsNone(self.validator.is_disabled)

    def test_is_syncing_false_by_default(self) -> None:
        self.assertFalse(self.validator.is_syncing)

    def test_is_council_member_none_by_default(self) -> None:
        self.assertIsNone(self.validator.is_council_member)

    def test_bonded_balance_none_by_default(self) -> None:
        self.assertIsNone(self.validator.bonded_balance)

    def test_number_of_peers_none_by_default(self) -> None:
        self.assertIsNone(self.validator.no_of_peers)

    def test_number_of_blocks_authored_zero_by_default(self) -> None:
        self.assertEqual(self.validator.no_of_blocks_authored, 0)

    def test_auth_index_NONE_by_default(self) -> None:
        self.assertEqual(self.validator.auth_index, NONE)

    def test_is_authoring_true_by_default(self) -> None:
        self.assertTrue(self.validator.is_authoring)

    def test_is_no_change_in_height_warning_sent_false_by_default(self) -> None:
        self.assertFalse(self.validator.is_no_change_in_height_warning_sent)

    def test_finalized_block_height_zero_by_default(self) -> None:
        self.assertEqual(self.validator.finalized_block_height, 0)

    def test_is_connected_to_api_server_true_by_default(self) -> None:
        self.assertTrue(self.validator.is_connected_to_api_server)
        self.assertTrue(self.full_node.is_connected_to_api_server)

    def test_status_returns_as_expected(self) -> None:
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

        self.assertEqual(
            self.validator.status(), "bonded_balance={}, is_syncing=False, "
                                     "no_of_peers={}, active={}, "
                                     "council_member={}, elected={}, "
                                     "disabled={}, "
                                     "no_of_blocks_authored={}, "
                                     "finalized_block_height={}".format(
                self.dummy_bonded_balance, self.dummy_no_of_peers,
                self.dummy_active, self.dummy_council_member,
                self.dummy_elected, self.dummy_disabled,
                self.dummy_no_of_blocks_authored,
                self.dummy_finalized_block_height))

    def test_first_set_as_down_sends_info_experiencing_delays_alert_and_sets_node_as_down(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertFalse(self.validator._initial_downtime_alert_sent)
        self.assertTrue(self.validator.is_down)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ExperiencingDelaysAlert)

    def test_second_set_as_down_sends_critical_cannot_access_node_alert_if_validator(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_as_down(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertTrue(self.validator.is_down)
        self.assertTrue(self.validator._initial_downtime_alert_sent)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              CannotAccessNodeAlert)

    def test_second_set_as_down_sends_warning_cannot_access_node_alert_if_non_validator(
            self) -> None:
        self.full_node.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_as_down(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertTrue(self.full_node._initial_downtime_alert_sent)
        self.assertTrue(self.full_node.is_down)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              CannotAccessNodeAlert)

    def test_third_set_as_down_does_nothing_if_within_time_interval_for_validator(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.validator.set_as_down(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(self.validator.is_down)

    def test_third_set_as_down_does_nothing_if_within_time_interval_for_non_validator(
            self) -> None:
        self.full_node.set_as_down(self.channel_set, self.logger)
        self.full_node.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        self.full_node.set_as_down(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertTrue(self.full_node.is_down)

    def test_third_set_as_down_sends_critical_alert_if_after_time_interval_for_validator(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        sleep(self.downtime_alert_time_interval_with_error_margin.seconds)
        self.validator.set_as_down(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertTrue(self.validator.is_down)
        self.assertTrue(self.validator._initial_downtime_alert_sent)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              StillCannotAccessNodeAlert)

    def test_third_set_as_down_sends_warning_alert_if_after_time_interval_for_non_validator(
            self) -> None:
        self.full_node.set_as_down(self.channel_set, self.logger)
        self.full_node.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts
        sleep(self.downtime_alert_time_interval_with_error_margin.seconds)
        self.full_node.set_as_down(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertTrue(self.full_node.is_down)
        self.assertTrue(self.full_node._initial_downtime_alert_sent)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              StillCannotAccessNodeAlert)

    def test_set_as_up_does_nothing_if_not_down(self) -> None:
        self.validator.set_as_up(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertFalse(self.validator.is_down)

    def test_set_as_up_sets_as_up_but_no_alerts_if_set_as_down_called_only_once(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_up(self.channel_set, self.logger)
        self.assertTrue(self.counter_channel.no_alerts())
        self.assertFalse(self.validator.is_down)

    def test_set_as_up_sets_as_up_and_sends_info_alert_if_set_as_down_called_twice(
            self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_up(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertFalse(self.validator.is_down)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NowAccessibleAlert)

    def test_set_as_up_resets_alert_time_interval(self) -> None:
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_down(self.channel_set, self.logger)
        self.validator.set_as_up(self.channel_set, self.logger)

        self.counter_channel.reset()  # ignore previous alerts

        self.validator.set_as_down(self.channel_set, self.logger)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertTrue(self.validator.is_down)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ExperiencingDelaysAlert)

    # Without the set_as_up, the set_as_down does not produce an alert

    def test_set_bonded_balance_raises_no_alerts_first_time_round(self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         self.dummy_bonded_balance)

    def test_set_bonded_balance_raises_no_alerts_if_bonded_balance_the_same(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         self.dummy_bonded_balance)

    def test_set_balance_no_alerts_if_difference_is_negative_below_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance - \
                             self.bonded_balance_threshold + 1
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         new_bonded_balance)

    def test_set_balance_no_alerts_if_difference_is_positive_below_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance + \
                             self.bonded_balance_threshold - 1
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         new_bonded_balance)

    def test_set_balance_no_alerts_if_difference_is_negative_and_equal_to_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance - \
                             self.bonded_balance_threshold
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         new_bonded_balance)

    def test_set_balance_no_alerts_if_difference_is_positive_and_equal_to_threshold_and_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance + \
                             self.bonded_balance_threshold
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.bonded_balance,
                         new_bonded_balance)

    def test_set_balance_raises_info_alert_if_difference_is_positive_above_threshold_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance + \
                             self.bonded_balance_threshold + 1
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              BondedBalanceIncreasedByAlert)
        self.assertEqual(self.validator.bonded_balance,
                         new_bonded_balance)

    def test_set_balance_raises_info_alert_if_difference_is_negative_above_threshold_no_balance_is_0(
            self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        new_bonded_balance = self.dummy_bonded_balance - \
                             self.bonded_balance_threshold - 1
        self.validator.set_bonded_balance(new_bonded_balance, self.channel_set,
                                          self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              BondedBalanceDecreasedByAlert)
        self.assertEqual(self.validator.bonded_balance, new_bonded_balance)

    def test_set_balance_raises_critical_alert_if_new_balance_0(self) -> None:
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)
        self.validator.set_bonded_balance(0, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              BondedBalanceDecreasedAlert)
        self.assertEqual(self.validator.bonded_balance, 0)

    def test_set_balance_info_alert_if_new_balance_non_0_from_0(self) -> None:
        self.validator.set_bonded_balance(0, self.channel_set, self.logger)
        self.validator.set_bonded_balance(self.dummy_bonded_balance,
                                          self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              BondedBalanceIncreasedAlert)
        self.assertEqual(self.validator.bonded_balance,
                         self.dummy_bonded_balance)

    def test_is_syncing_raises_warning_is_syncing_alert_first_time_round_if_now_is_syncing(
            self) -> None:
        self.validator.set_is_syncing(True, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert, IsSyncingAlert)
        self.assertEqual(self.validator.is_syncing, True)

    def test_is_syncing_raises_no_alerts_first_time_round_if_now_not_syncing(
            self) -> None:
        self.validator.set_is_syncing(False, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.is_syncing, False)

    def test_is_syncing_raises_no_alerts_from_true_to_true(self) -> None:
        self.validator.set_is_syncing(True, self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.set_is_syncing(True, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.is_syncing, True)

    # The case false to false was handled in test
    # `test_is_syncing_raises_no_alerts_first_time_round_if_now_not_syncing`

    def test_is_syncing_raises_info_is_no_longer_syncing_alert_from_true_to_false(
            self) -> None:
        self.validator.set_is_syncing(True, self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.set_is_syncing(False, self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              IsNoLongerSyncingAlert)
        self.assertEqual(self.validator.is_syncing, False)

    # The case false to true was handled in test
    # `test_is_syncing_raises_warning_is_syncing_alert_first_time_round_if_now_is_syncing`

    def test_set_no_of_peers_sets_and_raises_no_alerts_first_time_round_for_validator(
            self) -> None:
        self.validator.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.no_of_peers, self.dummy_no_of_peers)

    def test_set_no_of_peers_sets_and_raises_no_alerts_first_time_round_for_full_node(
            self) -> None:
        self.full_node.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.full_node.no_of_peers, self.dummy_no_of_peers)

    def test_set_no_of_peers_raises_no_alerts_if_no_peer_change_for_validators(
            self) -> None:
        self.validator.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)
        self.validator.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_peers_raises_no_alerts_if_no_peer_change_for_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)
        self.full_node.set_no_of_peers(self.dummy_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_peers_sets_and_raises_no_alerts_if_decrease_outside_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_greater_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_greater_than_danger_boundary - 1
        self.full_node.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_equal_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_greater_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_greater_than_danger_boundary - 2
        self.full_node.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_from_outside_to_inside_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_greater_than_danger_boundary,
            self.channel_set, self.logger)
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.full_node.no_of_peers,
                         self.full_node_no_of_peers_less_than_danger_boundary)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_inside_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_less_than_danger_boundary - 1
        self.full_node.set_no_of_peers(new_no_of_peers,
                                       self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_less_than_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_less_than_danger_boundary + 1
        self.full_node.set_no_of_peers(new_no_of_peers,
                                       self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_equal_to_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_less_than_danger_boundary + 2
        self.full_node.set_no_of_peers(new_no_of_peers,
                                       self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_from_inside_to_outside_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_greater_than_danger_boundary
        self.full_node.set_no_of_peers(new_no_of_peers,
                                       self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedOutsideDangerRangeAlert)
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_no_alerts_if_increase_from_outside_to_outside_danger_full_nodes(
            self) -> None:
        self.full_node.set_no_of_peers(
            self.full_node_no_of_peers_greater_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.full_node_no_of_peers_greater_than_danger_boundary + 1
        self.full_node.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.full_node.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_no_alerts_if_increase_from_outside_to_outside_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_greater_than_safe_boundary + 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_no_alerts_if_decrease_outside_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_greater_than_safe_boundary - 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertTrue(self.counter_channel.no_alerts())
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_equal_to_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_greater_than_safe_boundary - 2
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_from_outisde_safe_to_safe_outside_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_greater_than_safe_boundary - 3
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_warning_alert_if_decrease_inside_safe_outside_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_less_than_safe_boundary - 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_critical_alert_if_decrease_from_outside_safe_to_equal_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_peer_danger_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_critical_alert_if_decrease_from_outside_safe_inside_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_greater_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_no_of_peers_less_than_danger_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_critical_alert_if_decrease_from_safe_to_equal_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_peer_danger_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_critical_alert_if_decrease_from_safe_to_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_peer_danger_boundary - 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_critical_alert_if_decrease_inside_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_less_than_danger_boundary - 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersDecreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_inside_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = \
            self.validator_no_of_peers_less_than_danger_boundary + 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_equal_danger_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_peer_danger_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_danger_to_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_no_of_peers_less_than_safe_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_danger_to_outside_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_danger_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_no_of_peers_greater_than_safe_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedOutsideSafeRangeAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_inside_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_no_of_peers_less_than_safe_boundary + 1
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_safe_to_equal_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_peer_safe_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_peers_sets_and_raises_info_alert_if_increase_safe_to_outside_safe_validator(
            self) -> None:
        self.validator.set_no_of_peers(
            self.validator_no_of_peers_less_than_safe_boundary,
            self.channel_set, self.logger)
        new_no_of_peers = self.validator_no_of_peers_greater_than_safe_boundary
        self.validator.set_no_of_peers(new_no_of_peers, self.channel_set,
                                       self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              PeersIncreasedOutsideSafeRangeAlert)
        self.assertEqual(self.validator.no_of_peers, new_no_of_peers)

    def test_set_active_no_alerts_first_time_round_and_sets_active_true_if_now_active(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_active)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_active_no_alerts_if_active_and_now_active_and_sets_active_true(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_active(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_active)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_active_raises_info_alert_if_inactive_and_now_active_and_sets_active_true(
            self) \
            -> None:
        self.validator.set_active(False, self.channel_set, self.logger)
        self.validator.set_active(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_active)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNowActiveAlert)

    def test_set_active_no_alerts_first_time_round_if_now_inactive_and_sets_active_false(
            self) -> None:
        self.validator.set_active(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_active)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_active_no_alerts_if_inactive_and_still_inactive_and_sets_active_false(
            self) -> None:
        self.validator.set_active(False, self.channel_set, self.logger)
        self.validator.set_active(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_active)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_active_raises_critical_alert_if_active_and_now_not_active_and_sets_active_false(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_active(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_active)
        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNotActiveAlert)

    def test_set_elected_no_alerts_first_time_round_and_set_elected_true_if_now_elected(
            self) -> None:
        self.validator.set_elected(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_elected)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_elected_no_alerts_if_elected_and_still_elected_and_sets_elected_true(
            self) -> None:
        self.validator.set_elected(True, self.channel_set, self.logger)
        self.validator.set_elected(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_elected)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_elected_raises_info_alert_if_not_elected_and_now_elected_and_sets_elected_true(
            self) -> None:
        self.validator.set_elected(False, self.channel_set, self.logger)
        self.validator.set_elected(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_elected)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsElectedForTheNextSessionAlert)

    def test_set_elected_no_alerts_first_time_round_and_sets_elected_false_if_now_not_elected(
            self) -> None:
        self.validator.set_elected(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_elected)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_elected_no_alerts_if_not_elected_and_still_not_elected_and_sets_elected_false(
            self) -> None:
        self.validator.set_elected(False, self.channel_set, self.logger)
        self.validator.set_elected(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_elected)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_elected_raises_warning_alert_if_elected_and_now_not_elected_and_sets_elected_to_false(
            self) -> None:
        self.validator.set_elected(True, self.channel_set, self.logger)
        self.validator.set_elected(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_elected)
        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNotElectedForNextSessionAlert)

    def test_set_council_member_no_alerts_first_time_round_if_now_member_and_sets_to_true(
            self) -> None:
        self.validator.set_council_member(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_council_member)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_council_member_no_alerts_if_member_and_now_is_member_and_remains_set(
            self) -> None:
        self.validator.set_council_member(True, self.channel_set, self.logger)
        self.validator.set_council_member(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_council_member)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_council_member_raises_info_alert_if_not_member_and_now_member_and_sets_to_true(
            self) -> None:
        self.validator.set_council_member(False, self.channel_set, self.logger)
        self.validator.set_council_member(True, self.channel_set, self.logger)

        self.assertTrue(self.validator.is_council_member)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNowPartOfTheCouncilAlert)

    def test_set_council_member_no_alerts_first_time_round_and_unsets_if_now_not_member(
            self) -> None:
        self.validator.set_council_member(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_council_member)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_council_member_no_alerts_if_not_member_and_remains_not_member(
            self) -> None:
        self.validator.set_council_member(False, self.channel_set,
                                          self.logger)
        self.validator.set_council_member(False, self.channel_set,
                                          self.logger)

        self.assertFalse(self.validator.is_council_member)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_council_member_raises_info_alert_if_member_and_now_not_member_and_unsets(
            self) -> None:
        self.validator.set_council_member(True, self.channel_set, self.logger)
        self.validator.set_council_member(False, self.channel_set, self.logger)

        self.assertFalse(self.validator.is_council_member)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNoLongerPartOfTheCouncilAlert)

    def test_set_no_of_blocks_authored_raises_no_alerts_if_validator_deactivated(
            self) -> None:
        self.validator.set_active(False, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_does_not_alter_state_if_validator_deactivated(
            self) -> None:
        self.validator.set_active(False, self.channel_set, self.logger)

        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity
        old_is_authoring = self.validator.is_authoring

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored, 0)
        self.assertEqual(old_last_time_did_task,
                         self.validator.blocks_authored_alert_limiter.
                         last_time_that_did_task)
        self.assertEqual(old_time_of_last_block,
                         self.validator._time_of_last_block)
        self.assertEqual(old_time_of_last_block_check_activity,
                         self.validator._time_of_last_block_check_activity)
        self.assertEqual(old_is_authoring, self.validator._is_authoring)

    # The tests for set_no_of_blocks below assume that the validator is active

    def test_set_no_of_blocks_authored_raises_no_alerts_if_blocks_decreased(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored - 1
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_does_not_reset_state_if_blocks_decreased(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored - 1

        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity
        old_is_authoring = self.validator.is_authoring

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored,
                         self.dummy_no_of_blocks_authored)
        self.assertEqual(old_last_time_did_task,
                         self.validator.blocks_authored_alert_limiter.
                         last_time_that_did_task)
        self.assertEqual(old_time_of_last_block,
                         self.validator._time_of_last_block)
        self.assertEqual(old_time_of_last_block_check_activity,
                         self.validator._time_of_last_block_check_activity)
        self.assertEqual(old_is_authoring, self.validator._is_authoring)

    def test_set_no_of_blocks_authored_raises_info_alert_if_new_block_and_no_blocks_authored_alert_already_sent(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.blocks_authored_alert_limiter.did_task()
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)
        self.validator.set_no_of_blocks_authored(self.channel_set, self.logger,
                                                 0, self.dummy_era_index)
        self.counter_channel.reset()

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ANewBlockHasNowBeenAuthoredByValidatorAlert)

    def test_set_no_of_blocks_authored_raises_info_alert_if_new_block_and_interval_since_last_block_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        self.counter_channel.reset()

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored + 1
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ANewBlockHasNowBeenAuthoredByValidatorAlert)

    def test_set_no_of_blocks_authored_raises_no_alerts_if_new_block_and_interval_since_last_block_not_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored + 1
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_raises_no_alerts_if_new_block_and_no_blocks_authored_and_time_not_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.blocks_authored_alert_limiter.did_task()

        new_number_of_blocks_authored = self.dummy_no_of_blocks_authored
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_number_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_modifies_blocks_authored_state_on_new_block(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored,
                         self.dummy_no_of_blocks_authored)
        self.assertNotEqual(
            old_last_time_did_task, self.validator.
                blocks_authored_alert_limiter.last_time_that_did_task)
        self.assertNotEqual(old_time_of_last_block,
                            self.validator._time_of_last_block)
        self.assertNotEqual(old_time_of_last_block_check_activity,
                            self.validator._time_of_last_block_check_activity)

    def test_set_no_of_blocks_authored_sets_is_authoring_on_new_block_if_time_interval_alert_sent(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        self.counter_channel.reset()

        self.assertFalse(self.validator._is_authoring)
        new_no_of_blocks_authored = self.dummy_no_of_blocks_authored + 1
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_no_of_blocks_authored,
            self.dummy_era_index)
        self.assertTrue(self.validator._is_authoring)

    def test_set_no_of_blocks_authored_sets_is_authoring_on_new_block_if_no_blocks_alert_sent(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.blocks_authored_alert_limiter.did_task()

        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        self.validator.set_no_of_blocks_authored(self.channel_set, self.logger,
                                                 0, self.dummy_era_index)
        self.counter_channel.reset()

        self.assertFalse(self.validator._is_authoring)
        new_no_of_blocks_authored = self.dummy_no_of_blocks_authored + 1
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, new_no_of_blocks_authored,
            self.dummy_era_index)
        self.assertTrue(self.validator._is_authoring)

    def test_set_no_of_blocks_authored_raises_no_alerts_if_no_change_and_time_not_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_does_not_alter_state_if_no_change_and_time_not_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored,
                         self.dummy_no_of_blocks_authored)
        self.assertEqual(old_last_time_did_task,
                         self.validator.blocks_authored_alert_limiter.
                         last_time_that_did_task)
        self.assertEqual(old_time_of_last_block,
                         self.validator._time_of_last_block)
        self.assertEqual(old_time_of_last_block_check_activity,
                         self.validator._time_of_last_block_check_activity)

    def test_set_no_of_blocks_authored_raises_warning_alert_if_no_blocks_authored_and_time_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.blocks_authored_alert_limiter.did_task()
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        self.validator.set_no_of_blocks_authored(self.channel_set, self.logger,
                                                 0, self.dummy_era_index)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NoBlocksHaveYetBeenAuthoredInEraAlert)

    def test_set_no_of_blocks_authored_raises_warning_alert_if_blocks_authored_and_time_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              LastAuthoredBlockInEraAlert)

    def test_set_no_of_blocks_authored_resets_state_if_blocks_authored_and_time_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored,
                         self.dummy_no_of_blocks_authored)
        self.assertNotEqual(old_last_time_did_task,
                            self.validator.blocks_authored_alert_limiter.
                            last_time_that_did_task)
        self.assertEqual(old_time_of_last_block,
                         self.validator._time_of_last_block)
        self.assertNotEqual(old_time_of_last_block_check_activity,
                            self.validator._time_of_last_block_check_activity)
        self.assertFalse(self.validator._is_authoring)

    def test_set_no_of_blocks_authored_resets_state_if_no_blocks_authored_and_time_passed(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.blocks_authored_alert_limiter.did_task()
        sleep(self.max_time_alert_between_blocks_authored_with_error.seconds)

        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity
        self.validator.set_no_of_blocks_authored(self.channel_set, self.logger,
                                                 0, self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored, 0)
        self.assertNotEqual(old_last_time_did_task,
                            self.validator.blocks_authored_alert_limiter.
                            last_time_that_did_task)
        self.assertEqual(old_time_of_last_block,
                         self.validator._time_of_last_block)
        self.assertNotEqual(old_time_of_last_block_check_activity,
                            self.validator._time_of_last_block_check_activity)
        self.assertFalse(self.validator._is_authoring)

    def test_set_no_of_blocks_authored_raises_no_alerts_first_time_round(self) \
            -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_no_of_blocks_authored_modifies_state_first_time_round(
            self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)

        old_time_of_last_block = self.validator._time_of_last_block
        old_last_time_did_task = self.validator.blocks_authored_alert_limiter. \
            last_time_that_did_task
        old_time_of_last_block_check_activity = \
            self.validator._time_of_last_block_check_activity
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)

        self.assertEqual(self.validator.no_of_blocks_authored,
                         self.dummy_no_of_blocks_authored)
        self.assertNotEqual(old_last_time_did_task,
                            self.validator.blocks_authored_alert_limiter.
                            last_time_that_did_task)
        self.assertNotEqual(old_time_of_last_block,
                            self.validator._time_of_last_block)
        self.assertNotEqual(old_time_of_last_block_check_activity,
                            self.validator._time_of_last_block_check_activity)
        self.assertTrue(self.validator._is_authoring)

    def test_reset_no_of_blocks_authored_resets_no_of_blocks_to_0(self) -> None:
        self.validator.set_no_of_blocks_authored(
            self.channel_set, self.logger, self.dummy_no_of_blocks_authored,
            self.dummy_era_index)
        self.validator.reset_no_of_blocks_authored(self.channel_set,
                                                   self.logger)

        self.assertEqual(self.validator.no_of_blocks_authored, 0)

    def test_set_auth_index_does_not_set_if_validator_not_active(self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_auth_index(self.dummy_auth_index, self.logger)

        self.validator.set_active(False, self.channel_set, self.logger)
        new_auth_index = self.dummy_auth_index + 1
        self.validator.set_auth_index(new_auth_index, self.logger)

        self.assertEqual(self.validator.auth_index, self.dummy_auth_index)

    def test_set_auth_index_sets_if_validator_is_active(self) -> None:
        self.validator.set_active(True, self.channel_set, self.logger)
        self.validator.set_auth_index(self.dummy_auth_index, self.logger)

        self.assertEqual(self.validator.auth_index, self.dummy_auth_index)

    def test_update_height_no_alerts_if_increase_and_first_warning_not_sent(
            self) -> None:
        self.validator._finalized_block_height = \
            self.dummy_finalized_block_height
        new_height = self.dummy_finalized_block_height + 1

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_update_height_no_alerts_if_decrease_and_first_warning_not_sent(
            self) -> None:
        self.validator._finalized_block_height = \
            self.dummy_finalized_block_height
        new_height = self.dummy_finalized_block_height - 1

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_update_height_info_alert_if_increase_and_warning_sent(self) \
            -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        new_height = self.dummy_finalized_block_height + 1

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeFinalizedBlockHeightHasNowBeenUpdatedAlert)

    def test_update_height_info_alert_if_increase_and_both_warning_interval_alert_sent(
            self) -> None:
        # Initialize the limiters
        self.validator.finalized_height_alert_limiter.did_task()

        sleep(self.no_change_in_height_interval_seconds_with_error.seconds)

        # Sends first warning alert.
        self.validator.update_finalized_block_height(0, self.logger,
                                                     self.channel_set)
        self.counter_channel.reset()

        # Sends interval alert
        self.validator.update_finalized_block_height(0, self.logger,
                                                     self.channel_set)
        self.counter_channel.reset()

        new_height = self.dummy_finalized_block_height

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeFinalizedBlockHeightHasNowBeenUpdatedAlert)

    def test_update_height_unsets_warning_sent_if_height_increase(self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        new_height = self.dummy_finalized_block_height + 1

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)
        self.assertFalse(self.validator._no_change_in_height_warning_sent)

    def test_update_height_unsets_warning_sent_if_height_decrease(self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        new_height = self.dummy_finalized_block_height - 1

        self.validator.update_finalized_block_height(new_height, self.logger,
                                                     self.channel_set)
        self.assertFalse(self.validator._no_change_in_height_warning_sent)

    def test_update_height_modifies_state_if_new_height(self) -> None:
        old_finalized_block_height = self.validator.finalized_block_height
        old_time_of_last_height_change = \
            self.validator._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.validator._time_of_last_height_check_activity
        old_last_time_did_task = self.validator.finalized_height_alert_limiter. \
            last_time_that_did_task

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertNotEqual(old_finalized_block_height,
                            self.validator.finalized_block_height)
        self.assertNotEqual(old_time_of_last_height_change,
                            self.validator._time_of_last_height_change)
        self.assertNotEqual(old_time_of_last_height_check_activity,
                            self.validator._time_of_last_height_check_activity)
        self.assertNotEqual(old_last_time_did_task,
                            self.validator.finalized_height_alert_limiter.
                            last_time_that_did_task)

    def test_update_height_warning_alert_if_height_not_updated_warning_time_passed(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeFinalizedBlockHeightDidNotChangeInAlert)

    def test_update_height_no_alerts_if_height_not_updated_warning_time_not_passed(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_update_height_sets_warning_sent_if_height_not_updated_warning_time_passed(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertTrue(self.validator.is_no_change_in_height_warning_sent)

    def test_update_height_does_not_set_warning_sent_if_height_not_updated_warning_time_not_passed(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertFalse(self.validator.is_no_change_in_height_warning_sent)

    def test_update_height_critical_alert_if_validator_interval_time_passed_and_warning_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_interval_seconds_with_error.seconds)

        # To send the warning
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeFinalizedBlockHeightDidNotChangeInAlert)

    def test_update_height_warning_alert_if_full_node_interval_time_passed_and_warning_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_interval_seconds_with_error.seconds)

        # To send the warning
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeFinalizedBlockHeightDidNotChangeInAlert)

    def test_update_height_updates_state_if_validator_interval_time_passed_and_warning_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_interval_seconds_with_error.seconds)

        # To send the warning
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.validator.finalized_block_height
        old_time_of_last_height_change = \
            self.validator._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.validator._time_of_last_height_check_activity
        old_last_time_did_task = self.validator.finalized_height_alert_limiter. \
            last_time_that_did_task

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.validator.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.validator._time_of_last_height_change)
        self.assertNotEqual(old_time_of_last_height_check_activity,
                            self.validator._time_of_last_height_check_activity)
        self.assertNotEqual(old_last_time_did_task,
                            self.validator.finalized_height_alert_limiter.
                            last_time_that_did_task)

    def test_update_height_updates_state_if_full_node_interval_time_passed_and_warning_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_interval_seconds_with_error.seconds)

        # To send the warning
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.full_node.finalized_block_height
        old_time_of_last_height_change = \
            self.full_node._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.full_node._time_of_last_height_check_activity
        old_last_time_did_task = self.full_node. \
            finalized_height_alert_limiter.last_time_that_did_task

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.full_node.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.full_node._time_of_last_height_change)
        self.assertNotEqual(old_time_of_last_height_check_activity,
                            self.full_node._time_of_last_height_check_activity)
        self.assertNotEqual(old_last_time_did_task,
                            self.full_node.finalized_height_alert_limiter.
                            last_time_that_did_task)

    def test_update_height_no_critical_alert_if_validator_interval_time_not_passed_and_warning_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        # To send the warning because height has not changed
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertEqual(self.counter_channel.critical_count, 0)

    def test_update_height_no_alert_if_validator_interval_time_not_passed_and_warning_not_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_update_height_no_warning_alert_if_full_node_interval_time_not_passed_and_warning_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        # To send the warning because height has not changed
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.counter_channel.reset()

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertEqual(self.counter_channel.warning_count, 0)

    def test_update_height_no_alert_if_full_node_interval_time_not_passed_and_warning_not_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_update_height_no_state_update_if_validator_interval_time_not_passed_and_warning_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        # To send the warning because height has not changed
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.validator.finalized_block_height
        old_time_of_last_height_change = \
            self.validator._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.validator._time_of_last_height_check_activity
        old_last_time_did_task = self.validator.finalized_height_alert_limiter. \
            last_time_that_did_task

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.validator.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.validator._time_of_last_height_change)
        self.assertEqual(old_time_of_last_height_check_activity,
                         self.validator._time_of_last_height_check_activity)
        self.assertEqual(old_last_time_did_task,
                         self.validator.finalized_height_alert_limiter.
                         last_time_that_did_task)

    def test_update_height_no_state_update_if_validator_interval_time_not_passed_and_warning_not_sent(
            self) -> None:
        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.validator.finalized_block_height
        old_time_of_last_height_change = \
            self.validator._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.validator._time_of_last_height_check_activity
        old_last_time_did_task = self.validator. \
            finalized_height_alert_limiter.last_time_that_did_task

        self.validator.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.validator.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.validator._time_of_last_height_change)
        self.assertEqual(old_time_of_last_height_check_activity,
                         self.validator._time_of_last_height_check_activity)
        self.assertEqual(old_last_time_did_task,
                         self.validator.finalized_height_alert_limiter.
                         last_time_that_did_task)

    def test_update_height_no_state_update_if_full_node_interval_time_not_passed_and_warning_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)
        sleep(self.no_change_in_height_first_warning_seconds_with_error.seconds)

        # To send the warning
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.full_node.finalized_block_height
        old_time_of_last_height_change = \
            self.full_node._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.full_node._time_of_last_height_check_activity
        old_last_time_did_task = self.full_node. \
            finalized_height_alert_limiter.last_time_that_did_task

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.full_node.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.full_node._time_of_last_height_change)
        self.assertEqual(old_time_of_last_height_check_activity,
                         self.full_node._time_of_last_height_check_activity)
        self.assertEqual(old_last_time_did_task,
                         self.full_node.finalized_height_alert_limiter.
                         last_time_that_did_task)

    def test_update_height_no_state_update_if_full_node_interval_time_not_passed_and_warning_not_sent(
            self) -> None:
        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        old_finalized_block_height = self.full_node.finalized_block_height
        old_time_of_last_height_change = \
            self.full_node._time_of_last_height_change
        old_time_of_last_height_check_activity = \
            self.full_node._time_of_last_height_check_activity
        old_last_time_did_task = self.full_node. \
            finalized_height_alert_limiter.last_time_that_did_task

        self.full_node.update_finalized_block_height(
            self.dummy_finalized_block_height, self.logger, self.channel_set)

        self.assertEqual(old_finalized_block_height,
                         self.full_node.finalized_block_height)
        self.assertEqual(old_time_of_last_height_change,
                         self.full_node._time_of_last_height_change)
        self.assertEqual(old_time_of_last_height_check_activity,
                         self.full_node._time_of_last_height_check_activity)
        self.assertEqual(old_last_time_did_task,
                         self.full_node.finalized_height_alert_limiter.
                         last_time_that_did_task)

    def test_set_disabled_no_alerts_first_time_round_if_now_disabled_and_sets(
            self) -> None:
        self.validator.set_disabled(True, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertTrue(self.validator.is_disabled)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_disabled_no_alerts_if_disabled_and_remains_disabled(self) \
            -> None:
        self.validator.set_disabled(True, self.dummy_session_index,
                                    self.channel_set, self.logger)
        self.validator.set_disabled(True, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertTrue(self.validator.is_disabled)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_disabled_raises_critical_alert_if_not_disabled_and_now_disabled_and_sets(
            self) \
            -> None:
        self.validator.set_disabled(False, self.dummy_session_index,
                                    self.channel_set, self.logger)
        self.validator.set_disabled(True, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertTrue(self.validator.is_disabled)
        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorHasBeenDisabledInSessionAlert)

    def test_set_disabled_no_alerts_first_time_round_if_now_not_disabled_and_unsets(
            self) -> None:
        self.validator.set_disabled(False, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertFalse(self.validator.is_disabled)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_disabled_no_alerts_if_enabled_and_now_still_enabled_remains_unset(
            self) -> None:
        self.validator.set_disabled(False, self.dummy_session_index,
                                    self.channel_set, self.logger)
        self.validator.set_disabled(False, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertFalse(self.validator.is_disabled)
        self.assertTrue(self.counter_channel.no_alerts())

    def test_set_disabled_raises_info_alert_if_disabled_and_now_enabled_and_unsets(
            self) -> None:
        self.validator.set_disabled(True, self.dummy_session_index,
                                    self.channel_set, self.logger)
        self.validator.set_disabled(False, self.dummy_session_index,
                                    self.channel_set, self.logger)

        self.assertFalse(self.validator.is_disabled)
        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorIsNoLongerDisabledInSessionAlert)

    def test_slash_raises_critical_alert_if_amount_bigger_than_0(self) -> None:
        self.validator.slash(self.dummy_slash_amount, self.channel_set,
                             self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              ValidatorHasBeenSlashedAlert)

    def test_slash_raises_no_alerts_if_amount_less_or_equal_to_0(self) -> None:
        self.validator.slash(-1, self.channel_set, self.logger)
        self.validator.slash(0, self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_disconnect_from_api_raises_critical_alert_for_validators_if_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.critical_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeWasNotConnectedToApiServerAlert)

    def test_disconnect_from_api_raises_warning_alert_for_full_nodes_if_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.warning_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeWasNotConnectedToApiServerAlert)

    def test_disconnect_from_api_raises_no_alerts_for_validators_if_not_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.disconnect_from_api(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_disconnect_from_api_raises_no_alerts_for_full_nodes_if_not_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.disconnect_from_api(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_disconnect_from_api_sets_is_connected_false_for_validators_if_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)

        self.assertFalse(self.validator.is_connected_to_api_server)

    def test_disconnect_from_api_sets_is_connected_false_for_full_nodes_if_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)

        self.assertFalse(self.full_node.is_connected_to_api_server)

    def test_disconnect_from_api_sets_is_connected_false_for_validators_if_not_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.disconnect_from_api(self.channel_set, self.logger)

        self.assertFalse(self.validator.is_connected_to_api_server)

    def test_disconnect_from_api_sets_is_connected_false_for_full_nodes_if_not_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.disconnect_from_api(self.channel_set, self.logger)

        self.assertFalse(self.full_node.is_connected_to_api_server)

    def test_connect_with_api_raises_info_alert_for_validators_if_not_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.connect_with_api(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeConnectedToApiServerAgainAlert)

    def test_connect_with_api_raises_info_alert_for_full_nodes_if_not_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.connect_with_api(self.channel_set, self.logger)

        self.assertEqual(self.counter_channel.info_count, 1)
        self.assertIsInstance(self.counter_channel.latest_alert,
                              NodeConnectedToApiServerAgainAlert)

    def test_connect_with_api_raises_no_alerts_for_validators_if_connected_to_api(
            self) -> None:
        self.validator.connect_with_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_connect_with_api_raises_no_alerts_for_full_nodes_if_connected_to_api(
            self) -> None:
        self.full_node.connect_with_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.counter_channel.no_alerts())

    def test_connect_with_api_sets_is_connected_true_for_validators_if_connected_to_api(
            self) -> None:
        self.validator.connect_with_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.validator.is_connected_to_api_server)

    def test_connect_with_api_sets_is_connected_true_for_full_nodes_if_connected_to_api(
            self) -> None:
        self.full_node.connect_with_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.validator.is_connected_to_api_server)

    def test_connect_with_api_sets_is_connected_true_for_validators_if_not_connected_to_api(
            self) -> None:
        self.validator.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.validator.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.validator.is_connected_to_api_server)

    def test_connect_with_api_sets_is_connected_true_for_full_nodes_if_not_connected_to_api(
            self) -> None:
        self.full_node.disconnect_from_api(self.channel_set, self.logger)
        self.counter_channel.reset()
        self.full_node.connect_with_api(self.channel_set, self.logger)

        self.assertTrue(self.validator.is_connected_to_api_server)


class TestNodeWithRedis(unittest.TestCase):

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
        self.node_name = 'testnode'
        self.chain = 'testchain'
        self.redis_prefix = self.node_name + "@" + self.chain
        self.date = datetime.now().timestamp()
        self.logger = logging.getLogger('dummy')

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

        self.non_validator = Node(name=self.node_name, ws_url=None,
                                  node_type=NodeType.NON_VALIDATOR_FULL_NODE,
                                  stash_account_address='', chain=self.chain,
                                  redis=self.redis, is_archive_node=True,
                                  internal_conf=TestInternalConf)

        self.validator = Node(name=self.node_name, ws_url=None,
                              node_type=NodeType.VALIDATOR_FULL_NODE,
                              stash_account_address='', chain=self.chain,
                              redis=self.redis, is_archive_node=True,
                              internal_conf=TestInternalConf)

    def test_load_state_changes_nothing_if_nothing_saved(self):
        self.validator.load_state(self.logger)

        self.assertFalse(self.validator.is_down)
        self.assertIsNone(self.validator._went_down_at)
        self.assertIsNone(self.validator.bonded_balance)
        self.assertFalse(self.validator.is_syncing)
        self.assertIsNone(self.validator.no_of_peers)
        self.assertIsNone(self.validator.is_active)
        self.assertIsNone(self.validator.is_council_member)
        self.assertIsNone(self.validator.is_elected)
        self.assertIsNone(self.validator.is_disabled)
        self.assertEqual(self.validator.no_of_blocks_authored, 0)
        self.assertEqual(self.validator._time_of_last_block, NONE)
        self.assertTrue(self.validator.is_authoring)
        self.assertEqual(self.validator._time_of_last_block_check_activity,
                         NONE)
        self.assertEqual(self.validator._time_of_last_height_check_activity,
                         NONE)
        self.assertIsNotNone(self.validator._time_of_last_height_change)
        self.assertEqual(self.validator.finalized_block_height, 0)
        self.assertFalse(self.validator.is_no_change_in_height_warning_sent)
        self.assertEqual(self.validator.auth_index, NONE)

    def test_load_state_sets_values_to_saved_values(self):
        # Set Redis values manually
        hash_name = Keys.get_hash_blockchain(self.validator.chain)
        node = self.validator.name
        self.redis.hset_multiple_unsafe(hash_name, {
            Keys.get_node_went_down_at(node): str(self.date),
            Keys.get_node_bonded_balance(node): 456,
            Keys.get_node_is_syncing(node): str(True),
            Keys.get_node_no_of_peers(node): 789,
            Keys.get_node_active(node): str(True),
            Keys.get_node_council_member(node): str(True),
            Keys.get_node_elected(node): str(True),
            Keys.get_node_disabled(node): str(True),
            Keys.get_node_blocks_authored(node): 10,
            Keys.get_node_time_of_last_block(node): 12.4,
            Keys.get_node_is_authoring(node): str(False),
            Keys.get_node_time_of_last_block_check_activity(node): 123.4,
            Keys.get_node_time_of_last_height_check_activity(node): 456.6,
            Keys.get_node_time_of_last_height_change(node): 35.4,
            Keys.get_node_finalized_block_height(node): 43,
            Keys.get_node_no_change_in_height_warning_sent(node): str(True),
            Keys.get_node_auth_index(node): 45,
        })

        # Load the Redis values
        self.validator.load_state(self.logger)

        # Assert
        self.assertTrue(self.validator.is_down)
        self.assertEqual(self.validator._went_down_at, self.date)
        self.assertEqual(self.validator.bonded_balance, 456)
        self.assertTrue(self.validator.is_syncing)
        self.assertEqual(self.validator.no_of_peers, 789)
        self.assertTrue(self.validator.is_active)
        self.assertTrue(self.validator.is_council_member)
        self.assertTrue(self.validator.is_elected)
        self.assertTrue(self.validator.is_disabled)
        self.assertEqual(self.validator.no_of_blocks_authored, 10)
        self.assertEqual(self.validator._time_of_last_block, 12.4)
        self.assertFalse(self.validator.is_authoring)
        self.assertEqual(self.validator._time_of_last_block_check_activity,
                         123.4)
        self.assertEqual(self.validator._time_of_last_height_check_activity,
                         456.6)
        self.assertEqual(self.validator._time_of_last_height_change, 35.4)
        self.assertEqual(self.validator.finalized_block_height, 43)
        self.assertTrue(self.validator.is_no_change_in_height_warning_sent)
        self.assertEqual(self.validator.auth_index, 45)

    def test_load_state_sets_blocks_authored_timer_to_last_activity_if_not_NONE(
            self) -> None:
        hash_name = Keys.get_hash_blockchain(self.chain)
        self.redis.hset_multiple_unsafe(hash_name, {
            Keys.get_node_time_of_last_block_check_activity(
                self.node_name): 123.4
        })
        last_time = datetime.fromtimestamp(123.4)

        self.validator.load_state(self.logger)
        self.assertEqual(self.validator.blocks_authored_alert_limiter.
                         last_time_that_did_task, last_time)

    def test_load_state_sets_blocks_authored_timer_to_not_NONE_if_last_activity_NONE(
            self) -> None:
        self.validator.load_state(self.logger)
        self.assertIsNotNone(self.validator.blocks_authored_alert_limiter.
                             last_time_that_did_task)

    def test_load_state_sets_last_height_timer_to_last_activity_if_not_NONE(
            self) -> None:
        hash_name = Keys.get_hash_blockchain(self.chain)
        self.redis.hset_multiple_unsafe(hash_name, {
            Keys.get_node_time_of_last_height_check_activity(
                self.node_name): 123.4
        })
        last_time = datetime.fromtimestamp(123.4)

        self.validator.load_state(self.logger)
        self.assertEqual(self.validator.finalized_height_alert_limiter.
                         last_time_that_did_task, last_time)

    def test_load_state_sets_height_timer_to_not_NONE_if_last_activity_NONE(
            self) -> None:
        self.validator.load_state(self.logger)
        self.assertIsNotNone(self.validator.finalized_height_alert_limiter.
                             last_time_that_did_task)

    def test_load_state_sets_time_of_last_change_to_not_NONE_if_last_activity_NONE(
            self) -> None:
        self.validator.load_state(self.logger)
        self.assertIsNotNone(self.validator._time_of_last_height_change)

    def test_save_state_sets_values_to_current_values(self):
        # Set node values manually
        self.validator._went_down_at = self.date
        self.validator._bonded_balance = 456
        self.validator._is_syncing = True
        self.validator._no_of_peers = 789
        self.validator._active = True
        self.validator._council_member = True
        self.validator._elected = True
        self.validator._disabled = True
        self.validator._no_of_blocks_authored = 10
        self.validator._time_of_last_block = 1234.4
        self.validator._is_authoring = False
        self.validator._time_of_last_block_check_activity = 124.4
        self.validator._time_of_last_height_check_activity = 45.5
        self.validator._time_of_last_height_change = 45.5
        self.validator._finalized_block_height = 34
        self.validator._no_change_in_height_warning_sent = True
        self.validator._auth_index = 45

        # Save the values to Redis
        self.validator.save_state(self.logger)

        # Assert
        hash_name = Keys.get_hash_blockchain(self.validator.chain)
        self.assertEqual(float(self.redis.hget_unsafe(
            hash_name, Keys.get_node_went_down_at(self.validator.name))),
            self.date)
        self.assertEqual(self.redis.hget_int_unsafe(
            hash_name, Keys.get_node_bonded_balance(self.validator.name)), 456)
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_is_syncing(self.validator.name)))
        self.assertEqual(self.redis.hget_int_unsafe(
            hash_name, Keys.get_node_no_of_peers(self.validator.name)), 789)
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_active(self.validator.name)))
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_council_member(self.validator.name)))
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_elected(self.validator.name)))
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_disabled(self.validator.name)))
        self.assertEqual(self.redis.hget_int_unsafe(
            hash_name, Keys.get_node_blocks_authored(self.validator.name)), 10)
        self.assertEqual(float(self.redis.hget(
            hash_name, Keys.get_node_time_of_last_block(self.validator.name))),
            1234.4)
        self.assertFalse(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_is_authoring(self.validator.name)))
        self.assertEqual(float(self.redis.hget(
            hash_name, Keys.get_node_time_of_last_block_check_activity(
                self.validator.name))), 124.4)
        self.assertEqual(float(self.redis.hget(
            hash_name, Keys.get_node_time_of_last_height_check_activity(
                self.validator.name))), 45.5)
        self.assertEqual(float(self.redis.hget(
            hash_name,
            Keys.get_node_time_of_last_height_change(self.validator.name))),
            45.5)
        self.assertEqual(self.redis.hget_int_unsafe(
            hash_name,
            Keys.get_node_finalized_block_height(self.validator.name)), 34)
        self.assertTrue(self.redis.hget_bool_unsafe(
            hash_name, Keys.get_node_no_change_in_height_warning_sent(
                self.validator.name)))
        self.assertEqual(self.redis.hget_int_unsafe(
            hash_name, Keys.get_node_auth_index(self.validator.name)), 45)
