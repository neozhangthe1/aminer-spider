# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "[__trash_code__.py] Thursday, 2011-11-17 22:45:34"
'''

#from runner.proxy import proxy
from com.lish.ajia.googlescholar import models
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.models import Person
from com.lish.ajia.util.db import DB
from com.lish.pyutil.DataUtil import GoogleDataCleaner
from com.lish.pyutil.helper import ExceptionHelper
from settings import Settings
import editdist
import os
import re
import time

class PubMatcher:

	# @deprecated: too strict, deprecated at 2010-10-27		
	def matchAuthors_strict_v1(self, google_author_string, authors, debug_output=False):
		'''If the two author string matched, return True
		@return: boolean
		@param: 
		- google_author_string, e.g.
			… DeSmedt, W Du, W Kent, MA Ketabchi, WA … - …, 1991 - doi.ieeecomputersociety.org
			R Ahmed, P DeSmedt, W Du, W Kent, MA … - …, 1991 - doi.ieeecomputersociety.org
			 
		- authors, e.g.
			Rafi Ahmed,Philippe De Smedt,Weimin Du,William Kent,Mohammad A. Ketabchi,Witold Litwin,Abbas Rafii,Ming-Chien Shan

		'''
		ignore_sign = '&hellip;'
#		ignore_sign = '…'

		# process google part
		mark = google_author_string.find(' - ')
		if mark != -1:
			google_author_string = google_author_string[:google_author_string.find(' - ')]
		google_author_string = re.sub("(<(.*?)>)", "", google_author_string)
		google_author_string = re.sub("[^A-Za-z0-9,\s%s]" % ignore_sign, "", google_author_string)
		google_author_string = re.sub("\\s+", " ", google_author_string)
		google_author_string = google_author_string.strip()

		ignore_left = google_author_string.startswith(ignore_sign)
		ignore_right = google_author_string.endswith(ignore_sign)
		compact_google_str = self.__trans_to_compact(google_author_string, ignore_sign)
#		print '--- ', compact_google_str

		# process author part
		compact_authors = self.__trans_to_compact(authors, ignore_sign);
#		print ',,, ', compact_authors

		# compare
		cmp_gc = ''
		cmp_db = ''
		if ignore_left and not ignore_right:  # and compact_authors.endswith(compact_google_str):
			cmp_gc = compact_google_str
			cmp_db = compact_authors[-len(compact_google_str):]
		elif not ignore_left and ignore_right:  # and compact_authors.startswith(compact_google_str):
			cmp_gc = compact_google_str
			cmp_db = compact_authors[:len(compact_google_str)]
		elif ignore_left and ignore_right and compact_authors.find(compact_google_str) != -1:
			return True  # todo
		elif not ignore_left and not ignore_right:  # and compact_authors == compact_google_str:
			cmp_gc = compact_google_str
			cmp_db = compact_authors
		else:
			return False

		edd = editdist.distance(cmp_gc, cmp_db)
		if edd > 0:
			if debug_output:
				print '[ERR] editdist for "%s" and "%s" is %s' % (cmp_gc, cmp_db, edd)
		if edd <= 2:
			return True


	def __trans_to_compact(self, str_authors, ignore_sign):
		authors = str_authors.split(',')
		compact = []
		for author in authors:
			author = author.strip()
			if author.startswith(ignore_sign):
				compact.append(author[-1:])
			elif author.endswith(ignore_sign):
				compact.append(author[0:1])
			else:
				compact.append("".join((author[:1], author[-1:])))
		return ",".join(compact)




#		
# not used.
#
class PersonWalkThrough:
	'''Walk through all persons marked with the given update_generation.
	Order by id. And Call processer for each person.
	'''
	def __init__(self, udpate_generation, processer=None, limit=None, fetch_size=100):
		self.processer = processer
		self.gen = udpate_generation
		self.limit = limit
		self.fetch_size = fetch_size

		self.sql = '''select p.id, p.fullname, 0 from person p \
			where (p.u_citation_gen is null or p.u_citation_gen < %s) and id>%s limit %s'''

	def walk(self):
		''' Walkthrough all persons in db. '''
		while True:
			try:
				lastId = -1
	#			while True:
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
#				raise
			return data

	def default_processer(self, person):
		print person;
		
		
		
		
