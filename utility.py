from typing import Any, Optional
import subprocess as sp


def safe_cast(obj: Any, T) -> Optional[int]:
    """
    :param T: the type to cast to
    :return: something converted to an integer if possible, None if impossible
    """
    try:
        return T(obj)
    except ValueError:
        return None


def int_input(msg='') -> int:
    """
    Like input, but guaranteed to return an int.
    If the user doesn't input an int, it repeats the prompt.
    """
    x = safe_cast(input(msg), int)
    if x is None:
        x = int_input(msg)
    return x


def float_input(msg='') -> float:
    """
    Like int_input, but for floating point values
    """
    x = safe_cast(input(msg), float)
    while x is None:
        x = safe_cast(input(msg), float)
    return x


def bool_input(msg='') -> bool:
    """
    Similar to input, but returns a bool.
    :return: True if the user inputs 'y' or 'Y', False otherwise.
    """
    x = input(f'{msg} (y/n) ')
    return x.lower() == 'y'


def run_cmd(cmd, *args, silent=False) -> str:
    """
    Runs a terminal command.
    :param cmd: the name of the command.
    :param args: the arguments to pass it (should be strings).
    :param silent: Whether or not to fail silently
    :return: The stdout and stderr output that the command generated if it ran successfully.
    Otherwise, it returns '' after printing an error message.
    """
    try:
        raw_output = sp.check_output([cmd] + list(args), stderr=sp.STDOUT)
        return raw_output.decode('utf-8')
    except sp.CalledProcessError as e:
        if not silent:
            print('\nCould not execute command\n')
            print(e)
        return ''
