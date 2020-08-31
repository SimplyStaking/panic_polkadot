import hashlib
import os
from configparser import ConfigParser
from getpass import getpass

from src.utils.user_input import yn_prompt


def is_already_set_up(cp: ConfigParser, section: str) -> bool:
    # Find out if the section exists
    if section not in cp:
        return False

    # Find out if any value in the section (except for enabled) is filled-in
    for key in cp[section]:
        if key != 'enabled' and cp[section][key] != '':
            return True
    return False


def reset_section(section: str, cp: ConfigParser) -> None:
    # Remove and re-add specified section if it exists
    if cp.has_section(section):
        cp.remove_section(section)
    cp.add_section(section)


def setup_authentication(cp: ConfigParser) -> None:
    print('==== Authentication')
    print('For connections with the Web UI server to be secure, session-based '
          'authentication is used. You will now be asked to input a username, '
          'password, and a cookie secret (used to sign the cookie stored in '
          'the browser to avoid tampering). The inputted password will be '
          'hashed inside the config, so any future password changes should be '
          'made using the run_util_change_ui_auth_pass.py util. Note that if '
          'the authentication credentials are not inputted in the config, the '
          'UI server won\'t start. In addition to this, since the UI server is '
          'an HTTPS server, please also make sure that the key.pem and '
          'cert.pem files are included as presented in the documentation. This '
          'is important for maximum security.')

    if is_already_set_up(cp, 'authentication') and \
            not yn_prompt('Authentication for the UI is already set up. Do you '
                          'wish to replace the current config? (Y/n)\n'):
        return

    reset_section('authentication', cp)
    cp['authentication']['username'] = ''
    cp['authentication']['hashed_password'] = ''
    cp['authentication']['cookie_secret'] = ''

    auth_username = input('Please insert a username \n')
    print('Please insert a password')
    auth_password = getpass()
    salt = os.urandom(32)
    hashed_pass = hashlib.pbkdf2_hmac('sha256', auth_password.encode('utf-8'),
                                      salt, 100000)
    cookie_secret = input('Please insert a cookie secret. This should be '
                          'a string.\n')

    cp['authentication']['username'] = auth_username

    # First 64 characters are the salt, and the remaining characters
    # are the hashed password.
    cp['authentication']['hashed_password'] = (salt + hashed_pass).hex()
    cp['authentication']['cookie_secret'] = cookie_secret


def setup_ui(cp: ConfigParser) -> None:
    setup_authentication(cp)
    print()
