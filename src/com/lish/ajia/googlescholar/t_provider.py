# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.PersonUpdateTool import PersonUpdateTool, \
	PersonWalkThroughOrderByPubcount, PersonWalkThroughByGivenIDList
from com.lish.ajia.googlescholar.settings import Settings
from com.lish.pyutil.helper import ExceptionHelper
import sys
import threading
import time

#
# Thread Implementation of provide Persons
#
class ProviderThread(threading.Thread):
	'''Provider
	'''
	def __init__(self, extractorInstance, idList):
		threading.Thread.__init__(self)
		self.extractor = extractorInstance
		self.settings = Settings.getInstance()
		self.store = self.extractor.store
		self.personUpdater = PersonUpdateTool()
		self.idList = idList

	def run(self):
		try:
			data_run_out = False
			while not data_run_out:
				if self.idList is None or len(self.idList) == 0:
					walker = PersonWalkThroughOrderByPubcount(self.extractor.generation,
							processer=self.person_processer, fetch_size=100, fix_person_ext=True)
				else:
					walker = PersonWalkThroughByGivenIDList(self.extractor.generation,
							processer=self.person_processer, pids=self.idList, fix_person_ext=True);
				walker.walk()
				
				if self.personUpdater.isAllFinished(self.extractor.generation) or self.settings.byid:
					print "All data finished. Ended Provider."
					data_run_out = True
				print "All person walked, reload all"
				time.sleep(10)

			# reach here if all persons loaded
			self.extractor.waiting_to_finish = True
			print "$mgr/provider:> All person added to Queue, waiting for stop."
		except Exception, e:
			ExceptionHelper.print_exec(e)
			print '-' * 100
			print 'BIG Exception, and can\'t continue.'
			print '-' * 100
			sys.exit()
		finally:
			print '[INFO] ProviderThread Exit.'

	def person_processer(self, person):
		if person is None:
			return
		if person.id not in self.store.person_id_set:
			self.store.addToPersonQueue(person)
		else:
			time.sleep(1)
		#print "\t>>>>>>>> put [%s], qsize:%s" % (person, self.store.person_queue.qsize())
		time.sleep(0.1)

	def stop(self):
		print "$mgr:> provider thread ended."
		
		

		
