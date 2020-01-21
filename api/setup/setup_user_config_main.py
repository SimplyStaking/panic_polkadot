from configparser import ConfigParser

from setup.utils.user_input import yn_prompt


def is_already_set_up(cp: ConfigParser, section: str) -> bool:
    # Find out if the section exists
    if section not in cp:
        return False

    # Find out if any value in the section (except for enabled) is filled-in
    for key in cp[section]:
        if cp[section][key] != '':
            return True
    return False


def reset_section(section: str, cp: ConfigParser) -> None:
    # Remove and re-add specified section if it exists
    if cp.has_section(section):
        cp.remove_section(section)
    cp.add_section(section)


def setup_api_server(cp: ConfigParser) -> None:
    print('==== API Server')
    print('The API Server makes it possible to query Polkadot Nodes and '
          'retrieve certain data about the node and the blockchain')

    already_set_up = is_already_set_up(cp, 'api_server')
    if already_set_up and \
            not yn_prompt('API Server is already set up. Do you wish '
                          'to clear the current config? (Y/n)\n'):
        return

    reset_section('api_server', cp)
    cp['api_server']['port'] = ''

    if not already_set_up and \
            not yn_prompt('Do you wish to set up the API Server? (Y/n)\n'):
        return

    print('You will now be asked to input the port that will be used by the '
          'JS API.\nIf you will be using the JS API as a Docker container, '
          'you must leave this port as the default.')
    port = input('Please insert the port you would like the API Server to use: '
                 '(default: 3000)\n')
    port = '3000' if port == '' else port

    cp['api_server']['port'] = port


def setup_all(cp: ConfigParser) -> None:
    setup_api_server(cp)
    print()
    print('Setup finished.')
