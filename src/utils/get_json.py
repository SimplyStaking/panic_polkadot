import json
import logging
from typing import Dict

import requests

from src.utils.exceptions import (ApiCallFailedException,
                                  UnexpectedApiCallErrorException,
                                  NodeWasNotConnectedToApiServerException,
                                  UnexpectedApiErrorWhenReadingDataException,
                                  ConnectionWithNodeApiLostException,
                                  InvalidStashAccountAddressException,
                                  NodeIsNotAnArchiveNodeException)


def get_json(endpoint: str, logger: logging.Logger, params=None):
    if params is None:
        params = {}
    # The timeout must be slightly greater than the API timeout so that errors
    # could be received from the API.
    get_ret = requests.get(url=endpoint, params=params, timeout=15)
    get_ret.close()
    logger.debug('get_json: get_ret: %s', get_ret)
    return json.loads(get_ret.content.decode('UTF-8'))


def get_polkadot_json(endpoint: str, params: Dict, logger: logging.Logger,
                      api_call: str = ''):
    data = get_json(endpoint, logger, params)
    if 'result' in data:
        return data['result']
    elif 'error' in data:
        if 'API call {} failed.'.format(api_call) in data['error']:
            raise ApiCallFailedException(data['error'])
        elif 'An API for ' + params['websocket'] + \
                ' needs to be setup before it can be queried' in data['error']:
            raise NodeWasNotConnectedToApiServerException(data['error'])
        elif 'Lost connection with node.' == data['error']:
            raise ConnectionWithNodeApiLostException(data['error'])
        elif 'Invalid decoded address' in data['error']:
            raise InvalidStashAccountAddressException(
                "Stash account address {} does not exist."
                "".format(params['account_address']))
        elif "getStorage(key: StorageKey, at?: BlockHash): StorageData:: " \
             "-32603: Unknown error occured: Client(UnknownBlock(" \
             "\"State alread" in data['error']:
            raise NodeIsNotAnArchiveNodeException(data['error'])
        else:
            raise UnexpectedApiCallErrorException(data['error'])
    else:
        raise UnexpectedApiErrorWhenReadingDataException(data)
