#!/usr/bin/env python3

from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
import argparse
import os
import sys
import yaml

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Use APNS to send test push notifications to your iOS apps")
environment_group = parser.add_mutually_exclusive_group(required=True)
environment_group.add_argument("-p", "--prod", "--production", action="store_true", help="Use production environment")
environment_group.add_argument("-d", "--dev", "--development", action="store_true", help="Use development sandbox")
parser.add_argument("--token", action="store_true", required=False, help="Use token-based authentication")
parser.add_argument("--title", required=False, help="Alert title text")
parser.add_argument("--body", required=False, help="Alert body text")
parser.add_argument("--badge", type=int, required=False, help="Number to set in app icon badge")
parser.add_argument("--no_sound", action="store_true", help="Do not play sound")
parser.add_argument("--background", action="store_true", required=False, help="Deliver silently in background")
parser.add_argument("topic", help="Application Bundle ID")
parser.add_argument("device_token", help="Device Token")
args = parser.parse_args()

# Get certs and identifiers from config.yaml
with open ("config.yaml") as config_file:
	config_data = yaml.load(config_file, Loader=yaml.FullLoader)
	team_id = config_data["team-id"]
	auth_key = config_data["auth-key"]
	auth_key_filename = config_data["auth-key-filename"]
	cert_filename = config_data["cert-filename"]

# Configure notification payload
title = None
body = None
sound = "default"
badge = 0
gameID = None

if args.title:
	title = args.title
if args.body:
	body = args.body
if args.badge:
	badge = args.badge
if args.no_sound:
	sound = None

alert = PayloadAlert(title=title, body=body)
payload = Payload(alert=alert, sound=sound, badge=badge)

# Create session and post notification
if args.token:
	from apns2.credentials import TokenCredentials
	credentials = TokenCredentials(auth_key_path=auth_key_filename, auth_key_id=auth_key_id, team_id=team_id)
else:
	credentials = cert_filename

client = APNsClient(credentials=credentials, use_sandbox=args.dev)
client.send_notification(token_hex=args.device_token, notification=payload, topic=args.topic)