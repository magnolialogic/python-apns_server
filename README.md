# python-apns_server
Python server-side tools for managing APNS device tokens and generating test notifications

## Dependencies
[PyAPNs2](https://github.com/Pr0Ger/PyAPNs2)

[flask](https://pypi.org/project/Flask/)

[flask_restful](https://pypi.org/project/Flask-RESTful/)

## Usage
#### server.py
python + Flask micro RESTful API for receiving and storing APNS tokens from your iOS apps.


1. Copy `app.yaml` and `ssl.yaml` into script root directory
2. Use [certbot](https://certbot.eff.org/) to generate SSL certificate + key files
3. Update `ssl.conf` with paths to newly generated SSL cert + key and update `app.yaml` with your Xcode Team ID and paths to your cert + app key files
4. Start the server with `./server.py --debug`

To run as a system service skip step 4 and:
```
$ sudo ln -s /path/to/etc/apns_server.service /lib/systemd/system/apns_server.service
$ sudo systemctl enable apns_server
$ sudo systemctl start apns_server
```

#### apns_send.py
Use to send test notifications to your iOS app via APNS
```
usage: send.py [-h] [--prod] [--title TITLE] [--body BODY] [--badge BADGE]
               [--silent] [--background BACKGROUND]

Use APNS to send test push notifications to your iOS apps

optional arguments:
  -h, --help            show this help message and exit
  --prod, --production  Use production environment
  --title TITLE         Alert title text
  --body BODY           Alert body text
  --badge BADGE         Number to set in app icon badge
  --silent              Do not play sound
  --background BACKGROUND
                        Deliver quoted dict silently in background
```
