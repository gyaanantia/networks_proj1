import sys
import socket
import os


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

server_address = ("", int(sys.argv[1]))
# error_print("starting up on {} port {}".format(server_address[0], server_address[1]))

server = socket.create_server(server_address, family=socket.AF_INET, backlog=100) # TODO figure out backlog
# print(server.getsockname())

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = server.accept()

    try:
        # print('connection from', client_address)
        
        request = connection.recv(2**25).decode('utf-8')
        # print("------------------   REQUEST   -----------------------")
        # print(request)
        # print("-------------------------------------------------------")
        # print("--------------------     REPR    ------------------------")
        # print(repr(request))
        # print("-------------------------------------------------------")
        request_list = request.split("\r\n")
        # print("------------------   REQUEST LIST   ------------------")
        # print(request_list)
        # print("-------------------------------------------------------")
        
        if request_list[0].split(" ")[0] != 'GET':
            # print(1)
            # send a 405 response to the client
            response = "HTTP/1.0 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
            connection.sendall(bytes(response, encoding='utf-8'))
            connection.close()

        if request_list != ['']:
            path = request_list[0].split(" ")[1]
            # print("------------------   PATH   ------------------")
            # print(path)
            while path.startswith("/"):
                path = path[1:]
            # print("------------------   PATH   ------------------")
            # print(path)
            if not os.path.exists(path):
                # print(2)
                if not (path.endswith(".html") or path.endswith(".htm")): # TODO: Are we supposed to fix it like this?
                    # print(2.5)
                    path += ".html"

                if not os.path.exists(path):
                    # print(3)
                    # send a 404 response to the client
                    response = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                    connection.sendall(bytes(response, encoding='utf-8'))
                else:
                    # print(4)
                    # send a 403 response to the client
                    response = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n\r\n"
                    connection.sendall(bytes(response, encoding='utf-8'))

            elif not (path.endswith(".html") or path.endswith(".htm")): 
                # print(5)
                # send a 403 response to the client
                response = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n\r\n"
                connection.sendall(bytes(response, encoding='utf-8'))
            else:
                # print(6)
                # send a 200 response to the client
                response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
                connection.send(bytes(response, encoding='utf-8'))
                with open(path, 'r') as f:
                    for line in f:
                        connection.send(bytes(line, encoding='utf-8'))
                f.close()
      
    finally:
        print("closing connection")
        # Clean up the connection
        connection.close()

