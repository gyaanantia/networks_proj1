import sys
import socket


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

server_address = ("", int(sys.argv[1]))
# error_print("starting up on {} port {}".format(server_address[0], server_address[1]))

server = socket.create_server(server_address, family=socket.AF_INET, backlog=1) # TODO figure out backlog
print(server.getsockname())

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = server.accept()

    try:
        print('connection from', client_address)
        
        request = connection.recv(2**25).decode('utf-8')
        print(request)
            
    finally:
        # Clean up the connection
        connection.close()

    
# TODO: implement response codes: 200, 404, 500

