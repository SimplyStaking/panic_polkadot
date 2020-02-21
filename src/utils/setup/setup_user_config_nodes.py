from configparser import ConfigParser
from typing import Optional, List

from src.utils.config_parsers.user import NodeConfig
from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from src.utils.logging import DUMMY_LOGGER
from src.utils.user_input import yn_prompt


def get_node(nodes_so_far: List[NodeConfig],
             polkadot_api_data_wrapper: PolkadotApiWrapper,
             web_sockets_connected_to_api: List) -> Optional[NodeConfig]:
    # Get node's name
    node_names_so_far = [n.node_name for n in nodes_so_far]
    while True:
        node_name = input('Unique node name:\n')
        if node_name in node_names_so_far:
            print('Node name must be unique.')
        else:
            break

    # Get node's WS url
    while True:
        ws_url = input('Node\'s WS url (typically ws://NODE_IP:9944):\n')
        if ws_url in web_sockets_connected_to_api:
            print('Testing connection with node {}'.format(ws_url))
            try:
                polkadot_api_data_wrapper.ping_node(ws_url)
                print('Success.')
                break
            except Exception:
                if not yn_prompt('Failed to connect with node {}. Do you want '
                                 'to try again? (Y/n)\n'.format(ws_url)):
                    return None
        else:
            if not yn_prompt(
                    'Could not connect with the API Server at web socket '
                    '{}. Please make sure that the node was added in the '
                    'API\'s config. Do you want to try again? (Y/n)\n'.format(
                        ws_url, polkadot_api_data_wrapper.api_endpoint,
                        polkadot_api_data_wrapper.api_endpoint)):
                return None

    # Ask if node is a validator
    node_is_validator = yn_prompt('Is this node a validator? (Y/n)\n')

    # Ask if node is an archive node.
    # Note: if the node is a validator, it must also be an archive node.
    #       However, it was done this way in case of changes in future updates.
    node_is_archive_node = yn_prompt('Is this node an archive node? (Y/n)\n')

    # Get validator's stash account address.
    if node_is_validator:
        while True:
            stash_account_address = input('Please enter the validator\'s stash '
                                          'account address:\n')
            if not stash_account_address.strip():
                if not yn_prompt('You cannot leave the stash_account_address '
                                 'field empty for a validator. Do you want to '
                                 'try again? (Y/n)\n'):
                    return None
            else:
                break
    else:
        stash_account_address = ''

    # Return node
    return NodeConfig(node_name, ws_url, node_is_validator,
                      node_is_archive_node, True, True, stash_account_address)


def setup_nodes(cp: ConfigParser, api_endpoint: str) -> None:
    print('==== Nodes')
    print('To produce alerts, the alerter needs something to monitor! The list '
          'of nodes to be included in the monitoring will now be set up. This '
          'includes validators, sentries, and whether these nodes can be used '
          'as data sources to monitor a node\'s state indirectly. You may '
          'include nodes from multiple substrate chains in any order; PANIC '
          'will figure out which chain they belong to when you run it. Node '
          'names must be unique!\n\n'
          'Note that you will be asked whether a node is an archive node or '
          'not. This is done because for archive monitoring (which includes '
          '(alerting for)/detecting slashing events), the alerter needs '
          'blockchain data from the past. You do not need any archive data '
          'source nodes to run PANIC, but for archive monitoring to be enabled '
          'for a chain you must have at least one for that chain.')

    # Check if list already set up
    if len(cp.sections()) > 0 and \
            not yn_prompt('The list of nodes is already set up. Do you wish to '
                          'clear this list? You will then be asked to set up a '
                          'new list of nodes, if you wish to do so (Y/n)\n'):
        return

    # Clear config and initialise new list
    cp.clear()
    nodes = []

    # Ask if they want to set it up
    if not yn_prompt('Do you wish to set up the list of nodes? (Y/n)\n'):
        return

    # Get node details and append them to the list of nodes
    while True:
        # Check that API is running by retrieving some data which will be used.
        polkadot_api_data_wrapper = PolkadotApiWrapper(DUMMY_LOGGER,
                                                       api_endpoint)
        while True:
            try:
                web_sockets_connected_to_api = polkadot_api_data_wrapper. \
                    get_web_sockets_connected_to_an_api()
                break
            except Exception:
                if not yn_prompt('Could not connect with the API Server at '
                                 '\'{}\'. Please make sure that the API Server '
                                 'is running at the provided IP before '
                                 'proceeding further. Do you want to try '
                                 'again? (Y/n)\n'.format(api_endpoint)):
                    return
        node = get_node(nodes, polkadot_api_data_wrapper,
                        web_sockets_connected_to_api)
        if node is not None:
            nodes.append(node)
            if node.node_is_validator:
                print('Successfully added validator node.')
            else:
                print('Successfully added full node.')

        if not yn_prompt('Do you want to add another node? (Y/n)\n'):
            break

    # Add nodes to config
    for i, node in enumerate(nodes):
        section = 'node_' + str(i)
        cp.add_section(section)
        cp[section]['node_name'] = node.node_name
        cp[section]['node_ws_url'] = node.node_ws_url
        cp[section]['node_is_validator'] = str(node.node_is_validator)
        cp[section]['is_archive_node'] = str(node.is_archive_node)
        cp[section]['monitor_node'] = str(node.monitor_node)
        cp[section]['use_as_data_source'] = str(node.use_as_data_source)
        cp[section]['stash_account_address'] = node.stash_account_address
