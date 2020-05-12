import logging
from typing import Optional

from src.alerts.alerts import ApiIsDownAlert, ApiIsUpAgainAlert
from src.channels.channel import ChannelSet
from src.utils.get_json import get_polkadot_json
from src.utils.types import PolkadotWrapperType


class PolkadotApiWrapper:

    def __init__(self, logger: logging.Logger, api_endpoint: str):
        self._logger = logger
        self._api_endpoint = api_endpoint
        self._api_down = False

    @property
    def api_endpoint(self) -> str:
        return self._api_endpoint

    @property
    def is_api_down(self) -> bool:
        return self._api_down

    def get_block_hash(self, ws_url: str, block_number: int) -> \
            PolkadotWrapperType:
        api_call = 'chain/getBlockHash'
        endpoint = self._api_endpoint + '/api/rpc/' + api_call
        params = {'websocket': ws_url, 'block_number': block_number}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_finalized_head(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'chain/getFinalizedHead'
        endpoint = self._api_endpoint + '/api/rpc/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_header(self, ws_url: str, block_hash: str) -> PolkadotWrapperType:
        api_call = 'chain/getHeader'
        endpoint = self._api_endpoint + '/api/rpc/' + api_call
        params = {'websocket': ws_url, 'hash': block_hash}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_system_chain(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'system/chain'
        endpoint = self._api_endpoint + '/api/rpc/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_system_health(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'system/health'
        endpoint = self._api_endpoint + '/api/rpc/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_council_members(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'council/members'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_council_proposal_count(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'council/proposalCount'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_public_proposal_count(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'democracy/publicPropCount'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_referendum_count(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'democracy/referendumCount'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_referendum_info_of(self, ws_url: str, referendum_index: int) \
            -> PolkadotWrapperType:
        api_call = 'democracy/referendumInfoOf'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url, 'referendum_index': referendum_index}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_authored_blocks(self, ws_url: str, session_index: int,
                            validator_id: str) -> PolkadotWrapperType:
        api_call = 'imOnline/authoredBlocks'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url,
                  'validator_id': validator_id,
                  'session_index': session_index}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_received_heartbeats(self, ws_url: str, session_index: int,
                                auth_index: int) -> PolkadotWrapperType:
        api_call = 'imOnline/receivedHeartbeats'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url,
                  'auth_index': auth_index,
                  'session_index': session_index}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_current_index(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'session/currentIndex'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_disabled_validators(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'session/disabledValidators'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_session_validators(self, ws_url: str) -> PolkadotWrapperType:
        api_call = 'session/validators'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_derive_staking_validators(self, ws_url: str) \
            -> PolkadotWrapperType:
        api_call = 'staking/validators'
        endpoint = self._api_endpoint + '/api/derive/' + api_call
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_eras_stakers(self, ws_url: str, stash_account_address: str) \
            -> PolkadotWrapperType:
        api_call = 'staking/erasStakers'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url, 'account_id': stash_account_address}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_events(self, ws_url: str, block_hash: Optional[str]) \
            -> PolkadotWrapperType:
        api_call = 'system/events'
        endpoint = self._api_endpoint + '/api/query/' + api_call
        params = {'websocket': ws_url, 'block_hash': block_hash}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_slash_amount(self, ws_url: str, block_hash: Optional[str],
                         stash_account_address: str) -> PolkadotWrapperType:
        api_call = 'custom/getSlashAmount'
        endpoint = self._api_endpoint + '/api/' + api_call
        params = {'websocket': ws_url, 'block_hash': block_hash,
                  'account_address': stash_account_address}
        return get_polkadot_json(endpoint, params, self._logger, api_call)

    def get_web_sockets_connected_to_an_api(self) -> PolkadotWrapperType:
        endpoint = self._api_endpoint + '/api/getConnectionsList'
        params = {}
        return get_polkadot_json(endpoint, params, self._logger)

    def ping_api(self) -> PolkadotWrapperType:
        endpoint = self._api_endpoint + '/api/pingApi'
        params = {}
        return get_polkadot_json(endpoint, params, self._logger)

    def ping_node(self, ws_url: str) -> PolkadotWrapperType:
        endpoint = self._api_endpoint + '/api/pingNode'
        params = {'websocket': ws_url}
        return get_polkadot_json(endpoint, params, self._logger)

    def set_api_as_down(self, monitor: str, channels: ChannelSet) -> None:

        self._logger.debug('%s set_api_as_down: api_down(currently)=%s, '
                           'channels=%s', self, self._api_down, channels)

        if not self._api_down:
            channels.alert_error(ApiIsDownAlert(monitor))
        self._api_down = True

    def set_api_as_up(self, monitor: str, channels: ChannelSet) -> None:

        self._logger.debug('%s set_api_as_down: api_down(currently)=%s, '
                           'channels=%s', self, self._api_down, channels)

        if self._api_down:
            channels.alert_info(ApiIsUpAgainAlert(monitor))
        self._api_down = False
