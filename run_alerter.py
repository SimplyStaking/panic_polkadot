import concurrent.futures
import sys
from typing import Tuple, List

from alerter.src.alerting.alert_utils.get_channel_set import \
    get_full_channel_set
from alerter.src.alerting.alert_utils.get_channel_set import \
    get_periodic_alive_reminder_channel_set
from alerter.src.alerting.alerts.alerts import *
from alerter.src.alerting.periodic.periodic import PeriodicAliveReminder
from alerter.src.blockchain.blockchain import Blockchain
from alerter.src.commands.handlers.telegram import TelegramCommands
from alerter.src.monitoring.monitors.blockchain import BlockchainMonitor
from alerter.src.monitoring.monitors.github import GitHubMonitor
from alerter.src.monitoring.monitors.monitor_starters import \
    start_node_monitor, start_github_monitor, start_blockchain_monitor
from alerter.src.monitoring.monitors.node import NodeMonitor
from alerter.src.node.node import Node, NodeType
from alerter.src.utils.config_parsers.internal_parsed import InternalConf, \
    INTERNAL_CONFIG_FILE, INTERNAL_CONFIG_FILE_FOUND
from alerter.src.utils.config_parsers.user import NodeConfig, RepoConfig
from alerter.src.utils.config_parsers.user_parsed import UserConf, \
    MISSING_USER_CONFIG_FILES
from alerter.src.utils.data_wrapper.polkadot_api import \
    PolkadotApiWrapper
from alerter.src.utils.exceptions import *
from alerter.src.utils.get_json import get_json
from alerter.src.utils.logging import create_logger
from alerter.src.utils.redis_api import RedisApi


def log_and_print(text: str):
    logger_general.info(text)
    print(text)


def node_from_node_config(node_config: NodeConfig):
    # Test connection
    log_and_print('Trying to retrieve data from the API of {}'.format(
        node_config.node_name))
    try:
        chain = polkadot_api_data_wrapper.get_system_chain(
            node_config.node_ws_url)
        log_and_print('Success.')
    except Exception as e:
        logger_general.error(e)
        raise InitialisationException(
            'Failed to retrieve data from the API of {}'.format(
                node_config.node_name))

    # Get node type
    node_type = NodeType.VALIDATOR_FULL_NODE \
        if node_config.node_is_validator \
        else NodeType.NON_VALIDATOR_FULL_NODE

    # Check if validator stash account address exists by querying some data
    # which requires the validator's address. If address does not exist, an
    # exception is thrown.
    if node_config.node_is_validator:
        try:
            polkadot_api_data_wrapper.get_stakers(
                node_config.node_ws_url, node_config.stash_account_address)
        except InvalidStashAccountAddressException as e:
            logger_general.error(e.message)
            raise InitialisationException(e.message)
        except Exception as e:
            logger_general.error(e)
            raise InitialisationException(
                'Failed validating stash account address {}'.format(
                    node_config.stash_account_address))

    # Initialise node and load any state
    node = Node(node_config.node_name, node_config.node_ws_url, node_type,
                node_config.stash_account_address, chain, REDIS,
                node_config.is_archive_node, internal_conf=InternalConf)
    node.load_state(logger_general)

    # Return node
    return node


def test_connection_to_github_pages():
    for repo in UserConf.filtered_repos:
        # Get releases page
        releases_page = InternalConf.github_releases_template.format(
            repo.repo_page)

        # Test connection
        log_and_print('Trying to connect to {}'.format(releases_page))
        try:
            releases = get_json(releases_page, logger_general)
            if 'message' in releases and releases['message'] == 'Not Found':
                raise InitialisationException(
                    'Successfully reached {} but URL is '
                    'not valid.'.format(releases_page))
            else:
                log_and_print('Success.')
        except Exception:
            raise InitialisationException('Could not reach {}.'
                                          ''.format(releases_page))


