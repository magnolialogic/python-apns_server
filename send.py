#!/usr/bin/env python3

from apns_session import PushSession
import argparse
import sys
import yaml

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Use APNS to send test push notifications to your iOS apps")
parser.add_argument("--prod", "--production", action="store_false", help="Use production environment")
parser.add_argument("--title", required=False, default="Title", help="Alert title text")
parser.add_argument("--body", required=False, default="Body", help="Alert body text")
parser.add_argument("--badge", type=int, required=False, default=0, help="Number to set in app icon badge")
parser.add_argument("--silent", action="store_true", help="Do not play sound")
# parser.add_argument("--background", type=yaml.safe_load, required=False, help="Deliver quoted dict silently in background") # Pass a custom dictionary as background payload
parser.add_argument("--background", type=float, required=False, help="Deliver float data silently in the background")
parser.add_argument("--yaml", action="store_true", help="Use DeviceTokens from tokens.yaml instead of using APNS remote server API")
args = parser.parse_args()

# Generates a test notification which is by default only a sound
session = PushSession(background=args.background, title=args.title, body=args.body, badge=args.badge, silent=args.silent, dev=args.prod, yaml_tokens=args.yaml)
session.send()