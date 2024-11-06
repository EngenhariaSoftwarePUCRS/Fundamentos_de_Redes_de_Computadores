import re
from socket import socket, AF_INET, SOCK_DGRAM

from config import (
    MESSAGE_MAX_SIZE_UDP,
    REGEX_TABLE_ANNOUNCEMENT, REGEX_ROUTER_ANNOUNCEMENT, REGEX_MESSAGE,
    Address,
    server_host_ip, server_port,
)
from routing_table import RoutingTable


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_host_ip, server_port))

routing_table: RoutingTable


def main(neighbours_file: str):
    print(f'The server is ready to receive at {server_host_ip}:{server_port}')
    get_neighbours(neighbours_file)

    while True:
        message, client = server_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        message = message.decode()
        print(f'Received message: {message} from {client}')

        handle_message(message, client)


def get_neighbours(neighbours_file: str):
    try:
        neighbour_ips = []
        with open(neighbours_file, 'r') as file:
            for line in file:
                neighbour_ips.append(line.strip())
        global routing_table
        routing_table = RoutingTable(server_host_ip, neighbour_ips)
    except FileNotFoundError:
        raise FileNotFoundError(f'File {neighbours_file} not found')
    except Exception as e:
        raise Exception(f'An error occurred while reading the {neighbours_file} file: {e}')


def handle_message(message: str, sender: Address):
    if len(message) == 0:
        return

    if re.match(REGEX_TABLE_ANNOUNCEMENT, message):
        register_route(message, sender)
    
    # elif re.match(REGEX_ROUTER_ANNOUNCEMENT, message):
    #     register_router(message)

    # elif re.match(REGEX_MESSAGE, message):
    #     send_message(message)

    else:
        print(f'Invalid message: {message}')


def register_route(message: str, sender: Address):
    table_row = re.split(r'@', message)
    for row in table_row[1:]:
        ip, metric = row.split('-')
        # Check if I already know how to get to this IP
        route_to_ip = routing_table.get_route(ip)
        sender_ip = sender[0]
        if not route_to_ip:
            routing_table.register_route(ip, int(metric), sender_ip)
        else:
            # If I already know how to get to this IP, update the metric if it is lower
            if int(metric) < route_to_ip[1]:
                routing_table.update_route(ip, int(metric), sender_ip)


def send_message(message: str, sender: Address):
    if message.startswith('@'):
        nickname, message = message.split(' ', 1)
        print(f'Sending private message to {nickname}')
        for (nick, address) in neighbours:
            if f"@{nick}" == nickname:
                server_socket.sendto(message.encode(), address)
                break
    else:
        for (nickname, address) in neighbours:
            if address == sender:
                continue
            print(f'Sending message to {nickname}')
            server_socket.sendto(message.encode(), address)


if __name__ == '__main__':
    try:
        from sys import argv
        neighbours_file: str = argv[1] if len(argv) > 1 else 'roteadores.txt'
        main(neighbours_file)
    except KeyboardInterrupt:
        print('Server stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        server_socket.close()
        exit(0)
