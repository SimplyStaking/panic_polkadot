import logging
from datetime import timedelta, datetime
from typing import Optional, Dict, List

from pymongo.errors import PyMongoError
from redis import RedisError
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, \
    CallbackContext

from src.alerters.reactive.node import Node
from src.store.mongo.mongo_api import MongoApi
from src.store.redis.redis_api import RedisApi
from src.store.store_keys import *
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.types import NONE
from src.web.commands import Commands
from src.web.telegram.telegram_handler import TelegramCommandHandler


class TelegramCommands(Commands):

    def __init__(self, bot_token: str, authorised_chat_id: str,
                 logger: logging.Logger, redis: Optional[RedisApi],
                 mongo: Optional[MongoApi],
                 node_monitor_nodes_by_chain: Dict[str, List[Node]],
                 archive_alerts_disabled_by_chain: Dict[str, bool],
                 internal_conf: InternalConfig = InternalConf,
                 user_conf: UserConfig = UserConf) -> None:

        super().__init__(logger, redis, mongo, node_monitor_nodes_by_chain,
                         archive_alerts_disabled_by_chain,
                         internal_conf, user_conf)

        # Get default snooze and mute hours
        self._default_snooze_hours = \
            internal_conf.redis_twilio_snooze_key_default_hours
        self._default_mute_hours = \
            internal_conf.redis_periodic_alive_reminder_mute_key_default_hours

        # Set up command handlers (command and respective callback function)
        command_handlers = [
            CommandHandler('start', self._start_callback),
            CommandHandler('snooze', self._snooze_callback),
            CommandHandler('mute', self._mute_callback),
            CommandHandler('unmute', self._unmute_callback),
            CommandHandler('unsnooze', self._unsnooze_callback),
            CommandHandler('status', self._status_callback),
            CommandHandler('validators', self._validators_callback),
            CommandHandler('block', self._block_callback),
            CommandHandler('tx', self._tx_callback),
            CommandHandler('help', self._help_callback),
            MessageHandler(Filters.command, self._unknown_callback)
        ]

        # Create command handler with the command handlers
        self.cmd_handler = TelegramCommandHandler(
            bot_token, authorised_chat_id, command_handlers)

    def start_listening(self) -> None:
        # Start listening for commands
        self.cmd_handler.start_handling()

    def redis_running(self) -> bool:
        try:
            self._redis.ping_unsafe()
            return True
        except (RedisError, ConnectionResetError):
            pass
        except Exception as e:
            self._logger.error('Unrecognized error when accessing Redis: %s', e)
        return False

    def mongo_running(self) -> bool:
        try:
            self._mongo.ping_unsafe()
            return True
        except PyMongoError:
            pass
        except Exception as e:
            self._logger.error('Unrecognized error when accessing Mongo: %s', e)
        return False

    @staticmethod
    def formatted_reply(update: Update, reply: str):
        # Adds Markdown formatting
        update.message.reply_text(reply, parse_mode='Markdown')

    @staticmethod
    def trim_monitor_name(node_monitor: str) -> str:
        # ....(node).... -> node
        open_br = node_monitor.index('(')
        close_br = node_monitor.index(')')
        return node_monitor[open_br + 1:close_br]

    def _start_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/start: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Send welcome message
        update.message.reply_text("Welcome to the PANIC alerter bot!\n"
                                  "Type /help for more information.")

    def _snooze_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/snooze: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Does not make sense to snooze if twilio alerts not enabled
        if not self._user_conf.twilio_alerts_enabled:
            update.message.reply_text('Snoozing is not available given that '
                                      'Twilio calls were not set up.')
            return

        # Cannot snooze if Redis is not enabled
        if not self._redis_enabled:
            update.message.reply_text('Snoozing is not available given '
                                      'that Redis is not set up.')
            return

        # Expected: /snooze or /snooze <hours>
        message_parts = update.message.text.split(' ')
        if len(message_parts) not in [1, 2]:
            update.message.reply_text('I expected one or no values.')
            return

        # Get number of hours
        if len(message_parts) == 1:
            hours = self._default_snooze_hours
        else:  # len(message_parts) == 2
            try:
                hours = timedelta(hours=float(message_parts[1]))
            except ValueError:
                update.message.reply_text('Invalid no. of hours.')
                return

        # Set temporary Redis key signifying the snooze
        until = str(datetime.now() + hours)
        set_ret = self._redis.set_for(Keys.get_twilio_snooze(), until, hours)
        if set_ret is None:
            update.message.reply_text(
                'Snoozing unsuccessful due to an issue with '
                'Redis. Check /status to see if it is online.')
        else:
            extra_message_if_default = \
                " To snooze for a longer period of time, specify the number " \
                "of hours after the /snooze." if len(message_parts) == 1 else ""
            update.message.reply_text(
                'Calls have been snoozed for {} hours until {}.{}'
                ''.format(hours, until, extra_message_if_default))

    def _unsnooze_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/unsnooze: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Cannot unsnooze if Redis is not enabled
        if not self._redis_enabled:
            update.message.reply_text('Unsnoozing is not available given '
                                      'that Redis is not set up.')
            return

        # Cannot unsnooze if Redis not running
        if not self.redis_running():
            update.message.reply_text(
                'Unsnoozing unsuccessful due to an issue with '
                'Redis. Check /status to see if it is online.')
            return

        # Check if snooze key exists
        if not self._redis.exists(Keys.get_twilio_snooze()):
            update.message.reply_text('Twilio calls were not snoozed.')
            return

        # Unsnooze by deleting the snooze key
        self._redis.remove(Keys.get_twilio_snooze())
        update.message.reply_text('Twilio calls have been unsnoozed.')

    def _mute_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/mute: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Does not make sense to mute if reminder not enabled
        if not self._user_conf.par_enabled:
            update.message.reply_text('Muting is not available given that the '
                                      'periodic alive reminder is not set up.')
            return

        # Cannot mute if Redis is not enabled
        if not self._redis_enabled:
            update.message.reply_text('Muting is not available given that '
                                      'Redis is not set up.')
            return

        # Expected: /mute or /mute <hours>
        message_parts = update.message.text.split(' ')
        if len(message_parts) not in [1, 2]:
            update.message.reply_text('I expected one or no values.')
            return

        # Get number of hours
        if len(message_parts) == 1:
            hours = self._default_mute_hours
        else:  # len(message_parts) == 2
            try:
                hours = timedelta(hours=float(message_parts[1]))
            except ValueError:
                update.message.reply_text('Invalid no. of hours.')
                return

        # Set temporary Redis key signifying the mute
        until = str(datetime.now() + hours)
        set_ret = self._redis.set_for(Keys.get_alive_reminder_mute(), until,
                                      hours)
        if set_ret is None:
            update.message.reply_text(
                'Muting unsuccessful due to an issue with '
                'Redis. Check /status to see if it is online.')
        else:
            extra_message_if_default = \
                " To mute for a longer period of time, specify the number of " \
                "hours after the /mute." if len(message_parts) == 1 else ""
            update.message.reply_text(
                'The periodic alive reminder has been muted for {} hours until '
                '{}.{}'.format(hours, until, extra_message_if_default))

    def _unmute_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/unmute: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Cannot unmute if Redis is not enabled
        if not self._redis_enabled:
            update.message.reply_text('Unmuting is not available given '
                                      'that Redis is not set up.')
            return

        # Cannot unmute if Redis not running
        if not self.redis_running():
            update.message.reply_text(
                'Unmuting unsuccessful due to an issue with '
                'Redis. Check /status to see if it is online.')
            return

        # Check if mute key exists
        if not self._redis.exists(Keys.get_alive_reminder_mute()):
            update.message.reply_text('Periodic alive reminder was not muted.')
            return

        # Unmute by deleting the mute key
        self._redis.remove(Keys.get_alive_reminder_mute())
        update.message.reply_text('Periodic alive reminder has been unmuted.')

    def _get_monitor_last_update(self, key: str, name: str):
        last_upd = self._redis.get(key).decode('utf-8')
        last_upd = last_upd.split('.')[0]  # remove milliseconds
        last_upd = float(last_upd)
        last_upd = datetime.fromtimestamp(last_upd)
        return '- Last update from *{}*: `{}`.\n'.format(name, last_upd)

    def _get_redis_based_status(self):
        status = ""

        # Add Redis status if it is running
        if self._redis.is_live:
            status += '- Redis is running normally.\n'
        else:
            status += '- Redis is running normally but was not accessible ' \
                      'a short while ago. Recent updates might not be ' \
                      'available until the monitors detect Redis as alive. ' \
                      'Snoozing and muting might not work as expected.\n'

        # Add Twilio calls snooze state to status if Twilio enabled
        if self._user_conf.twilio_alerts_enabled:
            if self._redis.exists(Keys.get_twilio_snooze()):
                until = self._redis.get(Keys.get_twilio_snooze()).decode(
                    "utf-8")
                status += '- Twilio calls are snoozed until {}.\n'.format(until)
            else:
                status += '- Twilio calls are not snoozed.\n'

        # Add periodic alive reminder mute state to status if reminder enabled
        if self._user_conf.par_enabled:
            if self._redis.exists(Keys.get_alive_reminder_mute()):
                until = self._redis.get(Keys.get_alive_reminder_mute()).decode(
                    "utf-8")
                status += '- The periodic alive reminder has ' \
                          'been muted until {}.\n'.format(until)
            else:
                status += '- The periodic alive reminder is not muted.\n'

        # Add node monitor latest updates to status
        # TODO: consider getting nodes from config
        node_monitor_keys_list = self._redis.get_keys(
            Keys.get_node_monitor_alive("*"))
        node_monitor_names = [
            k.replace(Keys.get_node_monitor_alive(""), '')
            for k in node_monitor_keys_list]
        node_names = [self.trim_monitor_name(n) for n in node_monitor_names]
        for key, name in zip(node_monitor_keys_list, node_monitor_names):
            status += self._get_monitor_last_update(key, name)

        # Add note if no latest node monitor updates
        if len(node_monitor_keys_list) == 0:
            status += '- No recent update from node monitors.\n'

        # Print the current block height if archive alerts enabled for chain
        for nn, nmn in zip(node_names, node_monitor_names):
            if nn in self._archive_alerts_disabled_for_chain_by_node and \
                    not self._archive_alerts_disabled_for_chain_by_node[nn]:
                key_lh = Keys.get_node_monitor_last_height_checked(nmn)
                last_height_checked = self._redis.get_int(key_lh)
                if last_height_checked != NONE:
                    status += '- *{}* is currently in block height {}.\n' \
                        .format(nmn, last_height_checked)

        # Add blockchain monitor latest updates to status
        # TODO: consider getting blockchains from config
        blockchain_monitor_keys_list = self._redis.get_keys(
            Keys.get_blockchain_monitor_alive("*"))
        blockchain_monitor_names = [
            k.replace(Keys.get_blockchain_monitor_alive(""), '')
            for k in blockchain_monitor_keys_list
        ]
        for key, name in zip(blockchain_monitor_keys_list,
                             blockchain_monitor_names):
            status += self._get_monitor_last_update(key, name)

        # Add note if no latest blockchain monitor updates
        if len(blockchain_monitor_keys_list) == 0:
            status += '- No recent update from blockchain monitors.\n'

        return status

    def _get_mongo_based_status(self):
        status = ""

        if not self._mongo.is_live:
            status += '- Mongo is running normally but was not accessible ' \
                      'a short while ago. Recent alerts might be missing ' \
                      'from Mongo (and the UI) as a result, until the ' \
                      'monitors detect Mongo as alive.\n'
        else:
            status += '- Mongo is running normally.\n'

        return status

    def _status_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/status: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Start forming the status message
        status = ""
        update.message.reply_text('Generating status...')

        # Add mongo-based status if it is enabled and running
        if not self._user_conf.mongo_enabled:
            status += '- Mongo-based status update is not available given ' \
                      'that Mongo is not set up.\n'
        elif not self.mongo_running():
            status += '- Mongo is NOT accessible! This means that recent ' \
                      'alerts will be missing from Mongo as a result, ' \
                      'until the monitors detect Mongo as alive.\n'
        else:
            status += self._get_mongo_based_status()

        # Add redis-based status if it is enabled and running
        if not self._redis_enabled:
            # Status still shown since when Redis is not set up, the status
            # will be mostly empty. It's important to let the user know why.
            status += '- Redis-based status update is not available given ' \
                      'that Redis is not set up.\n'
        elif not self.redis_running():
            status += '- Redis is NOT accessible! This means calls are ' \
                      'considered not snoozed, the periodic alive reminder ' \
                      'is not muted, and any recent update from monitors is ' \
                      'not accessible.\n'
        else:
            status += self._get_redis_based_status()

        # Send status
        TelegramCommands.formatted_reply(
            update, status[:-1] if status.endswith('\n') else status)

    def _validators_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/validators: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Send list of links to validators
        update.message.reply_text(
            'Links to validators:\n'
            '  Polkascan: {}\n'
            '  Polkastats: {}\n'.format(
                self._internal_conf.validators_polkascan_link,
                self._internal_conf.validators_polkastats_link))

    def _block_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/block: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Expected: /block <block>
        message_parts = update.message.text.split(' ')
        if len(message_parts) != 2:
            update.message.reply_text("I expected exactly one value.")
            return

        # Send list of links to specified block
        try:
            block_height = int(message_parts[1])
            update.message.reply_text(
                'Links to block:\n'
                '  Polkascan: {}{}\n'
                '  Boka.Network: {}{}\n'
                '  Subscan: {}{}'.format(
                    self._internal_conf.block_polkascan_link_prefix,
                    block_height,
                    self._internal_conf.block_boka_network_link_prefix,
                    block_height,
                    self._internal_conf.block_subscan_link_prefix,
                    block_height))
        except ValueError:
            update.message.reply_text("I expected a block height.")

    def _tx_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/tx: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Expected: /tx <hash>
        message_parts = update.message.text.split(' ')
        if len(message_parts) != 2:
            update.message.reply_text("I expected exactly one value.")
            return

        # Send list of links to the specified transaction
        message_parts = update.message.text.split(' ')
        if len(message_parts) == 2:
            tx_hash = message_parts[1]
            update.message.reply_text(
                'Links to transaction:\n'
                '  Polkascan: {}\n'.format(
                    self._internal_conf.tx_polkascan_link_prefix +
                    str(tx_hash)))
        else:
            update.message.reply_text("I expected exactly one value.")

    def _help_callback(self, update: Update, context: CallbackContext):
        self._logger.info('/help: update=%s, context=%s', update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Send help message with available commands
        update.message.reply_text(
            'Hey! These are the available commands:\n'
            '  /start: welcome message\n'
            '  /ping: ping the Telegram commands handler\n'
            '  /snooze <hours>: snoozes phone calls for <hours>\n'
            '  /unsnooze: unsnoozes phone calls\n'
            '  /mute <hours>: mute periodic alive reminder for <hours>\n'
            '  /unmute: unmute periodic alive reminder\n'
            '  /status: shows status message\n'
            '  /validators: shows links to validators\n'
            '  /block <height>: shows link to specified block\n'
            '  /tx <tx-hash>: shows link to specified transaction\n'
            '  /help: shows this message')

    def _unknown_callback(self, update: Update,
                          context: CallbackContext) -> None:
        self._logger.info(
            'Received unrecognized command: update=%s, context=%s',
            update, context)

        # Check that authorised
        if not self.cmd_handler.authorise(update, context):
            return

        # Send a default message for unrecognized commands
        update.message.reply_text('I did not understand (Type /help)')
