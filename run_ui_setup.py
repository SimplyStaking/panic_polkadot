from configparser import ConfigParser

from src.utils.setup import setup_user_config_ui


def run() -> None:
    # Initialise UI parser
    cp_ui = ConfigParser()
    cp_ui.read('config/user_config_ui.ini')

    # Start setup
    print('Welcome to the PANIC UI setup!\n')
    try:
        setup_user_config_ui.setup_ui(cp_ui)
        with open('config/user_config_ui.ini', 'w') as f:
            cp_ui.write(f, space_around_delimiters=False)
        print('Saved config/user_config_ui.ini\n')

        print('Setup completed!')
    except KeyboardInterrupt:
        print('Setup process stopped.')
        return


if __name__ == '__main__':
    run()
