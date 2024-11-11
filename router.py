import re
import threading
import time
import readline
from socket import socket, AF_INET, SOCK_DGRAM

from config import (
    MESSAGE_MAX_SIZE_UDP,
    REGEX_TABLE_ANNOUNCEMENT, REGEX_ROUTER_ANNOUNCEMENT, REGEX_MESSAGE,
    Address,
    default_router_ip, router_port, default_neighbours_file,
)
from print import *
from routing_table import RoutingTable


router_socket = socket(AF_INET, SOCK_DGRAM)
router_socket.settimeout(1)

router_ip: str = default_router_ip
routing_table: RoutingTable

should_resend: bool = True


def main(self_ip: str, neighbours_file: str):
    global router_ip, should_resend
    router_ip = self_ip
    router_socket.bind((router_ip, router_port))
    print_ready(f'The server is ready to receive at {router_ip}:{router_port}')

    get_neighbours(router_ip, neighbours_file)

    enter_network(router_ip)

    threading.Thread(target=user_input_thread, daemon=True).start()

    counter = 0
    while True:
        counter += 1

        if counter % 3 == 0:
            print_table(routing_table)

        if counter % 15 == 0 or should_resend:
            print_send_message('Sending routing table to neighbours')
            r_table = routing_table.serialize_routing_table_to_string()
            routing_table.broadcast_message(r_table, router_socket)
            should_resend = False
            continue
        
        if counter == 35:
            print_kill_neighbours('Checking which neighbours are still alive...')
            routing_table.remove_dead_neighbours()
            counter = 0
            continue
        
        try:
            print_waiting('Waiting for messages...')
            message, client = router_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
            message = message.decode()
            print_message_received(f'Received message: {message} from {client}')
            handle_message(message, client)
        except:
            # If no message is received, pass
            pass
        
        time.sleep(1)


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


def enter_network(self_ip: str):
    routing_table.broadcast_message(f'*{self_ip}', router_socket)


def user_input_thread():
    def set_input_buffer(text):
        readline.set_pre_input_hook(lambda: readline.insert_text(text))
        readline.redisplay()

    while True:
        # ![YOUR_IP];[TARGET_IP];[MESSAGE]
        message = input()

        try:
            print_send_message('Sending message to the network')
            routing_table.broadcast_message(message, router_socket)
        except ValueError:
            print_('red', 'Invalid input. The correct format is ![YOUR_IP];[TARGET_IP];[MESSAGE]')


def handle_message(message: str, sender: Address):
    routing_table.alive_neighbour(sender[0])

    if len(message) == 0:
        return

    if re.match(REGEX_TABLE_ANNOUNCEMENT, message):
        handle_table(message, sender)
    
    elif re.match(REGEX_ROUTER_ANNOUNCEMENT, message):
        handle_new_router(message)

    elif re.match(REGEX_MESSAGE, message):
        handle_text_message(message)

    else:
        print_('red', f'Invalid message: {message}')


def handle_table(message: str, sender: Address):
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


def handle_new_router(message: str):
    global router_ip
    new_router_ip = message[1:]
    known_ips = routing_table.get_ips_from_routes()
    if new_router_ip not in known_ips:
        routing_table.register_route(new_router_ip, 1, router_ip)


def handle_text_message(message: str):
    sender_ip, target_ip, content = re.split(r';', message[1:])

    if target_ip == router_ip:
        print_message_received(f'Message received from {sender_ip}: {content}')
        return
    
    route_to_ip = routing_table.get_route(target_ip)
    if not route_to_ip:
        print_('red', f'No route found to {target_ip}')
        return

    next_hop, metric = route_to_ip
    print_send_message(f'Forwarding message to {target_ip} through {next_hop}, est. hop count: {metric}')
    if next_hop == router_ip:
        router_socket.sendto(message.encode(), (target_ip, router_port))
    else:
        router_socket.sendto(message.encode(), (next_hop, router_port))


if __name__ == '__main__':
    try:
        from sys import argv
        self_ip = argv[1] if len(argv) > 1 else default_router_ip
        neighbours_file: str = argv[2] if len(argv) > 2 else default_neighbours_file
        main(self_ip, neighbours_file)
    except KeyboardInterrupt:
        print_('green', 'Server stopped')
    except Exception as e:
        print_('red', f'An error occurred: {e}')
    finally:
        router_socket.close()
        exit(0)
