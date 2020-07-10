import hashlib
import os
import sys
from configparser import ConfigParser

from src.utils.exceptions import InitialisationException
from src.utils.user_input import yn_prompt


def run() -> None:
    if not cp_ui.has_section('authentication'):
        raise InitialisationException(
            'You cannot change your UI password because UI authentication is '
            'not set up yet. Please set it up using the run_ui_setup.py script.'
        )

    if not cp_ui.has_option('authentication', 'hashed_password'):
        raise InitialisationException(
            'Missing key authentication.hashed_password in the '
            'config/user_config_ui.ini config file. Please set up UI '
            'authentication again using the run_ui_setup.py script as your '
            'config is invalid.'
        )

    while True:
        new_pass = input('Please insert your new password.\n')

        # The salt is the first 64 characters
        salt = bytes.fromhex(cp_ui['authentication']['hashed_password'][:64])
        hashed_new_pass = hashlib.pbkdf2_hmac(
            'sha256', new_pass.encode('utf-8'), salt, 100000
        )

        # Ask user if he really wants to change the password if the new password
        # is the same as the old one.
        if hashed_new_pass == \
                bytes.fromhex(
                    cp_ui['authentication']['hashed_password'][64:128]):
            if not yn_prompt('The new password is exactly the same as the old '
                             'password. Do you want to insert a different '
                             'password instead? (Y/n)\n'):
                print("Password did not change.")
                return
        else:
            # Generate a new salt to avoid situations where the user is suddenly
            # logged in without authenticating himself. This can happen if the
            # stored password matches the new password and the user is currently
            # not authenticated.
            salt = os.urandom(32)

            # Generate another hash with the new salt
            hashed_new_pass = hashlib.pbkdf2_hmac(
                'sha256', new_pass.encode('utf-8'), salt, 100000
            )

            # First 64 characters are the salt, and the remaining characters
            # are the hashed password.
            cp_ui['authentication']['hashed_password'] = \
                (salt + hashed_new_pass).hex()
            break

    print("Password changed successfully")


if __name__ == '__main__':
    try:
        cp_ui = ConfigParser()
        cp_ui.read('config/user_config_ui.ini')
        run()
        with open('config/user_config_ui.ini', 'w') as f:
            cp_ui.write(f, space_around_delimiters=False)
        print('Saved config/user_config_ui.ini')
    except InitialisationException as ie:
        sys.exit(ie)
    except KeyboardInterrupt:
        print('Util stopped.')
