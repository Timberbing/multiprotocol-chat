from os import wait
import socket
import sctp
import time


cli = sctp.sctpsocket_udp(socket.AF_INET)
tmp = sctp.event_subscribe(cli)
tmp.set_association(1)
tmp.set_data_io(1)

cli.autoclose = 0 # no automatic closing of the associacion

cli_ = sctp.sctpsocket_udp(socket.AF_INET)
tmp = sctp.event_subscribe(cli_)
tmp.set_association(1)
tmp.set_data_io(1)

cli.bind(("127.0.0.1", 10001))
cli_.bind(("127.0.0.1", 10002))
cli.sctp_send(msg=b'0', to=("127.0.0.1", 10000))
cli_.sctp_send(msg=b'0', to=("127.0.0.1", 10000))
time.sleep(10)

cli.close()
time.sleep(3)
cli_.close()
 