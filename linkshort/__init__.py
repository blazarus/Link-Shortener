import sys, traceback, time
from jinja2 import Template
from flask import *
import os
import sqlite3
import random
app = Flask(__name__)
app.secret_key = os.urandom(24)
URL_PATTERN = "go/"
DATABASE = "linksDB.sqlite"

def connect_db():
	return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
	g.db = connect_db()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('badRedirect.html'), 404

@app.route('/')
def index():
	print "session object: " + str(session)
	if 'username' in session:
		print "logged in as: " + escape(session['username'])
		return render_template('home.html')
	print "not logged in, redirecting to login page"
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
	print "in login()"
	error = None
	if request.method == 'POST':
		input_username = request.form['username']
		input_password = request.form['password']
		result = sql_get_user(input_username, input_password)
		if not result:
			error = "Invalid username, password combo"
			print error
		else:
			print 'Login success, ' + str(result[0]) + ", " + str(result[1])
			session['id'] = result[0]
			session['username'] = result[1]
			return render_template('home.html')
	return render_template('login.html', error=error)
	
def sql_get_user(input_username, input_password):
	try:
		curs = g.db.execute("select id, username from users where username=? and password=?",\
													(input_username, input_password))
		result = curs.fetchone()
		print "query result: " + str(result)
		return result
	except Exception:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
		                              limit=4, file=sys.stdout)
	

@app.route('/signup', methods=['POST'])
def signup():
	print "in signup()"
	error = None
	if request.method == 'POST':
		input_username = request.form['username']
		input_password = request.form['password']
		if input_username == "Username" or input_username == "": #This is the default, dont' sign this person up
			error = "Must provide a valid username address"
		elif input_username and input_password:
			user_exists = sql_user_exists(input_username
			if user_exists:
				error = 'User with this username already exists'
				print error
			else:
				result = sql_add_user(input_username, input_password)
				#successfully signed up user, set session params and go to home page
				print "Successfully signed up user"
				session['id'] = result[0]
				session['username'] = result[1]
				return render_template('home.html')
	return render_template('login.html', error=error)
	
def sql_user_exists(input_username):
	print input_username
	curs = g.db.execute("select id, username from users where username=?",(input_username,))
	result = curs.fetchall()
	print "query result: " + str(result)
	return len(result) != 0
	
def sql_add_user(input_username, input_password):
	curs = g.db.execute("insert into users (username, password) values (?,?);",\
												(input_username, input_password))
	g.db.commit()
	curs.execute("select id, username from users where username=?",(input_username,))
	result = curs.fetchone()
	print "query result: " + str(result)
	return result
	
@app.route('/shorten')
def shorten():
	print "in shorten()"
	print "session object: " + str(session)
	error = None
	try:
		original_url = request.args['original_url']
		user_id = session['id']
		print "user id: " + str(user_id)
		short_suffix = shorten_url(original_url)
		sql_add_link(original_url, short_suffix, user_id)
		shortened = URL_PATTERN + short_suffix
		return jsonify(success=True, original_url=original_url, shortened_url=shortened)
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
		                              limit=4, file=sys.stdout)
		error="Could not shorten this url"
		return jsonify(success=False,error=error)
	
@app.route('/shorten/custom')
def shorten_custom():
	print "in shorten_custom()"
	error = None
	try:
		original = request.args['original_url']
		custom = request.args['custom_shortened_url']
		user_id = session['id']
		print "user id: " + str(user_id)
		if not sql_shorturl_exists(custom):
			sql_add_link(original, custom, user_id)
			print "Adding custom link was successful"
			return jsonify(success=True, original_url=original, shortened_url=custom)
		else:
			print "This short-link already exists, try again"
			error="This short-link already exists, try again"
			return jsonify(success=False,error=error)
	except:
		print "There was an exception in shorten_custom()"
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
		                              limit=4, file=sys.stdout)
		error="Could not shorten this url"
		return jsonify(success=False,error=error)
	
	
