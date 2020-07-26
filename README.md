# python-apnsTester
Python script for sending notifications via APNS

### Dependencies
[PyAPNs2](https://github.com/Pr0Ger/PyAPNs2)

### Usage
```
usage: apns_tester.py [-h] (-p | -d) [--token] [--title TITLE] [--body BODY] [--badge BADGE] [--no_sound]
                      [--background]
                      topic device_token

Use APNS to send test push notifications to your iOS apps

positional arguments:
  topic                 Application Bundle ID
  device_token          Device Token

optional arguments:
  -h, --help            show this help message and exit
  -p, --prod, --production
                        Use production environment
  -d, --dev, --development
                        Use development sandbox
  --token               Use token-based authentication
  --title TITLE         Alert title text
  --body BODY           Alert body text
  --badge BADGE         Number to set in app icon badge
  --no_sound            Do not play sound
  --background          Deliver silently in background
```
