# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG • elivoa@gmail.com
Time-stamp: "[DataWalker.py] modified by gb on Monday, 2009-09-14 at 16:17:50 on vivo.local"
'''

#from runner.proxy import proxy
from com.lish.ajia.googlescholar.models import Person, Publication
from com.lish.ajia.util.db import DB
from com.lish.pyutil.helper import ExceptionHelper
import MySQLdb
import sys
import time


# @Deprecated moved to PersonUpdateTool
class PersonWalker_citation_orderby_pubcount:
	'''Notice! Now It's not sorted by pubcount, use nature order.
	'''
	def __init__(self, gen, processer=None, limit=None, fetch_size=1000):
		self.processer = processer
		self.gen = gen
		self.limit = limit
		self.fetch_size = fetch_size

#		self.sql = '''select p.id, p.fullname, pe.pubcount from person p right join person_ext pe on p.id=pe.person_id 
#		where (pe.u_citation_gen is null or pe.u_citation_gen < %s) order by pe.pubcount desc limit %s'''

		self.sql = '''select p.id, p.fullname, 0 from person p \
			where (p.u_citation_gen is null or p.u_citation_gen < %s) and id>%s limit %s'''
#		self.sql = '''select p.id, p.fullname, 0 from person p \
#			where (p.u_citation_gen is null or p.u_citation_gen < %s) and id < 6 limit %s'''  # debug

	def walk(self):
		''' Walkthrough all persons in db. '''
		try:
			lastId = -1
			while True:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				#print self.sql % (self.gen, start_id, self.limit)
				cursor.execute(self.sql, (self.gen, lastId, self.fetch_size))
				data = cursor.fetchall()
				print "&-walker-:> walk person(citation) %s items" % cursor.rowcount
				if cursor.rowcount == 0:
					break
				id = 0
				for id, fullname, pubcount in data:
					lastId = id
					person = Person(id, fullname, pubcount)
					self.processer(person)
				cursor.close()
				conn.close()
				# sleep 10 minutes next loop
				time.sleep(20)

		except MySQLdb.Error, e: #@UndefinedVariable
			ExceptionHelper.print_exec(e)
			raise
		return data

	def default_processer(self, person):
		print person;


class PersonWalker_citation:
	'''PersonWalker python version
	author gb<elivoa|gmail.com> v0.1.0'''

	def __init__(self, gen, processer=None, limit=None, fetch_size=10):
		self.processer = processer
		self.gen = gen
		self.limit = limit
		self.fetch_size = fetch_size

		self.sql = '''select p.id, p.fullname from person p right join person_update_ext pe on p.id=pe.person_id 
		where (pe.u_citation_gen is null or pe.u_citation_gen < %s) and p.id > %s limit %s'''

	def walk(self):
		''' Walkthrough all persons in db. '''
		try:
			start_id = 0
			while True:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				#print self.sql % (self.gen, start_id, self.limit)
				cursor.execute(self.sql, (self.gen, start_id, self.fetch_size))
				data = cursor.fetchall()
				print "&-walker-:> walk person(citation) %s items" % cursor.rowcount
				if cursor.rowcount == 0:
					break
				id = 0
				for id, fullname in data:
					person = Person(id, fullname)
					self.processer(person)
				start_id = id
				cursor.close()
				conn.close()

		except MySQLdb.Error, e: #@UndefinedVariable
			print "Error %d: %s" % (e.args[0], e.args[1])
			raise
		return data

	def default_processer(self, person):
		print person;


