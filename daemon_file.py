import logging
import socket
import config
import json
import sctp
import struct
import threading
import os
from daemon import runner


client_base = {"clients": [
    {
        "ip": "192.168.0.1",
        "port": 2250,
        "nickname": "pepka",
        "online": True
    }
]}


class App():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = os.path.join(os.getcwd(), 'multiproto.pid')
        self.pidfile_timeout = 5

    def run(self):
        while True:
            # main thread
            self.multicast_handler()

    @staticmethod
    def tcp_handler(address):
        logger.info(f'Starting TCP session with {address}')
        # TCP socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', config.TCP_PORT))
        sock.connect(address)

        # convert dict structure to bytes
        msg = json.dumps(client_base).encode('utf-8')

        try:

            while True:
                data = sock.recv(1024)
                if not data:
                    break
                # TODO: there might be additional authentication for the user
                _nickname = data.decode('utf8')
                logger.info(f'New user named: {_nickname}')

                # send client base before the update
                sock.sendall(msg)

                # update client base
                client_base['clients'].append(
                    {
                        "ip": address[0],
                        "port": address[1],
                        "nickname": _nickname,
                        "online": True
                    }
                )
                # TODO: update client base via SCTP

        finally:
            sock.close()

    @staticmethod
    def sctp_handler(address):
        logger.info(f'Starting STCP session for {address}')
        # SCTP socket creation
        sock = sctp.sctpsocket_udp(socket.AF_INET)
        # get notifications on assoc state
        tmp = sctp.event_subscribe(sock)
        tmp.set_association(1)
        tmp.set_data_io(1)
        sock.autoclose = 0
        sock.bind(('', config.SCTP_PORT))
        sock.sctp_send(msg=b'0', to=address)

        while True:
            try:
                fromaddr, flags, msgret, notif = sock.sctp_recv(2048)
                if notif.state == 3:
                    logger.info(f'Client {sock.getpaddr(notif.assoc_id)} is down.')
                elif notif.state == 0:
                    logger.info(f'Client {sock.getpaddr(notif.assoc_id)} is up.')
            except:
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
            logger.info(f'Listening for multicast messages')
            data, address = sock.recvfrom(1024)
            logger.info(f'Received multicast message from {address}')

            # call TCP session
            thread = threading.Thread(target=self.tcp_handler, args=(address,), daemon=True)
            # run thread in the background as daemon
            thread.start()
            # call SCTP session
            _thread = threading.Thread(target=self.sctp_handler, args=(address,), daemon=True)
            # run thread in the background as daemon
            _thread.start()


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

