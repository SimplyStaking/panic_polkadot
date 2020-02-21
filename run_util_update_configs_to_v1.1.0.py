import os
from configparser import ConfigParser


def main():
    if not os.path.isfile('config/user_config_main.ini'):
        print('The main user config does not exist, so there is no need to '
              'update it.')
        print('To create this file, you can run the setup (run_setup.py).')
        return

    cp = ConfigParser()
    cp.read('config/user_config_main.ini')

    # Add mongo_enabled key to periodic_alive_reminder section
    if 'mongo_enabled' in cp['periodic_alive_reminder']:
        print('Periodic alive reminder config was already updated.')
    else:
        cp['periodic_alive_reminder']['mongo_enabled'] = 'False'
        print('Periodic alive reminder config UPDATED.')

    # Create mongo section
    if 'mongo' in cp:
        print('MongoDB config was already updated.')
    else:
        cp.add_section('mongo')
        cp['mongo']['enabled'] = str(False)
        cp['mongo']['host'] = ''
        cp['mongo']['port'] = ''
        cp['mongo']['db_name'] = ''
        cp['mongo']['user'] = ''
        cp['mongo']['pass'] = ''
        print('MongoDB config UPDATED.')

    with open('config/user_config_main.ini', 'w') as f:
        cp.write(f)
        print('The update process of the main config is finished.')


def nodes():
    if not os.path.isfile('config/user_config_nodes.ini'):
        print('The nodes user config does not exist, so there is no need to '
              'update it.')
        print('To create this file, you can run the setup (run_setup.py).')
        return

    cp = ConfigParser()
    cp.read('config/user_config_nodes.ini')

    sections = [cp[k] for k in cp.keys() if k.startswith('node_')]

    # If the nodes config file is empty, there are no sub-configs that need to
    # be updated.
    if len(sections) == 0:
        print("There are no nodes in the nodes user config file. "
              "Therefore, the nodes user config file does not need any "
              "updating.")
        return

    # For every sub-config, do the necessary updates if they are not already
    # done.
    for section in sections:
        if 'include_in_node_monitor' in section or \
                'include_in_blockchain_monitor' in section:
            print('The new keys \'monitor_node\' and \'use_as_data_source\' '
                  'have been set to true by default. This was done because '
                  'they have different meanings from the '
                  '\'include_in_blockchain_monitor\' and the '
                  '\'include_in_node_monitor\' keys.')
            cp.remove_option(section.name, 'include_in_node_monitor')
            cp.remove_option(section.name, 'include_in_blockchain_monitor')
            cp[section.name]['monitor_node'] = 'true'
            cp[section.name]['use_as_data_source'] = 'true'
            print(section.name + " config was successfully updated.")
        else:
            print(section.name + " config was already updated.")

    with open('config/user_config_nodes.ini', 'w') as f:
        cp.write(f)
        print('The update process of the nodes config is finished.')


def repos():
    if not os.path.isfile('config/user_config_repos.ini'):
        print('The repos user config does not exist, so there is no need to '
              'update it.')
        print('To create this file, you can run the setup (run_setup.py).')
        return

    cp = ConfigParser()
    cp.read('config/user_config_repos.ini')

    sections = [cp[k] for k in cp.keys() if k.startswith('repo_')]

    # If the repos config file is empty, there are no sub-configs that need to
    # be updated.
    if len(sections) == 0:
        print("There are no repos in the repos user config file. "
              "Therefore, the repos user config file does not need any "
              "updating.")
        return

    # For every sub-config, do the necessary updates if they are not already
    # done.
    for section in sections:
        if 'include_in_github_monitor' in section:
            cp[section.name]['monitor_repo'] = \
                cp[section.name]['include_in_github_monitor']
            cp.remove_option(section.name, 'include_in_github_monitor')
            print(section.name + " config was successfully updated.")
        else:
            print(section.name + " config was already updated.")

    with open('config/user_config_repos.ini', 'w') as f:
        cp.write(f)
        print('The update process of the repos config is finished.')


if __name__ == '__main__':
    main()
    nodes()
    repos()
