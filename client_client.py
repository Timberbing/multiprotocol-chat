"""
Client - Client communication overview:
    - Server provides clients with an IP:port list (all available clients).
    - Each client starts a TCP listener that other clients may connect to (listener runs in a separate thread, though also outputs to console).
    - When a client wants to message another client, a TCP connection is opened, data is sent and the connection is closed. 
"""

import sys
from typing import Dict, List
import socket
import struct
import config
import json
import threading
import random


class Client():
    def __init__(self):
        self.client_list = dict()
        self.username = ''

    @staticmethod
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

    def tcp_handler(self, _port: int):
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind(('', _port))
        sock_tcp.listen(5)

        # empty buffer
        buff = b''
        while True:
            print(f'CLIENT: Waiting for a TCP connection')
            connection, client_address = sock_tcp.accept()
            try:
                print(f'CLIENT: Connection from {client_address}')

                self.username = input('=== Provide Your Nickname === ')

                connection.sendall(bytes(self.username, encoding='utf8'))
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
                client_list = json.loads(buff.decode('utf-8'))
                self.client_list = client_list
                print(f'CLIENT: Closing TCP connection')
                # clean up the connection
                connection.close()
                break

    @staticmethod
    def tcp_listener(_port: int):
        s = socket.socket()
        # host = socket.gethostname()
        host = '0.0.0.0'
        s.bind((host, _port))
        s.listen(5)
        print('TCP listener started on port', _port)

        while True:
            conn, address = s.accept()
            data = conn.recv(1024)
            if not data:
                break
            data = data.decode('utf8')
            try:
                data_split = data.split()
                name = data_split[0]
                message = " ".join(data_split[1:])
                print(f'{name} says: {message}')
            except IndexError:
                print(f'{address} sends an empty message.')
            conn.sendall(bytes('OK', encoding='utf8'))

    @staticmethod
    def do_list(clients: List):
        print("Available clients:")

        for client in clients:
            print(f'address: {client["ip"]}:{client["port"]}, nickname: {client["nickname"]}')

    @staticmethod
    def do_connect(address: Dict, _username: str) -> bool:
        """
        address = {
            'ip': "IPv4_ADDR"
            'port: 1234
        }
        """
        msg = input('Please provide your message: ')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address['ip'], address['port']))

            s.sendall(bytes(f'{_username} {msg}', encoding='utf8'))
            resp = s.recv(1024)

            s.close()
        except socket.error as e:
            print('[ERR]', e)
            return False

        if resp.decode('utf8') == 'OK':
            return True
        else:
            return False

    def handle_actions(self, clients: List, _username: str):
        actions = ['list', 'msg', 'exit']

        input_split = input().split()
        action = input_split[0]

        if action not in actions:
            print('[ERR] Incorrect command')
            return

        if action == 'list':
            self.do_list(clients)

        if action == 'msg':
            try:
                client_address = input_split[1]
                client = {}
                # check if client_address is an IP:port string or client name
                cli_filtered = list(filter(lambda c: c['nickname'] == client_address, clients))
                print(cli_filtered)
                if len(cli_filtered): # client name found -> assign client
                    client['ip'] = cli_filtered[0]['ip']
                    # TODO: change this +1
                    client['port'] = cli_filtered[0]['port']+1
                else:
                    # split input to separate IP / port
                    client['ip'] = client_address.split(':')[0]
                    # TODO: change this +1
                    client['port'] = int(client_address.split(':')[1])+1

                success = self.do_connect(client, _username)
                if success:
                    print(f'Message to {client_address} delievered.')
                else:
                    print(f'Error sending data to {client_address}')
            except (IndexError, ValueError):
                print('[ERR] incorrect address / name')
                return

        if action == 'exit':
            print('Exiting...')
            sys.exit(1)


if __name__ == '__main__':
    usage_str = """
    Commands:
        list - display available clients
        msg CLIENT_NAME/CLIENT_ADDRESS - connect to one of the clients specified in <list>
        exit - close chat client
    """

    s = Client()

    port = random.randint(50_000, 65_000)
    # pass selected port to the TCP thread, in order to listen on the same port
    # thread in the background as daemon
    th = threading.Thread(target=s.tcp_handler, args=(port,), daemon=True)
    th.start()
    s.multicast_handler(port)
    th.join()

    print(s.client_list)

    # TODO: smart port allocation
    threading.Thread(target=s.tcp_listener, args=(port+1,)).start()

    print(usage_str)

    while True:
        s.handle_actions(s.client_list['clients'], s.username)
