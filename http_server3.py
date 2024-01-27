import sys
import socket
import os
import json


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

server_address = ("", int(sys.argv[1]))

server = socket.create_server(server_address, family=socket.AF_INET, backlog=100)

while True:
    print('waiting for a connection')
    connection, client_address = server.accept()

    try:
        req = connection.recv(2**25)
        request = req.decode('utf-8')
        request_list = request.split("\r\n")
        
        if request_list != ['']:
            if request_list[0].split(" ")[0] != 'GET':
                response = "HTTP/1.0 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n"
                connection.sendall(bytes(response, encoding='utf-8'))
                connection.close()

            else:
                path = request_list[0].split(" ")[1]
                while path.startswith("/"):
                    path = path[1:]
                    
                if not path.startswith("product"):
                    response = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                    connection.sendall(bytes(response, encoding='utf-8'))
                else:
                    if "?" not in path:
                        response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                        connection.sendall(bytes(response, encoding='utf-8'))
                    else:
                        params = path.split("?")[1]
                        if params == "":
                            response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                            connection.sendall(bytes(response, encoding='utf-8'))
                        else:
                            params = params.split("&")
                            operands_list = []
                            result = float(1)
                            bad_request = False
                            for param in params:
                                if "=" not in param:
                                    response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                                    connection.sendall(bytes(response, encoding='utf-8'))
                                    bad_request = True
                                    break
                                else:
                                    value = param.split("=")[1]
                                    try: 
                                        operands_list.append(float(value))
                                    except ValueError:
                                        response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
                                        connection.sendall(bytes(response, encoding='utf-8'))
                                        bad_request = True
                                        break
                                                
                            if not bad_request:
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
                                
                                response = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n"
                                response_dict = {"operation": "product", "operands": operands_list, "result": result}
                                response += json.dumps(response_dict)
                                response += "\r\n"
                                connection.sendall(bytes(response, encoding='utf-8'))

    except UnicodeDecodeError:
        if req == b'\xff\xf4\xff\xfd\x06':
            print("telnet end of request")
        else:
            response = "HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n"
            connection.send(bytes(response, encoding='utf-8'))
                            
    finally:
        print("closing connection")
        connection.close()

