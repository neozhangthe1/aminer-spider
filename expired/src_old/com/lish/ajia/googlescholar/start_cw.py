# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "[start_cw.py] Tuesday, 2011-11-15 23:03:45"

抓取scholar.google.com的数据

Dependency:
	py-editdist: http://www.mindrot.org/projects/py-editdist/

in pin query, title like 'Publication' will make search not available, remove all publications that only has 2 publications.

TODO:
 1. Use edit distance on title match, in person match, we can ignore 1-2 character not match. 
 	if only 1-2 character not matched and author list is matched, we can say this two paper is the same.
 	-- deprecated method, this method is not loose enough.
 	
 2. Search "Information Extraction from Case Low and Retrieval of Prior Cases by Partial Parsing and Query Generation"
 	in google scholar, we get this: Did you mean: "Information Extraction from Case Law and Retrieval of Prior Cases by Partial Parsing and Query Generation"
 	we can use edit distance on the two string, if less than 3, just click the link and match again.

'''
#from runner.proxy import proxy
from com.lish.ajia.googlescholar.daos import dbs, PersonDao, PublicationDao
from com.lish.ajia.googlescholar.models import Publication
from com.lish.ajia.googlescholar.pdfsaver import PDFLinkSaver
from com.lish.ajia.googlescholar.settings import Settings
from com.lish.ajia.googlescholar.store import Store
from com.lish.ajia.googlescholar.t_person_processer import PersonProcessThread
from com.lish.ajia.googlescholar.t_provider import ProviderThread
from com.lish.ajia.googlescholar.t_pub_processer import PubProcessThread
from com.lish.ajia.util.db import DB
from com.lish.ajia.util.web import HtmlRetriever
import MySQLdb
import datetime
import threading
import time

class GoogleScholarExtractor:
	'''Author gb<elivoa[AT]gmail.com> v0.4.0'''

	def __init__(self):
		print "Task: extract paper's citation from schooler.google.com.\n"
		self.settings = Settings.getInstance()
		self.debug = self.settings.debug

		# Configs
		self.mgr_interval 		 = 10		# seconds
		self.max_person_thread 	 = 2		# max threads used to extract person,
		self.max_pub_thread 	 = 2		# these 2 values can modified on the fly. diff in day or night

		# Threads and configurations
		self.t_mgr 				 = None 	# MgrThread(self)	# management thread, create
		self.t_provider 		 = None
		self.person_thread_pool	 = []		#= Queue.Queue(maxsize=self.max_person_thread)
		self.pub_thread_pool	 = []		#= Queue.Queue(maxsize=self.max_pub_thread)

		self.busy_semaphore 	 = 0 				# 用来监视是否所有的线程都处于Idle状态
		self.busy_semaphore_lock = threading.Lock() # 用来监视是否所有的线程都处于Idle状态

		# utils
		self.store				 = None

		# switchers & flags
		self.running 			 = True			# If False, threads will stop after current task.
		self.stopped			 = False		# If MGRThread can stop.
		self.pause 				 = False		# All works paused.
		self.waiting_to_finish 	 = False		# No additional data. all added to queue.
		self.num_report 		 = 0
		self.last_report_time	 = datetime.datetime.now()			# 上次Interval的时间

		self.restart_all_thread = False
		self.detect_exit_wait 	 = 0			# 当刚刚从pause模式退出来时，会有大量failed的任务，会导致立刻再次等待

		self.generation 		 = 0
		
		self.dao = dbs()
		self.personDao = PersonDao()
		self.pubDao = PublicationDao()

		if self.settings.save_pdflink:
			self.pdfcache = PDFLinkSaver.getInstance()

		# start
		self.determineGereration();

	# determine if the program could run or wait, or load continue status.
	def determineGereration(self):
		self.generation = self.dao.getGeneration()
		currentMinGen = self.dao.getMinGenerationInDB()
		currentMaxGen = self.dao.getMaxGenerationInDB()

		print '====================================================================='
		print " * Required update_generation is: [ %s ]." % (self.generation)
		print " * Current min update_generation is: [ %s ]." % (currentMinGen)
		
		# process generation
		if currentMinGen < self.generation == currentMaxGen or self.generation > currentMaxGen:
			print " * Not finished task, continue to finish current generation."
		elif self.generation == currentMinGen == currentMaxGen:
			print " * Just start new generation";
			self.generation = self.generation + 1
			self.dao.setGeneration(self.generation)
		else:
			print "=== Error: generation(%s) bigger than currentMinGen(%s)" % (self.generation, currentMinGen)
			self.generation = currentMaxGen
			self.dao.setGeneration(self.generation)

		# count task progress
		print " * Process NA Persons : %s." % self.reportPersonProgress(self.generation)
		print " * Process Publication: %s." % self.reportPublicationProgress(self.generation)
		print '====================================================================='


	def reportPersonProgress(self, udpate_generation):
		''' Return String that report progress of person.
		'''
		total = self.personDao.getPersonTotalCount()
		left = self.personDao.getPersonLeftCount(udpate_generation)
		progress = float(total - left) / total * 100.0 
		return "[%6.2f%%] %s/%s" % (progress, total - left, total)

	
	def reportPublicationProgress(self, udpate_generation):
		''' Return String that report progress of person.
		'''
		total = self.pubDao.getTotalCount()
		left = self.pubDao.getLeftCount(udpate_generation)
		progress = float(total - left) / total * 100.0
		return "[%6.2f%%] %s/%s" % (progress, total - left, total)


	def start(self):
		'''Extract Citation Multithread
		- Start main threads...
		- Manager Threads
		- Person Provider Thread
		- Publication Download Thread
		- ...
		'''
		self.store = Store(self.generation, self.mgr_interval)

		self.t_mgr = threading.Thread(target=self.mgrThreadBody, args=(), name='thread-mgr') # use method mgr.
		self.t_mgr.start()

		self.t_provider = ProviderThread(self,None)
		self.t_provider.start()

		# waiting to finish
		self.t_mgr.join()
		print "============ ALL END ============"


	def wait_for_pause(self):
		while self.pause:
			time.sleep(self.mgr_interval)

	#
	# Management Thread
	#
	def mgrThreadBody(self):
		'''Management Thread
		'''
		print "$init:> start mgr & provider."
		getter = HtmlRetriever.getInstance(self.settings.use_proxy)

		while self.running or not self.stopped:

			# interval seconds passed.
			interval_seconds = (datetime.datetime.now() - self.last_report_time).seconds
			if interval_seconds == 0: interval_seconds = 1
			self.last_report_time = datetime.datetime.now();

			# --------------------------------------------------------
			# strength by period of day. 
			hour = datetime.datetime.now().hour
			if hour <= 9: 					# 12h-9h
				self.max_person_thread = 25
				self.max_pub_thread = 75
			elif 22 <= hour:				# 9h-22h
				self.max_person_thread = 16
				self.max_pub_thread = 40
			else:							# 22h-24h
				self.max_person_thread = 22
				self.max_pub_thread = 60

			self.max_person_thread = 2
			self.max_pub_thread = 2
			# --------------------------------------------------------

			try:
				# save pdf link
				if self.settings.save_pdflink:
					self.pdfcache.flush()
			except e:
				print "ERROR: pdf link"
				print e

			# message
			message = None

			# 什么时候重启所有线程&进程。
			reload_all_thread = False
			if self.num_report % 1000 == 0:
				reload_all_thread = True
				message = "Kill & Restart All Thread."
			
			try:
				# Maintain Threads and get worker threads status.
				(num_persont_alive, num_pubt_alive) = self._maintainThreadPool(reload_all_thread)
			except e:
				print "ERROR: maintain threads and worker"
				print e

			try:
				# Finish Condition.
				if self._checkFinishCondition():
					self.running = False					# -> tell all threads finish.
					message = "MESSAGE! Send terminal signal to all worker thread."
			except e:
				print "ERROR: condition check"
				print e
				
			# if all worker threads stopped, mgrThread can stop.
			if num_persont_alive == 0 and num_pubt_alive == 0:
				self.stopped = True
				message = "Send terminal signal to mgr_thread."

			# check network and count 
			period_success_connection = getter.success_connection_count - getter.last_success_connection_count
			period_bad_connection = getter.bad_connection_count - getter.last_bad_connection_count
			total_connections = period_success_connection + period_bad_connection
			getter.last_success_connection_count = getter.success_connection_count
			getter.last_bad_connection_count = getter.bad_connection_count

			average_success_persecond = period_success_connection / float(interval_seconds)
			average_bad_persecond = period_bad_connection / float(interval_seconds)

			if False: # 是否Block模式，就是暂停整个程序
				if getter.detect_mode:
					if getter.detect_success_count > 3:
						getter.leave_detect_mode()
						self.detect_exit_wait = 1 # 刚出来时，下两轮都不要再进入block模式了。
				else:
					if total_connections * 0.9 < period_bad_connection:
						if self.detect_exit_wait > 0:
							print "---- waiting %s rounds ----" % self.detect_exit_wait
							self.detect_exit_wait -= 1
						else:
							getter.enter_detect_mode()

			try:
				# print report
				if not getter.detect_mode:
					str_report = None
					if not self.pause:
						self.num_report += 1
						str_report = self.num_report
					else:
						str_report = "paused"

					#--------------------------------------------------------------------------------
					# print interval string.
					report_strs = []
					report_strs.append("-" * 100)
					report_strs.append("\n")
					report_strs.append("$&mgr:%s(%s):> " % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str_report))
					report_strs.append("Person(%sT on %s), " % (num_persont_alive, self.store.person_queue.qsize()))
					report_strs.append("Pub(%sT on %s), " % (num_pubt_alive, len(self.store.pubmap)))
					report_strs.append("DBCache({{{ %s }}}), " % len(self.store.pub_db_cache))
					report_strs.append("T(busy/idle)(%s/%s), " % (self.busy_semaphore, self.max_person_thread + self.max_pub_thread - self.busy_semaphore))
					report_strs.append("\n")
					g = getter.success_connection_count
					b = getter.bad_connection_count
					t = g + b
					rate = 0
					if(t > 0):
						rate = g / float(t)
					report_strs.append("network(g+b=t)=(%s+%s=%s),rate=%.2f " % (g, b , t, rate))
					report_strs.append("interval-network(g+b=t)=(%s+%s=%s), " % (period_success_connection, period_bad_connection, total_connections))
					report_strs.append("avg:(g%.1f b%.1f in %s seconds.), " % (average_success_persecond, average_bad_persecond, interval_seconds))
					report_strs.append("\n")
					report_strs.append("time:(wait=%.2f, getlock=%.2f, get=%.2f)" % (self.store.ppt_wait, self.store.ppt_getlock, self.store.ppt_get))
					if message is not None:
						report_strs.append("\n")
						report_strs.append(message)
					report_strs.append("\n")
					report_strs.append(" * Process NA Persons : %s.\n" % self.reportPersonProgress(self.generation))
					report_strs.append(" * Process Publication: %s.\n" % self.reportPublicationProgress(self.generation))
					report_strs.append("-" * 100)
					report_strs.append("\n")

					print "".join(report_strs)
					#--------------------------------------------------------------------------------
			except e:
				print "ERROR: report error"
				print e

			try:
				# flush db cache
				self.store.flushDBCache()				# last flush cache to db.
				self.store.running = self.running		# pass main running thread to Store object.
			except e:
				print "ERROR: flush db cache"
				print e

			time.sleep(self.mgr_interval) 			# interval

		print "$mgr:> exit."

	def _checkFinishCondition(self):
		'''@return: true if all can stop.'''
		# Finish Condition.
		if self.waiting_to_finish and not self.pause: 		# Provider report finish and not paused.
			if self.busy_semaphore == 0: 					# all threads' status must be idle.
				if self.store.person_queue.empty() \
				  		and len(self.store.pubmap) == 0 \
				  		and len(self.store.pub_db_cache) == 0: 	# task queue must be empty
					left = self.pubDao.getLeftCount(self.generation)
					if left == 0:	# really finished.
						return True
		return False
	
	
	def _maintainThreadPool(self, reload_all_thread):
		'''
                Maintain ThreadPool, detect and restart, and set running threads on the fly.
		'''
		# Collect Information.
		num_persont_alive = 0
		num_pubt_alive = 0

                if reload_all_thread: # kill all thread first. 
			for idx_pub_t in range(0, self.max_pub_thread):
				t = None
				if len(self.pub_thread_pool) <= idx_pub_t:
					self.pub_thread_pool.append(t)
				else:
					t = self.pub_thread_pool[idx_pub_t]
				if t is not None:
					t.ask_to_stop = True
			self.pub_thread_pool = []

		# check and start all unstarted threads.
                idx_person_t = 0
		for idx_person_t in range(0, self.max_person_thread):
			t = None
			if len(self.person_thread_pool) <= idx_person_t:
                            self.person_thread_pool.append(t) # if len less than max size, increase with None.
			else:
                            t = self.person_thread_pool[idx_person_t]

			if t is None or not t.is_alive(): # if is None(new add) or dead.
				if self.running:
					t = PersonProcessThread(self)
					t.name = 'person-thread-' + str(idx_person_t)
					self.person_thread_pool[idx_person_t] = t
					t.start()
					num_persont_alive += 1
			else:
				num_persont_alive += 1

		# kill threads if needed.
		for i in range(idx_person_t, len(self.person_thread_pool) - 1): #@UnusedVariable
			t = self.person_thread_pool.pop(idx_person_t)
			t.stop()
			print "$mgr/thread:> kill thread %s" % t.name

		# check and start all unstarted threads.
                idx_pub_t = 0
		for idx_pub_t in range(0, self.max_pub_thread):
			t = None
			if len(self.pub_thread_pool) <= idx_pub_t:
				self.pub_thread_pool.append(t)
			else:
				t = self.pub_thread_pool[idx_pub_t]

			if t is None or not t.is_alive():
				if self.running:
					t = PubProcessThread(self)
					t.name = 'pub-thread-' + str(idx_pub_t)
					self.pub_thread_pool[idx_pub_t] = t
					t.start()
					num_pubt_alive += 1
			else:
				num_pubt_alive += 1

		# kill threads if needed.
		for i in range(idx_pub_t, len(self.pub_thread_pool) - 1): #@UnusedVariable
			t = self.pub_thread_pool.pop(idx_pub_t)
			t.stop()
			print "$mgr/thread:> kill thread %s" % t.name

		return (num_persont_alive, num_pubt_alive)


#######################################################
# Self Test
#######################################################
if __name__ == '__main__':
	print "====== Start Extract Citation ======"# -*- coding: utf-8 -*-
	inst = GoogleScholarExtractor()
	inst.start()


'''
Runner Platform Module: DB
KEG • elivoa@gmail.com
Time-stamp: "[DataWalker.py] modified by gb on Monday, 2009-09-14 at 16:17:50 on vivo.local"
'''

#from runner.proxy import proxy


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

