#!/usr/bin/env python3

"""
send.py
https://github.com/magnolialogic/python-apns_server
"""

import argparse
from APNSPushConnection import APNSPushConnection

def main():
	"""
	Sends APNS notification based on command-line arguments
	"""
	parser = argparse.ArgumentParser(description="Use APNS to send test push notifications to your iOS apps")
	parser.add_argument("--prod", "--production", action="store_false", help="Use production environment")
	parser.add_argument("--title", required=False, default="Title", help="Alert title text")
	parser.add_argument("--body", required=False, default="Body", help="Alert body text")
	parser.add_argument("--badge", type=int, required=False, default=0, help="Number to set in app icon badge")
	parser.add_argument("--silent", action="store_true", help="Do not play sound")
	# parser.add_argument("--background", type=yaml.safe_load, required=False, help="Deliver quoted dict silently in background")
	parser.add_argument("--background", type=float, required=False, help="Deliver float data silently in the background")
	parser.add_argument("--yaml", action="store_true", help="Use DeviceTokens from tokens.yaml instead of using APNS remote server API")
	args = parser.parse_args()

	session = APNSPushConnection(sandbox=args.prod, yaml_tokens=args.yaml)
	session.create_payload(background=args.background, title=args.title, body=args.body, silent=args.silent, badge=args.badge)
	session.push()

if __name__ == "__main__":
	main()
else:
	sys.exit("I am a script, do not import me.")