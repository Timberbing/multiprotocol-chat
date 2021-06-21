import socket
import sctp

sk = sctp.sctpsocket_tcp(socket.AF_INET)
sk.connect(("192.168.100.9", 36412))


print("Sending Message")

sk.sctp_send(msg='hello world')
sk.shutdown(0)


sk.close()
