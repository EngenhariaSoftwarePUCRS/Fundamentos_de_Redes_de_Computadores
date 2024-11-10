import re
import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM

from config import (
    MESSAGE_MAX_SIZE_UDP,
    REGEX_TABLE_ANNOUNCEMENT, REGEX_ROUTER_ANNOUNCEMENT, REGEX_MESSAGE,
    Address,
    server_host_ip, server_port,
)
from routing_table import RoutingTable


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.settimeout(1)

routing_table: RoutingTable


def main(server_ip: str = server_host_ip, neighbours_file: str = 'roteadores.txt'):
    server_socket.bind((server_ip, server_port))
    print(f'The server is ready to receive at {server_ip}:{server_port}')
    get_neighbours(server_ip, neighbours_file)

    threading.Thread(target=user_input_thread, daemon=True).start()

    counter = 0
    while True:
        counter += 1

        if counter % 5 == 0:
            routing_table.print_routing_table()

        if counter == 15:
            print("Sending routing table to neighbours")
            for neighbour in routing_table.get_neighbours():
                r_table = routing_table.serialize_routing_table_to_string()
                server_socket.sendto(r_table.encode(), (neighbour, server_port))
            continue

        if counter == 35:
            print("35")
            counter = 0
            continue

        try:
            print('Waiting for messages...')
            message, client = server_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
            message = message.decode()
            print(f'Received message: {message} from {client}')
            handle_message(message, client)
        except:
            # If no message is received, pass
            pass

        time.sleep(1)


def user_input_thread():
    while True:
        # ![YOUR_IP];[TARGET_IP];[MESSAGE]:
        user_input = input()
        try:
            _ip, target_ip, message = user_input.split(';')
            server_socket.sendto(message.encode(), (target_ip, server_port))
            print(f'Message sent to {target_ip}')
        except ValueError:
            print('Invalid input. The correct format is ![YOUR_IP];[TARGET_IP];[MESSAGE]')


def get_neighbours(self_ip: str, neighbours_file: str):
    try:
        neighbour_ips = []
        with open(neighbours_file, 'r') as file:
            for line in file:
                neighbour_ips.append(line.strip())
        global routing_table
        routing_table = RoutingTable(self_ip, neighbour_ips)
    except FileNotFoundError:
        raise FileNotFoundError(f'File {neighbours_file} not found')
    except Exception as e:
        raise Exception(f'An error occurred while reading the {neighbours_file} file: {e}')


def handle_message(message: str, sender: Address):
    if len(message) == 0:
        return

    if re.match(REGEX_TABLE_ANNOUNCEMENT, message):
        handle_route(message, sender)
    
    # elif re.match(REGEX_ROUTER_ANNOUNCEMENT, message):
    #     register_router(message)

    # elif re.match(REGEX_MESSAGE, message):
    #     send_message(message)

    else:
        print(f'Invalid message: {message}')


def handle_route(message: str, sender: Address):
    table_row = re.split(r'@', message)
    for row in table_row[1:]:
        ip, metric = row.split('-')
        # Check if I already know how to get to this IP
        route_to_ip = routing_table.get_route(ip)
        sender_ip = sender[0]
        if not route_to_ip and ip != routing_table.self_ip:
            metric = int(metric) + 1
            routing_table.register_route(ip, metric, sender_ip)
        else:
            # If I already know how to get to this IP, update the metric if it is lower
            if int(metric) < route_to_ip[1]:
                routing_table.update_route(ip, int(metric), sender_ip)

    # Remove routes that are no longer received
    known_ips = routing_table.get_ips_from_routes()
    received_ips = routing_table.parse_string_to_routing_table(message)
    received_ips = routing_table.get_ips_from_routes(received_ips)
    received_ips.append(sender[0])
    routes_to_remove = set(known_ips) - set(received_ips)
    for ip in routes_to_remove:
        routing_table.remove_route(ip)


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
        self_ip = argv[1] if len(argv) > 1 else server_host_ip
        neighbours_file: str = argv[2] if len(argv) > 2 else 'roteadores.txt'
        main(self_ip, neighbours_file)
    except KeyboardInterrupt:
        print('Server stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        server_socket.close()
        exit(0)
