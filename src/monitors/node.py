import logging
from datetime import datetime, timedelta
from typing import Optional, List

from src.alerters.reactive.node import Node
from src.alerts.alerts import FoundLiveArchiveNodeAgainAlert
from src.channels.channel import ChannelSet
from src.monitors.monitor import Monitor
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from src.utils.exceptions import \
    NoLiveNodeConnectedWithAnApiServerException, \
    NoLiveArchiveNodeConnectedWithAnApiServerException
from src.utils.parsing import parse_int_from_string
from src.utils.scaling import scale_to_pico
from src.utils.types import NONE


class NodeMonitor(Monitor):

    def __init__(self, monitor_name: str, channels: ChannelSet,
                 logger: logging.Logger, node_monitor_max_catch_up_blocks: int,
                 redis: Optional[RedisApi], node: Node,
                 archive_alerts_disabled: bool, data_sources: List[Node],
                 polkadot_api_endpoint: str,
                 internal_conf: InternalConfig = InternalConf):
        super().__init__(monitor_name, channels, logger, redis, internal_conf)

        self._node = node
        self._data_wrapper = PolkadotApiWrapper(logger, polkadot_api_endpoint)
        self._node_monitor_max_catch_up_blocks = \
            node_monitor_max_catch_up_blocks

        self._redis_alive_key_timeout = \
            self._internal_conf.redis_node_monitor_alive_key_timeout
        self._redis_last_height_key_timeout = \
            self._internal_conf.redis_node_monitor_last_height_key_timeout

        # The data sources for indirect monitoring are all nodes from the same
        # chain which have been set as a data source in the config.
        self._indirect_monitoring_data_sources = data_sources

        # The data sources for archive monitoring are all archive nodes from
        # the same chain that have been set as data source in the config.
        self._archive_monitoring_data_sources = [node for node in data_sources
                                                 if node.is_archive_node]
        self.last_data_source_used = None
        self._last_height_checked = NONE
        self._session_index = NONE
        self._era_index = NONE
        self._monitor_is_catching_up = False
        self._indirect_monitoring_disabled = len(data_sources) == 0
        self._no_live_archive_node_alert_sent = False
        self._archive_alerts_disabled = archive_alerts_disabled

        self.load_state()

    def is_catching_up(self) -> bool:
        return self._monitor_is_catching_up

    @property
    def indirect_monitoring_disabled(self) -> bool:
        return self._indirect_monitoring_disabled

    @property
    def node(self) -> Node:
        return self._node

    @property
    def session_index(self) -> int:
        return self._session_index

    @property
    def era_index(self) -> int:
        return self._era_index

    @property
    def last_height_checked(self) -> int:
        return self._last_height_checked

    @property
    def no_live_archive_node_alert_sent(self) -> bool:
        return self._no_live_archive_node_alert_sent

    @property
    def data_wrapper(self) -> PolkadotApiWrapper:
        return self._data_wrapper

    @property
    def indirect_monitoring_data_sources(self) -> List[Node]:
        return self._indirect_monitoring_data_sources

    @property
    def archive_monitoring_data_sources(self) -> List[Node]:
        return self._archive_monitoring_data_sources

    # The data_source_indirect function returns a node for the indirect
    # monitoring. Since indirect monitoring does not require data from past
    # chain state, the data_source_indirect function may return a node which is
    # not an archive node.
    @property
    def data_source_indirect(self) -> Node:
        nodes_connected_to_an_api = \
            self.data_wrapper.get_web_sockets_connected_to_an_api()
        # Get one of the nodes to use as data source
        for n in self._indirect_monitoring_data_sources:
            if n.ws_url in nodes_connected_to_an_api and not n.is_down:
                self.last_data_source_used = n
                self._data_wrapper.ping_node(n.ws_url)
                return n
        raise NoLiveNodeConnectedWithAnApiServerException()

    # The data_source_archive function returns a node for archive monitoring.
    # Since archive monitoring requires data from past chain state, the
    # data_source_archive function returns only nodes which are archive nodes.
    @property
    def data_source_archive(self) -> Node:
        nodes_connected_to_an_api = \
            self.data_wrapper.get_web_sockets_connected_to_an_api()
        # Get one of the archive nodes to use as data source
        for n in self._archive_monitoring_data_sources:
            if n.ws_url in nodes_connected_to_an_api and not n.is_down:
                self.last_data_source_used = n
                self._data_wrapper.ping_node(n.ws_url)
                return n
        raise NoLiveArchiveNodeConnectedWithAnApiServerException()

    def load_state(self) -> None:
        # If Redis is enabled, load the session index, era index, and last
        # height checked for slashing if any.
        if self.redis_enabled:
            key_si = Keys.get_node_monitor_session_index(self.monitor_name)
            key_ei = Keys.get_node_monitor_era_index(self.monitor_name)
            key_lh = Keys.get_node_monitor_last_height_checked(
                self.monitor_name)
            self._session_index = self.redis.get_int(key_si, NONE)
            self._era_index = self.redis.get_int(key_ei, NONE)
            self._last_height_checked = self.redis.get_int(key_lh, NONE)

            self.logger.debug(
                'Restored %s state: %s=%s, %s=%s, %s=%s', self._monitor_name,
                key_si, self._session_index, key_lh, self._last_height_checked,
                key_ei, self._era_index)

    def save_state(self) -> None:
        # If Redis is enabled, save the current time indicating that the node
        # monitor was alive at this time, the current session index, era index,
        # and the last height checked.
        if self.redis_enabled:
            key_si = Keys.get_node_monitor_session_index(self.monitor_name)
            key_ei = Keys.get_node_monitor_era_index(self.monitor_name)
            key_lh = Keys.get_node_monitor_last_height_checked(
                self.monitor_name)
            key_alive = Keys.get_node_monitor_alive(self.monitor_name)

            self.logger.debug(
                'Saving node monitor state: %s=%s, %s=%s, %s=%s',
                self._monitor_name, key_si, self._session_index, key_lh,
                self._last_height_checked, key_ei, self._era_index)

            # Set session and era index keys
            self.redis.set_multiple({
                key_si: self._session_index, key_ei: self._era_index
            })

            # Set last height checked key
            until = timedelta(seconds=self._redis_last_height_key_timeout)
            self.redis.set_for(key_lh, self._last_height_checked, until)

            # Set alive key (to be able to query latest update from Telegram)
            until = timedelta(seconds=self._redis_alive_key_timeout)
            self.redis.set_for(
                key_alive, str(datetime.now().timestamp()), until
            )

    def status(self) -> str:
        if self._node.is_validator:
            return self._node.status() + \
                   ', session_index={}, era_index={}, last_height_checked={}' \
                       .format(self._session_index, self._era_index,
                               self._last_height_checked)
        else:
            return self._node.status()

    def monitor_direct(self) -> None:
        # Check if node is accessible
        self._logger.debug('Checking if %s is alive', self._node)
        self._data_wrapper.ping_node(self._node.ws_url)
        self._node.set_as_up(self.channels, self.logger)

        # Get system_health
        system_health = self.data_wrapper.get_system_health(self._node.ws_url)

        # Get finalized block header
        finalized_head = self.data_wrapper.get_finalized_head(self.node.ws_url)
        finalized_block_header = self.data_wrapper.get_header(self.node.ws_url,
                                                              finalized_head)

        # Set is-syncing
        is_syncing = system_health['isSyncing']
        self._logger.debug('%s is syncing: %s', self._node, is_syncing)
        self._node.set_is_syncing(is_syncing, self.channels, self.logger)

        # Set number of peers
        no_of_peers = system_health['peers']
        self._logger.debug('%s no. of peers: %s', self._node, no_of_peers)
        self._node.set_no_of_peers(no_of_peers, self.channels, self.logger)

        # Update finalized block
        finalized_block_height = parse_int_from_string(
            str(finalized_block_header['number']))
        self._logger.debug('%s finalized_block_height: %s', self._node,
                           finalized_block_height)
        self._node.update_finalized_block_height(finalized_block_height,
                                                 self.logger, self.channels)

        # Set API as up, and declare that the node was connected to the API
        self.data_wrapper.set_api_as_up(self.monitor_name, self.channels)
        self.node.connect_with_api(self.channels, self.logger)

    def _check_for_slashing(self, height_to_check: int, archive_node: Node) \
            -> None:
        block_hash = self.data_wrapper.get_block_hash(archive_node.ws_url,
                                                      height_to_check)
        slash_amount = self.data_wrapper.get_slash_amount(
            archive_node.ws_url, block_hash, self.node.stash_account_address)

        if slash_amount > 0:
            scaled_slash_amount = round(scale_to_pico(slash_amount), 3)
            self.node.slash(scaled_slash_amount, self.channels, self.logger)

    def _check_for_new_session(self, new_session_index: int) -> None:

        self._logger.debug('%s session_index: %s', self._node,
                           new_session_index)

        if self._session_index is NONE:
            self._session_index = new_session_index
        elif self._session_index < new_session_index:
            self._session_index = new_session_index

            # The number of blocks authored are recorded per session not era
            self._node.reset_no_of_blocks_authored(self.channels, self.logger)

    def _check_for_new_era(self, new_era_index: int) -> None:

        self._logger.debug('%s era_index: %s', self._node, new_era_index)

        if self._era_index is NONE:
            self._era_index = new_era_index
        elif self._era_index < new_era_index:
            self._era_index = new_era_index

            # Reset timers on a new era to raise not authoring alerts per era,
            # not session.
            self._node.set_time_of_last_block(NONE, self.channels, self.logger)
            self._node.blocks_authored_alert_limiter.did_task()
            self._node.set_is_authoring(True, self.channels, self.logger)
            self._node.set_time_of_last_block_check_activity(
                NONE, self.channels, self.logger)

    def _monitor_archive_state(self) -> None:
        # Check for slashing
        # Data source must be saved to avoid situations where
        # last_height_to_check < finalized_block_height
        archive_node = self.data_source_archive
        last_height_to_check = archive_node.finalized_block_height
        if self._last_height_checked == NONE:
            self._last_height_checked = last_height_to_check - 1
        height_to_check = self._last_height_checked + 1

        # If the data source node's finalized height is less than the height
        # already checked, there is no need to check that block.
        if last_height_to_check < height_to_check:
            pass
        elif last_height_to_check - self._last_height_checked > \
                self._node_monitor_max_catch_up_blocks:
            height_to_check = last_height_to_check - \
                              self._node_monitor_max_catch_up_blocks
            self._check_for_slashing(height_to_check, archive_node)
            self._last_height_checked = height_to_check
        elif height_to_check <= last_height_to_check:
            self._check_for_slashing(height_to_check, archive_node)
            self._last_height_checked = height_to_check

        if last_height_to_check - self._last_height_checked > 2:
            self._monitor_is_catching_up = True
        else:
            self._monitor_is_catching_up = False

        # Unset, so that if in the next monitoring round an archive node is not
        # found, the operator is informed accordingly.
        if self._no_live_archive_node_alert_sent:
            self._no_live_archive_node_alert_sent = False
            self.channels.alert_info(FoundLiveArchiveNodeAgainAlert(
                self.monitor_name))

    def _monitor_indirect_validator(self) -> None:
        session_validators = self.data_wrapper.get_session_validators(
            self.data_source_indirect.ws_url)
        stakers_json = self.data_wrapper.get_eras_stakers(
            self.data_source_indirect.ws_url, self._node.stash_account_address)
        council_members = self.data_wrapper.get_council_members(
            self.data_source_indirect.ws_url)
        staking_validators = self.data_wrapper.get_derive_staking_validators(
            self.data_source_indirect.ws_url)
        new_session_index = parse_int_from_string(str(
            self.data_wrapper.get_current_index(
                self.data_source_indirect.ws_url)))
        new_number_of_blocks_authored = parse_int_from_string(str(
            self.data_wrapper.get_authored_blocks(
                self.data_source_indirect.ws_url, new_session_index,
                self.node.stash_account_address)))
        disabled_validators = self.data_wrapper.get_disabled_validators(
            self.data_source_indirect.ws_url)
        active_era = self.data_wrapper.get_active_era(
            self.data_source_indirect.ws_url)
        new_era_index = parse_int_from_string(str(active_era['index']))

        # Set active
        is_active = self._node.stash_account_address in session_validators
        self._logger.debug('%s active: %s', self._node, is_active)
        self.node.set_active(is_active, self.channels, self.logger)

        # Set auth_index
        if self._node.is_active:
            new_auth_index = session_validators.index(
                self.node.stash_account_address)
            self._logger.debug('%s auth_index: %s', self._node,
                               new_auth_index)
            self._node.set_auth_index(new_auth_index, self.logger)

        # Set disabled
        is_disabled = self.node.auth_index in disabled_validators
        self._logger.debug('%s disabled: %s', self._node, is_disabled)
        self.node.set_disabled(is_disabled, new_session_index, self.channels,
                               self.logger)

        # Set elected
        elected_validators = staking_validators['nextElected']
        is_elected = self._node.stash_account_address in elected_validators
        self._logger.debug('%s elected: %s', self._node, is_elected)
        self.node.set_elected(is_elected, self.channels, self.logger)

        # Set bonded_balance
        bonded_balance = parse_int_from_string(str(stakers_json['total']))
        self._logger.debug('%s bonded_balance: %s', self._node, bonded_balance)
        self._node.set_bonded_balance(bonded_balance, self.channels,
                                      self.logger)

        # Set council_member
        is_council_member = self._node.stash_account_address in council_members
        self._logger.debug('%s is council member: %s', self._node,
                           is_council_member)
        self.node.set_council_member(is_council_member, self.channels,
                                     self.logger)

        # Set session index
        self._check_for_new_session(new_session_index)

        # Set era index
        self._check_for_new_era(new_era_index)

        # Set number of blocks authored
        self._logger.debug('%s number_of_blocks_authored: %s',
                           self._node,
                           new_number_of_blocks_authored)
        self._node.set_no_of_blocks_authored(self.channels, self.logger,
                                             new_number_of_blocks_authored,
                                             self._era_index)

        if not self._archive_alerts_disabled:
            self._monitor_archive_state()

    def _monitor_indirect_full_node(self) -> None:
        # These are not needed for full nodes, and thus must be given a
        # dummy value since NoneTypes cannot be saved in redis.

        # Set session index and era index.
        self._session_index = NONE
        self._era_index = NONE

        # Set bonded balance
        balance = 0
        self._logger.debug('%s balance: %s', self._node, balance)
        self._node.set_bonded_balance(balance, self.channels, self.logger)

        # Set active
        self._logger.debug('%s is active: %s', self._node, False)
        self._node.set_active(False, self.channels, self.logger)

        # Set disabled
        self._logger.debug('%s is disabled: %s', self._node, False)
        self._node.set_disabled(False, self._session_index, self.channels,
                                self.logger)

        # Set elected
        self._logger.debug('%s is elected: %s', self._node, False)
        self._node.set_elected(False, self.channels, self.logger)

        # Set council_member
        self._logger.debug('%s is council member: %s', self._node, False)
        self._node.set_council_member(False, self.channels, self.logger)

    def monitor_indirect(self) -> None:
        if self._node.is_validator:
            self._monitor_indirect_validator()

            # Set API as up and declare the used node as connected with the API
            self.data_wrapper.set_api_as_up(self.monitor_name, self.channels)
            self.last_data_source_used.connect_with_api(
                self.channels, self.logger)
        else:
            self._monitor_indirect_full_node()

    def monitor(self) -> None:
        # Monitor part of the node state by querying the node directly
        self.monitor_direct()
        # Monitor part of the node state by querying the node indirectly if
        # indirect monitoring is enabled.
        if not self.indirect_monitoring_disabled:
            self.monitor_indirect()

        # Output status
        self._logger.info('%s status: %s', self._node, self.status())
