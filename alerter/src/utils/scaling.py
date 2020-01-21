from typing import Union

from alerter.src.utils.types import TERA, PICO


def scale_to_tera(num: float) -> Union[float, int]:
    return num * TERA


def scale_to_pico(num: float) -> float:
    return num * PICO
