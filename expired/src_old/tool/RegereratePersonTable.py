# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG • elivoa@gmail.com
Time-stamp: "root 2009/07/24 13:04:13"
'''

#from runner.proxy import proxy
from google_citation.DataWalker import PersonWalker, PublicationWalker
from google_citation.dbs import dbs, Author2PubDao, PersonDao
from runner.DB import DB
import MySQLdb
import sys

class RegereratePersonTable:
	'''Regenerate Person related table, sute for small amount of data.
	author gb<elivoa@gmail.com> v0.1.0'''

	def __init__(self):
		print "Rebuild Person Related Table."

		# datas
		global persons, author2pubs
		persons = {}
		author2pubs = {}
		self.personId = 0

		global db, a2pdao, personDao
		db = DB()
		a2pdao = Author2PubDao()
		personDao = PersonDao()

	def regenerate(self):
		# clear person, clear person_ext, clear author2pub
		self.truncateTables()
		self.loadData()

	def truncateTables(self):
		conn = db.getConnection()
		cursor = conn.cursor()
		cursor.execute("truncate table person")
		#cursor.execute("truncate table person_ext")
		cursor.execute("truncate table author2pub")
		cursor.close()
		conn.close()

	def loadData(self):
		walker = PublicationWalker(self.person_processer)
		walker.walk()

	def person_processer(self, pub):
		print "--processer--", pub
		authorList = pub.authors.split(",")
		position = 0
		for authorName in authorList:
			position = position + 1
			#get personId
			if(authorName in persons):
				authorId = persons[authorName]
			else:
				self.personId = self.personId + 1
				authorId = self.personId
				persons[authorName] = authorId
				personDao.savePerson(authorId, authorName)

			#update author2pub ## directly save author2pub
			a2pdao.save(authorId, pub.id, position)


#######################################################
# Self Test 
#######################################################		
if __name__ == '__main__':
	print "====== Start Regenerate Person table ======"
	inst = RegereratePersonTable()
	inst.regenerate()
	print "====== Program Finished ======"
