import socket
import sctp
import config
import json
import time

addr_server = ('127.0.0.1', 10000)
srv = sctp.sctpsocket_udp(socket.AF_INET)
tmp = sctp.event_subscribe(srv)
tmp.set_association(1)
tmp.set_data_io(1)
#srv.events = sctp.event_subscribe(srv)
srv.autoclose = 360
srv.bind(addr_server)
srv.listen(5)
 
while True:
    #srv_to_cli, _addr_client = srv.accept()
    try:
        fromaddr, flags, msgret, notif = srv.sctp_recv(2048)
        _ = "up" if notif.state==0 else "down"
        print(f"assoc: {notif.assoc_id} -> {_}")
        print('===============================================')
    except:
        pass

srv.close()

