import socket
import sctp
import config
import json

client_base = { "clients":
    [
        {
            "address": "192.168.0.24",
            "port": "2006",
            "nickname": "bulasie",
            "online": True
         },
        {
            "address": "192.168.0.25",
            "port": "2106",
            "nickname": "bamboleo",
            "online": False
        },
    ]
}

sock = sctp.sctpsocket_tcp(socket.AF_INET)
sock.bind((host, config.MULTICAST_PORT))
sock.listen(1)

while True:  
    # wait for a connection
    print ('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        # show who connected to us
        print ('connection from', client_address)
        # print connection
        # receive the data in small chunks and print it
        while True:
            data, address = sock.recvfrom(999)
            if data:
                # output received data
                print ("Data: %s" % data)
                connection.sendall("We received " + str(len(data)) + " bytes from you")
		print ("sending acknowledgement to ", address)
		sock.sendto(json.dumps(client_base).encode('utf-8'), address)
	    else:
                # no more data -- quit the loop
                print ("no more data.")
                break
    finally:
        # Clean up the connection
        connection.close()   
