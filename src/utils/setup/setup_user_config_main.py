from configparser import ConfigParser
from datetime import timedelta

from src.utils.data_wrapper.polkadot_api import PolkadotApiWrapper
from src.utils.datetime import strfdelta
from src.utils.setup.setup_user_config_main_tests import *
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


def setup_general(cp: ConfigParser) -> None:
    print('==== General')
    print('The first step is to set a unique identifier for the alerter. This '
          'can be any word that uniquely describes the setup being monitored. '
          'Uniqueness is very important if you are running multiple instances '
          'of the PANIC alerter, to avoid any possible namespace clashes. The '
          'name will only be used internally and will not show up in alerts.')

    if is_already_set_up(cp, 'general'):
        identifier = cp['general']['unique_alerter_identifier']
        if not yn_prompt(
                'A unique alerter identifier \'{}\' is already set. Do you '
                'wish to change this identifier? (Y/n)\n'.format(identifier)):
            return

    reset_section('general', cp)
    cp['general']['unique_alerter_identifier'] = ''

    while True:
        identifier = input('Please insert the unique identifier:\n')
        if len(identifier) != 0:
            break
        else:
            print('The unique identifier cannot be blank.')

    cp['general']['unique_alerter_identifier'] = identifier


def setup_telegram_alerts(cp: ConfigParser) -> None:
    print('---- Telegram Alerts')
    print('Alerts sent via Telegram are a fast and reliable means of alerting '
          'that we highly recommend setting up. This requires you to have a '
          'Telegram bot set up, which is a free and quick procedure.')

    if is_already_set_up(cp, 'telegram_alerts') and \
            not yn_prompt('Telegram alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('telegram_alerts', cp)
    cp['telegram_alerts']['enabled'] = str(False)
    cp['telegram_alerts']['bot_token'] = ''
    cp['telegram_alerts']['bot_chat_id'] = ''

    if not yn_prompt('Do you wish to set up Telegram alerts? (Y/n)\n'):
        return

    while True:
        while True:
            bot_token = input('Please insert your Telegram bot\'s API token:\n')
            bot_api = TelegramBotApi(bot_token, None)

            confirmation = bot_api.get_me()
            if not confirmation['ok']:
                print(str(confirmation))
            else:
                print('Successfully connected to Telegram bot.')
                break

        bot_chat_id = input('Please insert the chat ID for Telegram alerts:\n')
        bot_api = TelegramBotApi(bot_token, bot_chat_id)

        if yn_prompt('Do you wish to test Telegram alerts now? (Y/n)\n'):
            test = test_telegram_alerts(bot_api)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['telegram_alerts']['enabled'] = str(True)
    cp['telegram_alerts']['bot_token'] = bot_token
    cp['telegram_alerts']['bot_chat_id'] = bot_chat_id


def setup_email_alerts(cp: ConfigParser) -> None:
    print('---- Email Alerts')
    print('Email alerts are more useful as a backup alerting channel rather '
          'than the main one, given that one is much more likely to notice a '
          'a message on Telegram or a phone call. Email alerts also require '
          'an SMTP server to be set up for the alerter to be able to send.')

    if is_already_set_up(cp, 'email_alerts') and \
            not yn_prompt('Email alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('email_alerts', cp)
    cp['email_alerts']['enabled'] = str(False)
    cp['email_alerts']['smtp'] = ''
    cp['email_alerts']['from'] = ''
    cp['email_alerts']['to'] = ''
    cp['email_alerts']['user'] = ''
    cp['email_alerts']['pass'] = ''

    if not yn_prompt('Do you wish to set up email alerts? (Y/n)\n'):
        return

    while True:
        email_smtp = input('Please insert the SMTP server\'s address:\n')

        email_user = input('Please insert the username for SMTP authentication '
                           '(blank for no authentication):\n')
        if len(email_user) != 0:
            email_pass = input('Please insert the password for SMTP '
                               'authentication:\n')
        else:
            email_pass = ''

        email_from = input('Please specify the details of the sender in the '
                           'format shown below:\n\t'
                           'example_sender@email.com\n')

        email_to = input('Please specify the email address where you wish to '
                         'receive email alerts:\n\t'
                         'example_recipient@email.com\n')

        while yn_prompt('Do you wish to add another email address? (Y/n)\n'):
            email_to += ';' + input('Please insert the email address:\n')

        if yn_prompt('Do you wish to test email alerts now? The first '
                     'email address inserted will be used. (Y/n)\n'):
            test = test_email_alerts(email_smtp, email_from,
                                     email_to.split(';')[0],
                                     email_user, email_pass)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['email_alerts']['enabled'] = str(True)
    cp['email_alerts']['smtp'] = email_smtp
    cp['email_alerts']['from'] = email_from
    cp['email_alerts']['to'] = email_to
    cp['email_alerts']['user'] = email_user
    cp['email_alerts']['pass'] = email_pass


def setup_twilio_alerts(cp: ConfigParser) -> None:
    print('---- Twilio Alerts')
    print('Twilio phone-call alerts are the most important alerts since they '
          'are the best at grabbing your attention, especially when you\'re '
          'asleep! To set these up, you have to have a Twilio account set up, '
          'with a registered Twilio phone number and a verified phone number.'
          'The timed trial version of Twilio is free.')

    if is_already_set_up(cp, 'twilio_alerts') and \
            not yn_prompt('Twilio alerts are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    reset_section('twilio_alerts', cp)
    cp['twilio_alerts']['enabled'] = str(False)
    cp['twilio_alerts']['account_sid'] = ''
    cp['twilio_alerts']['auth_token'] = ''
    cp['twilio_alerts']['twilio_phone_number'] = ''
    cp['twilio_alerts']['phone_numbers_to_dial'] = ''

    if not yn_prompt('Do you wish to set up Twilio alerts? (Y/n)\n'):
        return

    while True:

        while True:
            account_sid = input('Please insert your Twilio account SID:\n')
            auth_token = input('Please insert your Twilio account AuthToken:\n')

            try:
                twilio_api = TwilioApi(account_sid, auth_token)
                print('Successfully connected to Twilio.')
                break
            except Exception as e:
                print('Something went wrong: {}'.format(e))

        twilio_no = input('Please insert your registered Twilio phone number '
                          'in the format shown below:\n\t'
                          'E.164 format, for example: +12025551234\n')

        to_dial = input('Please insert the first phone number to dial for '
                        'alerting purposes in the format shown below:\n\t'
                        'E.164 format, for example: +12025551234\n')

        while yn_prompt('Do you wish to add another number? (Y/n)\n'):
            to_dial += ';' + input('Please insert the phone number:\n')

        if yn_prompt('Do you wish to test Twilio alerts now? The first '
                     'phone number inserted will be called. (Y/n)\n'):
            test = test_twilio_alerts(twilio_no, to_dial.split(';')[0],
                                      twilio_api)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['twilio_alerts']['enabled'] = str(True)
    cp['twilio_alerts']['account_sid'] = account_sid
    cp['twilio_alerts']['auth_token'] = auth_token
    cp['twilio_alerts']['twilio_phone_number'] = twilio_no
    cp['twilio_alerts']['phone_numbers_to_dial'] = to_dial


def setup_alert_channels(cp: ConfigParser) -> None:
    print('==== Alerts')
    print('By default, alerts are output to a log file and to '
          'the console. Let\'s set up the rest of the alerts.')
    setup_telegram_alerts(cp)
    setup_email_alerts(cp)
    setup_twilio_alerts(cp)


def setup_telegram_commands(cp: ConfigParser) -> None:
    print('---- Telegram Commands')
    print('Telegram is also used as a two-way interface with the alerter and '
          'as an assistant, allowing you to do things such as snooze phone '
          'call alerts and to get the alerter\'s current status from Telegram. '
          'Once again, this requires you to set up a Telegram bot, which is '
          'free and easy. You can reuse the Telegram bot set up for alerts.')

    if is_already_set_up(cp, 'telegram_commands') and \
            not yn_prompt('Telegram commands are already set up. Do you '
                          'wish to clear the current config? (Y/n)\n'):
        return

    print('NOTE: If you are running more than one instance of the PANIC '
          'alerter, do not use the same telegram bot as the other instance/s.')

    reset_section('telegram_commands', cp)
    cp['telegram_commands']['enabled'] = str(False)
    cp['telegram_commands']['bot_token'] = ''
    cp['telegram_commands']['bot_chat_id'] = ''

    if not yn_prompt('Do you wish to set up Telegram commands? (Y/n)\n'):
        return

    while True:
        while True:
            bot_token = input('Please insert your Telegram bot\'s API token:\n')
            bot_api = TelegramBotApi(bot_token, None)

            confirmation = bot_api.get_me()
            if not confirmation['ok']:
                print(str(confirmation))
            else:
                print('Successfully connected to Telegram bot.')
                break

        bot_chat_id = input('Please insert the authorised chat ID:\n')

        if yn_prompt('Do you wish to test Telegram commands now? (Y/n)\n'):
            test = test_telegram_commands(bot_token, bot_chat_id)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['telegram_commands']['enabled'] = str(True)
    cp['telegram_commands']['bot_token'] = bot_token
    cp['telegram_commands']['bot_chat_id'] = bot_chat_id


def setup_commands(cp: ConfigParser) -> None:
    print('==== Commands')
    setup_telegram_commands(cp)


def setup_redis(cp: ConfigParser) -> None:
    print('==== Redis')
    print('Redis is used by the alerter to persist data every now and then, '
          'so that it can continue where it left off if it is restarted. It '
          'is also used to be able to get the status of the alerter and to '
          'have some control over it, such as to snooze Twilio phone calls.')

    if is_already_set_up(cp, 'redis') and \
            not yn_prompt('Redis is already set up. Do you wish '
                          'to clear the current config? (Y/n)\n'):
        return

    reset_section('redis', cp)
    cp['redis']['enabled'] = str(False)
    cp['redis']['host'] = ''
    cp['redis']['port'] = ''
    cp['redis']['password'] = ''

    if not yn_prompt('Do you wish to set up Redis? (Y/n)\n'):
        return

    while True:
        print('You will now be asked to input the IP of the Redis server.\n'
              'If you will be running PANIC using Docker, do not use '
              'localhost, instead use the full IP address (local or external) '
              'of the machine that the Redis container will be running on.')
        host = input('Please insert the Redis host IP: (default: localhost)\n')
        host = 'localhost' if host == '' else host

        print('You will now be asked to input the port of the Redis server.\n'
              'If you will be running PANIC using Docker, you should leave the '
              'port as the default. If you wish to run the Redis container on '
              'another port, please input this port number here and change the '
              '`REDIS_HOST_PORT` value inside the `panic_polkadot/.env` file.')
        port = input('Please insert the Redis host port: (default: 6379)\n')
        port = '6379' if port == '' else port

        password = input('Please insert the Redis password:\n')

        if yn_prompt('Do you wish to test Redis now? (Y/n)\n'):
            test = test_redis(host, port, password)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['redis']['enabled'] = str(True)
    cp['redis']['host'] = host
    cp['redis']['port'] = port
    cp['redis']['password'] = password


def setup_mongo(cp: ConfigParser) -> None:
    print('==== MongoDB')
    print('Mongo can be set up to persist any alert in a MongoDB collection.')

    if is_already_set_up(cp, 'mongo') and \
            not yn_prompt('Mongo is already set up. Do you wish '
                          'to clear the current config? (Y/n)\n'):
        return

    reset_section('mongo', cp)
    cp['mongo']['enabled'] = str(False)
    cp['mongo']['host'] = ''
    cp['mongo']['port'] = ''
    cp['mongo']['db_name'] = ''
    cp['mongo']['user'] = ''
    cp['mongo']['pass'] = ''

    if not yn_prompt('Do you wish to set up Mongo? (Y/n)\n'):
        return

    while True:
        print('You will now be asked to input the IP of the Mongo server.\n'
              'If you will be running PANIC using Docker, do not use '
              'localhost, instead use the full IP address (local or external) '
              'of the machine that the Mongo container will be running on.')
        host = input('Please insert the Mongo host IP: (default: localhost)\n')
        host = 'localhost' if host == '' else host

        print('You will now be asked to input the port of the Mongo server.\n'
              'If you will be running PANIC using Docker, you should leave the '
              'port as the default. If you wish to run the Mongo container on '
              'another port, please input this port number here and change the '
              '`MONGO_HOST_PORT` value inside the `panic_polkadot/.env` file.')
        port = input('Please insert the Mongo host port: (default: 27017)\n')
        port = '27017' if port == '' else port

        print('You will now be asked which database you wish to use to store '
              'the alerts. This will be auto-created if it does not exist. '
              'You can re-use the same database if another PANIC is installed.')
        while True:
            db_name = input('Please insert database name: (default: panic)\n')
            db_name = 'panic' if db_name == '' else db_name
            if ' ' in db_name:
                print('Database name cannot contain spaces.')
            else:
                break

        username = input('Please insert the username for authentication '
                         '(blank for no authentication):\n')
        if len(username) != 0:
            password = input('Please insert the password for authentication:\n')
        else:
            password = ''

        if yn_prompt('Do you wish to test Mongo now? (Y/n)\n'):
            test = test_mongo(host, port, username, password)
            if test == TestOutcome.RestartSetup:
                continue
            elif test == TestOutcome.SkipSetup:
                return
        break

    cp['mongo']['enabled'] = str(True)
    cp['mongo']['host'] = host
    cp['mongo']['port'] = port
    cp['mongo']['db_name'] = db_name
    cp['mongo']['user'] = username
    cp['mongo']['pass'] = password


def setup_periodic_alerts(cp: ConfigParser) -> None:
    print('==== Periodic alerts')
    setup_periodic_alive_reminder(cp)


def setup_periodic_alive_reminder(cp: ConfigParser) -> None:
    print('---- Periodic alive reminder')
    print('The periodic alive reminder is a way for the alerter to inform its '
          'users that it is still running.')

    if is_already_set_up(cp, 'periodic_alive_reminder') and \
            not yn_prompt('The periodic alive reminder is already set up. '
                          'Do you wish to clear the current config? (Y/n)\n'):
        return

    reset_section('periodic_alive_reminder', cp)
    cp['periodic_alive_reminder']['enabled'] = str(False)
    cp['periodic_alive_reminder']['interval_seconds'] = ''
    cp['periodic_alive_reminder']['email_enabled'] = ''
    cp['periodic_alive_reminder']['telegram_enabled'] = ''
    cp['periodic_alive_reminder']['mongo_enabled'] = ''

    if not yn_prompt('Do you wish to set up the periodic alive reminder? '
                     '(Y/n)\n'):
        return

    interval = input("Please enter the amount of seconds you want to "
                     "pass for the periodic alive reminder. Make sure that "
                     "you insert a positive integer.\n")
    while True:
        try:
            interval_number_rep = int(interval)
        except ValueError:
            interval = input("Input is not a valid integer. Please enter "
                             "another value:\n")
            continue
        if interval_number_rep > 0:
            time = timedelta(seconds=int(interval_number_rep))
            time = strfdelta(time, "{hours}h {minutes}m {seconds}s")
            if yn_prompt(
                    'You will be reminded that the alerter is still running '
                    'every {}. Is this correct (Y/n) \n'.format(time)):
                break
            else:
                interval = input(
                    "Please enter the amount of seconds you want to "
                    "pass for the periodic alive reminder. Make sure that "
                    "you insert a positive integer.\n")
        else:
            interval = input("Input is not a positive integer. Please enter "
                             "another value:\n")

    if is_already_set_up(cp, 'email_alerts') and \
            cp['email_alerts']['enabled'] and \
            yn_prompt('Would you like the periodic alive reminder '
                      'to send alerts via e-mail? (Y/n)\n'):
        email_enabled = str(True)
    else:
        email_enabled = str(False)

    if is_already_set_up(cp, 'telegram_alerts') and \
            cp['telegram_alerts']['enabled'] and \
            yn_prompt('Would you like the periodic alive reminder '
                      'to send alerts via Telegram? (Y/n)\n'):
        telegram_enabled = str(True)
    else:
        telegram_enabled = str(False)

    if is_already_set_up(cp, 'mongo') and cp['mongo']['enabled'] and \
            yn_prompt('Would you like the periodic alive reminder '
                      'to save alerts to Mongo? (Y/n)\n'):
        mongo_enabled = str(True)
    else:
        mongo_enabled = str(False)

    cp['periodic_alive_reminder']['enabled'] = str(True)
    cp['periodic_alive_reminder']['interval_seconds'] = interval
    cp['periodic_alive_reminder']['email_enabled'] = email_enabled
    cp['periodic_alive_reminder']['telegram_enabled'] = telegram_enabled
    cp['periodic_alive_reminder']['mongo_enabled'] = mongo_enabled


def setup_api(cp: ConfigParser) -> None:
    print('==== Polkadot API Server')
    print('The Polkadot API Server is used by the alerter to get data from the '
          'nodes. It is important that before running both the alerter and '
          'this setup, the Polkadot API Server is set up and running.')

    if is_already_set_up(cp, 'api') and \
            not yn_prompt('The Polkadot API Server is already set up. Do you '
                          'wish to replace the current config? (Y/n)\n'):
        return

    reset_section('api', cp)
    cp['api']['polkadot_api_endpoint'] = ''

    while True:
        print('You will now be asked to input the API Server\'s address\n'
              'If you will be running PANIC using Docker, do not use '
              'localhost, instead use the full IP address (local or external) '
              'of the machine that the API container will be running on.\n'
              'You should also set the port to 3000. Otherwise, you must run '
              'the API Docker using -p <port>:3000.')
        polkadot_api_endpoint = input('Please insert the API Server\'s address:'
                                      ' (default: http://localhost:3000)\n')
        polkadot_api_endpoint = 'http://localhost:3000' if \
            polkadot_api_endpoint == '' else polkadot_api_endpoint
        polkadot_api = PolkadotApiWrapper(DUMMY_LOGGER,
                                          polkadot_api_endpoint)
        print('Testing connection with endpoint {}'.
              format(polkadot_api_endpoint))
        try:
            polkadot_api.ping_api()
            print('Success.')
            break
        except Exception:
            if not yn_prompt('Failed to connect to endpoint. Do '
                             'you want to try again? (Y/n)\n'):
                return None

    cp['api']['polkadot_api_endpoint'] = polkadot_api_endpoint


def setup_all(cp: ConfigParser) -> None:
    setup_general(cp)
    print()
    setup_alert_channels(cp)
    print()
    setup_mongo(cp)
    print()
    setup_periodic_alerts(cp)
    print()
    setup_commands(cp)
    print()
    setup_redis(cp)
    print()
    setup_api(cp)
    print()
    print('Setup finished.')
