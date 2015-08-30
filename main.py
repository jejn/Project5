#!/usr/bin/env python
# coding: utf-8

import os
import urllib

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import ndb

import jinja2
import webapp2

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
							   extensions=['jinja2.ext.autoescape'], 
							   autoescape=True,)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
    	self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
    	t = JINJA_ENV.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))

guestbook_key = ndb.Key('Guestbook', 'about_gb')

#Dictionaries for Safari validation error case. 
form_errors = {"name_error": False,
			   "email_error": False,
			   "content_error": False}

form_input_holder = {"name_field": "",
					 "email_field": "",
					 "content_field": ""}

class Greeting(ndb.Model):
	author = ndb.StringProperty(indexed=False)
	email = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)

# Returns cached entries if present, otherwise stores db in GB_CACHE 
def greetings_cacher(update=False):
	key = "greetings"
	greetings = memcache.get(key)

	if greetings is None or update:

		greetings_query = Greeting.query(ancestor=guestbook_key).order(-Greeting.date)
		greetings = greetings_query.fetch()
		memcache.set(key, greetings)

	return greetings


class MainPage(Handler):
	def get(self):

		greetings = greetings_cacher()

		self.render("start.html", greetings=greetings,
								  form_errors=form_errors,
								  form_input_holder=form_input_holder)

		#Updates 'form_errors' for next submission 
		form_errors.update((k, False) for k in form_errors)


# Validates name in form only contains letters
def name_validator(name):
	if name == "":
		return False

	elif all(l.isalpha() or l.isspace() for l in name):
		return True

	else:
		return False


# Validates email in form contains '@' and '.'
def email_validator(email):
	if ("@" and ".") in email:
		return True

	else:
		return False


class GuestBook(webapp2.RequestHandler):
	def post(self):
		
		greeting = Greeting(parent=guestbook_key)

		greeting.author = self.request.get('author')
		greeting.email = self.request.get('email')
		greeting.content = self.request.get('content')
		
		valid_author = name_validator(greeting.author)
		valid_email = email_validator(greeting.email)

		# This to show that all fields are required in Safari if trying to submit empty fields
		if (valid_author and valid_email and greeting.content):
			greeting.put()
		
		else:
			if not valid_author:
				form_errors["name_error"] = True

			else:
				form_input_holder["name_field"] = greeting.author

			if not valid_email:
				form_errors["email_error"] = True

			else:
				form_input_holder["email_field"] = greeting.email

			if not greeting.content:
				form_errors["content_error"] = True

			else:
				form_input_holder["content_field"] = greeting.content
		
		greetings_cacher(True)
		self.redirect('/', MainPage)
		

class StageZeroHandler(Handler):
	def get(self):						  

		self.render("stage_0.html")

class StageOneHandler(Handler):
	def get(self):						  

		self.render("stage_1.html")

class StageTwoHandler(Handler):
	def get(self):						  

		self.render("stage_2.html")

class StageThreeHandler(Handler):
	def get(self):						  

		self.render("stage_3.html")

class StageFourHandler(Handler):
	def get(self):						  

		self.render("stage_4.html")

class StageFiveHandler(Handler):
	def get(self):						  

		self.render("stage_5.html")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', GuestBook),
    ('/stage_0', StageZeroHandler),
    ('/stage_1', StageOneHandler),
    ('/stage_2', StageTwoHandler),
    ('/stage_3', StageThreeHandler),
    ('/stage_4', StageFourHandler),
    ('/stage_5', StageFiveHandler)
], debug=True)