import base64
import logging
from binascii import Error as BinAsciiError
from typing import Optional, Union

logger = logging.getLogger(__name__)


def strtobool(value: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'value' is anything else.

    > note:: Copied from distutils.util.
    """
    value = value.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    if value in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value {value!r}")


def resolve_truthy_env_var_choice(env: str, choice: Optional[bool] = None) -> bool:
    """Pick explicit choice over truthy env value, if available, otherwise return truthy env value

    NOTE: Environment variable should be resolved by the caller.

    Parameters
    ----------
    env : str
        environment variable actual value
    choice : bool
        explicit choice

    Returns
    -------
    choice : str
        resolved choice as either bool or environment value
    """
    return choice if choice is not None else strtobool(env)


def resolve_env_var_choice(
    env: Optional[str] = None, choice: Optional[Union[str, float]] = None
) -> Optional[Union[str, float]]:
    """Pick explicit choice over env, if available, otherwise return env value received

    NOTE: Environment variable should be resolved by the caller.

    Parameters
    ----------
    env : str, Optional
        environment variable actual value
    choice : str|float, optional
        explicit choice

    Returns
    -------
    choice : str, Optional
        resolved choice as either bool or environment value
    """
    return choice if choice is not None else env


def base64_decode(value: str) -> bytes:
    try:
        logger.debug("Decoding base64 Kafka record item before parsing")
        return base64.b64decode(value)
    except (BinAsciiError, TypeError):
        raise ValueError("base64 decode failed")


def bytes_to_string(value: bytes) -> str:
    try:
        return value.decode("utf-8")
    except (BinAsciiError, TypeError):
        raise ValueError("base64 UTF-8 decode failed")
