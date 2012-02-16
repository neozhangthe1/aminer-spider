# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.models import Publication
from com.lish.ajia.util.db import DB, ConstantsDAO
from com.lish.pyutil.helper import ExceptionHelper
import MySQLdb
import sys


class PublicationDao:
	'''PublicationDAO
	'''
	
	def __init__(self):
		pass


	def getTotalCount(self):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select count(*) from publication")
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise


	def getLeftCount(self, generation):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select count(*) from publication p \
					where p.u_citation_gen is null or p.u_citation_gen < %s", generation) 
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise

		
	def getPublicationByPerson(self, personId, gen):
		'''Get all publications of a person'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				cursor.execute('''select p.id, p.year, p.title, p.pubkey, p.jconf, p.authors, p.ncitation, p.u_citation_gen 
				from publication p left join na_author2pub a2p on p.id=a2p.pid 
				where (p.u_citation_gen < %s or p.u_citation_gen is null) and a2p.aid=%s''', (gen, personId))
				data = cursor.fetchall()
				pubs = []
				for id, year, title, pubkey, jconf, authors, ncitation, gen in data:
					pub = Publication(id, year, title, pubkey, jconf, authors, ncitation)
					pubs.append(pub)
				cursor.close()
				conn.close ()
				return pubs
			except Exception, e:
				ExceptionHelper.print_exec(e)
#				raise

	def getPublicationByConf(self, jconf_id):
		'''Get all publications of a person'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				cursor.execute('''select p.id, p.year, p.title, p.pubkey, p.jconf, p.authors, p.startpage,\ 
					p.endpage, p.ncitation, p.u_citation_gen 
					from publication p 
					where p.jconf=%s''', jconf_id)
				data = cursor.fetchall()
				pubs = []
				for id, year, title, pubkey, jconf, authors, startpage, endpage, ncitation, gen  in data:
					pub = Publication(id, year, title, pubkey, jconf, authors, ncitation)
					pub.startpage = startpage
					pub.endpage = endpage
					pubs.append(pub)
				cursor.close()
				conn.close ()
				return pubs
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
#				sys.exit(1)
			return data

	def getPersonPubCount(self, personId):
		'''Get all publication count of a person'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				cursor.execute('''select count(*) from publication p left join author2pub a2p on p.id=a2p.pid 
					where a2p.aid=%s''', personId)
				data = cursor.fetchone()
				cursor.close()
				conn.close ()
				return data[0]
			except MySQLdb.Connection.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
#				sys.exit(1)
			return data

	def batchUpdate(self, gen, pubs):
		'''batch update pubs, params is ((ncitation, gen, id),...)'''
		params = []
		for pub in pubs:
			params.append((pub.ncitation, gen, pub.id))
			
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				cursor.execute("Set AUTOCOMMIT = 0")
				data = cursor.executemany("update publication set ncitation=%s, u_citation_gen=%s where id=%s", params)
				conn.commit()
				cursor.execute("Set AUTOCOMMIT = 1")
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise
			return data

	def resetPersonPublicationUpdateGen(self, personId):
		''' set publication's update_gen to 0 of one person'''
		while True:
			try:
				sql = '''update publication p left join na_author2pub a2p on p.id = a2p.pid set p.u_citation_gen=0 where a2p.aid=%s '''
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				cursor.execute(sql, (personId))
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except MySQLdb.Error, e: #@UndefinedVariable
				ExceptionHelper.print_exec(e)
#				raise


class Author2PubDao:
	'''Authro2pub
	'''
	def save(self, aid, pid, position):
		'''Save author2pub'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				data = cursor.execute("insert into author2pub (aid,pid,position) values(%s,%s,%s)", (aid, pid, position))
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise
			return data



class PersonDao:
	'''Person DAO
	'''
	
	def getPersonTotalCount(self):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select count(*) from na_person")
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e: #@UndefinedVariable
				ExceptionHelper.print_exec(e)
#				raise

	def getPersonLeftCount(self, generation):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select count(*) from na_person p left join person_update_ext pe on p.id=pe.id \
				 where pe.u_citation_gen is null or pe.u_citation_gen < %s", generation)
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise
		
	def markPersonUpdateCitationFinished(self, personId, gen):
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				data = cursor.execute("update person_update_ext set u_citation_gen=%s where id=%s;",
					(gen, personId))
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except Exception, e:
				ExceptionHelper.print_exec(e)
#				raise
			return data

	def setPersonUpdateGeneration(self, personId, gen):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("update person_update_ext set u_citation_gen=%s where id=%s", (gen, personId))
				cursor.close()
				conn.close()
				return cursor.rowcount
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
#				sys.exit (1)

	# @deprecated
	def save(self, person):
		'''Save author2pub'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				data = cursor.execute("insert into person (id, fullname) values (%s,%s)", (person.id, person.name))
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise
			return data
	
	# @deprecated
	def savePerson(self, personId, personName):
		'''Save author2pub'''
		while True:
			try:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				data = cursor.execute("insert into person (id, fullname) values (%s,%s)", (personId, personName))
				cursor.close()
				conn.close ()
				return cursor.rowcount
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise
			return data



class dbs:
	'''Google Citation DB
	DB Operations of this task is all here.
	'''

	# constants
	genkey = "arnet.update.generation"

	def __init__(self):
		self.constantsDao = ConstantsDAO()

	#######################################################
	# ConstantDao - Mainly do some thing with constants.
	#
	#	ConstantsDB Structure:
	#		id, name, value, time
	#
	# Keys in ConstantsDB:
	#	 arnet.update.generation
	#
	#######################################################
	def getGeneration(self): return int(self.constantsDao.getConstant(self.genkey));

	def setGeneration(self, newGeneration):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("update constants set value=%s where name=%s", (newGeneration, self.genkey))
				cursor.close()
				conn.close()
				return cursor.rowcount
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
#				sys.exit (1)

	def getMaxGenerationInDB(self):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select max(u_citation_gen) from person_update_ext")
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e:
				ExceptionHelper.print_exec(e)
#				raise

	def getMinGenerationInDB(self):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select min(u_citation_gen) from publication")
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e: 
				ExceptionHelper.print_exec(e)
#				raise









