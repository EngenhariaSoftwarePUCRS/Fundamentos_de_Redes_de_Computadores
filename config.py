from typing import Tuple


router_port = 9000

default_neighbours_file = 'roteadores.txt'
default_log_file = 'log.txt'

MESSAGE_MAX_SIZE_UDP = 1024

INTERVAL_DISPLAY_TABLE = 5
INTERVAL_SEND_TABLE = 15
# This interval affects the Ctrl+C interruption
# If it is too low, the program may loose some messages along the way
# If it is too high, it will take longer to stop the program
INTERVAL_RESET_SOCKET = 1000
CHECK_ALIVE_THRESHOLD = 35
INTERVAL_STEP = 1

REGEX_IPV4 = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
# @192.168.1.2-1@192.168.1.3-1 
# Ou seja, “@” indica uma tupla, IP de Destino e Métrica. A métrica é separada do IP por um “-” (hífen).
REGEX_TABLE_SYMBOL = r'@'
REGEX_TABLE_SEPARATOR_SYMBOL = r'-'
REGEX_TABLE_ANNOUNCEMENT = REGEX_TABLE_SYMBOL + REGEX_IPV4 + REGEX_TABLE_SEPARATOR_SYMBOL + r'\d+'
# *192.168.1.1 
# Ou seja, um * (asterisco) seguido do próprio endereço IP do roteador que entrou na rede. 
REGEX_ROUTER_SYMBOL = r'\*'
REGEX_ROUTER_ANNOUNCEMENT = REGEX_ROUTER_SYMBOL + REGEX_IPV4
# !192.168.1.2;192.168.1.1;Oi tudo bem? 
# Ou seja, “!” indica que uma mensagem de texto foi recebida. O primeiro endereço é o IP da origem, o segundo é o IP de destino e a seguir vem a mensagem de texto. Cada informação é separada um “;” (ponto e vírgula).
REGEX_MESSAGE_SYMBOL = r'!'
REGEX_MESSAGE_SEPARATOR_SYMBOL = r';'
REGEX_MESSAGE = REGEX_MESSAGE_SYMBOL + REGEX_IPV4 + REGEX_MESSAGE_SEPARATOR_SYMBOL + REGEX_IPV4 + REGEX_MESSAGE_SEPARATOR_SYMBOL + r'.+' 

Address = Tuple[str, int]

# Tuple with the following format: (ip, metrica, saida)
TableRow = Tuple[str, int, str]
