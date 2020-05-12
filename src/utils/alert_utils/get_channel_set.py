import logging
from typing import Optional

from src.channels.channel import ChannelSet
from src.channels.console import ConsoleChannel
from src.channels.email import EmailChannel
from src.channels.log import LogChannel
from src.channels.mongo import MongoChannel
from src.channels.telegram import TelegramChannel
from src.channels.twilio import TwilioChannel
from src.store.mongo.mongo_api import MongoApi
from src.store.redis.redis_api import RedisApi
from src.utils.alert_utils.email_sending import EmailSender
from src.utils.alert_utils.telegram_bot_api import TelegramBotApi
from src.utils.alert_utils.twilio_api import TwilioApi
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf
from src.utils.logging import create_logger


def _get_log_channel(alerts_log_file: str, channel_name: str,
                     logger_general: logging.Logger,
                     internal_conf: InternalConfig = InternalConf) \
        -> LogChannel:
    # Logger initialisation
    logger_alerts = create_logger(alerts_log_file, 'alerts',
                                  internal_conf.logging_level)
    return LogChannel(channel_name, logger_general, logger_alerts)


def _get_console_channel(channel_name: str,
                         logger_general: logging.Logger) -> ConsoleChannel:
    return ConsoleChannel(channel_name, logger_general)


def _get_telegram_channel(channel_name: str, logger_general: logging.Logger,
                          redis: Optional[RedisApi],
                          backup_channels_for_telegram: ChannelSet,
                          user_conf: UserConfig = UserConf) -> TelegramChannel:
    telegram_bot = TelegramBotApi(user_conf.telegram_alerts_bot_token,
                                  user_conf.telegram_alerts_bot_chat_id)
    telegram_channel = TelegramChannel(
        channel_name, logger_general, redis,
        telegram_bot, backup_channels_for_telegram)
    return telegram_channel


def _get_email_channel(channel_name: str, logger_general: logging.Logger,
                       redis: Optional[RedisApi],
                       user_conf: UserConfig = UserConf) -> EmailChannel:
    email = EmailSender(user_conf.email_smtp, user_conf.email_from,
                        user_conf.email_user, user_conf.email_pass)
    email_channel = EmailChannel(channel_name, logger_general,
                                 redis, email, user_conf.email_to)
    return email_channel


def _get_twilio_channel(channel_name: str, logger_general: logging.Logger,
                        redis: Optional[RedisApi],
                        backup_channels_for_twilio: ChannelSet,
                        internal_conf: InternalConfig = InternalConf,
                        user_conf: UserConfig = UserConf) -> TwilioChannel:
    twilio = TwilioApi(user_conf.twilio_account_sid,
                       user_conf.twilio_auth_token)
    twilio_channel = TwilioChannel(channel_name, logger_general,
                                   redis, twilio,
                                   user_conf.twilio_phone_number,
                                   user_conf.twilio_dial_numbers,
                                   internal_conf.twiml,
                                   internal_conf.twiml_is_url,
                                   backup_channels_for_twilio)
    return twilio_channel


def _get_mongo_channel(channel_name: str, logger_general: logging.Logger,
                       redis: Optional[RedisApi], mongo: MongoApi,
                       backup_channels_for_mongo: ChannelSet) -> MongoChannel:
    collection_name = InternalConf.mongo_coll_alerts_prefix + \
                      UserConf.unique_alerter_identifier
    mongo_channel = MongoChannel(channel_name, logger_general, redis, mongo,
                                 collection_name, backup_channels_for_mongo)
    return mongo_channel