#Will add random characters until it finds a shortened url not already being used
def shorten_url(original_url):
	shortened = ""
	chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',\
		'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',\
		'-','_',0,1,2,3,4,5,6,7,8,9]
	keep_trying = True
	while keep_trying:
		rand = random.randint(0,63)
		shortened += str(chars[rand])
		if not sql_shorturl_exists(shortened):
			keep_trying = False
	print "Suffix for shortened URL: " + shortened
	return shortened
	
def sql_shorturl_exists(short):
	curs = g.db.execute("select id from links where shortened_url=?",(short,))
	result = curs.fetchall()
	print "query result from checking if shortURL already exists: " + str(result)
	return len(result) != 0
	
def sql_add_link(original_url, shortened, user_id):
	curs = g.db.execute("insert into links (original_url, shortened_url, user) values (?,?,?)",\
												(original_url, shortened, user_id))
	g.db.commit()
	result = curs.fetchall()
	print "query result after inserting the link: " + str(result)
	return result
	
@app.route('/getLinks')
def get_links():
	print "in get_links()"
	error = None
	try:
		user_id = session['id']
		result = sql_get_links(user_id)
		link_list = []
		for r in result:
			since_time = get_datetime_yesterday()
			data = sql_get_link_data(r[0], since_time)
			print "redirect data: " + str(data)
			link = {"original_url":r[1], "shortened_url":URL_PATTERN+str(r[2]),\
			 		"date_created":r[4], "num_redirects_last_day":len(data)}
			link_list.append(link)
			print "Link: " + str(link)
		return jsonify(success=True,content=link_list)
	except Exception:
		print "Caught an exception while trying to get links: "
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
		                              limit=4, file=sys.stdout)
		error="There was a problem retrieving your links"
		return jsonify(success=False,error=error)

#These methods return the unix epoc time		
def get_datetime_yesterday():
	#number of seconds in a day
	return time.time() - 86400
	
	
def sql_get_links(user_id):
	curs = g.db.execute("select id, original_url, shortened_url, user, created \
						from links where user=? order by created asc",(user_id,))
	result = curs.fetchall()
	print "query result from getting all links for user: " + str(result)
	return result
	
#Returns list of dictionaries, each dictionary representing a recorded redirect
#since the inputted parameter
def sql_get_link_data(link_id, since_time):
	curs = g.db.execute("select link, time \
						from redirects where link=? and time>=datetime(?, 'unixepoch') order by time asc;",(link_id,since_time))
	result = curs.fetchall()
	print "query result from getting link data: " + str(result)
	redir_list = []
	for r in result:
		redir_list.append({'link':r[0],'time':r[1]})
	return redir_list
	
	
@app.route('/' + URL_PATTERN + '<suffix>')
def route(suffix):
	try:
		print "Short suffix: " + suffix
		result = get_redirect_url(suffix)
		link_id = result['id']
		redir_url = result['original_url']
		if redir_url:
			print "Redirecting to: " + str(redir_url)
			sql_record_redirect(link_id)
			if redir_url[:7] != "http://":
				redir_url = "http://" + str(redir_url)
				print "Redirecting to: " + str(redir_url)
			return render_template('redirect.html', redir_url = redir_url)
		else:
			print "Problem redirecting to expanded URL from suffix: " + suffix
			return render_template('badRedirect.html')
	except Exception:
		print "Caught an exception while trying to redirecting to expanded URL from suffix: "
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback,
		                              limit=4, file=sys.stdout)
		return render_template('badRedirect.html')

#Returns dictionary with id and original_url for that shortened url
def get_redirect_url(short):
	curs = g.db.execute("select id, original_url, shortened_url from links where shortened_url=?",(short,))
	result = curs.fetchone()
	print "query result for getting expanded url from short url: " + str(result)
	return {'id':result[0],'original_url':result[1]}
	
def sql_record_redirect(link_id):
	curs = g.db.execute("insert into redirects (link) values (?)",\
												(link_id,))
	g.db.commit()
	result = curs.fetchone()
	print "query result inserting a redirect record: " + str(result)
	return True
