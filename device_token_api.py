#!/usr/bin/env python3

import argparse
from flask import Flask
from flask_restful import Api, Resource, reqparse
import os
import sys
import yaml

parser = argparse.ArgumentParser(description="Flask RESTful microservice for managing iOS APNS device tokens")
parser.add_argument("--debug", action="store_true", help="Run Flask app in debug mode")
args = parser.parse_args()

app = Flask(__name__)
api = Api(app)

script_home = os.path.dirname(os.path.realpath(__file__))
token_file = "tokens.yaml"

with open(os.path.join(script_home, token_file)) as token_file:
	try:
		tokens = list(yaml.safe_load_all(token_file))
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

with open(os.path.join(script_home, "ssl.yaml")) as ssl_file:
	try:
		ssl_settings = yaml.safe_load(ssl_file)
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

def write_yaml(tokens):
	with open(os.path.join(script_home, token_file), "w") as token_file:
		try:
			updated_tokens = yaml.safe_dump_all(tokens)
			token_file.write("---\n")
			token_file.write(updated_tokens)
			token_file.write("...")
			token_file.truncate()
		except yaml.YAMLError:
			sys.exit(yaml.YAMLError)

class Token(Resource):
	def get(self, token):
		for entry in tokens:
			if (token == entry["deviceToken"]):
				return entry, 200
		return "Token not found", 404

	def post(self, token):
		parser = reqparse.RequestParser()
		parser.add_argument("name")
		parser.add_argument("bundleID")
		args = parser.parse_args()

		for entry in tokens:
			if (token == entry["deviceToken"]):
				return "User with token {token} already exists".format(token=token), 400

		token = {
			"name": args["name"],
			"bundleID": args["bundleID"],
			"deviceToken": token
		}

		tokens.append(token)
		write_yaml(tokens)
		return token, 201

	def put(self, token):
		parser = reqparse.RequestParser()
		parser.add_argument("name")
		parser.add_argument("bundleID")
		args = parser.parse_args()

		for entry in tokens:
			if (token == entry["deviceToken"]):
				entry["name"] = args["name"]
				entry["bundleID"] = args["bundleID"]
				write_yaml(tokens)
				return entry, 200

		token = {
			"name": args["name"],
			"bundleID": args["bundleID"],
			"deviceToken": token
		}

		tokens.append(token)
		write_yaml(tokens)
		return token, 201

	def delete(self, token):
		global tokens
		tokens = [entry for entry in tokens if entry["deviceToken"] != token]
		write_yaml(tokens)
		return "{token} has been deleted".format(token=token), 200

api.add_resource(Token, "/tokens/<string:token>")

app.run(ssl_context=(ssl_settings["cert-path"], ssl_settings["key-path"]), debug=args.debug)