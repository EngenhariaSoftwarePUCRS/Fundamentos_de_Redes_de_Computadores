from socket import socket, AF_INET, SOCK_DGRAM

from config import server_host_ip, server_port


client_socket = socket(AF_INET, SOCK_DGRAM)


def main():
    address = ('localhost', 9001)
    client_socket.bind(address)

    while True:
        message = ""
        while message.strip() == "":
            message = input().lstrip()

        client_socket.sendto(message.encode(), (server_host_ip, server_port))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Client stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        client_socket.close()
