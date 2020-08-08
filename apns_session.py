#!/usr/bin/env python3

from apns2.client import APNsClient
from apns2.credentials import TokenCredentials
from apns2.payload import Payload, PayloadAlert
import sys
import yaml

class Session:
	def __init__(self, background=None, title="Title", body="Body", silent=True, badge=0, dev=True):
		self.title = title
		self.body = body
		self.silent = silent
		self.badge = badge
		self.background = background
		self.dev = dev
		if silent:
			self.sound = None
		else:
			self.sound = "Default"

	def send(self):
		tokens = []

		# Get config data and enrolled tokens from YAML files
		with open ("app.yaml") as app_file:
			try:
				loaded_app = yaml.safe_load(app_file)
			except yaml.YAMLError:
				sys.exit(yaml.YAMLError)

		with open ("tokens.yaml") as token_file:
			try:
				loaded_tokens = [token for token in list(yaml.safe_load_all(token_file)) if not token == None]
				if len(loaded_tokens) == 0:
					sys.exit("No target device tokens in tokens.yaml")
			except yaml.YAMLError:
				sys.exit(yaml.YAMLError)

		# Assign loaded .yaml data to constants
		auth_key = loaded_app["auth-key"]
		auth_key_filename = loaded_app["auth-key-filename"]
		bundle_id = loaded_app["bundle-id"]
		cert_filename = loaded_app["cert-filename"]
		team_id = loaded_app["team-id"]
		token_audience = [target["device-token"] for target in loaded_tokens if target["bundle-id"] == bundle_id]

		# Create payload based on notification type
		if self.background:
			data = {"Data": self.background}
			payload = Payload(content_available=True, custom=data)
		else:
			alert = PayloadAlert(title=self.title, body=self.body)
			payload = Payload(alert=alert, sound=self.sound, badge=self.badge)

		# Create session and post notification
		credentials = TokenCredentials(auth_key_path=auth_key_filename, auth_key_id=auth_key, team_id=team_id)
		client = APNsClient(credentials=credentials, use_sandbox=self.dev)
		for target in token_audience:
			print("Sending APNS payload", payload.dict(), "to", target)
			client.send_notification(token_hex=target, notification=payload, topic=bundle_id)

if __name__ == "__main__":
	sys.exit("I am a module, not a script.")