#!/usr/bin/env python3

import argparse
from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse
import os
import sys
import yaml

parser = argparse.ArgumentParser(description="Flask RESTful microservice for managing iOS APNS device tokens")
parser.add_argument("--debug", action="store_true", help="Run Flask app in debug mode")
args = parser.parse_args()

script_home = os.path.dirname(os.path.realpath(__file__))
token_filename= "tokens.yaml"

with open(os.path.join(script_home, token_filename)) as token_file:
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
	with open(os.path.join(script_home, token_filename), "w") as token_file:
		try:
			updated_tokens = yaml.safe_dump_all(tokens)
			token_file.write("---\n")
			token_file.write(updated_tokens)
			token_file.write("...")
			token_file.truncate()
		except yaml.YAMLError:
			sys.exit(yaml.YAMLError)

def log_event(message):
	with open(os.path.join(script_home, "token_server.log"), "a") as log_file:
		log_file.write("{timestamp}: {message}\n".format(timestamp=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), message=message))

def valid_data(data):
	expected_keys = ["bundle-id", "device-token", "name"]
	if sorted(expected_keys) == sorted(list(data.keys())):
		for value in data.values():
			if value in ["", None]:
				return False
		return True
	else:
		return False

class Token(Resource):
	def get(self, token):
		for entry in tokens:
			if (token == entry["device-token"]):
				log_event("GET /token/{request} -> 200 Success {result}".format(request=token, result=entry))
				return entry, 200

		log_event("GET /token/{request} -> 404 NotFound".format(request=token))
		return "Token not found", 404

	def post(self, token):
		parser = reqparse.RequestParser()
		parser.add_argument("name")
		parser.add_argument("bundle-id")
		args = parser.parse_args()

		new_token = {
			"name": args["name"],
			"bundle-id": args["bundle-id"],
			"device-token": token
		}

		if valid_data(new_token):
			for entry in tokens:
				if (token == entry["device-token"]):
					log_event("POST /token/{request} -> 409 AlreadyExists {result}".format(request=token, result=entry))
					return "User with token {token} already exists".format(token=token), 409

			log_event("POST /token/{request} -> 201 Created {result}".format(request=token, result=new_token))
			tokens.append(new_token)
			write_yaml(tokens)
			return token, 201
		else:
			log_event("POST /token/{request} -> 400 Bad Request {result}".format(request=token, result=new_token))
			return new_token, 400


	def put(self, token):
		parser = reqparse.RequestParser()
		parser.add_argument("name")
		parser.add_argument("bundle-id")
		args = parser.parse_args()

		new_token = {
			"name": args["name"],
			"bundle-id": args["bundle-id"],
			"device-token": token
		}

		if valid_data(new_token):
			for entry in tokens:
				if (token == entry["device-token"]):
					if entry["name"] == args["name"] and entry["bundle-id"] == args["bundle-id"]:
						log_event("PUT /token/{request} -> 409 AlreadyExists {result}".format(request=token, result=entry))
						return entry, 409
					else:
						entry["name"] = args["name"]
						entry["bundle-id"] = args["bundle-id"]
						log_event("PUT /token/{request} -> 200 Success {result}".format(request=token, result=entry))
						write_yaml(tokens)
						return entry, 200

			log_event("PUT /token/{request} -> 201 Created {result}".format(request=token, result=new_token))
			tokens.append(new_token)
			write_yaml(tokens)
			return token, 201
		else:
			log_event("PUT /token/{request} -> 400 Bad Request {result}".format(request=token, result=new_token))
			return new_token, 400

	def delete(self, token):
		global tokens
		log_event("DELETE /token/{request} -> 200 Success".format(request=token))
		tokens = [entry for entry in tokens if entry["device-token"] != token]
		write_yaml(tokens)
		return "{token} has been deleted".format(token=token), 200

class Tokens(Resource):
	def get(self):
		log_event("GET /tokens -> 200 Success {result}".format(result=tokens))
		return tokens, 200

if __name__ == "__main__":
	app = Flask(__name__)
	api = Api(app)
	api.add_resource(Token, "/token/<string:token>")
	api.add_resource(Tokens, "/tokens")
	app.run(ssl_context=(ssl_settings["cert-path"], ssl_settings["key-path"]), debug=args.debug)