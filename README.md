# python-apns_server
Python server-side tools for managing APNS device tokens and generating test notifications

## Dependencies
[PyAPNs2](https://github.com/Pr0Ger/PyAPNs2)

[flask](https://pypi.org/project/Flask/)

[flask_restful](https://pypi.org/project/Flask-RESTful/)

## Usage
#### device_token_api.py
python + Flask micro RESTful API for receiving and storing APNS tokens from your iOS apps. Use [certbot](https://certbot.eff.org/) to generate SSL certificate + key files and update `token_server_config.yaml` with their paths.

symlink `token_server.service` into `/lib/systemd/system/` to run as a systemd service.

#### apns_tester.py
Use to send test notifications to your iOS app via APNS
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

###### Examples:

