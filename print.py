from typing import Literal
import threading

from config import default_log_file


print_semaphore = threading.Semaphore(1)

log_file: str = default_log_file


color_mapper = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'concealed': '\033[8m'
}


def print_ready(*args, **kwargs):
    print_('green', *args, **kwargs)


def print_table(*args, **kwargs):
    print_('cyan', *args, **kwargs)


def print_waiting(*args, **kwargs):
    print_('yellow', '\t' * 12, *args, **kwargs)


def print_send_message(*args, **kwargs):
    print_('blue', '\t' * 8, *args, **kwargs)


def print_kill_acquantainces(*args, **kwargs):
    print_('red', '\t' * 8, *args, **kwargs)


def print_message_received(*args, **kwargs):
    print_('magenta', '\t' * 4, *args, **kwargs)


def print_(color: Literal['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset', 'bold', 'underline', 'blink', 'reverse', 'concealed'], *args, log: bool = True, **kwargs):
    with print_semaphore:
        print(color_mapper[color], end='')
        print(*args, **kwargs)
        print(color_mapper['reset'], end='')
        if not log:
            write_to_log_file(' '.join(args))


def set_log_file(file: str) -> None:
    global log_file
    log_file = file


def write_to_log_file(message: str) -> None:
    try:
        with open(log_file, 'a') as log:
            log.write(message + '\n')
    except Exception as e:
        print_('red', f'Error writing to log file: {e}')
