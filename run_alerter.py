import concurrent.futures
import sys
from typing import Tuple, List

from src.alerters.proactive.periodic import PeriodicAliveReminder
from src.alerters.reactive.blockchain import Blockchain
from src.alerters.reactive.node import Node, NodeType
from src.alerts.alerts import *
from src.monitors.blockchain import BlockchainMonitor
from src.monitors.github import GitHubMonitor
from src.monitors.monitor_starters import start_node_monitor, \
    start_github_monitor, start_blockchain_monitor
from src.monitors.node import NodeMonitor
from src.store.mongo.mongo_api import MongoApi
from src.store.redis.redis_api import RedisApi
from src.utils.alert_utils.get_channel_set import get_full_channel_set
from src.utils.alert_utils.get_channel_set import \
    get_periodic_alive_reminder_channel_set
from src.utils.config_parsers.internal_parsed import InternalConf, \
    MISSING_INTERNAL_CONFIG_FILES
from src.utils.config_parsers.user import NodeConfig, RepoConfig
from src.utils.config_parsers.user_parsed import UserConf, \
    MISSING_USER_CONFIG_FILES
from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from src.utils.exceptions import *
from src.utils.get_json import get_json
from src.utils.logging import create_logger
from src.web.telegram.telegram import TelegramCommands


def log_and_print(text: str):
    logger_general.info(text)
    print(text)
    sys.stdout.flush()


def node_from_node_config(node_config: NodeConfig):
    # Test connection and match-up chain name
    log_and_print('Trying to retrieve data from the API of {}'.format(
        node_config.node_name))
    try:
        actual_chain = polkadot_api_data_wrapper.get_system_chain(
            node_config.node_ws_url)
        log_and_print('Success.')
        if actual_chain != node_config.chain_name:
            log_and_print(
                'WARNING: actual chain name of {} is \"{}\" not \"{}\". PANIC '
                'will continue using the supplied chain name \"{}\".'.format(
                    node_config.node_name, actual_chain,
                    node_config.chain_name, node_config.chain_name))
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
            polkadot_api_data_wrapper.get_eras_stakers(
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
                node_config.stash_account_address, node_config.chain_name,
                REDIS, node_config.is_archive_node, internal_conf=InternalConf)
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

        # Get the data sources which belong to the same chain and prioritise
        # them over the node itself as data sources for indirect node monitoring
        data_sources = [data_source for data_source in data_source_nodes
                        if node.chain == data_source.chain and
                        data_source.name != node.name]
        if node in data_source_nodes:
            data_sources.append(node)

        # Do not start if there is no data source.
        if len(data_sources) == 0:
            log_and_print(
                'Indirect monitoring will be disabled for node {} because no '
                'data source for chain {} was given in the nodes config file.'
                ''.format(node.name, node.chain))

        # Initialise monitor
        node_monitor = NodeMonitor(
            monitor_name, full_channel_set, logger_monitor_node,
            InternalConf.node_monitor_max_catch_up_blocks, REDIS, node,
            archive_alerts_disabled_by_chain[node.chain], data_sources,
            UserConf.polkadot_api_endpoint)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
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
    data_sources = blockchain_nodes_tuple[1]

    # Monitor name based on blockchain
    monitor_name = 'Blockchain monitor ({})'.format(blockchain_name)

    # Initialisation
    try:
        # Logger initialisation
        logger_monitor_blockchain = create_logger(
            InternalConf.blockchain_monitor_general_log_file_template.format(
                blockchain_name), blockchain_name,
            InternalConf.logging_level, rotating=True)

        # Create blockchain object
        blockchain = Blockchain(blockchain_name, REDIS)

        # Initialise monitor
        blockchain_monitor = BlockchainMonitor(
            monitor_name, blockchain, full_channel_set,
            logger_monitor_blockchain, REDIS, data_sources,
            UserConf.polkadot_api_endpoint)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started'.format(monitor_name))
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
        try:
            TelegramCommands(
                UserConf.telegram_cmds_bot_token,
                UserConf.telegram_cmds_bot_chat_id,
                logger_commands_telegram, REDIS, MONGO,
                node_monitor_nodes_by_chain, archive_alerts_disabled_by_chain,
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
            repo_config.repo_name, releases_page)
    except Exception as e:
        msg = '!!! Error when initialising {}: {} !!!'.format(monitor_name, e)
        log_and_print(msg)
        raise InitialisationException(msg)

    while True:
        # Start
        log_and_print('{} started.'.format(monitor_name))
        try:
            start_github_monitor(github_monitor,
                                 InternalConf.github_monitor_period_seconds,
                                 logger_monitor_github)
        except Exception as e:
            full_channel_set.alert_error(
                TerminatedDueToExceptionAlert(monitor_name, e))
        log_and_print('{} stopped.'.format(monitor_name))


def run_periodic_alive_reminder():
    if not UserConf.par_enabled:
        return

    name = "Periodic alive reminder"

    # Initialization
    par = PeriodicAliveReminder(
        UserConf.par_interval_seconds, par_channel_set, REDIS)

    while True:
        # Start
        log_and_print('{} started.'.format(name))
        try:
            par.start()
        except Exception as e:
            par_channel_set.alert_error(
                TerminatedDueToExceptionAlert(name, e))
        log_and_print('{} stopped.'.format(name))


