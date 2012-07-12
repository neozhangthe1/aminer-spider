# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "root 2009/07/24 13:04:13"
'''
from com.lish.ajia.googlescholar.daos import PersonDao, PublicationDao
from com.lish.ajia.googlescholar.extractor import Extractor
from com.lish.ajia.googlescholar.settings import Settings
from com.lish.pyutil.helper import ExceptionHelper
import Queue
import threading
import time


class Store:
	'''CrawlSrote - store items in memory.
	author gb<elivoa | gmail.com> v0.1.0
	@modify (Oct 09, 2009) 修改散装pub的crawl方式，一次访问能抓4个回来好像。 
	'''
	def __init__(self, generation, mgr_interval=5):
		self.settings = Settings.getInstance()
		self.debug = self.settings.debug

		self.gen = generation
		self.mgr_interval = mgr_interval

		self.person_queue 		 = Queue.Queue(maxsize=self.settings.person_cache_size)
		self.person_id_set	 	 = set([])	# sync with queue, quick contains using id. 

		self.pubmap		 		 = {}		# {id -> pub}
		self.person_pub_map		 = {}		# {person_id->[pub_id_list]} - person to pub_ids
		self.pub_db_cache 		 = {}

		self.pub_lock			 = threading.Lock()
		self.pub_dbcache_lock 	 = threading.RLock()

		self.running = True #sync ed with main running flag in mgr_interval_thread
		self.blocked_pub_t 		 = 0

		# time sum
		self.ppt_wait = 0
		self.ppt_getlock = 0
		self.ppt_get = 0

		self.person_dao = PersonDao()
		self.pub_dao = PublicationDao()

	
	def addToPersonQueue(self, person):
		if person is not None:
			self.person_queue.put(person, True)
			self.person_id_set.add(person.id) 

	def getFromPersonQueue(self, timeout=2):
		person = None
		try:
			person = self.person_queue.get(True, timeout);
		except Queue.Empty:
			print "[INFO][t_person_process] person_queue is empty. wait for %s seconds." % timeout
			return None
		if person is not None:
			self.person_id_set.remove(person.id)
		return person
		


	def getFromPubQueue(self):
		''' 从Store中的零散Pub中取下一个要抓取的pub组合
		(取几个pub拼成一个最长字符串用来抓取)
		如果遇到错误，可能返回None.
		@return: (url, pubs[])
		'''
		print_verbose = False
		try:
			while self.running and len(self.person_pub_map) == 0:
				time.sleep(self.mgr_interval)
				
			self.blocked_pub_t += 1
			with self.pub_lock: # lock
				self.blocked_pub_t -= 1
				pub_candidates = [] 	# {pubId -> pub_with_person_name}, candidates
				person_invalid = []  	# mark person that not valid, delete later
				for personId, ids in self.person_pub_map.iteritems():
					# if person with no ids， del this person.
					if ids is None or len(ids) == 0:
						person_invalid.append(personId)
					else:
						valid_ids = 0
						for pubId in ids:
							if print_verbose: print('\tcandidate pub %s' % pubId)
							
							if pubId in self.pubmap:
								_pub = self.pubmap[pubId]
								if _pub:
									pub_candidates.append(_pub)
									valid_ids += 1
									
								if print_verbose: 
									print('\tcandidate pub %s of person %s.' % (_pub.title, personId))

							if len(pub_candidates) > 0:  # enough
								if print_verbose:
									print('\tcandidates enough, length %s ' % len(pub_candidates))
								break

						if valid_ids == 0:  # means all pub of this person is not valid. just delete this person.
							person_invalid.append(personId)

				for personId in person_invalid:
					for pubId in self.person_pub_map[personId]:
						if pubId in self.pubmap:
#							print "[store](getFromPubQueue):delete pub(%s,[%s]) from pubmap, cause person(%s) " % (pubId, self.pubmap[pubId].ncitation, personId)
							del self.pubmap[pubId]
							
					del self.person_pub_map[personId]
#					print "[store](getFromPubQueue):delete person(%s) from person_pub_map, now length %s " % (personId, len(self.person_pub_map))

				# return None if not available
				if pub_candidates is None or len(pub_candidates) == 0:
					print('\t[store] Cannot be here. empty candidates. return null.')
					return None, None

				# gen query
				query, used_pubs, nouse_pubs = Extractor.pinMaxQuery(pub_candidates[:1])
				for pub in used_pubs:
					del self.pubmap[pub.id] # delete pub.
#					print "[store](getFromPubQueue):delete pub(%s, [%s]) from pubmap, now length %s " % (pub.id, pub.ncitation, len(self.pubmap))
					
				# Save nouse_pubs to dbcache, waiting to write to db.
				nouse_pubs += pub_candidates[1:]
				if nouse_pubs:
					for pub in nouse_pubs:
						self.putToPubdbcache(pub);

				return query, used_pubs

		except Exception, e:
			ExceptionHelper.print_exec(e)
			print ('Exception occurred: %s. ' % e)


	def getFromPubQueueBack(self):
		''' 从Store中的零散Pub中取下一个要抓取的pub组合，（取几个pub拼成一个最长字符串用来抓取)
			如果遇到错误，可能返回None.
			@return: (url, pubs[])
		'''
		print_verbose = True
		try:
			# block if no pub items.
			start = time.time()
			while self.running and len(self.person_pub_map) == 0:
				time.sleep(self.mgr_interval)
			dur = (time.time() - start)
			#print "---------============----------- get 1 wait %.4s" % dur
			if print_verbose: print('TimeUsed:%.4s ms, ' % dur)

			start = time.time()
			self.blocked_pub_t += 1
			with self.pub_lock: # lock
				self.blocked_pub_t -= 1
				# count
				self.ppt_wait += dur
				#print "---------============----------- get 3 getlock %.4s" % (time.time() - start)
				self.ppt_getlock += (time.time() - start)
				start = time.time()

				# select candidates
				pub_candidates = [] 	# {pubId -> pub_with_person_name}, candidates
				person_invalid = []  	# mark person that not valid, delete later
				for personId, ids in self.person_pub_map.iteritems():
					# if person with no ids， del this person.
					if ids is None or len(ids) == 0:
						person_invalid.append(personId)
					else:
						valid_ids = 0
						for pubId in ids:
							if print_verbose: print('\tcandidate pub %s' % pubId)
							if pubId in self.pubmap:
								_pub = self.pubmap[pubId]
								if _pub is not None:
									pub_candidates.append(_pub)
									valid_ids = valid_ids + 1
									if print_verbose: 
										print('\tcandidate pub %s of person %s.' % (_pub.title, personId))

							if len(pub_candidates) > 0:  # enough
								if print_verbose: print('\tcandidates enough, length %s ' % len(pub_candidates))
								break

						if valid_ids == 0:  # means all pub of this person is not valid. just delete this person.
							person_invalid.append(personId)

				for personId in person_invalid:
					del self.person_pub_map[personId]
#					print "[store](line 123):delete person(%s) from person_pub_map, now length %s " % (personId, len(self.person_pub_map))

				# return None if not available
				if pub_candidates is None or len(pub_candidates) == 0:
					print('\t[ERR] Cannot be here. empty candidates. return null.')
					return None, None

				# gen query
				query, used_pubs, nouse_pubs = Extractor.pinMaxQuery(pub_candidates[:1])
				for pub in used_pubs:
					del self.pubmap[pub.id] # delete pub.
#					print "[store](line 134):delete pub(%s) from pubmap, now length %s " % (pub.id, len(self.pubmap))
					
				# Save nouse_pubs to dbcache, waiting to write to db.
				nouse_pubs += pub_candidates[1:]
				if nouse_pubs:
					for pub in nouse_pubs:
						self.putToPubdbcache(pub);

				return query, used_pubs

		except Exception, e:
			ExceptionHelper.print_exec(e)
			print ('Exception occurred: %s. ' % e)


	def putToPubCache(self, person, pub):
		"""将pub放到缓存等待再搜一遍"""
		if person is None: return
		
		try:
			if pub is not None and pub.id not in self.pubmap:
				with self.pub_lock:
					self.pubmap[pub.id] = pub
#					print "[store](putToPubCache):add pub(%s, [%s]) to pubmap, now length %s, with person(%s)" % (pub.id, pub.ncitation, len(self.pubmap), person.id)
					if person.id not in self.person_pub_map:
						self.person_pub_map[person.id] = []
#						print "[store](putToPubCache):add person(%s) to person_pub_map, now length %s " % (person.id, len(self.person_pub_map))
					person_pub_list = self.person_pub_map[person.id]
					person_pub_list.append(pub.id)
		except Exception, e:
			ExceptionHelper.print_exec(e)
			
	def putToPubdbcache(self, pub):
		''' 将下载好的Pub放到缓存，等待存库。
		同时，查看pub中有没有已经存在等待下载的，也同时删除掉。
		'''
		if pub is not None:
			if pub.id in self.pubmap:		# if exist in allidset
				del self.pubmap[pub.id]	# 	remove from queue
				print "[store](putToPubdbCache):delete pub(%s, [%s]) from pubmap, now length %s " % (pub.id, pub.ncitation, len(self.pubmap))
			self.pub_db_cache[pub.id] = pub		# add to dbcache.


	def markPersonFinished(self, person):
		''' 这个人的全部论文抓取完毕，标记为已经抓取'''
		if person is not None:
			self.person_dao.markPersonUpdateCitationFinished(person.id, self.gen)


	def flushDBCache(self):
		''' 将内存中缓存的已经抓取的pub批量存入数据库中。
		'''
		try:
			if len(self.pub_db_cache) == 0: return
			print 'start flush to db.'
			temp = [] # pubs[]
			for i in range(0, len(self.pub_db_cache)): #@UnusedVariable
				(k, v) = self.pub_db_cache.popitem() #@UnusedVariable
				if v:
					temp.append(v)
					print "%s updated to db." % v
			if len(temp) > 0:
				self.pub_dao.batchUpdate(self.gen, temp)
			print 'end flush to db.'
			# @todo: flush db cache
		except Exception, e:
			ExceptionHelper.print_exec(e)


