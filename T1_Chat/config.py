from typing import Tuple


server_name = '127.0.0.1'
server_port_udp = 13000
server_udp = (server_name, server_port_udp)

ACK = 'ACK'
ACK_EMPTY = 'ACK (empty message)'
ACK_FILE = 'ACK (file sent)'
ACK_MSG = 'ACK (message sent)'
ACK_REFRESH = 'ACK (refreshed)'
ACK_REG = 'ACK (client registered)'
ACK_UNREG = 'ACK (client unregistered)'
NACK = 'NACK'
NACK_INVALID = 'NACK (invalid message)'
NACK_NOT_FOUND = 'NACK (client not found)'

MAX_SERVER_CONNECTIONS = 5

MESSAGE_MAX_SIZE_UDP = 1024

PREFIX_FILE = '/FILE'
PREFIX_MSG = '/MSG'
PREFIX_QUIT = '/QUIT'
PREFIX_REFRESH = '/REFRESH'
PREFIX_REG = '/REG'
PREFIX_WHOAMI = '/WHOAMI'

Address = Tuple[str, int]

# Tuple with the following format: (ip, metrica, saida)
TableRow = Tuple[str, int, str]
