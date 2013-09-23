# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "root 2009/07/24 13:04:13"
'''
from DBUtils.PooledDB import PooledDB
import MySQLdb
import datetime
import sys
from com.lish.pyutil.helper import ExceptionHelper

# Copied from google scholar citation project.
# Change to common.
class DB(object):
	__db_pool = None
	__shortcuts = None

	@staticmethod
	def pool():
		return DB.__db_pool

	@staticmethod
	def initpool(host, database, user, passwd):
		DB.__db_pool = DBPool(host, database, user, passwd)
		return DB.__db_pool

	@staticmethod
	def shortcuts():
		if (DB.__shortcuts is None):
			DB.__shortcuts = Shortcuts()
		return DB.__shortcuts

	def __init__(self):
		pass


class DBPool:
	def __init__(self, host, database, user, passwd):
		self.pool = PooledDB (
			MySQLdb, 3, 10,
			host=host,
			user=user,
			passwd=passwd,
			db=database
		)


	def getConnection(self):
		try:
			conn = self.pool.connection();
		except MySQLdb.DoesNotExist, e:
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
		except MySQLdb.DoesNotExist, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		return conn


class Shortcuts:
	def __init__(self):
		pass

	def getOne(self, sql):
		try:
			conn = DB.pool().getConnection();
			cursor = conn.cursor()
			cursor.execute(sql)
			row = cursor.fetchone()
			cursor.close()
			conn.close()
			return row[0]
		except MySQLdb.DoesNotExist, e:
			print "DAOError %d: %s" % (e.args[0], e.args[1])
	
	def execute(self, sql, *args):
		try:
			conn = DB.pool().getConnection();
			cursor = conn.cursor()
			cursor.execute(sql, args)
			cursor.close()
			conn.close()
			return cursor.rowcount
		except Exception, e:
			ExceptionHelper.print_exec(e)

#
# Constants
#
class ConstantsDAO:
	def __init__(self):
		pass

	# get constants
	def getConstant(self, key):
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
			raise e
			sys.exit (1)

	def setConstant(self, key, value):
		try:
			conn = DBPool.pool().getConnection();
			cursor = conn.cursor()
			cursor.execute("update constants set value=%s,time=%s where name=%s",
						(value, datetime.datetime.now(), key))
			cursor.close()
			conn.close()
			return cursor.rowcount
		except MySQLdb.DoesNotExist, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)


# Self Test
if __name__ == '__main__':
	print "done"