if __name__ == '__main__':
    if len(MISSING_INTERNAL_CONFIG_FILES) > 0:
        sys.exit('Internal config file {} is missing.'
                 ''.format(MISSING_INTERNAL_CONFIG_FILES[0]))
    elif len(MISSING_USER_CONFIG_FILES) > 0:
        sys.exit('User config file {} is missing. Make sure that you run the '
                 'setup script (run_setup.py) before running the alerter.'
                 ''.format(MISSING_USER_CONFIG_FILES[0]))

    # Global loggers and polkadot data wrapper initialisation
    logger_redis = create_logger(
        InternalConf.redis_log_file, 'redis',
        InternalConf.logging_level)
    logger_mongo = create_logger(
        InternalConf.mongo_log_file, 'mongo',
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

    # Mongo DB initialisation
    if UserConf.mongo_enabled:
        MONGO = MongoApi(logger_mongo, UserConf.mongo_db_name,
                         UserConf.mongo_host, UserConf.mongo_port,
                         username=UserConf.mongo_user,
                         password=UserConf.mongo_pass)
    else:
        MONGO = None

    # Alerters initialisation
    alerter_name = 'PANIC'
    full_channel_set = get_full_channel_set(
        alerter_name, logger_general, REDIS, log_file_alerts, MONGO)
    log_and_print('Enabled alerting channels (general): {}'.format(
        full_channel_set.enabled_channels_list()))
    par_channel_set = \
        get_periodic_alive_reminder_channel_set(alerter_name, logger_general,
                                                REDIS, log_file_alerts, MONGO)
    log_and_print('Enabled alerting channels (periodic alive reminder): {}'
                  ''.format(par_channel_set.
                            enabled_channels_list()))

    # Print number of enabled and disabled alerts
    enabled = len([b for b in InternalConf.alerts_enabled_map.values() if b])
    disabled = len(InternalConf.alerts_enabled_map.values()) - enabled
    log_and_print('Alert types enabled = {}'.format(enabled))
    log_and_print('Alert types disabled = {}'.format(disabled))

    # Nodes initialisation
    try:
        nodes = [node_from_node_config(n) for n in UserConf.filtered_nodes]
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Organize nodes into lists according to their category
    node_monitor_nodes = []
    data_source_nodes = []
    for node, node_conf in zip(nodes, UserConf.filtered_nodes):
        if node_conf.monitor_node:
            node_monitor_nodes.append(node)
        if node_conf.use_as_data_source:
            data_source_nodes.append(node)

    # Get the unique chains of the data sources and group the data source nodes
    # by chain. This is done for the blockchain monitor.
    data_sources_unique_chains = {n.chain for n in data_source_nodes}
    data_sources_by_chain = {chain: [node for node in data_source_nodes
                                     if node.chain == chain]
                             for chain in data_sources_unique_chains}

    # Get unique chains and group nodes by chain for node monitor
    node_monitor_unique_chains = {n.chain for n in node_monitor_nodes}
    node_monitor_nodes_by_chain = {chain: [node for node in node_monitor_nodes
                                           if node.chain == chain]
                                   for chain in node_monitor_unique_chains}

    # Disable archive monitoring for a chain if no data source is an archive
    # node for that chain, and inform the user if a chain has no data sources.
    archive_alerts_disabled_by_chain = {}
    # Infer chains from the list of nodes to be monitored
    for chain in node_monitor_unique_chains:
        archive_alerts_disabled = True
        # If the chain has data sources check whether these data sources are
        # archive nodes
        if chain in data_sources_unique_chains:
            for n in data_sources_by_chain[chain]:
                # If one of the data sources is an archive node enable archive
                # monitoring
                if n.is_archive_node:
                    archive_alerts_disabled = False
                    break
            if archive_alerts_disabled:
                print(
                    "Please note that since no data source is an archive node "
                    "for chain {}, archive monitoring will be disabled for "
                    "this chain. To enable archive monitoring, please restart "
                    "the alerter and modify the node config so that it "
                    "contains at least one archive data source node for chain "
                    "{}.".format(chain, chain))
        else:
            # If chain has no data sources inform the user that blockchain
            # monitoring is disabled for that chain.
            print("Please note that since no node of chain {} was set as a "
                  "data source, no blockchain monitor for chain {} will start."
                  .format(chain, chain))
        archive_alerts_disabled_by_chain[chain] = archive_alerts_disabled

    # Test connection to GitHub pages
    try:
        test_connection_to_github_pages()
    except InitialisationException as ie:
        logger_general.error(ie)
        sys.exit(ie)

    # Run monitors
    monitor_node_count = len(node_monitor_nodes)
    monitor_blockchain_count = len(data_source_nodes)
    monitor_github_count = len(UserConf.filtered_repos)
    commands_telegram_count = 1
    periodic_alive_reminder_count = 1
    total_count = sum(
        [monitor_node_count, monitor_github_count, monitor_blockchain_count,
         commands_telegram_count, periodic_alive_reminder_count])
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_count) \
            as executor:
        executor.map(run_monitor_nodes, node_monitor_nodes)
        executor.map(run_monitor_blockchain, data_sources_by_chain
                     .items())
        executor.map(run_monitor_github, UserConf.filtered_repos)
        executor.submit(run_commands_telegram)
        executor.submit(run_periodic_alive_reminder)