def run_monitor_nodes(node: Node):
    # Monitor name based on node
    monitor_name = 'Node monitor ({})'.format(node.name)
    try:
        # Logger initialisation
        logger_monitor_node = create_logger(
            InternalConf.node_monitor_general_log_file_template.format(
                node.name),
            node.name, InternalConf.logging_level, rotating=True)

        full_nodes = []
        for chain, all_nodes in node_monitor_nodes_by_chain.items():
            if chain == node.chain:
                full_nodes = [n for n in all_nodes if not n.is_validator]
                break

        # Do not start if there is no full nodes.
        if len(full_nodes) == 0:
            log_and_print(
                '!!! Could not start {}. It must have at least 1 full node!!!'
                ''.format(monitor_name))
            return

        # Initialise monitor
        node_monitor = NodeMonitor(
            monitor_name, full_channel_set, logger_monitor_node,
            InternalConf.node_monitor_max_catch_up_blocks, REDIS, node,
            archive_alerts_disabled_by_chain[node.chain], full_nodes,
            UserConf.polkadot_api_endpoint)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            start_node_monitor(node_monitor,
                               InternalConf.node_monitor_period_seconds,
                               logger_monitor_node)
        except (UnexpectedApiCallErrorException,
                UnexpectedApiErrorWhenReadingDataException,
                InvalidStashAccountAddressException) as e:
            full_channel_set.alert_error(
                TerminatedDueToFatalExceptionAlert(monitor_name, e))
            log_and_print('{} stopped.'.format(monitor_name))
            break
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_monitor_blockchain(blockchain_nodes_tuple: Tuple[str, List[Node]]):
    # Get blockchain and nodes
    blockchain_name = blockchain_nodes_tuple[0]
    nodes = blockchain_nodes_tuple[1]

    # Monitor name based on blockchain
    monitor_name = 'Blockchain monitor ({})'.format(blockchain_name)

    # Initialisation
    try:
        # Logger initialisation
        logger_monitor_blockchain = create_logger(
            InternalConf.blockchain_monitor_general_log_file_template.format(
                blockchain_name), blockchain_name,
            InternalConf.logging_level, rotating=True)

        # Get full nodes
        full_nodes = [n for n in nodes if not n.is_validator]

        # Do not start if not enough nodes
        if len(full_nodes) == 0:
            log_and_print('!!! Could not start {}. It must have at least 1 '
                          'full node!!!'.format(monitor_name))
            return

        # Create blockchain object
        blockchain = Blockchain(blockchain_name, REDIS)

        # Initialise monitor
        blockchain_monitor = BlockchainMonitor(
            monitor_name, blockchain, full_channel_set,
            logger_monitor_blockchain, REDIS, full_nodes,
            UserConf.polkadot_api_endpoint)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started'.format(monitor_name))
        sys.stdout.flush()
        try:
            start_blockchain_monitor(
                blockchain_monitor,
                InternalConf.blockchain_monitor_period_seconds,
                logger_monitor_blockchain)
        except (UnexpectedApiCallErrorException,
                UnexpectedApiErrorWhenReadingDataException) as e:
            full_channel_set.alert_error(
                TerminatedDueToFatalExceptionAlert(monitor_name, e))
            log_and_print('{} stopped.'.format(monitor_name))
            break
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_commands_telegram():
    # Fixed monitor name
    monitor_name = 'Telegram commands'

    # Check if Telegram commands enabled
    if not UserConf.telegram_cmds_enabled:
        return

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            TelegramCommands(
                UserConf.telegram_cmds_bot_token,
                UserConf.telegram_cmds_bot_chat_id,
                logger_commands_telegram, REDIS,
                InternalConf.redis_twilio_snooze_key,
                InternalConf.redis_periodic_alive_reminder_mute_key,
                InternalConf.redis_node_monitor_alive_key_prefix,
                InternalConf.redis_blockchain_monitor_alive_key_prefix
            ).start_listening()
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_monitor_github(repo_config: RepoConfig):
    # Monitor name based on repository
    monitor_name = 'GitHub monitor ({})'.format(repo_config.repo_name)

    # Initialisation
    try:
        # Logger initialisation
        logger_monitor_github = create_logger(
            InternalConf.github_monitor_general_log_file_template.format(
                repo_config.repo_page.replace('/', '_')), repo_config.repo_page,
            InternalConf.logging_level, rotating=True)

        # Get releases page
        releases_page = InternalConf.github_releases_template.format(
            repo_config.repo_page)

        # Initialise monitor
        github_monitor = GitHubMonitor(
            monitor_name, full_channel_set, logger_monitor_github, REDIS,
            repo_config.repo_name, releases_page,
            InternalConf.redis_github_releases_key_prefix)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        sys.stdout.flush()
        try:
            start_github_monitor(github_monitor,
                                 InternalConf.github_monitor_period_seconds,
                                 logger_monitor_github)
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_periodic_alive_reminder():
    if not UserConf.periodic_alive_reminder_enabled:
        return

    name = "Periodic alive reminder"

    # Initialization
    periodic_alive_reminder = PeriodicAliveReminder(
        UserConf.interval_seconds, periodic_alive_reminder_channel_set,
        InternalConf.redis_periodic_alive_reminder_mute_key, REDIS)

    while True:
        # Start
        log_and_print('{} started.'.format(name))
        sys.stdout.flush()
        try:
            periodic_alive_reminder.start()
        except Exception as e:
            periodic_alive_reminder_channel_set.alert_error(
                TerminatedDueToExceptionAlert(name, e))
        log_and_print('{} stopped.'.format(name))


