import sys
import socket


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parse_url(url):
    if url.startswith('http://'):
        body = url.replace('http://', '')
        while body[-1] == '/':
            body = body[:-1]
        body = body.split(":")
        if len(body) == 2:
            if body[1].isnumeric():
                if "/" in body[0]:
                    inds = body[0].split("/")
                    host = inds[0]
                    inds.remove(host)
                    path = "/".join(inds)
                else:
                    host = body[0]
                    path = ""
                return host, path, int(body[1])
            else:
                error_print("Invalid URL: ports must be integers")
                sys.exit(1)  # TODO: ask about different exit codes
        elif len(body) > 2:
            error_print("Invalid URL: must not have more than one port")
            sys.exit(1)
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
        sys.exit(1)


# TODO: ask about timeouts

url = sys.argv[1]
url_host, url_path, url_port = parse_url(url)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((url_host, url_port))

req = "GET /{} HTTP/1.0\r\nHost:{}\r\n\r\n".format(url_path, url_host)
req = bytes(req, encoding='utf-8')
sock.send(req)
response = sock.recv(2**25, socket.MSG_WAITALL).decode('utf-8')
print(response)
sock.close()
sys.exit(0)
# request = "GET ..... {} .......".format(sys.argv[1])
#
# request = bytes(string, encoding="utf-8")
