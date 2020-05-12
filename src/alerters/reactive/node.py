import logging
from datetime import timedelta
from typing import Optional

from src.alerts.alerts import *
from src.channels.channel import ChannelSet
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import *
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.datetime import strfdelta
from src.utils.scaling import scale_to_tera, scale_to_pico
from src.utils.timing import TimedTaskLimiter
from src.utils.types import NONE


class NodeType(Enum):
    VALIDATOR_FULL_NODE = 1,
    NON_VALIDATOR_FULL_NODE = 2


class Node:
    def __init__(self, name: str, ws_url: Optional[str], node_type: NodeType,
                 stash_account_address: Optional[str], chain: str,
                 redis: Optional[RedisApi], is_archive_node: bool,
                 internal_conf: InternalConfig = InternalConf) -> None:
        super().__init__()

        self.name = name
        self._ws_url = ws_url
        self._node_type = node_type
        self._stash_account_address = stash_account_address
        self._chain = chain
        self._redis = redis
        self._redis_enabled = redis is not None
        self._redis_hash = Keys.get_hash_blockchain(self.chain)

        self._went_down_at = None
        self._bonded_balance = None
        self._is_syncing = False
        self._no_of_peers = None
        self._initial_downtime_alert_sent = False

        self._no_change_in_height_warning_sent = False
        self._active = None
        self._disabled = None
        self._elected = None
        self._council_member = None
        self._no_of_blocks_authored = 0
        self._finalized_block_height = 0
        self._time_of_last_block = NONE
        self._time_of_last_block_check_activity = NONE
        self._time_of_last_height_check_activity = NONE
        self._time_of_last_height_change = NONE

        self._auth_index = NONE
        self._is_authoring = True
        self._is_archive_node = is_archive_node

        self._validator_peer_danger_boundary = \
            internal_conf.validator_peer_danger_boundary
        self._validator_peer_safe_boundary = \
            internal_conf.validator_peer_safe_boundary
        self._full_node_peer_danger_boundary = \
            internal_conf.full_node_peer_danger_boundary
        self._max_time_between_blocks_authored = \
            internal_conf.max_time_alert_between_blocks_authored
        self._no_change_in_height_first_warning_seconds = \
            internal_conf.no_change_in_height_first_warning_seconds
        self._no_change_in_height_interval_seconds = \
            internal_conf.no_change_in_height_interval_seconds

        self._downtime_alert_limiter = TimedTaskLimiter(
            internal_conf.downtime_alert_time_interval)
        self._blocks_authored_alert_limiter = TimedTaskLimiter(
            self._max_time_between_blocks_authored)
        self._finalized_height_alert_limiter = TimedTaskLimiter(
            timedelta(seconds=int(self._no_change_in_height_interval_seconds)))

        self._change_in_bonded_balance_threshold = \
            internal_conf.change_in_bonded_balance_threshold

    def __str__(self) -> str:
        return self.name

    @property
    def is_validator(self) -> bool:
        return self._node_type == NodeType.VALIDATOR_FULL_NODE

    @property
    def is_archive_node(self) -> bool:
        return self._is_archive_node

    @property
    def is_down(self) -> bool:
        return self._went_down_at is not None

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def is_elected(self) -> bool:
        return self._elected

    @property
    def is_disabled(self) -> bool:
        return self._disabled

    @property
    def is_syncing(self) -> bool:
        return self._is_syncing

    @property
    def is_council_member(self) -> bool:
        return self._council_member

    @property
    def bonded_balance(self) -> int:
        return self._bonded_balance

    @property
    def blocks_authored_alert_limiter(self) -> TimedTaskLimiter:
        return self._blocks_authored_alert_limiter

    @property
    def finalized_height_alert_limiter(self) -> TimedTaskLimiter:
        return self._finalized_height_alert_limiter

    @property
    def stash_account_address(self) -> str:
        return self._stash_account_address

    @property
    def ws_url(self) -> str:
        return self._ws_url

    @property
    def no_of_peers(self) -> int:
        return self._no_of_peers

    @property
    def chain(self) -> str:
        return self._chain

    @property
    def no_of_blocks_authored(self) -> int:
        return self._no_of_blocks_authored

    @property
    def auth_index(self) -> int:
        return self._auth_index

    @property
    def is_authoring(self) -> bool:
        return self._is_authoring

    @property
    def is_no_change_in_height_warning_sent(self) -> bool:
        return self._no_change_in_height_warning_sent

    @property
    def finalized_block_height(self) -> int:
        return self._finalized_block_height

    def set_time_of_last_block(self, time_of_last_block: float,
                               channels: ChannelSet, logger: logging.Logger) \
            -> None:

        logger.debug('%s set_time_of_last_block: time_of_last_block(currently)'
                     '=%s, channels=%s', self, self._time_of_last_block,
                     channels)

        self._time_of_last_block = time_of_last_block

    def set_is_authoring(self, is_authoring: bool, channels: ChannelSet,
                         logger: logging.Logger) -> None:

        logger.debug('%s set_is_authoring: is_authoring(currently)=%s, '
                     'channels=%s', self, self._is_authoring, channels)

        self._is_authoring = is_authoring

    def set_time_of_last_block_check_activity(
            self, time_of_last_block_check_activity: float,
            channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug('%s set_time_of_last_block_check_activity: '
                     'time_of_last_block_check_activity(currently)=%s, '
                     'channels=%s', self,
                     self._time_of_last_block_check_activity, channels)

        self._time_of_last_block_check_activity = \
            time_of_last_block_check_activity

    def status(self) -> str:
        return "bonded_balance={}, is_syncing={}, no_of_peers={}, " \
               "active={}, council_member={}, elected={}, disabled={}, " \
               "no_of_blocks_authored={}, finalized_block_height={}". \
            format(self.bonded_balance, self.is_syncing, self.no_of_peers,
                   self.is_active, self.is_council_member, self.is_elected,
                   self.is_disabled, self.no_of_blocks_authored,
                   self.finalized_block_height)

    def load_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, load any previously stored state
        if self._redis_enabled:
            self._went_down_at = self._redis.hget(
                self._redis_hash, Keys.get_node_went_down_at(self.name), None)
            self._bonded_balance = self._redis.hget_int(
                self._redis_hash, Keys.get_node_bonded_balance(self.name), None)
            self._is_syncing = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_is_syncing(self.name), False)
            self._no_of_peers = self._redis.hget_int(
                self._redis_hash, Keys.get_node_no_of_peers(self.name), None)
            self._active = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_active(self.name), None)
            self._council_member = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_council_member(self.name), None)
            self._elected = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_elected(self.name), None)
            self._disabled = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_disabled(self.name), None)
            self._no_of_blocks_authored = self._redis.hget_int(
                self._redis_hash, Keys.get_node_blocks_authored(self.name), 0)
            self._time_of_last_block = float(self._redis.hget(
                self._redis_hash,
                Keys.get_node_time_of_last_block(self.name), NONE))
            self._is_authoring = self._redis.hget_bool(
                self._redis_hash, Keys.get_node_is_authoring(self.name), True)
            self._time_of_last_block_check_activity = float(self._redis.hget(
                self._redis_hash,
                Keys.get_node_time_of_last_block_check_activity(self.name),
                NONE))
            self._time_of_last_height_check_activity = float(self._redis.hget(
                self._redis_hash,
                Keys.get_node_time_of_last_height_check_activity(self.name),
                NONE))
            self._time_of_last_height_change = float(self._redis.hget(
                self._redis_hash,
                Keys.get_node_time_of_last_height_change(self.name), NONE))
            self._finalized_block_height = self._redis.hget_int(
                self._redis_hash,
                Keys.get_node_finalized_block_height(self.name), 0)
            self._no_change_in_height_warning_sent = self._redis.hget_bool(
                self._redis_hash,
                Keys.get_node_no_change_in_height_warning_sent(self.name),
                False)
            self._auth_index = self._redis.hget_int(
                self._redis_hash, Keys.get_node_auth_index(self.name), NONE)

            if self._time_of_last_block_check_activity != NONE:
                self.blocks_authored_alert_limiter. \
                    set_last_time_that_did_task(datetime.fromtimestamp(
                    self._time_of_last_block_check_activity))
            else:
                self.blocks_authored_alert_limiter.did_task()

            if self._time_of_last_height_check_activity != NONE:
                self._finalized_height_alert_limiter.set_last_time_that_did_task(
                    datetime.fromtimestamp(
                        self._time_of_last_height_check_activity))
            else:
                self._finalized_height_alert_limiter.did_task()
                self._time_of_last_height_change = datetime.now().timestamp()

            # To avoid the return of byte hget values.
            if self._went_down_at is not None:
                self._went_down_at = float(self._went_down_at)

            logger.debug(
                'Restored %s state: _went_down_at=%s,  _bonded_balance=%s, '
                '_is_syncing=%s, _no_of_peers=%s, _active=%s, _council_member'
                '=%s, _elected=%s, _disabled=%s, _no_of_blocks_authored=%s,'
                ' _time_of_last_block=%s, _is_authoring=%s, _'
                '_time_of_last_block_check_activity=%s, '
                '_time_of_last_height_change=%s, '
                '_time_of_last_height_check_activity, '
                '_finalized_block_height=%s,'
                ' _no_change_in_height_warning_sent=%s, _auth_index=%s',
                self.name, self._went_down_at, self._bonded_balance,
                self._is_syncing, self._no_of_peers, self._active,
                self._council_member, self._elected, self._disabled,
                self._no_of_blocks_authored, self._time_of_last_block,
                self._is_authoring, self._time_of_last_block_check_activity,
                self._time_of_last_height_change,
                self._time_of_last_height_check_activity,
                self._finalized_block_height,
                self._no_change_in_height_warning_sent, self._auth_index)

    def save_state(self, logger: logging.Logger) -> None:
        # If Redis is enabled, store the current state
        if self._redis_enabled:
            logger.debug(
                'Saving %s state: _went_down_at=%s,  _bonded_balance=%s, '
                '_is_syncing=%s, _no_of_peers=%s, _active=%s, _council_member'
                '=%s, _elected=%s, _disabled=%s, _no_of_blocks_authored=%s,'
                ' _time_of_last_block=%s, _is_authoring=%s, _'
                '_time_of_last_block_check_activity=%s, '
                '_time_of_last_height_change=%s, '
                '_time_of_last_height_check_activity, '
                '_finalized_block_height=%s,'
                ' _no_change_in_height_warning_sent=%s, _auth_index=%s',
                self.name, self._went_down_at, self._bonded_balance,
                self._is_syncing, self._no_of_peers, self._active,
                self._council_member, self._elected, self._disabled,
                self._no_of_blocks_authored, self._time_of_last_block,
                self._is_authoring, self._time_of_last_block_check_activity,
                self._time_of_last_height_change,
                self._time_of_last_height_check_activity,
                self._finalized_block_height,
                self._no_change_in_height_warning_sent, self._auth_index)

            # Set values
            self._redis.hset_multiple(self._redis_hash, {
                Keys.get_node_went_down_at(self.name): str(self._went_down_at),
                Keys.get_node_bonded_balance(self.name): self._bonded_balance,
                Keys.get_node_is_syncing(self.name): str(self._is_syncing),
                Keys.get_node_no_of_peers(self.name): self._no_of_peers,
                Keys.get_node_active(self.name): str(self._active),
                Keys.get_node_council_member(self.name):
                    str(self._council_member),
                Keys.get_node_elected(self.name): str(self._elected),
                Keys.get_node_disabled(self.name): str(self._disabled),
                Keys.get_node_blocks_authored(self.name):
                    self._no_of_blocks_authored,
                Keys.get_node_time_of_last_block(self.name):
                    self._time_of_last_block,
                Keys.get_node_is_authoring(self.name): str(self._is_authoring),
                Keys.get_node_time_of_last_block_check_activity(self.name):
                    self._time_of_last_block_check_activity,
                Keys.get_node_time_of_last_height_check_activity(self.name):
                    self._time_of_last_height_check_activity,
                Keys.get_node_time_of_last_height_change(self.name):
                    self._time_of_last_height_change,
                Keys.get_node_finalized_block_height(self.name):
                    self._finalized_block_height,
                Keys.get_node_no_change_in_height_warning_sent(self.name):
                    str(self._no_change_in_height_warning_sent),
                Keys.get_node_auth_index(self.name): self._auth_index
            })

    def set_as_down(self, channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug('%s set_as_down: is_down(currently)=%s, channels=%s',
                     self, self.is_down, channels)

        # Alert (varies depending on whether was already down)
        if self.is_down and not self._initial_downtime_alert_sent:
            if self.is_validator:
                channels.alert_critical(CannotAccessNodeAlert(self.name))
            else:
                channels.alert_warning(CannotAccessNodeAlert(self.name))
            self._downtime_alert_limiter.did_task()
            self._initial_downtime_alert_sent = True
        elif self.is_down and self._downtime_alert_limiter.can_do_task():
            went_down_at = datetime.fromtimestamp(self._went_down_at)
            downtime = strfdelta(datetime.now() - went_down_at,
                                 "{hours}h, {minutes}m, {seconds}s")
            if self.is_validator:
                channels.alert_critical(StillCannotAccessNodeAlert(
                    self.name, went_down_at, downtime))
            else:
                channels.alert_warning(StillCannotAccessNodeAlert(
                    self.name, went_down_at, downtime))
            self._downtime_alert_limiter.did_task()
        elif not self.is_down:
            # Do not alert for now just in case this is a connection hiccup
            channels.alert_info(ExperiencingDelaysAlert(self.name))
            self._went_down_at = datetime.now().timestamp()
            self._initial_downtime_alert_sent = False

    def set_as_up(self, channels: ChannelSet, logger: logging.Logger) -> None:

        logger.debug('%s set_as_up: is_down(currently)=%s, channels=%s',
                     self, self.is_down, channels)

        # Alert if node was down
        if self.is_down:
            # Only send accessible alert if inaccessible alert was sent
            if self._initial_downtime_alert_sent:
                went_down_at = datetime.fromtimestamp(self._went_down_at)
                downtime = strfdelta(datetime.now() - went_down_at,
                                     "{hours}h, {minutes}m, {seconds}s")
                channels.alert_info(NowAccessibleAlert(
                    self.name, went_down_at, downtime))

            # Reset downtime-related values
            self._downtime_alert_limiter.reset()
            self._went_down_at = None

    def set_bonded_balance(self, new_bonded_balance: int, channels: ChannelSet,
                           logger: logging.Logger) -> None:

        logger.debug(
            '%s set_bonded_balance: before=%s, new=%s, channels=%s',
            self, self.bonded_balance, new_bonded_balance, channels)

        # Alert if bonded_balance has changed
        if self.bonded_balance not in [None, new_bonded_balance]:
            # Extracted data is in tera, therefore, to give more meaningful
            # alerts, the bonded balance will be scaled down.
            threshold = scale_to_tera(self._change_in_bonded_balance_threshold)
            scaled_new_bal = round(scale_to_pico(new_bonded_balance), 3)
            scaled_bal = round(scale_to_pico(self.bonded_balance), 3)

            if self.is_validator and new_bonded_balance == 0:  # N to 0
                channels.alert_critical(BondedBalanceDecreasedAlert(
                    self.name, scaled_bal, scaled_new_bal))
            elif self.is_validator and self.bonded_balance == 0:  # 0 to N
                channels.alert_info(BondedBalanceIncreasedAlert(
                    self.name, scaled_bal, scaled_new_bal))
            else:  # Any change
                diff = new_bonded_balance - self.bonded_balance
                if abs(diff) > threshold:
                    if diff > 0:
                        channels.alert_info(BondedBalanceIncreasedByAlert(
                            self.name, scaled_bal, scaled_new_bal))
                    else:
                        channels.alert_info(BondedBalanceDecreasedByAlert(
                            self.name, scaled_bal, scaled_new_bal))

        # Update bonded balance
        self._bonded_balance = new_bonded_balance

    def set_is_syncing(self, now_is_syncing: bool, channels: ChannelSet,
                       logger: logging.Logger) -> None:
        logger.debug(
            '%s set_is_syncing: before=%s, new=%s, channels=%s',
            self, self.is_syncing, now_is_syncing, channels)

        # Alert if is syncing has changed
        if not self.is_syncing and now_is_syncing:
            channels.alert_warning(IsSyncingAlert(self.name))
        elif self.is_syncing and not now_is_syncing:
            channels.alert_info(IsNoLongerSyncingAlert(self.name))

        # Update is-syncing
        self._is_syncing = now_is_syncing

    def set_no_of_peers(self, new_no_of_peers: int, channels: ChannelSet,
                        logger: logging.Logger) -> None:

        logger.debug(
            '%s set_no_of_peers: before=%s, new=%s, channels=%s',
            self, self.no_of_peers, new_no_of_peers, channels)

        # Variable alias for improved readability
        if self.is_validator:
            danger = self._validator_peer_danger_boundary
            safe = self._validator_peer_safe_boundary
        else:
            danger = self._full_node_peer_danger_boundary
            safe = None

        # Alert if number of peers has changed
        if self.no_of_peers not in [None, new_no_of_peers]:
            if self.is_validator:
                if new_no_of_peers <= self._validator_peer_safe_boundary:
                    # beneath safe boundary
                    if new_no_of_peers > self.no_of_peers:  # increase
                        channels.alert_info(PeersIncreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    elif new_no_of_peers > danger:
                        # decrease outside danger range
                        channels.alert_warning(PeersDecreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    else:  # decrease inside danger range
                        channels.alert_critical(PeersDecreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                elif self._no_of_peers <= self._validator_peer_safe_boundary \
                        < new_no_of_peers:
                    # increase outside safe range for the first time
                    channels.alert_info(
                        PeersIncreasedOutsideSafeRangeAlert(self.name, safe))
            else:
                if new_no_of_peers > self.no_of_peers:  # increase
                    if new_no_of_peers <= danger:
                        # increase inside danger range
                        channels.alert_info(PeersIncreasedAlert(
                            self.name, self.no_of_peers, new_no_of_peers))
                    elif self.no_of_peers <= danger < new_no_of_peers:
                        # increase outside danger range
                        channels.alert_info(
                            PeersIncreasedOutsideDangerRangeAlert(
                                self.name, danger))
                elif new_no_of_peers > danger:  # decrease outside danger range
                    pass
                else:  # decrease inside danger range
                    channels.alert_warning(PeersDecreasedAlert(
                        self.name, self.no_of_peers, new_no_of_peers))

        # Update number of peers
        self._no_of_peers = new_no_of_peers

    def set_active(self, now_is_active: bool, channels: ChannelSet,
                   logger: logging.Logger) -> None:
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s set_active: active(currently)=%s, channels=%s',
                     self, self.is_active, channels)

        if self.is_active not in [now_is_active, None]:
            if now_is_active:
                channels.alert_info(ValidatorIsNowActiveAlert(self.name))
            else:
                channels.alert_critical(ValidatorIsNotActiveAlert(self.name))
        self._active = now_is_active

    def set_elected(self, now_is_elected: bool, channels: ChannelSet,
                    logger: logging.Logger) -> None:
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s set_elected: elected(currently)=%s, channels=%s',
                     self, self.is_elected, channels)

        if self.is_elected not in [now_is_elected, None]:
            if now_is_elected:
                channels.alert_info(
                    ValidatorIsElectedForTheNextSessionAlert(self.name))
            else:
                channels.alert_warning(
                    ValidatorIsNotElectedForNextSessionAlert(self.name))
        self._elected = now_is_elected

    def set_council_member(self, now_is_council_member: bool,
                           channels: ChannelSet, logger: logging.Logger):
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s set_council_member: council_member(currently)=%s, '
                     'channels=%s', self, self.is_council_member, channels)

        if self.is_council_member not in [now_is_council_member, None]:
            if now_is_council_member:
                channels.alert_info(
                    ValidatorIsNowPartOfTheCouncilAlert(self.name))
            else:
                channels.alert_info(
                    ValidatorIsNoLongerPartOfTheCouncilAlert(self.name))
        self._council_member = now_is_council_member

    def set_no_of_blocks_authored(self, channels: ChannelSet,
                                  logger: logging.Logger,
                                  new_no_of_blocks_authored: int,
                                  session_index: int):
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s set_no_of_blocks_authored: no_of_blocks_'
                     'authored(currently)=%s, channels=%s', self,
                     self._no_of_blocks_authored, channels)

        if self.is_active:
            if self._no_of_blocks_authored < new_no_of_blocks_authored:
                self._no_of_blocks_authored = new_no_of_blocks_authored
                self._time_of_last_block = datetime.now().timestamp()
                self.blocks_authored_alert_limiter.did_task()
                self._time_of_last_block_check_activity = \
                    datetime.now().timestamp()
                if self._is_authoring is False:
                    self._is_authoring = True
                    channels.alert_info(
                        ANewBlockHasNowBeenAuthoredByValidatorAlert(self.name))
            elif self._no_of_blocks_authored == \
                    new_no_of_blocks_authored and \
                    self.blocks_authored_alert_limiter.can_do_task():
                if self._time_of_last_block != NONE:
                    time_interval = strfdelta(
                        datetime.now() - datetime.fromtimestamp(
                            self._time_of_last_block),
                        "{hours}h, {minutes}m, {seconds}s")
                    channels.alert_warning(
                        LastAuthoredBlockInSessionAlert(
                            self.name, time_interval, session_index))
                else:
                    channels.alert_warning(
                        NoBlocksHaveYetBeenAuthoredInSessionAlert(
                            self.name, session_index))
                self._is_authoring = False
                self.blocks_authored_alert_limiter.did_task()
                self._time_of_last_block_check_activity = \
                    datetime.now().timestamp()

    def reset_no_of_blocks_authored(self, channels: ChannelSet,
                                    logger: logging.Logger):
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s reset_no_of_blocks_authored: no_of_blocks_'
                     'authored(currently)=%s, channels=%s', self,
                     self._no_of_blocks_authored, channels)

        self._no_of_blocks_authored = 0

    def set_auth_index(self, new_auth_index: int, logger: logging.Logger):
        logger.debug('%s set_auth_index: auth_index(currently)=%s',
                     self, self._auth_index)
        if self.is_active:
            self._auth_index = new_auth_index

    def update_finalized_block_height(self, new_finalized_height: int,
                                      logger: logging.Logger,
                                      channels: ChannelSet):
        logger.debug('%s update_finalized_block_height: finalized_block_height'
                     ' (currently)=%s', self, self._finalized_block_height)

        current_timestamp = datetime.now().timestamp()
        if self._finalized_block_height != new_finalized_height:
            if self.is_no_change_in_height_warning_sent:
                self._no_change_in_height_warning_sent = False
                channels.alert_info(
                    NodeFinalizedBlockHeightHasNowBeenUpdatedAlert(self.name))
            if self._finalized_block_height > new_finalized_height:
                logger.info('The finalized height of node {} decreased to {}.'
                            .format(self, self._finalized_block_height))
            self._finalized_block_height = new_finalized_height
            self._time_of_last_height_change = current_timestamp
            self._time_of_last_height_check_activity = current_timestamp
            self._finalized_height_alert_limiter.set_last_time_that_did_task(
                datetime.fromtimestamp(current_timestamp))
        else:
            timestamp_difference = current_timestamp - \
                                   self._time_of_last_height_change
            time_interval = strfdelta(timedelta(seconds=int(
                timestamp_difference)), "{hours}h, {minutes}m, {seconds}s")

            if not self.is_no_change_in_height_warning_sent and \
                    timestamp_difference > \
                    self._no_change_in_height_first_warning_seconds:
                self._no_change_in_height_warning_sent = True
                channels.alert_warning(
                    NodeFinalizedBlockHeightDidNotChangeInAlert(self.name,
                                                                time_interval))
            elif self._finalized_height_alert_limiter.can_do_task() and \
                    self.is_no_change_in_height_warning_sent:
                if self.is_validator:
                    channels.alert_critical(
                        NodeFinalizedBlockHeightDidNotChangeInAlert(
                            self.name, time_interval))
                else:
                    channels.alert_warning(
                        NodeFinalizedBlockHeightDidNotChangeInAlert(
                            self.name, time_interval))
                self._time_of_last_height_check_activity = current_timestamp
                self._finalized_height_alert_limiter. \
                    set_last_time_that_did_task(
                    datetime.fromtimestamp(current_timestamp))

    def set_disabled(self, now_is_disabled: bool, session: int,
                     channels: ChannelSet, logger: logging.Logger):
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s set_disabled: _disabled(currently)=%s, '
                     'channels=%s', self, self.is_disabled, channels)

        if self.is_disabled not in [now_is_disabled, None]:
            if now_is_disabled:
                channels.alert_critical(
                    ValidatorHasBeenDisabledInSessionAlert(self.name, session))
            else:
                channels.alert_info(
                    ValidatorIsNoLongerDisabledInSessionAlert(
                        self.name, session))
        self._disabled = now_is_disabled

    def slash(self, amount: float, channels: ChannelSet,
              logger: logging.Logger):
        # NOTE: This function assumes that the node is a validator.

        logger.debug('%s slash: channels=%s', self, channels)

        if amount > 0:
            channels.alert_critical(
                ValidatorHasBeenSlashedAlert(self.name, amount))
