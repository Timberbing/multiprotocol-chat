"""
Client - Client communication overview:
    - Server provides clients with an IP:port list (all available clients).
    - Each client starts a TCP listener that other clients may connect to (listener runs in a separate thread, though also outputs to console).
    - When a client wants to message another client, a TCP connection is opened, data is sent and the connection is closed. 
"""

import socket
import threading
import sys
from typing import Dict, List


def tcp_listener(port: int):
    s = socket.socket()
    # host = socket.gethostname()
    host = '0.0.0.0'
    s.bind((host, port))
    s.listen(5)
    print('TCP listener started on port', port)

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


def do_list(clients: List):
    print("Available clients:")
    
    for client in clients:
        print(f'address: {client["ip"]}:{client["port"]}, nickname: {client["name"]}')


def do_connect(address: Dict, username: str) -> bool:
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
        
        s.sendall(bytes(f'{username} {msg}', encoding='utf8'))
        resp = s.recv(1024)
        
        s.close()
    except socket.error as e:
        print('[ERR]', e)
        return False

    if resp.decode('utf8') == 'OK':
        return True
    else:
        return False


def handle_actions(clients: List, username: str):
    actions = ['list', 'msg', 'exit',]

    input_split = input().split()
    action = input_split[0]

    if action not in actions:
        print('[ERR] Incorrect command')
        return

    if action == 'list':
        do_list(clients)

    if action == 'msg':
        try:
            client_address = input_split[1]
            client = {}
            # check if client_address is an IP:port string or client name
            cli_filtered = list(filter(lambda c: c['name'] == client_address, clients))
            
            if len(cli_filtered): # client name found -> assign client
                client = cli_filtered[0]
            else:
                # split input to separate IP / port
                client['ip'] = client_address.split(':')[0]
                client['port'] = int(client_address.split(':')[1])
            
            success = do_connect(client, username)
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


# this should be replaced with a dynamic list provided by the server
client_list = [
    {
        'ip': '127.0.0.1',
        'port': 1234,
        'name': 'client1',
    },
    {
        'ip': '127.0.0.1',
        'port': 6969,
        'name': 'client2',
    },
    {
        'ip': '127.0.0.1',
        'port': 8888,
        'name': 'client3',
    },
]

usage_str = """
Commands:
    list - display available clients
    msg CLIENT_NAME/CLIENT_ADDRESS - connect to one of the clients specified in <list>
    wait - allow other clients to connect to you 
    exit - close chat client
"""

if __name__ == '__main__':
    listener_port = 5000
    
    while True:
        try:
            listener_port = int(input('TCP Listener port number (must be an integer): '))
            break
        except ValueError:
            print('[ERR] Incorrect port number.')
    
    username = input('Your Username: ')

    threading.Thread(target=tcp_listener, args=(listener_port,)).start()


    print(usage_str)

    while True:
        handle_actions(client_list, username)