#######################################################
# PersonWalker - Python version.
#	now support person id and fullname.
#######################################################
class PersonWalker:
	'''PersonWalker python verson
	author gb<elivoa@gmail.com> v0.1.0'''

	def __init__(self, processer=None, sql_condition=None, limit=None, fetch_size=10):
		self.processer = processer
		self.sql_condition = sql_condition # this or others.
		self.limit = limit
		self.fetch_size = fetch_size
		self.replace_sql = None;
		self.replace_sql_params = None;

	def walk(self):
		''' Walkthrough all persons in db. '''
		try:
			# prepare sql and params
			sql_template = "%s %s %s"
			sql_param_sql = ""
			sql_param_condition = ""
			sql_param_limit = ""
			params = []
			if self.replace_sql:
				sql_param_sql = self.replace_sql + " and id > %s" # ugly
			else:
				sql_param_sql = "select id, fullname from person where %s %r"

			if self.sql_condition is not None:
				sql_param_condition = self.sql_condition

			if self.replace_sql:
				sql_param_sql = self.replace_sql + " and id > %s" # ugly

			# params
			if self.replace_sql_params is not None:
				if type(self.replace_sql_params).__name__ == 'list':
					params.extend(self.replace_sql_params)
				else:
					params.append(self.replace_sql_params)

			# sql_template_param
			if self.limit > 0:
				sql_param_limit = "limit %s"
				params.append(self.limit)

			sql = sql_template % (sql_param_sql, sql_param_condition, sql_param_limit)

			print sql
			sys.exit()
			conn = DB.pool().getConnection()

#			///////////////////////
#				Arrays.fill(hands, null);
#
#		int count = 0;
#		long nStartID = 0;
#		while (true) {
#			List < T > models = null;
#			try {
#				models = getModelsFrom(nStartID);
#			} catch (SQLException e) {
#				e.printStackTrace();
#			}
#			if (null == models || models.size() <= 0) {
#				break;
#			}
#
#			for (T model : models) {
#				nStartID = getID(model);
#				// true logic
#				foot.process(model);
#				if (stopWalker) {
#					System.out.println(" walker stoped.");
#					return;
#				}
#			}
#
#			// throw away
#			models = null;
#
#			// print
#			System.out.print("walk through " + count * DATA_FETCH_SIZE + " items.\r");
#			count + +;
#			// if ((count + + +1) % 10 == 0) {
#			// System.out.print("\t" + count + "\n");
#			// }
#		}
#		System.out.println("walk throuh complete. " + count * DATA_FETCH_SIZE + " items.");
#			///////////////////////



			cursor = conn.cursor()

			if(self.replace_sql):
				if self.replace_sql_params is not None:
					cursor.execute(self.replace_sql, self.replace_sql_params)
				else:
					cursor.execute(self.replace_sql)
			else:
				cursor.execute("select id, fullname from person where %s %r", (self.sql_condition, self.limit))

			data = cursor.fetchall()
			print "walk through %s items" % cursor.rowcount
			for id, fullname in data:
				person = Person(id, fullname)
				self.processer(person)
			cursor.close()
			conn.close ()
		except MySQLdb.Error, e: #@UndefinedVariable
			print "Error %d: %s" % (e.args[0], e.args[1])
			raise
		return data

	def default_processer(self, person):
		print person;


#######################################################
# PersonWalker - Python version.
#	now support person id and fullname.
#######################################################
class PublicationWalker:
	'''PublicationWalker python verson
	author gb<elivoa@gmail.com> v0.1.0'''

	def __init__(self, processer, sql_condition="1=1"):
		self.processer = processer
		self.sql_condition = sql_condition

		self.replace_sql = None;
		self.replace_sql_params = None;

		self.limit = "limit 5"

	def walk(self):
		''' Walkthrough all pubs in db. '''
		try:
			conn = DB.pool().getConnection()
			cursor = conn.cursor()
			if(self.replace_sql):
				if(self.replace_sql_params):
					cursor.execute(self.replace_sql, self.replace_sql_params)
				else:
					cursor.execute(self.replace_sql)
			else:
				# id, year, title, pubkey, jconf, authors, startpage, endpage, ncitation
				cursor.execute("select id, year, title, pubkey, jconf, authors, ncitation from publication where %s", self.sql_condition)
			data = cursor.fetchall()
			print "walk through %s items" % cursor.rowcount
			for id, year, title, pubkey, jconf, authors, ncitation in data:
				pub = Publication(id, year, title, pubkey, jconf, authors, ncitation)
				self.processer(pub)
			cursor.close()
			conn.close ()
		except MySQLdb.DoesNotExist, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			raise
		return data

	def default_processer(self, person):
		print person;

#######################################################
# Self Test PersonWalker - Python version.
#	now support person id and fullname.
#######################################################		
if __name__ == '__main__':
	walker = PersonWalker_citation(gen=11, limit=50, fetch_size=10)
	walker.processer = walker.default_processer
	walker.walk()




