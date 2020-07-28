#!/usr/bin/env python3

from apns2.client import APNsClient
from apns2.credentials import TokenCredentials
from apns2.payload import Payload, PayloadAlert
import argparse
import sys
import yaml

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Use APNS to send test push notifications to your iOS apps")
parser.add_argument("--prod", "--production", action="store_false", help="Use production environment")
parser.add_argument("--title", required=False, help="Alert title text")
parser.add_argument("--body", required=False, help="Alert body text")
parser.add_argument("--badge", type=int, required=False, help="Number to set in app icon badge")
parser.add_argument("--no_sound", action="store_true", help="Do not play sound")
parser.add_argument("--background", type=yaml.safe_load, required=False, help="Deliver quoted dict silently in background")
args = parser.parse_args()

# Get config data and enrolled tokens from YAML files
with open ("apns_send_config.yaml") as config_file:
	try:
		loaded_config = yaml.safe_load(config_file)
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

with open ("tokens.yaml") as token_file:
	try:
		loaded_tokens = list(yaml.safe_load_all(token_file))
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

# Assign loaded .yaml data to constants
auth_key = loaded_config["auth-key"]
auth_key_filename = loaded_config["auth-key-filename"]
bundle_id = loaded_config["bundle-id"]
cert_filename = loaded_config["cert-filename"]
team_id = loaded_config["team-id"]
token_audience = [target["device-token"] for target in loaded_tokens if target["bundle-id"] == bundle_id]

# Configure notification payload
title = None
body = None
sound = "default"
badge = 0
gameID = None

if args.background:
	data = args.background
	payload = Payload(content_available=True, custom=data)
else:
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
credentials = TokenCredentials(auth_key_path=auth_key_filename, auth_key_id=auth_key, team_id=team_id)
client = APNsClient(credentials=credentials, use_sandbox=args.prod)
for target in token_audience:
	print("Sending APNS payload", payload.dict(), "to", target)
	client.send_notification(token_hex=target, notification=payload, topic=bundle_id)