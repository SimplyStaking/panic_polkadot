from datetime import datetime
from enum import Enum

_ALERT_ID = 0


def _next_id():
    global _ALERT_ID
    _ALERT_ID += 1
    return _ALERT_ID


class SeverityCode(Enum):
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    ERROR = 4


class AlertCode(Enum):
    ExperiencingDelaysAlert = _next_id(),
    CannotAccessNodeAlert = _next_id(),
    StillCannotAccessNodeAlert = _next_id(),
    NowAccessibleAlert = _next_id(),
    CouldNotFindLiveNodeConnectedToApiServerAlert = _next_id(),
    CouldNotFindLiveArchiveNodeConnectedToApiServerAlert = _next_id(),
    FoundLiveArchiveNodeAgainAlert = _next_id(),
    NodeWasNotConnectedToApiServerAlert = _next_id(),
    NodeConnectedToApiServerAgainAlert = _next_id(),
    NodeInaccessibleDuringStartup = _next_id(),
    BondedBalanceIncreasedAlert = _next_id(),
    BondedBalanceDecreasedAlert = _next_id(),
    BondedBalanceIncreasedByAlert = _next_id(),
    BondedBalanceDecreasedByAlert = _next_id(),
    PeersIncreasedAlert = _next_id(),
    PeersIncreasedOutsideDangerRangeAlert = _next_id(),
    PeersIncreasedOutsideSafeRangeAlert = _next_id(),
    PeersDecreasedAlert = _next_id(),
    IsSyncingAlert = _next_id(),
    IsNoLongerSyncingAlert = _next_id(),
    ValidatorIsNotActiveAlert = _next_id(),
    ValidatorIsNowActiveAlert = _next_id(),
    ValidatorIsNotElectedForNextSessionAlert = _next_id(),
    ValidatorIsElectedForTheNextSessionAlert = _next_id(),
    ValidatorHasBeenDisabledInSessionAlert = _next_id(),
    ValidatorIsNoLongerDisabledInSessionAlert = _next_id(),
    ValidatorHasBeenSlashedAlert = _next_id(),
    LastAuthoredBlockInEraAlert = _next_id(),
    NoBlocksHaveYetBeenAuthoredInEraAlert = _next_id(),
    ANewBlockHasNowBeenAuthoredByValidatorAlert = _next_id(),
    NewReferendumAlert = _next_id(),
    NewPublicProposalAlert = _next_id(),
    NewCouncilProposalAlert = _next_id(),
    ValidatorIsNowPartOfTheCouncilAlert = _next_id(),
    ValidatorIsNoLongerPartOfTheCouncilAlert = _next_id(),
    ValidatorSetSizeDecreasedAlert = _next_id(),
    ValidatorSetSizeIncreasedAlert = _next_id(),
    NodeFinalizedBlockHeightDidNotChangeInAlert = _next_id(),
    NodeFinalizedBlockHeightHasNowBeenUpdatedAlert = _next_id(),
    ProblemWhenDialingNumberAlert = _next_id(),
    ProblemWhenCheckingIfCallsAreSnoozedAlert = _next_id(),
    NewGitHubReleaseAlert = _next_id(),
    CannotAccessGitHubPageAlert = _next_id(),
    RepoInaccessibleDuringStartup = _next_id(),
    AlerterAliveAlert = _next_id(),
    ApiIsUpAgainAlert = _next_id(),
    ApiIsDownAlert = _next_id(),
    ErrorWhenReadingDataFromNode = _next_id(),
    TerminatedDueToExceptionAlert = _next_id(),
    TerminatedDueToFatalExceptionAlert = _next_id(),
    ProblemWithTelegramBot = _next_id(),
    NodeIsNotAnArchiveNodeAlert = _next_id(),
    ProblemWithMongo = _next_id()
    TestAlert = _next_id()


class Alert:

    def __init__(self, alert_code: AlertCode, message: str) -> None:
        self._alert_code = alert_code
        self._message = message

    @property
    def alert_code(self) -> AlertCode:
        return self._alert_code

    @property
    def message(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self.message


class ExperiencingDelaysAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ExperiencingDelaysAlert,
            'Experiencing delays when trying to access {}.'.format(node))


class CannotAccessNodeAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.CannotAccessNodeAlert,
            'I cannot access {}.'.format(node))


class StillCannotAccessNodeAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            AlertCode.StillCannotAccessNodeAlert,
            'I still cannot access {}. Node became inaccessible at {} '
            'and has been inaccessible for (at most) {}.'.format(
                node, went_down_at, downtime))


class NowAccessibleAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            AlertCode.NowAccessibleAlert,
            '{} is now accessible. Node became inaccessible '
            'at {} and was inaccessible for (at most) {}.'
            ''.format(node, went_down_at, downtime))


class CouldNotFindLiveNodeConnectedToApiServerAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__(
            AlertCode.CouldNotFindLiveNodeConnectedToApiServerAlert,
            '{} could not find a live node connected to the API '
            'Server to use as a data source.'.format(monitor))


class CouldNotFindLiveArchiveNodeConnectedToApiServerAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__(
            AlertCode.CouldNotFindLiveArchiveNodeConnectedToApiServerAlert,
            '{} could not find a live archive node connected to the API '
            'Server. Slashing alerts will now be disabled temporarily as these '
            'require data from previous blocks. Other functionality will '
            'continue running normally.'.format(monitor))


class FoundLiveArchiveNodeAgainAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__(
            AlertCode.FoundLiveArchiveNodeAgainAlert,
            '{} found an archive node. This means that archive monitoring '
            '(which includes slashing) is now enabled.'.format(monitor))


class NodeWasNotConnectedToApiServerAlert(Alert):

    def __init__(self, node_name: str) -> None:
        super().__init__(
            AlertCode.NodeWasNotConnectedToApiServerAlert,
            'Node {} was not connected with the API server. Please add the '
            'node to the API server nodes config and restart the API server.'
            ''.format(node_name))


class NodeConnectedToApiServerAgainAlert(Alert):

    def __init__(self, node_name: str) -> None:
        super().__init__(
            AlertCode.NodeConnectedToApiServerAgainAlert,
            'Node {} was connected with the API server again.'
            ''.format(node_name))


class NodeInaccessibleDuringStartup(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.NodeInaccessibleDuringStartup,
            'Node {} was not accessible during PANIC startup. {} will NOT be '
            'monitored until it is accessible and PANIC restarted afterwards. '
            'Some features of PANIC might be affected.'.format(node, node))


class BondedBalanceIncreasedAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        super().__init__(
            AlertCode.BondedBalanceIncreasedAlert,
            '{} total bonded balance INCREASED from {} to {}.'.format(
                node, old_balance, new_balance))


class BondedBalanceDecreasedAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        super().__init__(
            AlertCode.BondedBalanceDecreasedAlert,
            '{} total bonded balance DECREASED from {} to {}.'.format(
                node, old_balance, new_balance))


class BondedBalanceIncreasedByAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        change = round(new_balance - old_balance, 3)
        super().__init__(
            AlertCode.BondedBalanceIncreasedByAlert,
            '{} total bonded balance INCREASED by {} from {} to {}.'.format(
                node, change, old_balance, new_balance))


class BondedBalanceDecreasedByAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        change = round(old_balance - new_balance, 3)
        super().__init__(
            AlertCode.BondedBalanceDecreasedByAlert,
            '{} total bonded balance DECREASED by {} from {} to {}.'.format(
                node, change, old_balance, new_balance))


class PeersIncreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            AlertCode.PeersIncreasedAlert,
            '{} peers INCREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class PeersIncreasedOutsideDangerRangeAlert(Alert):

    def __init__(self, node: str, danger: int) -> None:
        super().__init__(
            AlertCode.PeersIncreasedOutsideDangerRangeAlert,
            '{} peers INCREASED to more than {} peers. No further peer change '
            'alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, danger, danger))


class PeersIncreasedOutsideSafeRangeAlert(Alert):

    def __init__(self, node: str, safe: int) -> None:
        super().__init__(
            AlertCode.PeersIncreasedOutsideSafeRangeAlert,
            '{} peers INCREASED to more than {} peers. No further peer change'
            ' alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, safe, safe))


class PeersDecreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            AlertCode.PeersDecreasedAlert,
            '{} peers DECREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class IsSyncingAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.IsSyncingAlert,
            '{} is in syncing state.'.format(node))


class IsNoLongerSyncingAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.IsNoLongerSyncingAlert,
            '{} is no longer syncing.'.format(node))


