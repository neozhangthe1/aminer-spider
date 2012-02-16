# -*- coding: utf-8 -*-
import datetime


class ProxyModel:
	def __init__(self, ip, port, type):
		self.ip = ip
		self.port = port
		self.type = type
		self.location = None
		self.validate_date = None

		'''
		这个值的作用：PriorityQueue的值。调整策略：
		值为0-100，默认值为50. 当第一次访问不通, 加30分钟不能访问的时间。错误计数＋1
		'''
		self.value = 50				# PriorityQueue Sort Value.
		self.invalid_time = None	# Wait time, don't use this proxy before this time.
		self.cnt_failed = 0
		self.cnt_success = 0
		self.cnt_banned = 0

	def take_a_rest(self, seconds=0, minutes=0):
		self.invalid_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds, minutes=minutes)
		#print "%s - %s = %s" % (datetime.now(), self.invalid_time, datetime.now() > self.invalid_time)

	def isInRest(self):
		if self.invalid_time is None: return False
		if datetime.datetime.now() < self.invalid_time:
			return True
		return False

	def __str__(self):
		return "proxy(%s>%s:%s)" % (self.type, self.ip, self.port)

	def __cmp__(self, other):
		if not isinstance(other, ProxyModel):
			return (-1)
		return cmp(self.value, other.value)

	def to_line(self):
		return "%s:%s\t%s\t%s\t%s\t%s" % (self.ip, self.port, self.type, self.value, self.location, self.validate_date)


class ProxyKey:
	def __init__(self, ip, value):
		self.ip = ip
		self.value = 50

	def __str__(self):
		return "proxykey(%s, %s)" % (self.ip, self.value)

	def __cmp__(self, other):
		if not isinstance(other, ProxyKey):
			return (-1)
		return cmp(self.value, other.value)

