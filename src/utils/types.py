from typing import Union, Dict, List

NONE = -1
RedisType = Union[bytes, str, int, float]
PolkadotWrapperType = Union[Dict, Dict[str, Dict], List, str, int, bool]
TERA = 10 ** 12
PICO = 10 ** -12
