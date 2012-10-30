DEFAULT_DB_NAME = "linksDB.sqlite"


def setup(db_name):
	import sqlite3
	conn = sqlite3.connect(DEFAULT_DB_NAME)

	curs = conn.cursor()
	curs.execute('drop table if exists users;')
	curs.execute('create table users(\
					id integer primary key,\
					username string,\
					password string,\
					unique (username)\
					);')
	
	curs.execute('drop table if exists links;')
	curs.execute('create table links (\
					id integer primary key autoincrement,\
					original_url string,\
	 				shortened_url string,\
					user integer references users(id),\
					created timestamp default CURRENT_TIMESTAMP,\
					unique (shortened_url)\
	 );')

	curs.execute('drop table if exists redirects;')
	curs.execute('create table redirects (\
					id integer primary key autoincrement,\
					link integer references links(id) ,\
	 				time timestamp default CURRENT_TIMESTAMP\
	 );')
	conn.commit()
	print "Finished setting up database"

if __name__ == '__main__':
	setup(DEFAULT_DB_NAME)