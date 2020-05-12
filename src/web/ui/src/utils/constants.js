const ALERTS_CONFIG_SECTION_NAMES = {
  severities_enabled_disabled: 'Severities',
  access_to_nodes_alerts_enabled_disabled: 'Node Access Alerts',
  bonded_balance_alerts_enabled_disabled: 'Bonded Balance Alerts',
  no_of_peers_alerts_enabled_disabled: 'Number of Peers Alerts',
  is_syncing_alerts_enabled_disabled: 'Is Syncing Alerts',
  session_alerts_enabled_disabled: 'Session Alerts',
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
  LastAuthoredBlockInSessionAlert: 'Last authored block was long ago',
  NoBlocksHaveYetBeenAuthoredInSessionAlert: 'No blocks authored',
  ANewBlockHasNowBeenAuthoredByValidatorAlert:
    'A new block has now been authored',
  ValidatorHasBeenDisabledInSessionAlert: 'Validator disabled',
  ValidatorIsNoLongerDisabledInSessionAlert: 'Validator no longer disabled',
  ValidatorHasBeenSlashedAlert: 'Validator slashed',
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

const MONITOR_TYPES = {
  blockchain_monitor: 'Blockchain Monitor',
  node_monitor: 'Node monitor',
};

const PICO = 10 ** -12;

export {
  ALERTS_CONFIG_SECTION_NAMES,
  ALERTS_CONFIG_ALERT_NAMES,
  MONITOR_TYPES,
  PICO,
};
