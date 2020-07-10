import PropTypes from 'prop-types';

const ALERTS_CONFIG_SECTION_NAMES = {
  severities_enabled_disabled: 'Severities',
  access_to_nodes_alerts_enabled_disabled: 'Node Access Alerts',
  bonded_balance_alerts_enabled_disabled: 'Bonded Balance Alerts',
  no_of_peers_alerts_enabled_disabled: 'Number of Peers Alerts',
  is_syncing_alerts_enabled_disabled: 'Is Syncing Alerts',
  session_alerts_enabled_disabled: 'Session Alerts',
  era_alerts_enabled_disabled: 'Era Alerts',
  blockchain_alerts_enabled_disabled: 'Blockchain Alerts',
  finalized_block_height_alerts_enabled_disabled: 'Finalized Height Alerts',
  twilio_alerts_enabled_disabled: 'Twilio Alerts',
  github_alerts_enabled_disabled: 'GitHub Alerts',
  periodic_alive_reminder_alerts_enabled_disabled:
    'Periodic Alive Reminder Alerts',
  api_server_alerts_enabled_disabled: 'API Server Alerts',
  other_alerts_enabled_disabled: 'Other Alerts',
};

const ALERTS_CONFIG_ALERT_NAMES = {
  Info: 'Info',
  Warning: 'Warning',
  Critical: 'Critical',
  Error: 'Error',
  ExperiencingDelaysAlert: 'Node experiencing delays',
  CannotAccessNodeAlert: 'Cannot access node',
  StillCannotAccessNodeAlert: 'Still cannot access node',
  NowAccessibleAlert: 'Node accessible again',
  CouldNotFindLiveNodeConnectedToApiServerAlert:
    'No live node connected to the API server',
  CouldNotFindLiveArchiveNodeConnectedToApiServerAlert:
    'No live archive node connected to the API server',
  FoundLiveArchiveNodeAgainAlert: 'Found live archive node again',
  NodeWasNotConnectedToApiServerAlert: 'Node was not connected to API Server',
  NodeConnectedToApiServerAgainAlert: 'Node connected to API Server again',
  NodeInaccessibleDuringStartup: 'Node inaccessible during startup',
  BondedBalanceIncreasedAlert: 'Validator bonded balance increase',
  BondedBalanceDecreasedAlert: 'Validator bonded balance decrease',
  BondedBalanceIncreasedByAlert: 'Validator bonded balance increase by amount',
  BondedBalanceDecreasedByAlert: 'Validator bonded balance decrease by amount',
  PeersIncreasedAlert: 'Node peer increase',
  PeersIncreasedOutsideDangerRangeAlert:
    'Node peer increase outside danger range',
  PeersIncreasedOutsideSafeRangeAlert: 'Node peer increase outside safe range',
  PeersDecreasedAlert: 'Node peer decrease',
  IsSyncingAlert: 'Node is syncing',
  IsNoLongerSyncingAlert: 'Node is no longer syncing',
  ValidatorIsNotActiveAlert: 'Validator no longer active',
  ValidatorIsNowActiveAlert: 'Validator active',
  ValidatorIsNotElectedForNextSessionAlert: 'Validator not elected',
  ValidatorIsElectedForTheNextSessionAlert: 'Validator elected',
  ValidatorHasBeenDisabledInSessionAlert: 'Validator disabled',
  ValidatorIsNoLongerDisabledInSessionAlert: 'Validator no longer disabled',
  ValidatorHasBeenSlashedAlert: 'Validator slashed',
  LastAuthoredBlockInEraAlert: 'Last authored block was long ago',
  NoBlocksHaveYetBeenAuthoredInEraAlert: 'No blocks authored',
  ANewBlockHasNowBeenAuthoredByValidatorAlert:
    'A new block has now been authored',
  NewReferendumAlert: 'New referendum',
  NewPublicProposalAlert: 'New public proposal',
  NewCouncilProposalAlert: 'New council proposal',
  ValidatorIsNowPartOfTheCouncilAlert: 'Validator part of the council',
  ValidatorIsNoLongerPartOfTheCouncilAlert:
    'Validator no longer part of the council',
  ValidatorSetSizeDecreasedAlert: 'Validator set decrease',
  ValidatorSetSizeIncreasedAlert: 'Validator set increase',
  NodeFinalizedBlockHeightDidNotChangeInAlert: 'Finalized height not updating',
  NodeFinalizedBlockHeightHasNowBeenUpdatedAlert: 'Finalized height updated',
  ProblemWhenDialingNumberAlert: 'Problem when dialing number',
  ProblemWhenCheckingIfCallsAreSnoozedAlert:
    'Problem when checking if calls are snoozed',
  NewGitHubReleaseAlert: 'New GitHub release',
  CannotAccessGitHubPageAlert: 'GitHub page inaccessible',
  RepoInaccessibleDuringStartup: 'Repo inaccessible during startup',
  AlerterAliveAlert: 'Alerter still running',
  ApiIsDownAlert: 'API Server down',
  ApiIsUpAgainAlert: 'API Server up again',
  ErrorWhenReadingDataFromNode: 'Node data reading error',
  TerminatedDueToExceptionAlert: 'Exception termination',
  TerminatedDueToFatalExceptionAlert: 'Fatal exception termination',
  ProblemWithTelegramBot: 'Problem with Telegram bot',
  NodeIsNotAnArchiveNodeAlert: 'Node not an archive node',
  ProblemWithMongo: 'MongoDB problem',
  TestAlert: 'Test Alert',
};

