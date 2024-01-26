import sys
import socket


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parse_url(url):
    if url.startswith("http://"):
        body = url.replace("http://", "")
        while body[-1] == "/":
            body = body[:-1]
        body = body.split(":")
        if (len(body) == 2):  # TODO: this is wrong, the port does not always go at the end, the path goes after

            # if second portion has /, take from 0 to that index
            # eg. http://moore.wot.eecs.northwestern.edu:10002/rfc2616.html
            # vs. http://portquiz.net:8080/ or http://portquiz.net:8080
            # http://moore.wot.eecs.northwestern.edu/rfc2616.html

            host = body[0]

            if "/" in body[1]:
                index_port_end = body[1].find("/")
                port = body[1][0 : index_port_end]
                if not port.isnumeric():
                    error_print("Invalid URL: ports must be integers")
                    sys.exit(1)
                path = body[1][index_port_end + 1:]

            else:
                port = body[1]
                path = ""

            return host, path, int(port)
            

        elif len(body) > 2:
            error_print("Invalid URL: must not have more than one port")
            sys.exit(2)

        else:
            if "/" in body[0]:
                inds = body[0].split("/")
                host = inds[0]
                inds.remove(host)
                path = "/".join(inds)
            else:
                host = body[0]
                path = ""
            return host, path, 80
    else:
        error_print("Invalid URL: all URLs must start with 'http://'")
        sys.exit(3)


def send_request(url):
    url_host, url_path, url_port = parse_url(url)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(url_host, url_port)
    sock.connect((url_host, url_port))

    req = "GET /{} HTTP/1.0\r\nHost:{}\r\nAccept: text/html\r\n\r\n".format(
        url_path, url_host
    )
    req = bytes(req, encoding="utf-8")
    sock.send(req)
    return sock.recv(2**25, socket.MSG_WAITALL).decode("utf-8")


def parse_response(response):
    if "Content-Type: text/html" in response:
        resp_list = response.split("\r\n\r\n")
        if len(resp_list) == 2:
            header = resp_list[0].split("\r\n")
            body = resp_list[1]
            code = int(header[0].split(" ")[1])
            header.remove(header[0])

            header_dict = {}
            for line in header:
                line = line.split(": ")
                if line[0] in header_dict:
                    header_dict[line[0].lower()].append(line[1])
                else:
                    header_dict[line[0].lower()] = [line[1]]
        else:
            error_print("Invalid response: must have exactly one blank line")
            sys.exit(4)

        if code >= 400:
            error_print("Invalid response: status code {}".format(code))
            print(body)
            sys.exit(5)

        elif code == 301 or code == 302:
            error_print("Redirected to {}".format(header_dict["location"][0]))
            return header_dict["location"][0]

        elif code == 200:
            print(body)
            sys.exit(0)
    else:
        error_print("Invalid response: must have Content-Type: text/html")
        sys.exit(6)


url = sys.argv[1]

for i in range(10):
    response = send_request(url)
    url = parse_response(response)

error_print("Too many redirects")
sys.exit(7)
