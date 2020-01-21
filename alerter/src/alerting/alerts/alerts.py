from datetime import datetime


class Alert:

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self.message


class ExperiencingDelaysAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            'Experiencing delays when trying to access {}.'.format(node))


class CannotAccessNodeAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('I cannot access {}.'.format(node))


class StillCannotAccessNodeAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            'I still cannot access {}. Node became inaccessible at {} '
            'and has been inaccessible for (at most) {}.'.format(
                node, went_down_at, downtime))


class NowAccessibleAlert(Alert):

    def __init__(self, node: str, went_down_at: datetime,
                 downtime: str) -> None:
        super().__init__(
            '{} is now accessible. Node became inaccessible '
            'at {} and was inaccessible for (at most) {}.'
            ''.format(node, went_down_at, downtime))


class CouldNotFindLiveFullNodeConnectedToApiServerAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__('{} could not find a live full node connected to the '
                         'custom JS API server to use as a data source.'
                         .format(monitor))


class CouldNotFindLiveArchiveFullNodeConnectedToApiServerAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__('{} could not find a live archive full node connected '
                         'to the custom JS API server. Slashing alerts will '
                         'now be disabled as these require data from previous '
                         'blocks. Other functionality will continue running '
                         'normally'.format(monitor))


class FoundLiveArchiveFullNodeAgainAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__('{} found an archive full node. This means that '
                         'archive monitoring (which includes slashing) is now '
                         'enabled.'.format(monitor))


class BondedBalanceIncreasedAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        super().__init__(
            '{} total bonded balance INCREASED from {} to {}.'.format(
                node, old_balance, new_balance))


class BondedBalanceDecreasedAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        super().__init__(
            '{} total bonded balance DECREASED from {} to {}.'.format(
                node, old_balance, new_balance))


class BondedBalanceIncreasedByAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        change = round(new_balance - old_balance, 3)
        super().__init__(
            '{} total bonded balance INCREASED by {} from {} to {}.'.format(
                node, change, old_balance, new_balance))


class BondedBalanceDecreasedByAlert(Alert):

    def __init__(self, node: str, old_balance: float, new_balance: float) \
            -> None:
        change = round(old_balance - new_balance, 3)
        super().__init__(
            '{} total bonded balance DECREASED by {} from {} to {}.'.format(
                node, change, old_balance, new_balance))


class PeersIncreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            '{} peers INCREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class PeersIncreasedOutsideDangerRangeAlert(Alert):

    def __init__(self, node: str, danger: int) -> None:
        super().__init__(
            '{} peers INCREASED to more than {} peers. No further peer change '
            'alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, danger, danger))


class PeersIncreasedOutsideSafeRangeAlert(Alert):

    def __init__(self, node: str, safe: int) -> None:
        super().__init__(
            '{} peers INCREASED to more than {} peers. No further peer change'
            ' alerts will be sent unless the number of peers goes below {}.'
            ''.format(node, safe, safe))


class PeersDecreasedAlert(Alert):

    def __init__(self, node: str, old_peers: int, new_peers: int) -> None:
        super().__init__(
            '{} peers DECREASED from {} to {}.'.format(
                node, old_peers, new_peers))


class IsSyncingAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} is in syncing state.'.format(node))


class IsNoLongerSyncingAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} is no longer syncing.'.format(node))


class ValidatorIsNotActiveAlert(Alert):
    def __init__(self, node: str) -> None:
        super().__init__('{} is not active in this session.'.format(node))


class ValidatorIsNowActiveAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} is now active in this session.'.format(node))


class ValidatorIsNotElectedForNextSessionAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            '{} was not elected to validate in the next session. '
            '{} needs a higher bonded balance for it to be elected.'
                .format(node, node))


class ValidatorIsElectedForTheNextSessionAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('{} was elected to validate in the next session.'
                         .format(node, node))


class LastAuthoredBlockInSessionAlert(Alert):

    def __init__(self, node: str, time_of_last_authored_block: str,
                 session: int) -> None:
        super().__init__(
            'The last authored block in session {} by validator {} was at '
            'least {} ago.'.format(session, node, time_of_last_authored_block))


class NoBlocksHaveYetBeenAuthoredInSessionAlert(Alert):

    def __init__(self, node: str, session: int) -> None:
        super().__init__(
            'No blocks have yet been authored by node {} in session {}.'
                .format(node, session))


class ANewBlockHasNowBeenAuthoredByValidatorAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('Validator {} is now authoring blocks again.'
                         .format(node))


class ValidatorHasBeenDisabledInSessionAlert(Alert):

    def __init__(self, node: str, session: int) -> None:
        super().__init__('Validator {} has been disabled in session {}'
                         .format(node, session))


