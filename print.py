from typing import Literal


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
    print_('yellow', *args, **kwargs)


def print_route_send(*args, **kwargs):
    print_('blue', *args, **kwargs)


def print_kill_neighbours(*args, **kwargs):
    print_('red', *args, **kwargs)


def print_message_received(*args, **kwargs):
    print_('magenta', *args, **kwargs)


def print_(color: Literal['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset', 'bold', 'underline', 'blink', 'reverse', 'concealed'], *args, **kwargs):
    print(color_mapper[color], end='')
    print(*args, **kwargs)
    print(color_mapper['reset'], end='')
