import socket
import struct
import config
import json
import threading
import random


def multicast_handler(client_port: int):
    # create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', client_port))
    # set a timeout so the socket does not block indefinitely when trying to receive data.
    sock.settimeout(0.2)

    # Set the time-to-live for messages to 1 so they do not go past the local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # send request to the multicast group
        print(f'CLIENT: Sending multicast message to {config.MULTICAST_IP}')

        message = 'SERVER DISCOVERY'
        multicast_group = (config.MULTICAST_IP, config.MULTICAST_PORT)
        sock.sendto(bytes(message, encoding='utf-8'), multicast_group)
    finally:
        sock.close()


def tcp_handler(port: int):
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.bind(('', port))
    sock_tcp.listen(5)

    # empty buffer
    buff = b''
    while True:
        print(f'CLIENT: Waiting for a TCP connection')
        connection, client_address = sock_tcp.accept()
        try:
            print(f'CLIENT: Connection from {client_address}')

            username = input('=== Provide Your Nickname === ')
            connection.sendall(bytes(username, encoding='utf8'))
            # receive the data in chunks and add to the buffer
            while True:
                print(f'CLIENT: Waiting for the server to send client base')
                data = connection.recv(512)
                buff += data
                if not data:
                    break
                break
        finally:
            print(f'CLIENT: Client base received')
            res_dict = json.loads(buff.decode('utf-8'))
            # print(res_dict)
            print(f'CLIENT: Closing TCP connection')
            # clean up the connection
            connection.close()
            break


if __name__ == '__main__':
    port = random.randint(50_000, 65_000)
    # pass selected port to the TCP thread, in order to listen on the same port
    # thread in the background as daemon
    th = threading.Thread(target=tcp_handler, args=(client_port,), daemon=True)
    th.start()
    multicast_handler(port)
    th.join()

