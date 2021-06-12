import logging
import socket
import config
import json
import struct
import threading
import time
import os
from daemon import runner
from datetime import datetime

client_base = { "clients":
    [
        {
            "address": "192.168.0.1",
            "port": "2208",
            "nickname": "nikita",
            "online": True
         },
        {
            "address": "192.168.0.2",
            "port": "2208",
            "nickname": "pobeda",
            "online": False
        },
    ]
}


class App():   
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  os.path.join(os.getcwd(), 'multiproto.pid')
        self.pidfile_timeout = 5

    def run(self):
        while True:
            # logger.debug("Debug message")
            # logger.info("Info message")
            # logger.warn("Warning message")
            # logger.error("Error message")
            # logger.info(f'LOG: {datetime.now()}')
            self.multicast_handler()

    @staticmethod
    def tcp_handler(client_address):
        # TCP socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(client_address)

        # convert dict structure to bytes
        msg = json.dumps(client_base).encode('utf-8')

        try:
            sock.sendall(msg)
        finally:
            print('closing socket')
            sock.close()
        pass

    def multicast_handler(self):
        server_address = ('', config.MULTICAST_PORT)

        # UDP socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind to the server address
        sock.bind(server_address)

        # IP string to bytes conversion
        mcast_group = socket.inet_aton(config.MULTICAST_IP)
        # listen on all interfaces `socket.INADDR_ANY`
        mreq = struct.pack('4sL', mcast_group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Receive/respond loop
        while True:
            print('\nwaiting to receive message')
            logger.info(f'Listening for multicast messages')
            data, address = sock.recvfrom(1024)

            print('received %s bytes from %s' % (len(data), address))
            logger.info(f'Received multicast message from {address}')
            print(data)

            print('sending acknowledgement to', address)
            logger.info(f'Starting TCP session with {address}')
            # call TCP session
            thread = threading.Thread(target=self.tcp_handler, args=address)
            # run thread in the background as daemon
            thread.daemon = True
            thread.start()
            # sock.sendto(json.dumps(client_base).encode('utf-8'), address)


if __name__ == '__main__':
    app = App()
    logger = logging.getLogger("Multiprotocol Chat")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(os.path.join(os.getcwd(), "multiproto.log"))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()

