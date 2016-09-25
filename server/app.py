#!/usr/bin/env python

import js2py
import logging
import jinja2
import webapp2
import os
import json
from webob import exc

# Initialize logging when running standalone
if __name__ == '__main__':
	logging.getLogger().setLevel(logging.INFO)

# Load template
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "views")),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
TEMPLATE = JINJA_ENVIRONMENT.get_template('index.html')
EMPTY_TEMPLATE = TEMPLATE.render({"state": "undefined", "html": ""})

# Load the precompiled version of the JS server. This is the fastest way to
# load the JavaScript code.
from server import server
js = server.server

# Compile the JS server at run-time.
# This is very slow, but can be handy when you want to compile with 
# `webpack --watch` during debugging
# import urllib
# logging.info("Compiling server.js ...")
# context = js2py.EvalJs({
# 	'encodeURIComponent': lambda x: urllib.quote(x)
# }) 
# _, server = js2py.run_file("server.js", context)
# js = server.server
# logging.info("Compiling server.js finished")

# Render the application with given state
def render(state):
	try:
		result = js.render(state).to_dict()
		# Something seems to be going wrong, and some escaped characters aren't
		# unescaped properly. A bug in js2py?
		result["html"] = result["html"].replace("$&", ">")
		return result
	except js2py.base.PyJsException, e:
		logging.error(e)
		logging.error("To get more information, run:")
		logging.error("    ./renderComponent '" + json.dumps(state).replace("'", "'\\''") + "'")
		raise exc.HTTPBadRequest

# Dummy state
def get_state_from_db():
	return { "value": 42 }

class CounterHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.headers.get("X-DevServer") == None:
			self.response.write(TEMPLATE.render(
				render(get_state_from_db()))
			)
		else:
			self.response.write(TEMPLATE.render({
				"state": "undefined", 
				"html": ""
			}))

class StateHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] = "application/json"
		self.response.write(json.dumps(get_state_from_db()))

app = webapp2.WSGIApplication([
	('/api/state', StateHandler),
	('/', CounterHandler),
], debug=True)

def main():
	from paste import httpserver, urlmap, urlparser
	root_app = urlmap.URLMap()
	root_app["/js"] = urlparser.make_static({}, os.path.join("public", "js"))
	root_app["/"] = app
	httpserver.serve(root_app, host='127.0.0.1', port='8080')
	
if __name__ == '__main__':
	main()
