import socket
import struct
import sys
import config
import json

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

server_address = ('', config.MULTICAST_PORT)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group on all interfaces.
mcast_group = socket.inet_aton(config.MULTICAST_IP)
mreq = struct.pack('4sL', mcast_group, socket.INADDR_ANY)  # listen on all interfaces `socket.INADDR_ANY`
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)

    print('received %s bytes from %s' % (len(data), address))
    print(data)

    print('sending acknowledgement to', address)
    sock.sendto(json.dumps(client_base).encode('utf-8'), address)
