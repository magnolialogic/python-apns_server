#!/bin/env python3

from datetime import datetime
import os
import sys

def log_event(message):
	with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "access.log"), "a") as log_file:
		log_file.write("{timestamp}: {message}\n".format(timestamp=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), message=message))

if __name__ == "__main__":
	sys.exit("I am a module.")