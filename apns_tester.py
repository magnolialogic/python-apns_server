#!/usr/bin/env python3

from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
import argparse
import os
import pprint
import sys
import yaml

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Use APNS to send test push notifications to your iOS apps")
environment_group = parser.add_mutually_exclusive_group(required=True)
environment_group.add_argument("-p", "--prod", "--production", action="store_true", help="Use production environment")
environment_group.add_argument("-d", "--dev", "--development", action="store_true", help="Use development sandbox")
environment_group.add_argument("--update-device-token", required=False, help="Update device token in config.yaml")
parser.add_argument("--token", action="store_true", required=False, help="Use token-based authentication")
parser.add_argument("--title", required=False, help="Alert title text")
parser.add_argument("--body", required=False, help="Alert body text")
parser.add_argument("--badge", type=int, required=False, help="Number to set in app icon badge")
parser.add_argument("--no_sound", action="store_true", help="Do not play sound")
parser.add_argument("--background", action="store_true", required=False, help="Deliver silently in background")
parser.add_argument("--bundle", required=True, help="App Bundle ID")
args = parser.parse_args()

# Get certs and identifiers from config.yaml
with open ("config.yaml", "r+") as config_file:
	try:
		loaded_file = list(yaml.safe_load_all(config_file))
	except yaml.YAMLError:
		print(yaml.YAMLError)

	for entry in loaded_file:
		if entry["name"] == args.bundle:
			team_id = entry["team-id"]
			auth_key = entry["auth-key"]
			auth_key_filename = entry["auth-key-filename"]
			cert_filename = entry["cert-filename"]
			device_token = entry["device-token"]

			if args.update_device_token:
				entry["device-token"] = args.update_device_token

	if args.update_device_token:
		if not args.bundle in [entry["name"] for entry in loaded_file]:
			sys.exit("Bundle ID not found in config.yaml")

		try:
			updated_config = yaml.safe_dump_all(loaded_file)
			config_file.seek(0)
			config_file.write("---\n")
			config_file.write(updated_config)
			config_file.write("...")
			config_file.truncate()
		except yaml.YAMLError:
			print(yaml.YAMLError)

		sys.exit()

# Configure notification payload
title = None
body = None
sound = "default"
badge = 0
gameID = None

if args.background:
	data = {
		"Size" : 96.0
	}
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

print("Sending APNS payload", payload.dict(), "to", device_token)

# Create session and post notification
if args.token:
	from apns2.credentials import TokenCredentials
	credentials = TokenCredentials(auth_key_path=auth_key_filename, auth_key_id=auth_key, team_id=team_id)
else:
	credentials = cert_filename

client = APNsClient(credentials=credentials, use_sandbox=args.dev)
client.send_notification(token_hex=device_token, notification=payload, topic=args.bundle)