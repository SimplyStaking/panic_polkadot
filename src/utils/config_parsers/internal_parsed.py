import os

from src.utils.config_parsers.internal import InternalConfig

INTERNAL_CONFIG_FILE_MAIN = 'config/internal_config_main.ini'
INTERNAL_CONFIG_FILE_ALERTS = 'config/internal_config_alerts.ini'

INTERNAL_CONFIG_FILES = [INTERNAL_CONFIG_FILE_MAIN,
                         INTERNAL_CONFIG_FILE_ALERTS]
MISSING_INTERNAL_CONFIG_FILES = [f for f in INTERNAL_CONFIG_FILES
                                 if not os.path.isfile(f)]

if len(MISSING_INTERNAL_CONFIG_FILES) == 0:
    InternalConf = InternalConfig(INTERNAL_CONFIG_FILE_MAIN,
                                  INTERNAL_CONFIG_FILE_ALERTS)
else:
    InternalConf = None
