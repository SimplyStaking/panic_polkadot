import logging
from datetime import datetime, timedelta
from typing import List, Optional

from alerter.src.alerting.channels.channel import ChannelSet
from alerter.src.blockchain.blockchain import Blockchain
from alerter.src.monitoring.monitors.monitor import Monitor
from alerter.src.node.node import Node
from alerter.src.utils.config_parsers.internal import InternalConfig
from alerter.src.utils.config_parsers.internal_parsed import InternalConf
from alerter.src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from alerter.src.utils.exceptions import \
    NoLiveFullNodeConnectedWithAnApiServerException
from alerter.src.utils.redis_api import RedisApi


class BlockchainMonitor(Monitor):

    def __init__(self, monitor_name: str, blockchain: Blockchain,
                 channels: ChannelSet, logger: logging.Logger,
                 redis: Optional[RedisApi], all_full_nodes: List[Node],
                 polkadot_api_endpoint: str,
                 internal_conf: InternalConfig = InternalConf):
        super().__init__(monitor_name, channels, logger, redis, internal_conf)

        self._blockchain = blockchain
        self._all_full_nodes = all_full_nodes
        self._data_wrapper = PolkadotApiWrapper(logger, polkadot_api_endpoint)

        self.last_full_node_used = None

        self._redis_alive_key_timeout = \
            self._internal_conf.redis_blockchain_monitor_alive_key_timeout
        self._redis_alive_key = \
            self._internal_conf.redis_blockchain_monitor_alive_key_prefix + \
            self._monitor_name

    @property
    def data_wrapper(self) -> PolkadotApiWrapper:
        return self._data_wrapper

    @property
    def blockchain(self) -> Blockchain:
        return self._blockchain

    def save_state(self) -> None:
        # If Redis is enabled save the current time, indicating that the monitor
        # was alive at this time.
        if self.redis_enabled:
            self.logger.debug('Saving %s state', self._monitor_name)

            # Set alive key (to be able to query latest update from Telegram)
            key = self._redis_alive_key
            until = timedelta(seconds=self._redis_alive_key_timeout)
            self.redis.set_for(key, str(datetime.now()), until)

    @property
    def data_source(self) -> Node:
        nodes_connected_to_an_api = \
            self.data_wrapper.get_web_sockets_connected_to_an_api()
        # Get one of the full nodes to use as data source
        for n in self._all_full_nodes:
            if n.ws_url in nodes_connected_to_an_api and not n.is_down:
                self.last_full_node_used = n
                self._data_wrapper.ping_node(n.ws_url)
                return n
        raise NoLiveFullNodeConnectedWithAnApiServerException()

    def status(self) -> str:
        return self.blockchain.status()

    def _check_for_new_referendums(self, new_referendum_count: int) -> None:

        if self.blockchain.referendum_count is None:
            self.blockchain.set_referendum_count(
                new_referendum_count, self.channels, self.logger)
            return

        while self.blockchain.referendum_count < new_referendum_count:
            referendum_info = self._data_wrapper.get_referendum_info_of(
                self.data_source.ws_url, self.blockchain.referendum_count)
            self.blockchain.set_referendum_count(
                self.blockchain.referendum_count + 1, self.channels,
                self.logger, referendum_info)

    def monitor(self) -> None:
        # Get new data.
        new_referendum_count = self._data_wrapper.get_referendum_count(
            self.data_source.ws_url)
        new_council_prop_count = self._data_wrapper.get_council_proposal_count(
            self.data_source.ws_url)
        new_public_prop_count = self._data_wrapper.get_public_proposal_count(
            self.data_source.ws_url)
        session_validators = self._data_wrapper.get_session_validators(
            self.data_source.ws_url)
        new_validator_set_size = len(session_validators)

        # Check for referendums
        self._logger.debug('%s referendum_count: %s', self.blockchain,
                           new_referendum_count)
        self._check_for_new_referendums(new_referendum_count)

        # Set council prop count
        self._logger.debug('%s council_prop_count: %s', self.blockchain,
                           new_council_prop_count)
        self.blockchain.set_council_prop_count(new_council_prop_count,
                                               self.channels, self.logger)

        # Set public prop count
        self._logger.debug('%s public_prop_count: %s', self.blockchain,
                           new_public_prop_count)
        self.blockchain.set_public_prop_count(new_public_prop_count,
                                              self.channels, self.logger)

        # Set validator set size
        self._logger.debug('%s validator_set_size: %s', self.blockchain,
                           new_validator_set_size)
        self.blockchain.set_validator_set_size(new_validator_set_size,
                                               self.channels, self.logger)

        # Set API as up
        self.data_wrapper.set_api_as_up(self.monitor_name, self.channels)

        self.logger.info('%s status: %s', self._monitor_name, self.status())