class ValidatorIsNoLongerDisabledInSessionAlert(Alert):

    def __init__(self, node: str, session: int) -> None:
        super().__init__('Validator {} is no longer disabled in session {}'
                         .format(node, session))


class NewReferendumAlert(Alert):

    def __init__(self, referendum_number: int, end_block: int) -> None:
        super().__init__('Referendum {} is now available. Voting will stop '
                         'when block height {} is reached.'
                         .format(referendum_number, end_block))


class NewPublicProposalAlert(Alert):

    def __init__(self, proposal_number: int):
        super().__init__('Public proposal {} has been created.'
                         .format(proposal_number))


class NewCouncilProposalAlert(Alert):

    def __init__(self, proposal_number: int):
        super().__init__('Council proposal {} has been created.'
                         .format(proposal_number))


class ValidatorIsNowPartOfTheCouncilAlert(Alert):

    def __init__(self, node: str):
        super().__init__('{} is now part of the council'.format(node))


class ValidatorIsNoLongerPartOfTheCouncilAlert(Alert):

    def __init__(self, node: str):
        super().__init__('{} is no longer part of the council'.format(node))


class ValidatorSetSizeDecreasedAlert(Alert):

    def __init__(self, set_size: int) -> None:
        super().__init__('The validator set size decreased to {}'
                         .format(set_size))


class ValidatorSetSizeIncreasedAlert(Alert):

    def __init__(self, set_size: int) -> None:
        super().__init__('The validator set size increased to {}'
                         .format(set_size))


class ValidatorHasBeenSlashedAlert(Alert):

    def __init__(self, node: str, amount: float):
        super().__init__('{} has been slashed {}.'.format(node, amount))


class NodeFinalizedBlockHeightDidNotChangeInAlert(Alert):

    def __init__(self, node: str, time_of_last_update: str) -> None:
        super().__init__('The finalized block height of node {} was updated at '
                         'least {} ago.'.format(node, time_of_last_update))


class NodeFinalizedBlockHeightHasNowBeenUpdatedAlert(Alert):

    def __init__(self, node: str) -> None:
        super().__init__('The finalized block height of node {} was updated.'
                         .format(node))


class ProblemWhenDialingNumberAlert(Alert):

    def __init__(self, number: str, exception: Exception) -> None:
        super().__init__(
            'Problem encountered when dialing {}: {}'.format(number, exception))


class ProblemWhenCheckingIfCallsAreSnoozedAlert(Alert):

    def __init__(self) -> None:
        super().__init__('Problem encountered when checking if '
                         'calls are snoozed. Calling anyways.')


class NewGitHubReleaseAlert(Alert):

    def __init__(self, release_name: str, repo_name: str) -> None:
        super().__init__(
            '{} of {} has just been released.'.format(release_name, repo_name))


class CannotAccessGitHubPageAlert(Alert):

    def __init__(self, page: str) -> None:
        super().__init__('I cannot access GitHub page {}.'.format(page))


class AlerterAliveAlert(Alert):

    def __init__(self) -> None:
        super().__init__('Still running.')


class ApiIsUpAgainAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__('{} connected with the custom JS API server again.'
                         .format(monitor))


class ApiIsDownAlert(Alert):

    def __init__(self, monitor: str) -> None:
        super().__init__('{} lost connection with the custom JS API server. '
                         'Please make sure that the custom JS API server is '
                         'running, otherwise the monitor cannot retrieve data.'
                         .format(monitor))


class ErrorWhenReadingDataFromNode(Alert):

    def __init__(self, node: str) -> None:
        super().__init__(
            'Error when reading data from {}. Alerter '
            'will continue running normally.'.format(node))


class TerminatedDueToExceptionAlert(Alert):

    def __init__(self, component: str, exception: Exception) -> None:
        super().__init__(
            '{} terminated due to exception: {}'.format(component, exception))


class TerminatedDueToFatalExceptionAlert(Alert):

    def __init__(self, component: str, exception: Exception) -> None:
        super().__init__(
            '{} terminated due to fatal exception: {}. {} will NOT restart '
            'to prevent spam.'.format(component, exception, component))


class ProblemWithTelegramBot(Alert):

    def __init__(self, description: str) -> None:
        super().__init__(
            'Problem encountered with telegram bot: {}'.format(description))


class FullNodeIsNotAnArchiveNodeAlert(Alert):

    def __init__(self, monitor: str, node: str) -> None:
        super().__init__('{} is not an archive node. {} Will try to find '
                         'another archive node. When restarting PANIC please '
                         'make sure that the user_config_node file is modified '
                         'accordingly, since non archive nodes store data from '
                         'the last 256 blocks.'.format(monitor, node))
