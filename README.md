# python-apns_tester
Python script for sending notifications via APNS

### Dependencies
[PyAPNs2](https://github.com/Pr0Ger/PyAPNs2)

### Usage
```
usage: apns_tester.py [-h] (-p | -d | --update-device-token UPDATE_DEVICE_TOKEN) [--token]
                      [--title TITLE] [--body BODY] [--badge BADGE] [--no_sound] [--background] --bundle
                      BUNDLE

Use APNS to send test push notifications to your iOS apps

optional arguments:
  -h, --help            show this help message and exit
  -p, --prod, --production
                        Use production environment
  -d, --dev, --development
                        Use development sandbox
  --update-device-token UPDATE_DEVICE_TOKEN
                        Update device token in config.yaml
  --token               Use token-based authentication
  --title TITLE         Alert title text
  --body BODY           Alert body text
  --badge BADGE         Number to set in app icon badge
  --no_sound            Do not play sound
  --background          Deliver silently in background
  --bundle BUNDLE       App Bundle ID
```
