import re
import threading
import time
# For some unknown reason, the import of readline is necessary for the input to work as expected
import readline
from socket import gethostname, gethostbyname, socket, AF_INET, SOCK_DGRAM

from config import (
    MESSAGE_MAX_SIZE_UDP,
    INTERVAL_DISPLAY_TABLE, INTERVAL_SEND_TABLE, INTERVAL_RESET_SOCKET, INTERVAL_STEP, CHECK_ALIVE_THRESHOLD,
    REGEX_TABLE_SYMBOL, REGEX_TABLE_SEPARATOR_SYMBOL, REGEX_TABLE_ANNOUNCEMENT,
    REGEX_ROUTER_SYMBOL, REGEX_ROUTER_ANNOUNCEMENT,
    REGEX_MESSAGE_SEPARATOR_SYMBOL, REGEX_MESSAGE,
    Address, router_port, default_neighbours_file,
)
from print import *
from routing_table import RoutingTable


router_socket = socket(AF_INET, SOCK_DGRAM)
router_socket.settimeout(INTERVAL_RESET_SOCKET)

send_table_awake = threading.Event()
stop_threads = threading.Event()

router_ip: str
routing_table: RoutingTable

counter: int = 0


def main(neighbours_file: str):
    router_socket.bind((router_ip, router_port))

    print_header()

    get_neighbours(neighbours_file)

    enter_network()

    threads = [
        threading.Thread(target=print_table_thread, daemon=True),
        threading.Thread(target=send_table_thread, daemon=True),
        threading.Thread(target=receive_messages_thread, daemon=True),
        threading.Thread(target=user_input_thread, daemon=True),
        threading.Thread(target=remove_dead_acquantainces_thread, daemon=True),
    ]
    for thread in threads:
        thread.start()
        time.sleep(1 / len(threads))

    global counter
    try:
        while not stop_threads.is_set():
            counter += INTERVAL_STEP
            time.sleep(INTERVAL_STEP)
    except KeyboardInterrupt:
        stop_threads.set()
        print_('yellow', 'Stopping threads, please type "Enter" to stop input thread and wait a few seconds...')
    finally:
        for thread in threads:
            print_('yellow', f'Stopping thread {thread.name}...')
            thread.join()
        print_('green', f'{len(threads)} threads stopped successfully')
        router_socket.close()


def print_header():
    print_ready(f'The server is ready to receive at {router_ip}:{router_port}')
    print_('white')
    print_table("Table")
    print_message_received("Messages received")
    print_send_message("Messages sent")
    print_waiting("Waiting for messages")
    print_('white')


def get_neighbours(neighbours_file: str):
    try:
        neighbour_ips = []
        with open(neighbours_file, 'r') as file:
            for line in file:
                neighbour_ips.append(line.strip())
        global routing_table
        routing_table = RoutingTable(router_ip, neighbour_ips)
    except FileNotFoundError:
        raise FileNotFoundError(f'File {neighbours_file} not found')
    except Exception as e:
        raise Exception(f'An error occurred while reading the {neighbours_file} file: {e}')


def enter_network():
    routing_table.broadcast_message_neighbours(f'{REGEX_ROUTER_SYMBOL}{router_ip}', router_socket)


def print_table_thread():
    while not stop_threads.is_set():
        print_('white')
        print_table("=" * 10 + " ROUTING TABLE " + "=" * 10)
        print_table(routing_table.__str__())
        time.sleep(INTERVAL_DISPLAY_TABLE)


def send_table_thread():
    while not stop_threads.is_set():
        print_send_message('Sending routing table to neighbours')
        r_table = routing_table.serialize_routing_table_to_string()
        routing_table.broadcast_message_neighbours(r_table, router_socket)
        send_table_awake.wait(INTERVAL_SEND_TABLE)
        send_table_awake.clear()


def send_table_immediately():
    send_table_awake.set()
    

def receive_messages_thread():
    while not stop_threads.is_set():
        try:
            print_waiting('Waiting for messages...')
            message, client = router_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
            message = message.decode()
            routing_table.alive_acquantaince(client[0], counter)
            print_message_received(f'Received message: {message} from {client}')
            handle_message(message, client)
        except ConnectionResetError:
            pass
        except TimeoutError:
            pass
        except KeyboardInterrupt:
            break
        except OSError as e:
            if e.errno == 10038:
                break
            raise e
        except Exception as e:
            print_('red', f'An error occurred while receiving messages: {e}')
        time.sleep(INTERVAL_STEP)


