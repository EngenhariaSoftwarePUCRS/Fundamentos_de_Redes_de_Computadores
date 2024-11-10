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
from print import *
from routing_table import RoutingTable


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.settimeout(1)

routing_table: RoutingTable

should_resend: bool = False


def main(server_ip: str = server_host_ip, neighbours_file: str = 'roteadores.txt'):
    server_socket.bind((server_ip, server_port))
    print_ready(f'The server is ready to receive at {server_ip}:{server_port}')
    get_neighbours(server_ip, neighbours_file)

    threading.Thread(target=user_input_thread, daemon=True).start()

    global should_resend
    counter = 0
    while True:
        if counter % 3 == 0:
            print_table(routing_table)

        if counter % 15 == 0 or should_resend:
            print_route_send("Sending routing table to neighbours")
            for neighbour in routing_table.get_neighbours():
                r_table = routing_table.serialize_routing_table_to_string()
                server_socket.sendto(r_table.encode(), (neighbour, server_port))
            should_resend = False
            continue

        if counter == 35:
            print_kill_neighbours('Checking which neighbours are still alive...')
            routing_table.remove_dead_neighbours()
            counter = 0
            continue

        try:
            print_waiting('Waiting for messages...')
            message, client = server_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
            message = message.decode()
            print_message_received(f'Received message: {message} from {client}')
            handle_message(message, client)
        except:
            # If no message is received, pass
            pass

        counter += 1
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
    routing_table.alive_neighbour(sender[0])

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
    global should_resend
    table_row = re.split(r'@', message)
    for row in table_row[1:]:
        ip, metric = row.split('-')
        # Check if I already know how to get to this IP
        route_to_ip = routing_table.get_route(ip)
        sender_ip = sender[0]
        if ip == routing_table.self_ip:
            pass
        elif not route_to_ip:
            metric = int(metric) + 1
            routing_table.register_route(ip, metric, sender_ip)
            should_resend = True
        else:
            old_metric = route_to_ip[1]
            new_metric = int(metric) + 1
            if new_metric < old_metric:
                # If I already know how to get to this IP, update the metric if it is lower
                routing_table.update_route(ip, new_metric, sender_ip)
                should_resend = True

    # Remove routes that are no longer received
    known_ips = routing_table.get_ips_from_routes()
    received_ips = routing_table.parse_string_to_routing_table(message)
    received_ips = routing_table.get_ips_from_routes(received_ips)
    received_ips.append(sender[0])
    routes_to_remove = set(known_ips) - set(received_ips)
    if routes_to_remove:
        for ip in routes_to_remove:
            routing_table.remove_route(ip)
        should_resend = True


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
