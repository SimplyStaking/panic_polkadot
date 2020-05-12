import logging
from datetime import datetime, timedelta
from typing import List, Optional

from src.alerters.reactive.blockchain import Blockchain
from src.alerters.reactive.node import Node
from src.channels.channel import ChannelSet
from src.monitors.monitor import Monitor
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import Keys
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from src.utils.exceptions import NoLiveNodeConnectedWithAnApiServerException


class BlockchainMonitor(Monitor):

    def __init__(self, monitor_name: str, blockchain: Blockchain,
                 channels: ChannelSet, logger: logging.Logger,
                 redis: Optional[RedisApi], data_sources: List[Node],
                 polkadot_api_endpoint: str,
                 internal_conf: InternalConfig = InternalConf):
        super().__init__(monitor_name, channels, logger, redis, internal_conf)

        self._blockchain = blockchain
        self.data_sources = data_sources
        self._data_wrapper = PolkadotApiWrapper(logger, polkadot_api_endpoint)

        self.last_data_source_used = None

        self._redis_alive_key_timeout = \
            self._internal_conf.redis_blockchain_monitor_alive_key_timeout

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
            key = Keys.get_blockchain_monitor_alive(self.monitor_name)
            until = timedelta(seconds=self._redis_alive_key_timeout)
            self.redis.set_for(key, str(datetime.now().timestamp()), until)

    @property
    def data_source(self) -> Node:
        nodes_connected_to_an_api = \
            self.data_wrapper.get_web_sockets_connected_to_an_api()
        # Get one of the nodes to use as data source
        for n in self.data_sources:
            if n.ws_url in nodes_connected_to_an_api and not n.is_down:
                self.last_data_source_used = n
                self._data_wrapper.ping_node(n.ws_url)
                return n
        raise NoLiveNodeConnectedWithAnApiServerException()

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
