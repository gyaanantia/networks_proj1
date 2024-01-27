import sys
import socket
import os
import select


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

server_address = ("", int(sys.argv[1]))

server = socket.create_server(server_address, family=socket.AF_INET, backlog=100)

server.setblocking(False)


read_list = [server]


while True:
    print("waiting for a connection")
    read_socket, _, _ = select.select(read_list, [], read_list)

    for r_socket in read_socket:
        if r_socket is server:
            connection, client_address = r_socket.accept()
            connection.setblocking(False)
            read_list.append(connection)
        else:
            try:
                req = r_socket.recv(2**25)
                request = req.decode('utf-8')

                request_list = request.split("\r\n")

                if request_list != ['']:
                    if request_list[0].split(" ")[0] != 'GET':
                        response = "HTTP/1.0 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
                        r_socket.send(bytes(response, encoding='utf-8')) 
                        read_list.remove(r_socket)
                        r_socket.close()
                    else:
                        path = request_list[0].split(" ")[1]
                        while path.startswith("/"):
                            path = path[1:]

                        if not os.path.exists(path):
                            if not (path.endswith(".html") or path.endswith(".htm")):
                                path += ".html"

                            if not os.path.exists(path):
                                response = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                                r_socket.send(bytes(response, encoding='utf-8'))
                            else:
                                response = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n\r\n"
                                r_socket.send(bytes(response, encoding='utf-8'))
                        elif not (path.endswith(".html") or path.endswith(".htm")): 
                            response = "HTTP/1.0 403 Forbidden\r\nContent-Type: text/html\r\n\r\n"
                            r_socket.send(bytes(response, encoding='utf-8'))
                        else:
                            response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
                            r_socket.send(bytes(response, encoding='utf-8'))
                            with open(path, 'r') as f:
                                for line in f:
                                    r_socket.send(bytes(line, encoding='utf-8'))
                            f.close()

                read_list.remove(r_socket)
            except UnicodeDecodeError:
                if req == b'\xff\xf4\xff\xfd\x06':
                    print("telnet end of request")
                else:
                    response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                    r_socket.send(bytes(response, encoding='utf-8'))
                read_list.remove(r_socket)
            finally:
                print("closing connection")
                r_socket.close()
    

