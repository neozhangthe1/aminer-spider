# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher
import threading
import datetime
from com.lish.pyutil.helper import ExceptionHelper

#
# Thread Implementation of PersonProcessThread
#
class PersonProcessThread(threading.Thread):
	'''
	 Thread Implementation of processing Person
	'''
	def __init__(self, extractorInstance):
		threading.Thread.__init__(self)

		self.extractor = extractorInstance
		self.store = self.extractor.store
		self.pubdao = PublicationDao()

		self.person = None	# set this and start.
		self.ask_to_stop = False
		self.last_action = datetime.datetime.now()

	def mark(self):
		self.last_action = datetime.datetime.now()
		
	def check_idle(self):
		"not work for 0.5 hour"
		return (datetime.datetime.now() - self.last_action).seconds < 1800
		
	def run(self):
		while self.extractor.running and not self.ask_to_stop:
			# acquire person
			self.mark()
			self.person = None
			self.extractor.wait_for_pause() # wait if paused
			self.person = self.store.getFromPersonQueue(timeout=self.extractor.mgr_interval)
			self.extractor.wait_for_pause() # wait again

			if self.person is not None:  # process person.
				with self.extractor.busy_semaphore_lock: 
					self.extractor.busy_semaphore += 1
					self.extractor.busy_person_semaphore += 1
				try:
					self.process_person()
				except Exception, e:
					ExceptionHelper.print_exec(e)
#					raise
					if self.person is not None:
						print "[ERROR] < pub back person %s:" % self.person
						self.store.addToPersonQueue(self.person)
				finally:
					with self.extractor.busy_semaphore_lock: 
						self.extractor.busy_semaphore -= 1
						self.extractor.busy_person_semaphore -= 1

		print "***********************************"
		print "$thread/%s:> Stopped." % self.name
		print "***********************************"

	def stop(self):
		self.ask_to_stop = True

	def process_person(self):
		''' real logic of process person '''
		# all pubs need to update citation number.
		# totalPubCount = self.pubdao.getPersonPubCount(self.person.id)

		pubs = self.pubdao.getPublicationByPerson(self.person.id, self.extractor.generation)

		if pubs is not None and len(pubs) == 0:
			self.store.markPersonFinished(self.person)
			print "[*] Mark Person as Finished '%s'." % self.person
			return

		print "$Ex/get:> person '%s' has %d papers to crawl" % (self.person.names, len(pubs))
		# by crawlByPerson, a lot of publication maybe found and update.
		pubs_found = None
		pubs_notfound = None
		if len(pubs) > 4:
			all_models = Extractor.getInstance().getNodesByPersonName(self.person.names)
			if all_models is not None:
				print "=" * 100
				(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(pubs, all_models)
				if pubs_found is None or pubs_notfound is None:
					print "[ERROR][-/-] person '%s', pubs_found is None or pubs_notfound is None, return"\
						% self.person
					return
				print "{+A}[%s+%s=%s] Download by page, [found + not_found = total], person '%s'." % (
					len(pubs_found), len(pubs_notfound), len(pubs_found) + len(pubs_notfound), self.person
				)
			else:
				pubs_notfound = pubs
		else:
			pubs_found = []
			pubs_notfound = pubs

		if pubs_found is not None:
			for pub in pubs_found:
				self.store.putToPubdbcache(pub)
				print "{-A}[%4s] %s" % (pub.ncitation, pub)
	
		if pubs_notfound is not None:
			for pub in pubs_notfound:
				self.store.putToPubCache(self.person, pub)
