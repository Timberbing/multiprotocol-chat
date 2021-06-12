import socket
import struct
import sys
import config
import json
import threading

message = 'SERVER DISCOVERY'
multicast_group = (config.MULTICAST_IP, config.MULTICAST_PORT)


def tcp_handler():
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (config.SERVER_IP, config.TCP_PORT)
    sock_tcp.bind(server_address)

    sock_tcp.listen(1)

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print(sys.stderr, 'connection from', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print('received "%s"' % data)
                if data:
                    print('sending data back to the client')
                    connection.sendall(data)
                else:
                    print('no more data from', client_address)
                    break
        finally:
            # Clean up the connection
            connection.close()


thread = threading.Thread(target=tcp_handler, args=())
# run thread in the background as daemon
# thread.daemon = True
thread.start()

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(0.2)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:

    # Send data to the multicast group
    print('sending "%s"' % message)
    sent = sock.sendto(bytes(message, encoding='utf-8'), multicast_group)

    # Look for responses from all recipients
    while True:
        print('waiting to receive')
        try:
            data, server = sock.recvfrom(1024)
        except socket.timeout:
            print('timed out, no more responses')
            break
        else:
            res_dict = json.loads(data.decode('utf-8'))
            print(res_dict)

finally:
    print('closing socket')
    sock.close()
    # sock_tcp.close()