def get_full_channel_set(channel_name: str, logger_general: logging.Logger,
                         redis: Optional[RedisApi], alerts_log_file: str,
                         mongo: Optional[MongoApi],
                         internal_conf: InternalConfig = InternalConf,
                         user_conf: UserConfig = UserConf) -> ChannelSet:
    # Initialise list of channels with default channels
    channels = [
        _get_console_channel(channel_name, logger_general),
        _get_log_channel(alerts_log_file, channel_name, logger_general,
                         internal_conf)
    ]

    # Initialise backup channel sets with default channels
    backup_channels_for_telegram = ChannelSet(channels)
    backup_channels_for_twilio = ChannelSet(channels)
    backup_channels_for_mongo = ChannelSet(channels)

    # Add telegram alerts to channel set if they are enabled from config file
    if user_conf.telegram_alerts_enabled:
        telegram_channel = _get_telegram_channel(
            channel_name, logger_general, redis,
            backup_channels_for_telegram, user_conf)
        channels.append(telegram_channel)
    else:
        telegram_channel = None

    # Add email alerts to channel set if they are enabled from config file
    if user_conf.email_alerts_enabled:
        email_channel = _get_email_channel(channel_name, logger_general,
                                           redis, user_conf)
        channels.append(email_channel)
    else:
        email_channel = None

    # Add twilio alerts to channel set if they are enabled from config file
    if user_conf.twilio_alerts_enabled:
        twilio_channel = _get_twilio_channel(channel_name, logger_general,
                                             redis, backup_channels_for_twilio,
                                             internal_conf, user_conf)
        channels.append(twilio_channel)
    else:
        # noinspection PyUnusedLocal
        twilio_channel = None

    # Add mongo alerts to channel set if they are enabled from config file
    if user_conf.mongo_enabled:
        mongo_channel = _get_mongo_channel(channel_name, logger_general, redis,
                                           mongo, backup_channels_for_mongo)
        channels.append(mongo_channel)
    else:
        mongo_channel = None

    # Set up email channel as backup channel for telegram, twilio, mongo
    if email_channel is not None:
        backup_channels_for_telegram.add_channel(email_channel)
        backup_channels_for_twilio.add_channel(email_channel)
        backup_channels_for_mongo.add_channel(email_channel)

    # Set up telegram channel as backup channel for twilio, mongo
    if telegram_channel is not None:
        backup_channels_for_twilio.add_channel(telegram_channel)
        backup_channels_for_mongo.add_channel(telegram_channel)

    # Set up mongo channel as backup channel for telegram and twilio
    if mongo_channel is not None:
        backup_channels_for_telegram.add_channel(mongo_channel)
        backup_channels_for_twilio.add_channel(mongo_channel)

    return ChannelSet(channels)


def get_periodic_alive_reminder_channel_set(
        channel_name: str, logger_general: logging.Logger,
        redis: Optional[RedisApi], alerts_log_file: str,
        mongo: Optional[MongoApi],
        internal_conf: InternalConfig = InternalConf,
        user_conf: UserConfig = UserConf) -> ChannelSet:
    # Initialise list of channels with default channels
    channels = [
        _get_console_channel(channel_name, logger_general),
        _get_log_channel(alerts_log_file, channel_name, logger_general,
                         internal_conf)
    ]

    # Initialise backup channel sets with default channels
    backup_channels_for_telegram = ChannelSet(channels)
    backup_channels_for_mongo = ChannelSet(channels)

    # Add telegram alerts to channel set if they are enabled from config file
    if user_conf.telegram_alerts_enabled and \
            user_conf.par_telegram_enabled:
        telegram_channel = _get_telegram_channel(channel_name, logger_general,
                                                 redis,
                                                 backup_channels_for_telegram,
                                                 user_conf)
        channels.append(telegram_channel)
    else:
        telegram_channel = None

    # Add email alerts to channel set if they are enabled from config file
    if user_conf.email_alerts_enabled and \
            user_conf.par_email_enabled:
        email_channel = _get_email_channel(channel_name, logger_general,
                                           redis, user_conf)
        channels.append(email_channel)
    else:
        email_channel = None

    # Add mongo alerts to channel set if they are enabled from config file
    if user_conf.mongo_enabled:
        mongo_channel = _get_mongo_channel(channel_name, logger_general, redis,
                                           mongo, backup_channels_for_mongo)
        channels.append(mongo_channel)
    else:
        # noinspection PyUnusedLocal
        mongo_channel = None

    # Set up email channel as backup channel for telegram, mongo
    if email_channel is not None:
        backup_channels_for_telegram.add_channel(email_channel)
        backup_channels_for_mongo.add_channel(email_channel)

    # Set up telegram channel as backup channel for mongo
    if telegram_channel is not None:
        backup_channels_for_mongo.add_channel(telegram_channel)

    return ChannelSet(channels)
