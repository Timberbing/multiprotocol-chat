import _sctp
import sctp
from sctp import *
import time
import config

client = "127.0.0.1"
server = "SERVER_IP"
sport = 2904
cport = 2905

if _sctp.getconstant("IPPROTO_SCTP") != 132:
    raise (Exception("getconstant failed"))
csocket = sctpsocket(socket.AF_INET, socket.SOCK_STREAM, None)

saddr = (server, sport)

print("TCP %r ----------------------------------------------" % (saddr,))

csocket.initparams.max_instreams = 3
csocket.initparams.num_ostreams = 3
caddr = (client, cport)

csocket.bindx([caddr])
csocket.events.clear()
csocket.events.data_io = 1

csocket.connect(saddr)

while 1:
    while True:
        data = input('input:')
        if not data:
            break
        csocket.sctp_send(data)
        fromaddr, flags, msgret, notif = csocket.sctp_recv(1024)
        print(" Msg arrived, msg:", msgret)

        if flags & FLAG_NOTIFICATION:
            raise (Exception("We did not subscribe to receive notifications!"))
            # else:
            print("%s" % msgret)
    break

csocket.close()