class ValidatorIsNotActiveAlert(Alert):
    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ValidatorIsNotActiveAlert,
            '{} is not active in this session.'.format(node))


class ValidatorIsNowActiveAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ValidatorIsNowActiveAlert,
            '{} is now active in this session.'.format(node))


class ValidatorIsNotElectedForNextSessionAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ValidatorIsNotElectedForNextSessionAlert,
            '{} was not elected to validate in the next session. '
            '{} needs a higher bonded balance for it to be elected.'
                .format(node, node))


class ValidatorIsElectedForTheNextSessionAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ValidatorIsElectedForTheNextSessionAlert,
            '{} was elected to validate in the next session.'
            ''.format(node, node))


class ValidatorHasBeenDisabledInSessionAlert(Alert):

    def __init__(self, node: str, session: int) -> None:
        super().__init__(
            AlertCode.ValidatorHasBeenDisabledInSessionAlert,
            'Validator {} has been disabled in session {}'
            ''.format(node, session))


class ValidatorIsNoLongerDisabledInSessionAlert(Alert):

    def __init__(self, node: str, session: int) -> None:
        super().__init__(
            AlertCode.ValidatorIsNoLongerDisabledInSessionAlert,
            'Validator {} is no longer disabled in session {}'
            ''.format(node, session))


class ValidatorHasBeenSlashedAlert(Alert):

    def __init__(self, node: str, amount: float):
        super().__init__(
            AlertCode.ValidatorHasBeenSlashedAlert,
            '{} has been slashed {}.'.format(node, amount))


class LastAuthoredBlockInEraAlert(Alert):

    def __init__(self, node: str, time_since_last_authored_block: str,
                 era: int) -> None:
        super().__init__(
            AlertCode.LastAuthoredBlockInEraAlert,
            'The last authored block in era {} by validator {} was at '
            'least {} ago.'.format(era, node, time_since_last_authored_block))


class NoBlocksHaveYetBeenAuthoredInEraAlert(Alert):

    def __init__(self, node: str, era: int) -> None:
        super().__init__(
            AlertCode.NoBlocksHaveYetBeenAuthoredInEraAlert,
            'No blocks have yet been authored by node {} in era {}.'
                .format(node, era))


class ANewBlockHasNowBeenAuthoredByValidatorAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ANewBlockHasNowBeenAuthoredByValidatorAlert,
            'Validator {} is now authoring blocks again.'.format(node))


class NewReferendumAlert(Alert):

    def __init__(self, referendum_number: int, end_block: int) -> None:
        super().__init__(
            AlertCode.NewReferendumAlert,
            'Referendum {} is now available. Voting will stop when block '
            'height {} is reached.'.format(referendum_number, end_block))


class NewPublicProposalAlert(Alert):

    def __init__(self, proposal_number: int):
        super().__init__(
            AlertCode.NewPublicProposalAlert,
            'Public proposal {} has been created.'.format(proposal_number))


class NewCouncilProposalAlert(Alert):

    def __init__(self, proposal_number: int):
        super().__init__(
            AlertCode.NewCouncilProposalAlert,
            'Council proposal {} has been created.'.format(proposal_number))


class ValidatorIsNowPartOfTheCouncilAlert(Alert):

    def __init__(self, node: str):
        super().__init__(
            AlertCode.ValidatorIsNowPartOfTheCouncilAlert,
            '{} is now part of the council'.format(node))


class ValidatorIsNoLongerPartOfTheCouncilAlert(Alert):

    def __init__(self, node: str):
        super().__init__(
            AlertCode.ValidatorIsNoLongerPartOfTheCouncilAlert,
            '{} is no longer part of the council'.format(node))


class ValidatorSetSizeDecreasedAlert(Alert):

    def __init__(self, set_size: int) -> None:
        super().__init__(
            AlertCode.ValidatorSetSizeDecreasedAlert,
            'The validator set size decreased to {}'.format(set_size))


class ValidatorSetSizeIncreasedAlert(Alert):

    def __init__(self, set_size: int) -> None:
        super().__init__(
            AlertCode.ValidatorSetSizeIncreasedAlert,
            'The validator set size increased to {}'.format(set_size))


