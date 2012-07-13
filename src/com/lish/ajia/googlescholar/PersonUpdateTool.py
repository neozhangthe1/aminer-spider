# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.models import Person
from com.lish.ajia.util.db import DB
from com.lish.pyutil.helper import ExceptionHelper
import MySQLdb
import time


class PersonUpdateTool:
	
	def __init__(self):
		pass
	
	
	def insertPersonExt(self, person_id, update_generation=0, pubcount=0):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("insert into person_update_ext(id,u_citation_gen,pubcount) values(%s,%s,%s)",
							 (person_id, update_generation, 0))
				cursor.close()
				conn.close()
				return cursor.rowcount
			except MySQLdb.Error, e: #@UndefinedVariable
				ExceptionHelper.print_exec(e)
#				raise
			
			
	def isAllFinished(self, update_generation):
		while True:
			conn = DB.pool().getConnection()
			cursor = conn.cursor()
			sql = "select \
				(select count(*) from na_person) as a, \
				(select count(*) from person_update_ext pe where pe.u_citation_gen=%s) as b \
			";
			cursor.execute(sql, (update_generation))
			data = cursor.fetchone()
			return data[0] == data[1]
			
			
			
class PersonWalkThroughOrderByPubcount:
	'''Walk through all persons marked with the given update_generation.
	Order by id. And Call processer for each person.
	'''
	
	def __init__(self, update_generation, processer=None, limit=None, fetch_size=100, fix_person_ext=True):
		self.processer = processer
		self.update_generation = update_generation
		self.limit = limit
		self.fetch_size = fetch_size
		self.fix_person_ext = fix_person_ext	# if person_ext not exist, create it.

		self.person_update_tool = PersonUpdateTool()

		self.sql = '''select p.id, p.names, pe.pubcount 
			from na_person p left join person_update_ext pe on p.id=pe.id \
			where (pe.u_citation_gen is null or pe.u_citation_gen < %s) and p.id>%s \
			limit %s'''
#			order by pe.pubcount desc limit %s'''
			
			
	def walk(self):
		''' Walk through all persons in database. '''
		""" this place put while true inner """
		while True:
			try:
				lastId = -1
				#former while true here
	#			while True:
				conn = DB.pool().getConnection()
				cursor = conn.cursor()
				#print self.sql % (self.gen, start_id, self.limit)
				cursor.execute(self.sql, (self.update_generation, lastId, self.fetch_size))
				data = cursor.fetchall()
				print "&[Walker]> walk through na_person, %s items" % cursor.rowcount
				if cursor.rowcount == 0:
					break
				id = 0
				for id, names, pubcount in data:
					# fix 
					if self.fix_person_ext and pubcount is None:
						self.person_update_tool.insertPersonExt(id, self.update_generation, pubcount)

					lastId = id
					namelist = names.split(",")
					for name in namelist:
						name = name.strip()
					# Call callback
					self.processer(Person(id, namelist, pubcount))
				cursor.close()
				conn.close()

			except MySQLdb.Error, e: #@UndefinedVariable
				ExceptionHelper.print_exec(e)
#				raise
			return data

	def default_processer(self, person):
		print person;



class PersonWalkThroughByGivenIDList:
	'''Walk through given id list. And Call processer for each person.
	'''
	
	def __init__(self, update_generation, processer=None, pids=[], fix_person_ext=True):
		self.processer = processer
		self.update_generation = update_generation
		self.pids = pids
		self.fix_person_ext = fix_person_ext	# if person_ext not exist, create it.
		self.person_update_tool = PersonUpdateTool()
		# self.sql = '''select p.id, p.names from na_person p where p.id in (%s)'''
		self.sql = '''select p.id, p.names, pe.id, pe.pubcount 
			from na_person p left join person_update_ext pe on p.id=pe.id \
			where (pe.u_citation_gen is null or pe.u_citation_gen < %s) and p.id in %s '''

	def walk(self):
		''' Get by pids. '''
		while True:
			try:
				print "&[Walker]> walk through na_person, BY_ID_LIST: %s items" % self.pids
				conn = DB.pool().getConnection()
				cursor = conn.cursor()

				# sql
				temp = []
				for item in self.pids:
					temp.append(str(item))
				inwhere = "".join(["(", ",".join(temp) , ")"])

				self.sql = '''select p.id, p.names, pe.id, pe.pubcount 
					from na_person p left join person_update_ext pe on p.id=pe.id \
					where (pe.u_citation_gen is null or pe.u_citation_gen < %s) and p.id in %s ''' % (self.update_generation, inwhere)
				cursor.execute(self.sql)
				data = cursor.fetchall()
				if cursor.rowcount == 0:
					return
				for pid, names, peid, pubcount in data:
					# fix 
					if self.fix_person_ext and peid is None:
						self.person_update_tool.insertPersonExt(pid, self.update_generation, pubcount)
					namelist = names.split(",")
					for name in namelist:
						name = name.strip()
					# Call callback
					self.processer(Person(pid, namelist, pubcount))
				cursor.close()
				conn.close()

			except MySQLdb.Error, e: #@UndefinedVariable
				ExceptionHelper.print_exec(e)
#				raise
			return data

	def default_processer(self, person):
		print person;






class PersonWalkThroughOrderByPubcountTest:
	def __init__(self):
		self.inst = PersonWalkThroughByGivenIDList(0, processer=self.testProcesser, pids=[123, 444, 555]);
#		self.inst = PersonWalkThroughOrderByPubcount(0, processer=self.testProcesser);
		self.updateTool = PersonUpdateTool()
		
	def testWalk(self):
		print "** Test PersonWalkThroughOrderByPubcount:"
		self.inst.walk()
		print "** ^o^nnmn TEST Done."
		
	def testProcesser(self, person):
		print person
	
	def testIsAllFinished(self):
		print self.updateTool.isAllFinished(3)
	
	
if __name__ == "__main__":
	test = PersonWalkThroughOrderByPubcountTest()
	test.testWalk()
#	test.testIsAllFinished()
	
	














