# -*- coding: utf-8 -*-
import threading
import time
import datetime

from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.pubmatcher import PubMatcher
from com.lish.pyutil.helper import ExceptionHelper


#
# Thread Implementation of PersonProcessThread
#
class PubProcessThread(threading.Thread):
	''' Thread Implementation of processing Publication
	'''

	def __init__(self, extractorInstance):
		threading.Thread.__init__(self)

		self.extractor = extractorInstance
		self.store = self.extractor.store

		#self.pub = None	# set this and start.
		self.ask_to_stop = False
		self.last_action = datetime.datetime.now()

	def mark(self):
		self.last_action = datetime.datetime.now()
		
	def check_idle(self):
		"not work for 1 hour"
		return (datetime.datetime.now() - self.last_action).seconds < 3600
		
	def stop(self):
		self.ask_to_stop = True

	def run(self):
		while self.extractor.running and not self.ask_to_stop:
			self.mark()
			self.extractor.wait_for_pause() # wait if paused
			
			query, used_pubs = self.store.getFromPubQueue()
			if used_pubs is None or len(used_pubs) == 0:
				print "[ERROR][t_pub_process:%s] Queue is Empty.(%s,%s)" % (self.name, query, used_pubs)
				time.sleep(10)
				continue
			self.extractor.wait_for_pause() # wait again

			with self.extractor.busy_semaphore_lock: 
				self.extractor.busy_semaphore += 1
				self.extractor.busy_pub_semaphore += 1

			pubs_found = None
			pubs_notfound = None
			try:
				all_models = Extractor.getInstance().getNodesByPubs(used_pubs)
				if all_models is not None:
					(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(used_pubs, all_models)
					if pubs_found is None or pubs_notfound is None:
						print '[ERROR][-/-] some pubs, pubs_found is None or pubs_notfound is None, return'
						return
					print "{+P}[%s/%s] [found/notfound] pub, query[%s]." % (len(pubs_found), len(pubs_notfound), query)
				else:
					pubs_notfound = used_pubs
			except Exception, e:
				ExceptionHelper.print_exec(e)
				print '-------------------------------------------------------'
				print 'query:', 	query
				print 'all_models', all_models
				print 'used_pubs', used_pubs
				print '-------------------------------------------------------'
				return
			finally:
				with self.extractor.busy_semaphore_lock: 
					self.extractor.busy_semaphore -= 1
					self.extractor.busy_pub_semaphore -= 1
			
			if pubs_found is not None:
				for pub in pubs_found:
					self.store.putToPubdbcache(pub)
					print "{-P}[%4s] %s" % (pub.ncitation, pub.title)

			if pubs_notfound is not None:
				for pub in pubs_notfound:
#					pub.ncitation = -1
					self.store.putToPubdbcache(pub)
					print "{-P}[%4s] %s" % (pub.ncitation, pub.title)

		print "$thread/%s:> Stopped." % self.name
		
	def runOriginal(self):
		while self.extractor.running and not self.ask_to_stop:
			self.mark()
			self.extractor.wait_for_pause() # wait if paused
#			url, url_without_author, pubs_in_url = store.getFromPubQueue() # get url and pubs
			
			query, used_pubs = self.store.getFromPubQueue() # get url and pubs
			if used_pubs is None or len(used_pubs) == 0:
				print "[ERROR][t_pub_process:%s] Queue is Empty.(%s,%s)" % (self.name, query, used_pubs)
				time.sleep(10)
				continue
			self.extractor.wait_for_pause() # wait again

			with self.extractor.busy_semaphore_lock: 
				self.extractor.busy_semaphore += 1
				self.extractor.busy_pub_semaphore += 1

			pubs_found = None
			pubs_notfound = None
			try:
				all_models = Extractor.getInstance().getNodesByPubs(used_pubs)
				if all_models is not None:
					(pubs_found, pubs_notfound) = PubMatcher.getInstance().matchPub(used_pubs, all_models)
					if pubs_found is None or pubs_notfound is None:
						print '[ERROR][-/-] some pubs, pubs_found is None or pubs_notfound is None, return'
						return
					print "{+P}[%s/%s] [found/notfound] pub, query[%s]." % (len(pubs_found), len(pubs_notfound), query)
				else:
					pubs_notfound = used_pubs
			except Exception, e:
				ExceptionHelper.print_exec(e)
				print '-------------------------------------------------------'
				print 'query:', 	query
				print 'all_models', all_models
				print 'used_pubs', used_pubs
				print '-------------------------------------------------------'
				return
			finally:
				with self.extractor.busy_semaphore_lock: 
					self.extractor.busy_semaphore -= 1
					self.extractor.busy_pub_semaphore -= 1
			
			if pubs_found is not None:
				for pub in pubs_found:
					self.store.putToPubdbcache(pub)
					print "{-P}[%4s] %s" % (pub.ncitation, pub.title)

			if pubs_notfound is not None:
				for pub in pubs_notfound:
#					pub.ncitation = -1
					self.store.putToPubdbcache(pub)
					print "{-P}[%4s] %s" % (pub.ncitation, pub.title)

		print "$thread/%s:> Stopped." % self.name
