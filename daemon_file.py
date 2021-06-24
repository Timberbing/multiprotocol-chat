import logging
import socket
import config
import json
import sctp
import struct
import threading
import os
from daemon import runner


client_base = {"clients": []}

cli_assoc = dict()


class App():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = os.path.join(os.getcwd(), 'multiproto.pid')
        self.pidfile_timeout = 5

    def run(self):
        thread = threading.Thread(target=self.sctp_handler, args=(), daemon=True)
            # run thread in the background as daemon
        thread.start()  
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
    def update_client_base(socket):
        for client in client_base['clients']:
            if client['online'] == True:
                _ = (client['ip'], client['port'])
                logger.info(f'Sending client base update to...{_[0]}:{_[1]}')
                # do not send the client its own information
                _tmp = {"clients": 
                    [
                        x for x in client_base['clients'] if x['ip']!= client['ip'] or x['port']!= client['port']
                    ]
                } 
                if _tmp['clients']:
                    # convert dict structure to bytes
                    logger.info(_tmp)
                    msg = json.dumps(_tmp).encode('utf-8')
                    socket.sctp_send(msg, to=_)

    def sctp_handler(self):
        logger.info(f'Starting STCP session')
        # SCTP socket creation
        sock = sctp.sctpsocket_udp(socket.AF_INET)
        # get notifications on assoc state
        tmp = sctp.event_subscribe(sock)
        tmp.set_association(1)
        sock.bind(('', config.SCTP_PORT))
        sock.listen(5)

        while True:
            try:
                fromaddr, flags, msgret, notif = sock.sctp_recv(2048)
                if notif.state == 3:
                    _ = cli_assoc[notif.assoc_id]
                    del cli_assoc[notif.assoc_id]
                    logger.info(f'Client {_[0]}:{_[1]} is down.')

                    for client in client_base['clients']:
                        if client['ip'] == _[0] and client['port'] == _[1] and client['online']==True:
                            client['online'] = False

                    self.update_client_base(sock)
                    
                else:
                    _ = sock.getpaddrs(notif.assoc_id)[1]
                    logger.info(f'Client {_[0]}:{_[1]} is up.')
                    # assign association id to the client
                    cli_assoc[notif.assoc_id] = _

                    for client in client_base['clients']:
                        if client['ip'] == _[0] and client['port'] == _[1] and client['online']==False:
                            client['online'] = True

                    self.update_client_base(sock)

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

