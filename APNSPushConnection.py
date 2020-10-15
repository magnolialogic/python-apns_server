#!/usr/bin/env python3

"""
APNSPushSession.py
https://github.com/magnolialogic/python-apns_server
"""

import sys
from json import loads
import requests
import yaml
from apns2.client import APNsClient
from apns2.credentials import TokenCredentials
from apns2.payload import Payload, PayloadAlert

class APNSPushConnection:
	"""
	Create and push APNS notification to iOS devices
	"""

	def __init__(self, sandbox=True, yaml_tokens=False):
		self.sandbox = sandbox
		self.yaml = yaml_tokens

		self.payload = None
		self.tokens = []

		with open("app.yaml") as app_file:
			try:
				loaded_app = yaml.safe_load(app_file)
			except yaml.YAMLError:
				sys.exit(yaml.YAMLError)
			else:
				self.config = {
					"auth-key": loaded_app["auth-key"],
					"auth-key-filename": loaded_app["auth-key-filename"],
					"bundle-id": loaded_app["bundle-id"],
					"cert-filename": loaded_app["cert-filename"],
					"team-id": loaded_app["team-id"],
					"api-url": loaded_app["api-url"] + "/tokens/" + loaded_app["bundle-id"]
				}

		self.credentials = TokenCredentials(auth_key_path=self.config["auth-key-filename"], auth_key_id=self.config["auth-key"], team_id=self.config["team-id"])
		self.client = APNsClient(credentials=self.credentials, use_sandbox=self.sandbox)

		self.load_tokens()

	def load_tokens(self):
		"""
		Loads tokens from remote notification server or YAML file
		"""
		if self.yaml:
			with open("tokens.yaml") as token_file:
				try:
					loaded_tokens = [token for token in list(yaml.safe_load_all(token_file)) if token is not None]
				except yaml.YAMLError:
					sys.exit(yaml.YAMLError)
				else:
					self.tokens = [target["device-token"] for target in loaded_tokens if target["bundle-id"] == self.config["bundle-id"]]
					if len(self.tokens) == 0:
						sys.exit("Invalid data: no device tokens defined with matching BundleID")
		else:
			try:
				self.tokens = list(loads(requests.get(self.config["api-url"]).text))
			except: # pylint: disable=W0702
				sys.exit("Invalid data: no device tokens in JSON response, check remote notification server.")

	def create_payload(self, background=None, title="Title", body="Body", silent=True, badge=0): # pylint: disable=R0913
		"""
		Constructs APNS payload
		"""
		if silent:
			sound = None
		else:
			sound = "Default"
		if background is not None:
			data = {"Data": background}
			self.payload = Payload(content_available=True, custom=data)
		else:
			alert = PayloadAlert(title=title, body=body)
			self.payload = Payload(alert=alert, sound=sound, badge=badge)

	def push(self):
		"""
		Sends APNS notification to given device IDs
		"""
		if not None in self.__dict__.values() and len(self.tokens) > 0:
			for target in self.tokens:
				print("Sending APNS payload", self.payload.dict(), "to", target)
				self.client.send_notification(token_hex=target, notification=self.payload, topic=self.config["bundle-id"])
		else:
			sys.exit("Invalid data: failed to send notification, check configuration data.")

if __name__ == "__main__":
	sys.exit("I am not a script.")