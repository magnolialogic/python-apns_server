#!/usr/bin/env python3

from apns_session import Session
import argparse
from datetime import datetime
from flask import Flask, g
from flask_restful import Api, fields, marshal_with, reqparse, Resource
import os
import sqlite3
import sys
import yaml

parser = argparse.ArgumentParser(description="Flask RESTful microservice for managing iOS APNS device tokens")
parser.add_argument("--debug", action="store_true", help="Run Flask app in debug mode")
args = parser.parse_args()

script_home = os.path.dirname(os.path.realpath(__file__))

users_filename = "users.yaml"
users_file_mode = "r" if os.path.exists(users_filename) else "w"
users = []

user_fields = {
	"bundleID": fields.String,
	"device-token": fields.List(fields.String),
	"name": fields.String,
	"userID": fields.String
}

# Read YAML config files

with open(os.path.join(script_home, users_filename), users_file_mode) as users_file:
	if users_file_mode == "r":
		try:
			users = list(yaml.safe_load_all(users_file))
			users = [user for user in users if user != None]
		except yaml.YAMLError:
			sys.exit(yaml.YAMLError)
	else:
		users_file.write("---\n")
		users_file.write("...\n")
		users_file.truncate()

with open(os.path.join(script_home, "ssl.yaml")) as ssl_file:
	try:
		ssl_settings = yaml.safe_load(ssl_file)
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

def write_yaml(users):
	with open(os.path.join(script_home, users_filename), "w") as user_file:
		try:
			updated_users = yaml.safe_dump_all(users)
			user_file.write("---\n")
			user_file.write(updated_users)
			user_file.write("...\n")
			user_file.truncate()
		except yaml.YAMLError:
			sys.exit(yaml.YAMLError)

# Convenience methods

def log_event(message):
	with open(os.path.join(script_home, "access.log"), "a") as log_file:
		log_file.write("{timestamp}: {message}\n".format(timestamp=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), message=message))

def valid_data(data):
	expected_keys = ["bundle-id", "device-token", "name", "user-id"]
	if sorted(expected_keys) == sorted(list(data.keys())):
		for value in data.values():
			if value in ["", None]:
				return False
		return True
	else:
		return False

# Flask Resources

class Tokens(Resource):
	"""
	Returns all DeviceTokens
	/tokens
	GET-ONLY
	"""
	def get(self):
		tokens = []
		for entry in users:
			tokens.append(entry["device-token"])
		log_event("GET /tokens -> 200 Success {result}".format(result=tokens))
		return tokens, 200

class TokensForUser(Resource):
	"""
	Returns all DeviceTokens for a given UserID
	GET ONLY
	/user/<string_user_id>/tokens
	"""
	def get(self, user_id):
		for entry in users:
			if user_id == entry["user-id"]:
				log_event("GET /user/{user}/token -> 200 Success".format(user=user_id))
				return entry["device-token"], 200

class User(Resource):
	"""
	User for given UserID
	/user/<string:user_id>
	GET, POST, PUT, PATCH, DELETE
	"""
	def get(self, user_id):
		for entry in users:
			if user_id == entry["user-id"]:
				log_event("GET /user/{request} -> 200 Success {result}".format(request=user_id, result=entry))
				return entry, 200

		log_event("GET /user/{request} -> 404 NotFound".format(request=user_id))
		return "User not found", 404

	def post(self, user_id):
		global users
		parser = reqparse.RequestParser()
		parser.add_argument("bundle-id", type=str)
		parser.add_argument("device-token", type=str)
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		new_user = {
			"name": args["name"],
			"bundle-id": args["bundle-id"],
			"device-token": args["device-token"],
			"user-id": user_id
		}

		if valid_data(new_user):
			for entry in users:
				if user_id == entry["user-id"]:
					log_event("POST /user/{request} -> 409 AlreadyExists {result}".format(request=user_id, result=entry))
					return "User with token {user_id} already exists".format(user_id=user_id), 409

			updated_users = [user for user in users if not user == None]
			updated_users.append(new_user)
			users = updated_users
			write_yaml(users)
			log_event("POST /user/{request} -> 201 Created {result}".format(request=user_id, result=new_user))
			return new_user, 201
		else:
			log_event("POST /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=new_user))
			return new_user, 400

	def put(self, user_id):
		parser = reqparse.RequestParser()
		parser.add_argument("bundle-id", type=str)
		parser.add_argument("device-token", type=str)
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		new_user = {
			"name": args["name"],
			"bundle-id": args["bundle-id"],
			"device-token": args["device-token"],
			"user-id": user_id
		}

		if valid_data(new_user):
			for entry in users:
				if user_id == entry["user-id"]:
					entry["name"] = args["name"]
					entry["bundle-id"] = args["bundle-id"]
					entry["device-token"] = args["device-token"]
					log_event("PUT /user/{request} -> 200 Success {result}".format(request=user_id, result=entry))
					write_yaml(users)
					return entry, 200

			log_event("PUT /user/{request} -> 201 Created {result}".format(request=user_id, result=new_user))
			users.append(new_user)
			write_yaml(users)
			return new_user, 201
		else:
			log_event("PUT /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=new_user))
			return new_user, 400

	def patch(self, user_id):
		parser = reqparse.RequestParser()
		parser.add_argument("bundle-id", type=str)
		parser.add_argument("device-token", type=str)
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		new_user = {
			"name": args["name"],
			"bundle-id": args["bundle-id"],
			"device-token": args["device-token"],
			"user-id": user_id
		}

		if valid_data(new_user):
			for entry in users:
				if user_id == entry["user-id"]:
					if entry["name"] == args["name"] and entry["bundle-id"] == args["bundle-id"] and entry["device-token"] == args["device-token"]:
						log_event("PATCH /user/{request} -> 304 NotModified {result}".format(request=user_id, result=entry))
						return new_user, 304
					else:
						if entry["name"] != args["name"]: entry["name"] = args["name"]
						if entry["bundle-id"] != args["bundle-id"]: entry["bundle-id"] = args["bundle-id"]
						if entry["device-token"] != args["device-token"]: entry["device-token"] = args["device-token"]
						log_event("PATCH /user/{request} -> 200 Success {result}".format(request=user_id, result=entry))
						write_yaml(users)
						return new_user, 200

			log_event("PATCH /user/{request} -> 404 NotFound {result}".format(request=user_id, result=new_user))
			return new_user, 404
		else:
			log_event("PATCH /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=new_user))
			return new_user, 400

	def delete(self, user_id):
		global users
		for entry in users:
			if user_id == entry["user-id"]:
				log_event("DELETE /user/{request} -> 200 Success".format(request=user_id))
				users = [entry for entry in users if entry["user-id"] != user_id]
				write_yaml(users)
				return "{user} has been deleted".format(user=user_id), 200

		log_event("DELETE /user/{request} -> 404 NotFound".format(request=user_id))
		return "{user} not found".format(user=user_id), 404

class Users(Resource):
	"""
	Returns UserIDs for all Users
	GET ONLY
	"""
	def get(self):
		return users, 200

# Do The Thing

api_version = "/v1/"

if __name__ == "__main__":
	app = Flask(__name__)
	api = Api(app)
	api.add_resource(Tokens, api_version + "/tokens")
	api.add_resource(TokensForUser, api_version + "/user/<string:user_id>/tokens")
	api.add_resource(User, api_version + "/user/<string:user_id>")
	api.add_resource(Users, api_version + "/users")
	app.run(ssl_context=(ssl_settings["cert-path"], ssl_settings["key-path"]), debug=args.debug)
