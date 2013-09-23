# -*- coding: utf-8 -*-
from com.lish.namedisambiguation.checker import checker
from com.lish.pyutil import helper
from com.lish.pyutil.db import DB
from com.lish.pyutil.helper import ExceptionHelper
import threading
import time
from com.lish.namedisambiguation.settings import Settings


class GoogleResultDBUpdater():
	'''Select one item in db(GoogleResult) and check if two titles in 
	same page. and then update True or False in db
	'''

	def __init__(self):
		self.max_threads = 2
		self.google_checker = checker()
	
	def update(self):
		ResetTimestampThread().start()
		for i in range(0, self.max_threads):
			t = GoogleResultUpdateThread(self.google_checker)
			t.start()
			time.sleep(0.4)
			print 'start thread: ', i 

class ResetTimestampThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		while True:
			reset_sql = "update GoogleResult_mark set updatetime = null where google is null and CURRENT_TIMESTAMP - updatetime > 300 limit 20" 
			DB.shortcuts().execute(reset_sql)
			print "-- interval reset timestamp --"
			time.sleep(60)
	
class GoogleResultUpdateThread(threading.Thread):
	def __init__(self, google_checker):
		threading.Thread.__init__(self)
		self.settings = Settings.getInstance()
		self.google_checker = google_checker
		
	def run(self):
		try:
			while True:
				data = self.popTitlesFromDB()
				if data is not None:
					(id, title1, title2) = data
					google_boolean_result = self.google_checker.isInSamePage(title1, title2, self.settings.use_proxy)
					if google_boolean_result.result == True:
						self.setGoogleValue(id, 1, google_boolean_result.links);
					else:
						self.setGoogleValue(id, 0);
				time.sleep(0.5)
		except Exception, e:
			helper.ExceptionHelper.print_exec(e)
		print 'Main Thread Done'
	
	def popTitlesFromDB(self):
		sql = 'select id,titleA,titleB from GoogleResult_mark where google is null and updatetime is null  order by id limit 1' 
		try:
			conn = DB.pool().getConnection()
			cursor = conn.cursor()
			cursor.execute(sql)
			data = cursor.fetchall()
			
			if(data and len(data) == 1):
				(id, title1, title2) = data[0]
				updateSQL = 'update GoogleResult_mark set updatetime = CURRENT_TIMESTAMP where id = %s' 
				cursor.execute(updateSQL, (id,))
				return id, title1, title2
		except Exception, e:
			ExceptionHelper.print_exec(e)
		finally:
			cursor.close()
			conn.close()

	def setGoogleValue(self, id, google_value, links=''):
		sql = 'update GoogleResult_mark set google = %s, url = %s where id = %s limit 1'  
		if links is None:
			linkstr = ''
		else:
			linkstr = '\n'.join(links)
			
		try:
			conn = DB.pool().getConnection()
			cursor = conn.cursor()
			cursor.execute(sql, (google_value, linkstr, id,))
		except Exception, e:
			ExceptionHelper.print_exec(e)
		finally:
			cursor.close()
			conn.close()
		print '[UPDATE]id:%s, Value:%s' % (id, google_value)
			

if __name__ == '__main__':
#	pool = DB.initpool("localhost", "arnet_local", "root", "root")
	DB.initpool("10.1.1.209", "arnet_int2", "root", "root")
#	GoogleResultDBUpdater().popTitlesFromDB()
#	GoogleResultUpdateThread().run()
	GoogleResultDBUpdater().update()
#	ResetTimestampThread().run()



