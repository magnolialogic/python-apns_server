# python-apns_server
Python server-side tools for managing APNS device tokens and generating test notifications

## Dependencies
[PyAPNs2](https://github.com/Pr0Ger/PyAPNs2)

[flask](https://pypi.org/project/Flask/)

[flask_restful](https://pypi.org/project/Flask-RESTful/)

## Usage
#### device_token_api.py
python + Flask micro RESTful API for receiving and storing APNS tokens from your iOS apps. Use [certbot](https://certbot.eff.org/) to generate SSL certificate + key files and update `ssl.yaml` with their paths.

To run as a system service:
```
$ sudo ln -s token_server.service /lib/systemd/system/token_server.service
$ sudo systemctl enable token_server
$ sudo systemctl start token_server
```

#### apns_send.py
Use to send test notifications to your iOS app via APNS
```
usage: apns_send.py [-h] [--prod] [--title TITLE] [--body BODY]
                    [--badge BADGE] [--no_sound] [--background BACKGROUND]

Use APNS to send test push notifications to your iOS apps

optional arguments:
  -h, --help            show this help message and exit
  --prod, --production  Use production environment
  --title TITLE         Alert title text
  --body BODY           Alert body text
  --badge BADGE         Number to set in app icon badge
  --no_sound            Do not play sound
  --background BACKGROUND
                        Deliver quoted dict silently in background
```