if __name__ == '__main__':
    if not INTERNAL_CONFIG_FILE_FOUND:
        sys.exit('Config file {} is missing.'.format(INTERNAL_CONFIG_FILE))
    elif len(MISSING_USER_CONFIG_FILES) > 0:
        sys.exit('Config file {} is missing. Make sure that you run the setup '
                 'script (run_setup.py) before running the alerter.'
                 ''.format(MISSING_USER_CONFIG_FILES[0]))

    # Global loggers and polkadot data wrapper initialisation
    logger_redis = create_logger(
        InternalConf.redis_log_file, 'redis',
        InternalConf.logging_level)
    logger_general = create_logger(
        InternalConf.general_log_file, 'general',
        InternalConf.logging_level, rotating=True)
    logger_commands_telegram = create_logger(
        InternalConf.telegram_commands_general_log_file, 'commands_telegram',
        InternalConf.logging_level, rotating=True)
    log_file_alerts = InternalConf.alerts_log_file
    polkadot_api_data_wrapper = \
        PolkadotApiWrapper(logger_general, UserConf.polkadot_api_endpoint)

    # Redis initialisation
    if UserConf.redis_enabled:
        REDIS = RedisApi(
            logger_redis, InternalConf.redis_database, UserConf.redis_host,
            UserConf.redis_port, password=UserConf.redis_password,
            namespace=UserConf.unique_alerter_identifier)
    else:
        REDIS = None

    # Alerters initialisation
    alerter_name = 'PANIC'
    full_channel_set = get_full_channel_set(
        alerter_name, logger_general, REDIS, log_file_alerts)
    log_and_print('Enabled alerting channels (general): {}'.format(
        full_channel_set.enabled_channels_list()))
    periodic_alive_reminder_channel_set = \
        get_periodic_alive_reminder_channel_set(alerter_name, logger_general,
                                                REDIS, log_file_alerts)
    log_and_print('Enabled alerting channels (periodic alive reminder): {}'
                  ''.format(periodic_alive_reminder_channel_set.
                            enabled_channels_list()))
    sys.stdout.flush()

    # Nodes initialisation
    try:
        nodes = [node_from_node_config(n) for n in UserConf.filtered_nodes]
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Organize nodes into lists according to how they will be monitored
    node_monitor_nodes = []
    blockchain_monitor_nodes = []
    for node, node_conf in zip(nodes, UserConf.filtered_nodes):
        if node_conf.include_in_node_monitor:
            node_monitor_nodes.append(node)
        if node_conf.include_in_blockchain_monitor:
            blockchain_monitor_nodes.append(node)

    # Get unique chains and group nodes by chain for blockchain monitor
    blockchain_monitor_unique_chains = {n.chain for n in
                                        blockchain_monitor_nodes}
    blockchain_monitor_nodes_by_chain = {chain: [node for node in
                                                 blockchain_monitor_nodes
                                                 if node.chain == chain]
                                         for chain in
                                         blockchain_monitor_unique_chains}

    # Get unique chains and group nodes by chain for node monitor
    node_monitor_unique_chains = {n.chain for n in node_monitor_nodes}
    node_monitor_nodes_by_chain = {chain: [node for node in node_monitor_nodes
                                           if node.chain == chain]
                                   for chain in node_monitor_unique_chains}

    # Disable archive monitoring for a chain if no full node is an archive node
    # for that chain.
    archive_alerts_disabled_by_chain = {}
    for chain, nodes in node_monitor_nodes_by_chain.items():
        archive_alerts_disabled = True
        for n in nodes:
            if not n.is_validator and n.is_archive_node:
                archive_alerts_disabled = False
                break
        archive_alerts_disabled_by_chain[chain] = archive_alerts_disabled
        if archive_alerts_disabled:
            print("Please note that since no archive full node has been "
                  "included in node monitoring for chain {}, "
                  "archive monitoring will be disabled for this chain. "
                  "To enable archive monitoring, please restart the alerter "
                  "and modify the node config so that it contains at least one "
                  "archive full node for node monitoring, for chain {}."
                  .format(chain, chain))

    # Test connection to GitHub pages
    try:
        test_connection_to_github_pages()
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Run monitors
    monitor_node_count = len(node_monitor_nodes)
    monitor_blockchain_count = len(blockchain_monitor_nodes)
    monitor_github_count = len(UserConf.filtered_repos)
    commands_telegram_count = 1
    periodic_alive_reminder_count = 1
    total_count = sum(
        [monitor_node_count, monitor_github_count, monitor_blockchain_count,
         commands_telegram_count, periodic_alive_reminder_count])
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_count) \
            as executor:
        executor.map(run_monitor_nodes, node_monitor_nodes)
        executor.map(run_monitor_blockchain, blockchain_monitor_nodes_by_chain
                     .items())
        executor.map(run_monitor_github, UserConf.filtered_repos)
        executor.submit(run_commands_telegram)
        executor.submit(run_periodic_alive_reminder)
