import sys
import socket
import os
import json


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
        req = connection.recv(2**25)
        request = req.decode('utf-8')
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
        
        if request_list != ['']:
            if request_list[0].split(" ")[0] != 'GET':
                # print(1)
                # send a 405 response to the client
                response = "HTTP/1.0 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
                connection.sendall(bytes(response, encoding='utf-8'))
                connection.close()

            else:
                path = request_list[0].split(" ")[1]
                # print("------------------   PATH   ------------------")
                # print(path)
                while path.startswith("/"):
                    path = path[1:]
                # print("------------------   PATH   ------------------")
                # print(path)
                    
                if not path.startswith("product"):
                    print(2)
                    response = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                    connection.sendall(bytes(response, encoding='utf-8'))
                else:
                    if "?" not in path:
                        print(3)
                        response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                        connection.sendall(bytes(response, encoding='utf-8'))
                    else:
                        params = path.split("?")[1]
                        if params == "":
                            print(4)
                            response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                            connection.sendall(bytes(response, encoding='utf-8'))
                        else:
                            params = params.split("&")
                            operands_list = []
                            result = float(1)
                            bad_request = False
                            for param in params:
                                if "=" not in param:
                                    print(5)
                                    response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                                    connection.sendall(bytes(response, encoding='utf-8'))
                                    bad_request = True
                                    break
                                else:
                                    value = param.split("=")[1]
                                    print("------------------   VALUE   ------------------")
                                    print(value)
                                    try: 
                                        operands_list.append(float(value))
                                    except ValueError:
                                        print(6)
                                        response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                                        connection.sendall(bytes(response, encoding='utf-8'))
                                        bad_request = True
                                        break
                                                
                            if not bad_request:
                                print(7)
                                negs = 0
                                for operand in operands_list: 
                                    if float(operand) < 0:
                                        negs += 1
                                
                                for operand in operands_list:
                                    try:
                                        result *= float(operand)
                                    except OverflowError:
                                        if negs % 2 == 0:
                                            result = "inf"
                                        else:
                                            result = "-inf"
                                            #TODO: check why this breaks firefox, but sends the right value
                                
                                response = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n"
                                response_dict = {"operation": "product", "operands": operands_list, "result": result}
                                response += json.dumps(response_dict)
                                response += "\r\n"
                                connection.sendall(bytes(response, encoding='utf-8'))
                                print("------------------   RESPONSE   ------------------")
                                print(response)

    except UnicodeDecodeError:
        if req == b'\xff\xf4\xff\xfd\x06':
            print("telnet end of request")
        else:
            response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
            connection.send(bytes(response, encoding='utf-8'))
                            
    finally:
        print("closing connection")
        # Clean up the connection
        connection.close()

