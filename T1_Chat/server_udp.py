from socket import socket, AF_INET, SOCK_DGRAM

from config import (
    ACK_EMPTY, ACK_FILE, ACK_MSG, ACK_REG, ACK_UNREG,
    MESSAGE_MAX_SIZE_UDP,
    NACK_INVALID,
    PREFIX_FILE, PREFIX_MSG, PREFIX_QUIT, PREFIX_REG, PREFIX_WHOAMI,
    Address, server_udp, TableRow,
)


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(server_udp)

neighbours: list[str] = []
table: list[TableRow] = []


def main():
    print(f'The server is ready to receive at {server_udp}')
    get_neighbours()

    while True:
        message, client = server_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        message = message.decode()
        print(f'Received message: {message} from {client}')

        handle_message(message, client)


def get_neighbours(neighbours_file: str = 'roteadores.txt'):
    try:
        with open(neighbours_file, 'r') as file:
            for line in file:
                neighbours.append(line.strip())
    except FileNotFoundError:
        raise FileNotFoundError(f'File {neighbours_file} not found')
    except Exception as e:
        raise Exception(f'An error occurred while reading the {neighbours_file} file: {e}')


def handle_message(message: str, client: Address):
    if len(message) == 0:
        server_socket.sendto(ACK_EMPTY.encode(), client)
        return

    if not message.startswith('/'):
        server_socket.sendto(NACK_INVALID.encode(), client)
        return

    # Workaround to always split the message in two parts
    if ' ' not in message:
        message += ' '
    prefix, message = message.split(' ', 1)

    # If message starts with '/REG' add the client to the list of neighbours
    if prefix == PREFIX_REG:
        register(nickname=message, address=client)
        server_socket.sendto(ACK_REG.encode(), client)
    
    # If message starts with '/WHOAMI' return the client's nickname, host and port
    elif prefix == PREFIX_WHOAMI:
        for client_db in neighbours:
            _nickname, address = client_db
            if address == client:
                server_socket.sendto(str(client_db).encode(), client)
        return
    
    # If message starts with '/MSG' send a message to all neighbours
    elif prefix == PREFIX_MSG:
        send_message(message, sender=client)
        server_socket.sendto(ACK_MSG.encode(), client)
        return

    # If message starts with '/FILE' send a file to all neighbours
    elif prefix == PREFIX_FILE:
        send_file(message, sender=client)
        server_socket.sendto(ACK_FILE.encode(), client)

    # If message starts with '/QUIT' remove the client from the list of neighbours
    elif prefix == PREFIX_QUIT:
        unregister(address=client)
        server_socket.sendto(ACK_UNREG.encode(), client)

    else:
        print('Invalid message')
        server_socket.sendto(NACK_INVALID.encode(), client)


def register(nickname: str, address: Address):
    print(f'{nickname} connected')
    neighbours.append((nickname, address))


def unregister(address: Address):
    # Remove the client from the list of neighbours
    for (nickname, address_db) in neighbours:
        if address_db == address:
            print(f'{nickname} disconnected')
            neighbours.remove((nickname, address))
            break


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


def send_file(message: str, sender: Address):
    # Future bug: if the file name starts with '@', it will be treated as a nickname
    if message.startswith('@'):
        nickname = message.split(' ')[0]
        print(f'Sending file to {nickname}')
        for (nick, address) in neighbours:
            if f"@{nick}" == nickname:
                message = message.removeprefix(f'{nickname} ')
                server_socket.sendto(message.encode(), address)
                break
    else:
        for client in neighbours:
            if client == sender:
                continue
            print(f'Sending file to {client}')
            _nickname, address = client
            server_socket.sendto(message.encode(), address)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Server stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        server_socket.close()
        exit(0)
