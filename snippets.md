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
NC = '\033[0m'

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

    def dbg(text):
        if args.debug:
            print(f"[{log._ts()}] [{GREY}DEBUG{NC}] {GREY}{text}{NC}")
# ...
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debugging output')
```

## Proxy
```python
# ...
if args.proxy:
    proxies = {
        'http':'http://127.0.0.1:8080',
        'https':'http://127.0.0.1:8080'
    }
# ...
parser.add_argument("--proxy", help='proxy everything through burp', action='store_true', default=False)
```