class NodeFinalizedBlockHeightDidNotChangeInAlert(Alert):

    def __init__(self, node: str, time_of_last_update: str) -> None:
        super().__init__(
            AlertCode.NodeFinalizedBlockHeightDidNotChangeInAlert,
            'The finalized block height of node {} was updated at '
            'least {} ago.'.format(node, time_of_last_update))


class NodeFinalizedBlockHeightHasNowBeenUpdatedAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.NodeFinalizedBlockHeightHasNowBeenUpdatedAlert,
            'The finalized block height of node {} was updated.'.format(node))


class ProblemWhenDialingNumberAlert(Alert):

    def __init__(self, number: str, exception: Exception) -> None:
        super().__init__(
            AlertCode.ProblemWhenDialingNumberAlert,
            'Problem encountered when dialing {}: {}'.format(number, exception))


class ProblemWhenCheckingIfCallsAreSnoozedAlert(Alert):

    def __init__(self) -> None:
        super().__init__(
            AlertCode.ProblemWhenCheckingIfCallsAreSnoozedAlert,
            'Problem encountered when checking if calls are snoozed. '
            'Calling anyways.')


class NewGitHubReleaseAlert(Alert):

    def __init__(self, release_name: str, repo_name: str) -> None:
        super().__init__(
            AlertCode.NewGitHubReleaseAlert,
            '{} of {} has just been released.'.format(release_name, repo_name))


class CannotAccessGitHubPageAlert(Alert):

    def __init__(self, page: str) -> None:
        super().__init__(
            AlertCode.CannotAccessGitHubPageAlert,
            'I cannot access GitHub page {}.'.format(page))


class RepoInaccessibleDuringStartup(Alert):

    def __init__(self, repo: str) -> None:
        super().__init__(
            AlertCode.RepoInaccessibleDuringStartup,
            'Repo {} was not accessible during PANIC startup. {} will NOT be '
            'monitored until it is accessible and PANIC restarted afterwards. '
            ''.format(repo, repo))


class AlerterAliveAlert(Alert):

    def __init__(self) -> None:
        super().__init__(AlertCode.AlerterAliveAlert, 'Still running.')


class ApiIsUpAgainAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__(
            AlertCode.ApiIsUpAgainAlert,
            '{} connected with the API Server again.'.format(monitor))


class ApiIsDownAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__(
            AlertCode.ApiIsDownAlert,
            '{} lost connection with the API Server. Please make '
            'sure that the API Server is running, otherwise the '
            'monitor cannot retrieve data.'.format(monitor))


class ErrorWhenReadingDataFromNode(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            AlertCode.ErrorWhenReadingDataFromNode,
            'Error when reading data from {}. Alerter '
            'will continue running normally.'.format(node))


class TerminatedDueToExceptionAlert(Alert):

    def __init__(self, component: str, exception: Exception) -> None:
        super().__init__(
            AlertCode.TerminatedDueToExceptionAlert,
            '{} terminated due to exception: {}'.format(component, exception))


class TerminatedDueToFatalExceptionAlert(Alert):

    def __init__(self, component: str, exception: Exception) -> None:
        super().__init__(
            AlertCode.TerminatedDueToFatalExceptionAlert,
            '{} terminated due to fatal exception: {} {} will NOT restart '
            'to prevent spam.'.format(component, exception, component))


class ProblemWithTelegramBot(Alert):

    def __init__(self, description: str) -> None:
        super().__init__(
            AlertCode.ProblemWithTelegramBot,
            'Problem encountered with telegram bot: {}'.format(description))


class NodeIsNotAnArchiveNodeAlert(Alert):

    def __init__(self, monitor: str, node: str) -> None:
        super().__init__(
            AlertCode.NodeIsNotAnArchiveNodeAlert,
            '{} is not an archive node. {} Will try to find another archive '
            'node. When restarting PANIC please make sure that the '
            'user_config_node file is modified accordingly since non archive '
            'nodes only store data from the last 256 blocks.'
            ''.format(monitor, node))


class ProblemWithMongo(Alert):

    def __init__(self, exception: Exception) -> None:
        super().__init__(
            AlertCode.ProblemWithMongo,
            'Problem encountered with Mongo: {}'.format(exception))