const NAVBAR_NAV_ITEMS = {
  Dashboard: '/',
  Alerts: {
    Logs: '/alerts/logs',
    Preferences: '/alerts/preferences',
  },
  Settings: {
    Main: '/settings/main',
    Nodes: '/settings/nodes',
    Repos: '/settings/repositories',
  },
};

const SEVERITY_COLOUR_REPRESENTATION = {
  CRITICAL: '#EA4335',
  WARNING: '#FBBC05',
  ERROR: '#b9abc6',
  INFO: '#34A853',
};

const MONITOR_TYPES = {
  blockchain_monitor: 'Blockchain Monitor',
  node_monitor: 'Node monitor',
};

const NODE_CONFIG_TYPE = PropTypes.shape({
  node_name: PropTypes.string,
  chain_name: PropTypes.string,
  node_ws_url: PropTypes.string,
  node_is_validator: PropTypes.string,
  is_archive_node: PropTypes.string,
  monitor_node: PropTypes.string,
  use_as_data_source: PropTypes.string,
  stash_account_address: PropTypes.string,
});

const ALERT_TYPE = PropTypes.shape({
  severity_: PropTypes.string,
  message_: PropTypes.string,
  timestamp_: PropTypes.number,
});

const REPO_CONFIG_TYPE = PropTypes.shape({
  repo_name: PropTypes.string,
  repo_page: PropTypes.string,
  monitor_repo: PropTypes.string,
});

const BLOCKCHAIN_TYPE = PropTypes.shape({
  name: PropTypes.string,
  referendumCount: PropTypes.number,
  publicPropCount: PropTypes.number,
  councilPropCount: PropTypes.number,
  validatorSetSize: PropTypes.number,
});

const NODE_TYPE = PropTypes.shape({
  name: PropTypes.string,
  chain: PropTypes.string,
  isValidator: PropTypes.bool,
  wentDownAt: PropTypes.number,
  isDown: PropTypes.bool,
  isSyncing: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  noOfPeers: PropTypes.number,
  lastHeightUpdate: PropTypes.number,
  height: PropTypes.number,
  bondedBalance: PropTypes.number,
  isActive: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isDisabled: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isElected: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isCouncilMember: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  noOfBlocksAuthored: PropTypes.number,
});

const MONITOR_TYPE = PropTypes.shape({
  name: PropTypes.string,
  chain: PropTypes.string,
  lastUpdate: PropTypes.number,
});

const PICO = 10 ** -12;

export {
  ALERTS_CONFIG_SECTION_NAMES, ALERTS_CONFIG_ALERT_NAMES, MONITOR_TYPES,
  PICO, NAVBAR_NAV_ITEMS, SEVERITY_COLOUR_REPRESENTATION, NODE_CONFIG_TYPE,
  ALERT_TYPE, REPO_CONFIG_TYPE, BLOCKCHAIN_TYPE, NODE_TYPE, MONITOR_TYPE,
};
