#!/usr/bin/python
import os
import unittest
import tempfile
import json
import linkshort
import flask
from linkshort import setupdb

app = flask.Flask(__name__)

class FlaskrTestCase(unittest.TestCase):
	
	clean_db = True

	def setUp(self):
		self.db_fd, linkshort.app.config['DATABASE'] = tempfile.mkstemp()
		print "temp database name: " + str(linkshort.app.config['DATABASE'])
		linkshort.app.config['TESTING'] = True
		self.app = linkshort.app.test_client()
		if (self.clean_db):
			print "Cleaning database"
			setupdb.setup(linkshort.app.config['DATABASE'])
			self.signup('test', 'test')
			rv = self.clean_db = False

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(linkshort.app.config['DATABASE'])
		
	def signup(self, username, password):
		return self.app.post('/signup', data=dict(
			username=username,
			password=password
		), follow_redirects=True)
		
	def login(self, username, password):
		return self.app.post('/login', data=dict(
			username=username,
			password=password
		), follow_redirects=True)

	def test_index(self):
		rv = self.app.get("/")
		assert "<title>Link Shortener</title>" in rv.data
		
	def test_signup_login(self):
		rv = self.login('wrong', 'bad')
		assert 'Error: Invalid username, password combo' in rv.data
		#This user has already been manually added to the DB
		rv = self.login('test', 'test')
		assert '<h1>Shorten a URL</h1>' in rv.data
		
	def test_links(self):
		self.url_dict = {}
		self.login('test', 'test')
		self.helper_test_short()
		self.helper_test_custom()
		self.helper_test_get_links()
		self.helper_test_routing()
		self.helper_test_data()
		
	################ Helpers ################ 
	def helper_test_short(self):
		for x in range(100):
			rv = self.app.get("/shorten?original_url=www.google.com")
			jsondata = json.loads(rv.data)
			assert jsondata["success"] == True
			short = jsondata["shortened_url"]
			original = jsondata["original_url"]
			self.url_dict[short] = original
			#arbitrary length for a short url, with only 100 links this should be reasonable
			#Note that the short url includes 'go/' at the beginning
			assert len(short) <= 6, "short url was too long: " + str(short)
		assert len(self.url_dict) == 100
	
	def helper_test_custom(self):
		rv = self.app.get("/shorten/custom?" \
				"original_url=www.google.com&custom_shortened_url=google")
		jsondata = json.loads(rv.data)
		assert jsondata["success"] == True, str(jsondata["error"])
		short = jsondata["shortened_url"]
		original = jsondata["original_url"]
		self.url_dict["go/" + str(short)] = original
		rv = self.app.get("/shorten/custom?" \
				"original_url=www.google.com&custom_shortened_url=google")
		jsondata = json.loads(rv.data)
		assert jsondata["success"] == False
		assert jsondata["error"] == "This short-link already exists, try again"
		
	def helper_test_get_links(self):
		rv = self.app.get("/getLinks")
		jsondata = json.loads(rv.data)
		assert jsondata["success"] == True, str(jsondata["error"])
		temp = {}
		for link in jsondata["content"]:
			short = link["shortened_url"]
			original = link["original_url"]
			temp[short] = original
		assert self.url_dict == temp
		
	def helper_test_routing(self):
		rv = self.app.get("/go/notvalid")
		assert "Sorry, this link does not exist" in rv.data
		for link in self.url_dict.keys():
			rv = self.app.get(link)
			assert 'window.location.href = "http://www.google.com";' in rv.data, str(rv.data)
		for x in range(9):
			rv = self.app.get("/go/google")
			assert 'window.location.href = "http://www.google.com";' in rv.data, str(rv.data)
			
	def helper_test_data(self):
		rv = self.app.get("/getLinks")
		jsondata = json.loads(rv.data)
		assert jsondata["success"] == True, str(jsondata["error"])
		for link in jsondata["content"]:
			redirs = link["num_redirects_last_day"]
			expected = 1
			if link["shortened_url"] == "go/google":
				expected = 10
			assert redirs == expected, "Number of redirects recorded was " \
								+ str(redirs) + ", should have been " + str(expected)
		
		
	

if __name__ == '__main__':
	unittest.main()