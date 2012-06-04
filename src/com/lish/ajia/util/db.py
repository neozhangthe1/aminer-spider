# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
elivoa | gmail.com
Time-stamp: "[db.py] Monday, 2012-02-06 18:41:42"
'''
from DBUtils.PooledDB import PooledDB
from com.lish.ajia.googlescholar.settings import Settings
import MySQLdb
import datetime
import sys


class DB(object):
	__db_pool = None
	__shortcuts = None

	@staticmethod
	def pool():
		if (DB.__db_pool is None):
			DB.__db_pool = DBPool()
		return DB.__db_pool

	@staticmethod
	def shortcuts():
		if (DB.__shortcuts is None):
			DB.__shortcuts = Shortcuts()
		return DB.__shortcuts

	def __init__(self):
		pass


class DBPool:

	def __init__(self):
		self.settings = Settings.getInstance()
		self.pool = PooledDB (
			MySQLdb, 3, 20,
			host=self.settings.db_host,
			user=self.settings.db_user,
			passwd=self.settings.db_passwd,
			port=self.settings.db_port,
			db=self.settings.db_database,
			maxusage=20
		)


	def getConnection(self):
		try:
			conn = self.pool.connection();
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		return conn

	def getNonPoolConnection(self):
		try:
			conn = MySQLdb.connect(
				host=self.settings.db_host,
				user=self.settings.db_user,
				passwd=self.settings.db_passwd,
				db=self.settings.db_database
			)
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		return conn


class Shortcuts:
	def __init__(self):
		pass

	def getOne(self, sql):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute(sql)
				row = cursor.fetchone()
				cursor.close()
				conn.close()
				return row[0]
			except MySQLdb.Error, e:
				print "DAOError %d: %s" % (e.args[0], e.args[1])

#
# Constants
#
class ConstantsDAO:
	def __init__(self):
		pass

	# get constants
	def getConstant(self, key):
		while True:
			try:
				conn = DB.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("select value from constants where name = %s ", key)
				row = cursor.fetchone()
				cursor.close()
				conn.close ()
				return row[0]
			except Exception, e:
				print e
				import traceback
				traceback.print_exc()
#				raise e
#				sys.exit (1)

	def setConstant(self, key, value):
		while True:
			try:
				conn = DBPool.pool().getConnection();
				cursor = conn.cursor()
				cursor.execute("update constants set value=%s,time=%s where name=%s",
							(value, datetime.datetime.now(), key))
				cursor.close()
				conn.close()
				return cursor.rowcount
			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])
#				sys.exit (1)


# Self Test
if __name__ == '__main__':
	try:
		c = ConstantsDAO()
		print c.getConstant("abc")
	except Exception, e:
		if e.__str__().find('Lost connection to MySQL') >= 0:
			print 'xxx'
			


