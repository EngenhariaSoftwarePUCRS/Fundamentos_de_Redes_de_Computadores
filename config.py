from typing import Tuple


router_port = 9000

default_neighbours_file = 'roteadores.txt'

MESSAGE_MAX_SIZE_UDP = 1024

REGEX_IPV4 = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
# @192.168.1.2-1@192.168.1.3-1 
# Ou seja, “@” indica uma tupla, IP de Destino e Métrica. A métrica é separada do IP por um “-” (hífen).
REGEX_TABLE_ANNOUNCEMENT = r'@' + REGEX_IPV4 + r'-\d+'
# *192.168.1.1 
# Ou seja, um * (asterisco) seguido do próprio endereço IP do roteador que entrou na rede. 
REGEX_ROUTER_ANNOUNCEMENT = r'\*' + REGEX_IPV4
# !192.168.1.2;192.168.1.1;Oi tudo bem? 
# Ou seja, “!” indica que uma mensagem de texto foi recebida. O primeiro endereço é o IP da origem, o segundo é o IP de destino e a seguir vem a mensagem de texto. Cada informação é separada um “;” (ponto e vírgula).
REGEX_MESSAGE = r'!' + REGEX_IPV4 + r';' + REGEX_IPV4 + r';.+' 

Address = Tuple[str, int]

# Tuple with the following format: (ip, metrica, saida)
TableRow = Tuple[str, int, str]