def user_input_thread():
    while not stop_threads.is_set():
        # ![YOUR_IP];[TARGET_IP];[MESSAGE]
        message = input()

        try:
            print_send_message(f'Sending message "{message}" to the network')
            self_ip = re.split(REGEX_MESSAGE_SEPARATOR_SYMBOL, message[1:])[0]
            if self_ip != router_ip:
                print_('red', f'{self_ip} is not the same as {router_ip}. Please use {router_ip} as the sender IP')
                continue

            handle_text_message(message)
        except ValueError:
            print_('red', 'Invalid input. The correct format is ![YOUR_IP];[TARGET_IP];[MESSAGE]')


def remove_dead_acquantainces_thread():
    global counter
    while not stop_threads.is_set():
        removed_acquantainces = routing_table.remove_dead_acquantainces(counter, CHECK_ALIVE_THRESHOLD)
        if removed_acquantainces:
            print_kill_acquantainces(f'Removed dead acquantainces {removed_acquantainces}...')
            send_table_immediately()
        time.sleep(INTERVAL_STEP)


def handle_message(message: str, sender: Address):
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
    global counter

    message += f"{REGEX_TABLE_SYMBOL}{sender[0]}{REGEX_TABLE_SEPARATOR_SYMBOL}{1}"

    sender_ip = sender[0]
    routing_table.alive_acquantaince(sender_ip, counter)

    must_resend_table: bool = False

    table_row = re.split(REGEX_TABLE_SYMBOL, message)
    for row in table_row[1:]:
        ip, metric = row.split(REGEX_TABLE_SEPARATOR_SYMBOL)
        # Check if I already know how to get to this IP
        route_to_ip = routing_table.get_route(ip)
        routing_table.alive_acquantaince(ip, counter)
        if ip == routing_table.self_ip:
            pass
        elif not route_to_ip:
            metric = int(metric)
            if ip != sender_ip:
                metric += 1
            routing_table.register_route(ip, metric, sender_ip)
            must_resend_table = True
        else:
            old_metric = route_to_ip[1]
            new_metric = int(metric) + 1
            if new_metric < old_metric:
                # If I already know how to get to this IP, update the metric if it is lower
                routing_table.update_route(ip, new_metric, sender_ip)
                must_resend_table = True

    # Remove routes that are no longer received
    known_acquantaince_ips = routing_table.get_acquantainces()
    known_neighbour_ips = routing_table.get_neighbours()
    received_ips = routing_table.parse_string_to_routing_table(message)
    received_ips = routing_table.get_acquantainces(received_ips)
    indirect_neighbours = set(known_acquantaince_ips) - set(known_neighbour_ips)
    routes_to_remove = indirect_neighbours - set(received_ips)
    if routes_to_remove:
        for ip in routes_to_remove:
            routing_table.remove_route(ip)
        must_resend_table = True
    
    if must_resend_table:
        send_table_immediately()


def handle_new_router(message: str):
    global router_ip
    new_router_ip = message[1:]
    if new_router_ip == router_ip:
        print_('red', f"{new_router_ip} is already taken! (By me)")
        return

    route_to_new_ip = routing_table.get_route(new_router_ip)
    if not route_to_new_ip:
        routing_table.register_route(new_router_ip, 1, new_router_ip)
    else:
        routing_table.update_route(new_router_ip, 1, new_router_ip)

    routing_table.alive_acquantaince(new_router_ip, counter)
    send_table_immediately()


def handle_text_message(message: str):
    sender_ip, target_ip, *content = re.split(REGEX_MESSAGE_SEPARATOR_SYMBOL, message[1:])
    content = REGEX_MESSAGE_SEPARATOR_SYMBOL.join(content)

    if target_ip == router_ip:
        print_message_received(f'Message received from {sender_ip}: {content}')
        return
    
    next_hop, hop_count = routing_table.get_route(target_ip)
    if not next_hop:
        print_('red', f'No route found to {target_ip}')
        return

    metric = hop_count
    while metric != 1:
        next_hop, metric = routing_table.get_route(next_hop)

    print_send_message(f'Forwarding message to {target_ip} through {next_hop}, est. hop count: {hop_count}')
    router_socket.sendto(message.encode(), (next_hop, router_port))


if __name__ == '__main__':
    try:
        from sys import argv
        if len(argv) < 4:
            print_('yellow', 'usage: python router.py [<neighbours_file>] [<router_ip>] [<log_file>]', log=False)
        neighbours_file = argv[1] if len(argv) > 1 else default_neighbours_file
        router_ip = argv[2] if len(argv) > 2 else gethostbyname(gethostname())
        if len(argv) > 3:
            set_log_file(argv[3])
        clear_log_file()
        main(neighbours_file)
    except KeyboardInterrupt:
        print_('green', 'Server stopping...')
    except Exception as e:
        print_('red', f'An error occurred: {e}')
    finally:
        router_socket.close()
        exit(0)
