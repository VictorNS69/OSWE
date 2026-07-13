# VSCode Debugging Cheatsheet — OSWE Languages
Other links:
- <https://bernas.gitbook.io/oswe-everything/debbuging/debbuging-new>
- <https://notes.awfulsecurity.org/oswe/oswe-code-review-cheat-sheet/debugging>
## General VSCode Debug Config Location
All configs live in `.vscode/launch.json` inside the project root.

Command palette: `Debug: Open launch.json` or click the gear in the Run/Debug panel.


## PHP (Xdebug)
- <https://marketplace.visualstudio.com/items?itemName=xdebug.php-debug>
### Install
```bash
# Debian/Kali target
sudo apt install php-xdebug
# or via pecl
pecl install xdebug
```

### php.ini config (target/attacker box running the app)
```ini
xdebug.mode=debug
xdebug.start_with_request=yes
xdebug.client_host=127.0.0.1   ; or attacker IP for remote
xdebug.client_port=9003
```

### VSCode extension
`PHP Debug` (Xdebug) by Xdebug.

### launch.json — Local attach
```json
{
  "name": "Listen for Xdebug",
  "type": "php",
  "request": "launch",
  "port": 9003
}
```

### launch.json — Remote attach
```json
{
  "name": "Listen for Xdebug (remote)",
  "type": "php",
  "request": "launch",
  "port": 9003,
  "pathMappings": {
    "/var/www/html": "${workspaceFolder}"
  },
  "hostname": "0.0.0.0"
}
```
- SSH tunnel: `ssh -R 9003:127.0.0.1:9003 user@target` (target pushes debug traffic back through the tunnel to your VSCode instance).
- Trigger via query string if `start_with_request=trigger`: `?XDEBUG_SESSION_START=1`.

## Java (JDWP)
- <https://code.visualstudio.com/docs/java/java-debugging>
### Enable debug agent on target JVM
```bash
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 -jar app.jar
```
- `suspend=y` if you need it to halt at startup (useful for catching early init bugs/exploits).
- `address=*:5005` binds all interfaces — for remote testing, bind to `127.0.0.1:5005` and tunnel instead.

### VSCode extension
`Debugger for Java` (Microsoft), part of Java Extension Pack.

### launch.json — local or remote attach
```json
{
  "type": "java",
  "name": "Attach to JDWP",
  "request": "attach",
  "hostName": "127.0.0.1",
  "port": 5005,
  "projectName": "app"
}
```
- Remote: `ssh -L 5005:127.0.0.1:5005 user@target`, then `hostName: 127.0.0.1` locally.
- Source mapping: ensure decompiled/source jar matches target bytecode, or set breakpoints won't bind.

## Python (debugpy)
- <https://code.visualstudio.com/docs/python/debugging>
### Install
```bash
pip install debugpy
```

