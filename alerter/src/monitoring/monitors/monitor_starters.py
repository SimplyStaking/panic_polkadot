import http.client
import logging
import time
from json import JSONDecodeError

import urllib3.exceptions
from requests.exceptions import ConnectionError as ReqConnectionError, \
    ReadTimeout

from alerter.src.alerting.alerts.alerts import *
from alerter.src.monitoring.monitors.blockchain import BlockchainMonitor
from alerter.src.monitoring.monitors.github import GitHubMonitor
from alerter.src.monitoring.monitors.node import NodeMonitor
from alerter.src.utils.config_parsers.internal import InternalConfig
from alerter.src.utils.config_parsers.internal_parsed import InternalConf
from alerter.src.utils.exceptions import *
from alerter.src.utils.timing import TimedTaskLimiter


def start_node_monitor(node_monitor: NodeMonitor, monitor_period: int,
                       logger: logging.Logger):
    # Start
    while True:
        # Read node data
        try:
            logger.debug('Reading %s.', node_monitor.node)
            node_monitor.monitor_direct()
            logger.debug('Done reading %s.', node_monitor.node)
        except (ConnectionWithNodeApiLostException,
                NodeWasNotConnectedToApiServerException):
            node_monitor.node.set_as_down(node_monitor.channels, logger)
        except (ReqConnectionError, ReadTimeout):
            node_monitor.data_wrapper.set_api_as_down(node_monitor.monitor_name,
                                                      node_monitor.channels)
        except (http.client.IncompleteRead, urllib3.exceptions.IncompleteRead,
                ApiCallFailedException) \
                as e:
            logger.error(e)
            logger.error("Alerter will continue running normally.")
        except (UnexpectedApiCallErrorException,
                UnexpectedApiErrorWhenReadingDataException) as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise e

        try:
            logger.debug('Reading %s data indirectly.', node_monitor.node)
            node_monitor.monitor_indirect()
            logger.debug('Done reading %s data indirectly.', node_monitor.node)
        except NoLiveFullNodeConnectedWithAnApiServerException:
            node_monitor.channels.alert_critical(
                CouldNotFindLiveFullNodeConnectedToApiServerAlert(
                    node_monitor.monitor_name))
        except NoLiveArchiveFullNodeConnectedWithAnApiServerException:
            if not node_monitor.no_live_archive_node_alert_sent:
                node_monitor.channels.alert_warning(
                    CouldNotFindLiveArchiveFullNodeConnectedToApiServerAlert(
                        node_monitor.monitor_name))
                node_monitor._no_live_archive_node_alert_sent = True
                node_monitor._monitor_is_catching_up = False
        except NodeIsNotAnArchiveNodeException:
            node_monitor.channels.alert_error(FullNodeIsNotAnArchiveNodeAlert(
                node_monitor.last_full_node_used, node_monitor.monitor_name))
            node_monitor.last_full_node_used._is_archive_node = False
        except (ConnectionWithNodeApiLostException,
                NodeWasNotConnectedToApiServerException):
            node_monitor.last_full_node_used.set_as_down(node_monitor.channels,
                                                         logger)
        except (ReqConnectionError, ReadTimeout):
            node_monitor.data_wrapper.set_api_as_down(node_monitor.monitor_name,
                                                      node_monitor.channels)
        except (http.client.IncompleteRead, urllib3.exceptions.IncompleteRead,
                ApiCallFailedException) as e:
            logger.error(e)
            logger.error("Alerter will continue running normally.")
        except (UnexpectedApiCallErrorException,
                UnexpectedApiErrorWhenReadingDataException) as e:
            raise e
        except InvalidStashAccountAddressException as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise e

        node_monitor.logger.info('%s status: %s', node_monitor.node,
                                 node_monitor.status())

        # Save all state
        node_monitor.save_state()
        node_monitor.node.save_state(logger)

        # Sleep
        if not node_monitor.is_catching_up():
            logger.debug('Sleeping for %s seconds.', monitor_period)
            time.sleep(monitor_period)


def start_blockchain_monitor(blockchain_monitor: BlockchainMonitor,
                             monitor_period: int, logger: logging.Logger):
    # Start
    while True:
        # Read blockchain data
        try:
            logger.debug('Reading blockchain data.')
            blockchain_monitor.monitor()
            logger.debug('Done reading blockchain data.')
        except NoLiveFullNodeConnectedWithAnApiServerException:
            blockchain_monitor.channels.alert_critical(
                CouldNotFindLiveFullNodeConnectedToApiServerAlert(
                    blockchain_monitor.monitor_name))
        except (ConnectionWithNodeApiLostException,
                NodeWasNotConnectedToApiServerException):
            blockchain_monitor.last_full_node_used.set_as_down(
                blockchain_monitor.channels, logger)
        except (ReqConnectionError, ReadTimeout):
            blockchain_monitor.data_wrapper.set_api_as_down(
                blockchain_monitor.monitor_name, blockchain_monitor.channels)
        except (http.client.IncompleteRead, urllib3.exceptions.IncompleteRead,
                ApiCallFailedException) as e:
            logger.error(e)
            logger.error("Alerter will continue running normally.")
        except (UnexpectedApiCallErrorException,
                UnexpectedApiErrorWhenReadingDataException) as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise e

        # Save all state
        blockchain_monitor.save_state()
        blockchain_monitor.blockchain.save_state(logger)

        # Sleep
        logger.debug('Sleeping for %s seconds.', monitor_period)
        time.sleep(monitor_period)


def start_github_monitor(github_monitor: GitHubMonitor, monitor_period: int,
                         logger: logging.Logger,
                         internal_config: InternalConfig = InternalConf):
    # Set up alert limiter
    github_error_alert_limiter = TimedTaskLimiter(
        internal_config.github_error_interval_seconds)

    # Start
    while True:
        # Read GitHub releases page
        try:
            logger.debug('Reading %s.', github_monitor.releases_page)
            github_monitor.monitor()
            logger.debug('Done reading %s.', github_monitor.releases_page)

            # Save all state
            github_monitor.save_state()

            # Reset alert limiter
            github_error_alert_limiter.reset()
        except (ReqConnectionError, ReadTimeout) as conn_err:
            if github_error_alert_limiter.can_do_task():
                github_monitor.channels.alert_error(
                    CannotAccessGitHubPageAlert(github_monitor.releases_page))
                github_error_alert_limiter.did_task()
            logger.error('Error occurred when accessing {}: {}.'
                         ''.format(github_monitor.releases_page, conn_err))
        except JSONDecodeError as json_error:
            logger.error(json_error)  # Ignore such errors
        except Exception as e:
            logger.error(e)
            raise e

        # Sleep
        logger.debug('Sleeping for %s seconds.', monitor_period)
        time.sleep(monitor_period)
