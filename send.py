#!/usr/bin/env python3

from apns_session import Session
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
parser.add_argument("--background", type=yaml.safe_load, required=False, help="Deliver quoted dict silently in background")
args = parser.parse_args()

# Generates a test notification which is by default only a sound
session = Session(background=args.background, title=args.title, body=args.body, badge=args.badge, silent=args.silent, dev=args.prod)
session.send()