### Attach mode
Inject into running script
```bash
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client app.py
```
Or inject into code directly (useful for exploit scripts you're actively debugging):
```python
import debugpy
print('[*] starting debug server on 0.0.0.0:5678')
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

### VSCode extension
`Python` (Microsoft) — debugpy is bundled.

### launch.json — Local attach
```json
{
  "name": "Python: Launch exploit.py",
  "type": "debugpy",
  "request": "launch",
  "program": "${file}",
  "console": "integratedTerminal",
  "args": ["--target", "http://127.0.0.1:8080", "--debug"]
}
```
Set `args` to match your argparse flags.

### launch.json — Remote attach
```json
{
  "name": "Python: Attach (remote)",
  "type": "debugpy",
  "request": "attach",
  "connect": {
    "host": "127.0.0.1",
    "port": 5678
  },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/root/exploit"
    }
  ]
}
```
- Tunnel: `ssh -L 5678:127.0.0.1:5678 user@target`
- `pathMappings` is critical if the script path on the remote differs local workspace

## Node.js (Inspector Protocol)
- <https://code.visualstudio.com/docs/nodejs/nodejs-debugging>
### Enable inspector on target
```bash
node --inspect=0.0.0.0:9229 server.js
# or break on first line:
node --inspect-brk=0.0.0.0:9229 server.js
```

### VSCode extension
Built-in — no extension needed (`pwa-node` debug type).

### launch.json — Local attach
```json
{
  "name": "Node: Launch",
  "type": "node",
  "request": "launch",
  "program": "${workspaceFolder}/server.js"
}
```

### launch.json — Remote attach
```json
{
  "name": "Node: Attach (remote)",
  "type": "node",
  "request": "attach",
  "address": "127.0.0.1",
  "port": 9229,
  "localRoot": "${workspaceFolder}",
  "remoteRoot": "/opt/app",
  "protocol": "inspector"
}
```
- Tunnel: `ssh -L 9229:127.0.0.1:9229 user@target`
- For Electron/desktop app targets (rare in OSWE but occasionally relevant for client-side JS logic), use `"type": "pwa-chrome"` attach with `--remote-debugging-port`.


## .NET (vsdbg)
- <https://code.visualstudio.com/docs/csharp/debugger-settings>
### Install debugger on target (no Visual Studio license needed)
```bash
curl -sSL https://aka.ms/getvsdbgsh | bash /dev/stdin -v latest -l ~/vsdbg
```

### VSCode extension
`C#` (Microsoft, ms-dotnettools.csharp) — uses vsdbg by default, or configure `netcoredbg` manually for non-MS-licensed remote scenarios.

### launch.json — Local
```json
{
  "name": ".NET Launch",
  "type": "coreclr",
  "request": "launch",
  "program": "${workspaceFolder}/bin/Debug/net8.0/App.dll",
  "cwd": "${workspaceFolder}"
}
```

### launch.json — Remote attach (via SSH + netcoredbg)
```json
{
  "name": ".NET Attach (remote)",
  "type": "coreclr",
  "request": "attach",
  "processId": "${command:pickRemoteProcess}",
  "pipeTransport": {
    "pipeProgram": "ssh",
    "pipeArgs": ["-T", "user@target"],
    "debuggerPath": "/home/user/netcoredbg/netcoredbg",
    "pipeCwd": "${workspaceFolder}"
  },
  "sourceFileMap": {
    "/remote/path/to/source": "${workspaceFolder}"
  }
}
```
- This uses VSCode's pipe transport rather than a raw port tunnel.

## Go (Delve)
- <https://code.visualstudio.com/docs/languages/go>
### Install
```bash
go install github.com/go-delve/delve/cmd/dlv@latest
```

### Run headless server on target
```bash
dlv debug --headless --listen=0.0.0.0:2345 --api-version=2 --accept-multiclient ./main.go
# or attach to running process
dlv attach <PID> --headless --listen=0.0.0.0:2345 --api-version=2
```

### VSCode extension
`Go` (Google/golang.go) — bundles Delve integration.

### launch.json — Local
```json
{
  "name": "Go: Launch",
  "type": "go",
  "request": "launch",
  "mode": "debug",
  "program": "${workspaceFolder}"
}
```

### launch.json — Remote attach
```json
{
  "name": "Go: Attach (remote)",
  "type": "go",
  "request": "attach",
  "mode": "remote",
  "remotePath": "/root/go/src/app",
  "port": 2345,
  "host": "127.0.0.1",
  "substitutePath": [
    {
      "from": "${workspaceFolder}",
      "to": "/root/go/src/app"
    }
  ]
}
```
- Tunnel: `ssh -L 2345:127.0.0.1:2345 user@vps`
- Note: newer Delve/VSCode-Go versions deprecate `"mode": "remote"` in favor of `dlv --headless` + plain `"request": "attach"` with `"mode": "local"` and `port` set — check your installed `dlv` version with `dlv version` before assuming syntax.
