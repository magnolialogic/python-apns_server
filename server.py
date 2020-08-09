#!/usr/bin/env python3

from apns_session import Session
import argparse
from datetime import datetime
from flask import Flask
from flask_restful import Api, reqparse, Resource
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import yaml

# Constants

api_version = "1"
script_home = os.path.dirname(os.path.realpath(__file__))

# Parse command-line arguments

parser = argparse.ArgumentParser(description="Flask RESTful microservice for managing iOS APNS device tokens")
parser.add_argument("--debug", action="store_true", help="Run Flask app in debug mode")
args = parser.parse_args()

# Read YAML config file

with open(os.path.join(script_home, "config.yaml")) as config_file:
	try:
		config = yaml.safe_load(config_file)
	except yaml.YAMLError:
		sys.exit(yaml.YAMLError)

# Configure Flask app and set up SQLite DB

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config["sqlite-path"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

session_relationship_table = db.Table("session_relationship",
	db.Column("id", db.Integer, primary_key=True),
	db.Column("session_id", db.Integer, db.ForeignKey("session.id"), nullable=False),
	db.Column("user_id", db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
)

# Convenience methods

def log_event(message):
	with open(os.path.join(script_home, "access.log"), "a") as log_file:
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

# Flask Resources

class AllTokenIDs(Resource):
	"""
	Returns all DeviceTokens
	/tokens
	GET-ONLY
	"""
	def get(self):
		tokens = [token.id for token in TokenTable.query.all()]
		log_event("GET /tokens -> 200 Success")
		return tokens, 200

class AllTokensForBundleID(Resource):
	"""
	Returns all DeviceTokens for a given BundleID
	/tokens/<string:bundle_id>
	GET-ONLY
	"""
	def get(self, bundle_id):
		tokens = [token.id for token in TokenTable.query.filter_by(bundle_id=bundle_id).all()]
		log_event("GET /tokens/{bundle_id} -> 200 Success".format(bundle_id=bundle_id))
		return tokens, 200

class AllTokensForUserID(Resource):
	"""
	Returns all DeviceTokens for a given UserID
	/user/<string:user_id>/tokens
	GET-ONLY
	"""
	def get(self, user_id):
		user_record = UserTable.query.filter_by(id=user_id).first()
		if user_record:
			tokens = [token.id for token in user_record.tokens]
			log_event("GET /user/{user}/tokens -> 200 Success".format(user=user_id))
			return tokens, 200
		else:
			return "User {user_id} does not exist".format(user_id=user_id), 404

class AllUserIDs(Resource):
	"""
	Returns UserIDs for all Users
	/users
	GET-ONLY
	"""
	def get(self):
		all_users = [entry.id for entry in UserTable.query.all()]
		log_event("GET /users -> 200 Success")
		return all_users, 200

class AllUsersForBundleID(Resource):
	"""
	Returns all UserIDs for given BundleID
	/users/<string:bundle_id>
	GET-ONLY
	"""
	def get(self, bundle_id):
		all_users = list(dict.fromkeys([token.user_id for token in TokenTable.query.filter_by(bundle_id=bundle_id) if token.bundle_id == bundle_id]))
		log_event("GET /users/{bundle_id} -> 200 Success".format(bundle_id=bundle_id))
		return all_users, 200

class TokenByID(Resource):
	"""
	Returns DeviceToken for given ID
	/token/<string:token_id>
	GET, DELETE
	"""
	def get(self, token_id):
		token = TokenTable.query.filter_by(id=token_id).first()
		if token:
			log_event("GET /token/{token_id} -> 200 Success".format(token_id=token_id))
			return {"id": token.id, "bundle-id": token.bundle_id, "user": token.user.name, "user-id": token.user_id}, 200
		else:
			log_event("GET /token/{token_id} -> 404 NotFound".format(token_id=token_id))
			return "{token_id} not found".format(token_id=token_id), 404

	def delete(self, token_id):
		if TokenTable.query.filter_by(id=token_id).first():
			TokenTable.query.filter_by(id=token_id).delete()
			db.session.commit()
			log_event("DELETE /token/{token_id} -> 200 Success".format(token_id=token_id))
			return "{token_id} has been deleted".format(token_id=token_id), 200
		else:
			log_event("DELETE /token/{token_id} -> 404 NotFound".format(token_id=token_id))
			return "{token_id} not found".format(token_id=token_id), 404

class UserByID(Resource):
	"""
	User for given UserID
	/user/<string:user_id>
	GET, POST, PUT, PATCH, DELETE
	"""
	def get(self, user_id):
		"""
		Gets info for given UserID
		"""
		user_record = UserTable.query.filter_by(id=user_id).first()
		if user_record:
			user = {
				"admin": str(bool(user_record.admin)),
				"device-tokens": [token.id for token in user_record.tokens],
				"name": user_record.name,
				"user-id": user_record.id
			}
			log_event("GET /user/{request} -> 200 Success {result}".format(request=user_id, result=user))
			return user, 200
		else:
			log_event("GET /user/{request} -> 404 NotFound".format(request=user_id))
			return "User {user_id} not found".format(user_id=user_id), 404

	def post(self, user_id):
		"""
		Creates given UserID
		"""
		parser = reqparse.RequestParser()
		parser.add_argument("bundle-id", type=str)
		parser.add_argument("device-token", type=str)
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		if valid_data(args):
			user_record = UserTable.query.filter_by(id=user_id).first()
			if user_record:
				log_event("POST /user/{request} -> 409 AlreadyExists".format(request=user_id))
				return "User {user_id} already exists".format(user_id=user_id), 409
			else:
				db.session.add(UserTable(id=user_id, name=args["name"]))
				db.session.add(TokenTable(id=args["device-token"], user_id=user_id, bundle_id=args["bundle-id"]))
				db.session.commit()
				log_event("POST /user/{request} -> 201 Created {result}".format(request=user_id, result=args))
				return "Created user {user_id}".format(user_id=user_id), 201
		else:
			log_event("POST /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=args))
			return args, 400

	def put(self, user_id):
		"""
		Creates or completely replaces given UserID
		"""
		parser = reqparse.RequestParser()
		parser.add_argument("bundle-id", type=str)
		parser.add_argument("device-token", type=str)
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		if valid_data(args):
			user_record = UserTable.query.filter_by(id=user_id)
			if user_record.first():
				user_record.update(dict(name=args["name"]))
				if args["device-token"] not in [token.id for token in user_record.first().tokens]:
					db.session.add(TokenTable(id=args["device-token"], bundle_id=args["bundle-id"], user_id=user_id))
				else:
					TokenTable.query.filter_by(id=args["device-token"]).update(dict(id=args["device-token"], user_id=user_id, bundle_id=args["bundle-id"]))
				db.session.commit()
				log_event("PUT /user/{request} -> 200 Success".format(request=user_id))
				return "User {user_id} updated".format(user_id=user_id), 200
			else:
				log_event("PUT /user/{request} -> 201 Created".format(request=user_id))
				return "Created user {user_id}".format(user_id=user_id), 201
		else:
			log_event("PUT /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=args))
			return args, 400

	def patch(self, user_id):
		"""
		Updates Name for given UserID
		"""
		parser = reqparse.RequestParser()
		parser.add_argument("name", type=str)
		args = parser.parse_args()

		if args["name"] not in ["", None]:
			user_record = UserTable.query.filter_by(id=user_id)
			if user_record.first():
				if user_record.first().name != args["name"]:
					user_record.update(dict(name=args["name"]))
					db.session.commit()
					log_event("PATCH /user/{request} -> 200 Success {result}".format(request=user_id, result=args))
					return "Updated name for user {user_id}".format(user_id=user_id), 200
				else:
					log_event("PATCH /user/{request} -> 304 NotModified {result}".format(request=user_id, result=args))
					return 304
			else:
				log_event("PATCH /user/{request} -> 404 NotFound {result}".format(request=user_id, result=args))
				return "User {user_id} not found".format(user_id=user_id), 404

		else:
			log_event("PATCH /user/{request} -> 400 Bad Request {result}".format(request=user_id, result=args))
			return args, 400

	def delete(self, user_id):
		"""
		Deletes given User and associated DeviceTokens
		"""
		user_record = UserTable.query.filter_by(id=user_id).first()
		if user_record:
			for token in TokenTable.query.filter_by(user_id=user_record.id).all():
				db.session.delete(token)
			db.session.delete(user_record)
			db.session.commit()
			log_event("DELETE /user/{request} -> 200 Success".format(request=user_id))
			return "{user} has been deleted".format(user=user_id), 200
		else:
			log_event("DELETE /user/{request} -> 404 NotFound".format(request=user_id))
			return "{user} not found".format(user=user_id), 404

# SQLAlchemy models

class SessionRelationship(object):
	def __init__(self, session_id, user_id):
		self.session_id = session_id
		self.user_id = user_id

class UserTable(db.Model):
	__tablename__ = "user"
	id = db.Column(db.Text, primary_key=True)
	admin = db.Column(db.Integer, default=0, nullable=False)
	name = db.Column(db.Text, nullable=False)
	tokens = db.relationship("TokenTable", backref="user", lazy=True)

	def __repr__(self):
		return "<User %r>" % self.name

class BundleTable(db.Model):
	__tablename__ = "bundle"
	id = db.Column(db.Text, primary_key=True)

	def __repr__(self):
		return "<Bundle %r>" % self.id

class TokenTable(db.Model):
	__tablename__ = "token"
	id = db.Column(db.Text, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	bundle_id = db.Column(db.Text, db.ForeignKey("bundle.id"), nullable=False)

	def __repr__(self):
		return "<Token %r>" % self.id

class SessionTable(db.Model):
	__tablename__ = "session"
	id = db.Column(db.Integer, primary_key=True)
	active = db.Column(db.Integer, default=0, nullable=False)
	users = db.relationship("UserTable", secondary=session_relationship_table, lazy="subquery", backref=db.backref("sessions", lazy=True))

	def __repr__(self):
		return "<Session %r>" % self.id

# Do The Thing

if __name__ == "__main__":
	db.mapper(SessionRelationship, session_relationship_table)
	api = Api(app)
	api_root = "/v" + api_version
	print(api_root)
	api.add_resource(AllTokenIDs, api_root + "/tokens")
	api.add_resource(AllTokensForBundleID, api_root + "/tokens/<string:bundle_id>")
	api.add_resource(AllTokensForUserID, api_root + "/user/<string:user_id>/tokens")
	api.add_resource(AllUserIDs, api_root + "/users")
	api.add_resource(AllUsersForBundleID, api_root + "/users/<string:bundle_id>")
	api.add_resource(TokenByID, api_root + "/token/<string:token_id>")
	api.add_resource(UserByID, api_root + "/user/<string:user_id>")
	app.run(ssl_context=(config["cert-path"], config["key-path"]), debug=args.debug)
