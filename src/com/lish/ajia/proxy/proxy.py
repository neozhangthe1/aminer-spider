# -*- coding: utf-8 -*-
from Queue import PriorityQueue
from com.lish.ajia.proxy.proxyloader import *
from multiprocessing import Pipe, Manager
from multiprocessing.process import Process
from threading import Thread
import sys
from com.lish.pyutil.helper import ExceptionHelper

class ProxyMgr(Process):
	''' @todo: 采用pipe的形式管理Proxies，ProxyProcess中包括三个线程以及两个Pipe与MainProcess连接。
		Pipes：一个用来向外发送proxies，另一个用来接收返回的Proxies的执行状况，并更新状态。
		Threads：一个Thread是管理线程，用来启动和管理Proxy模块的运作。
				另外两个管理发送和接收反馈Proxy的Pipe。
		Proxies的存储：proxies必须线程安全，多个线程直接管理。可以不必进程安全，因为进程外不在直接访问proxies。
			Proxy用IP作为Key，可以支持用Key快速找到Proxy，以及一个策略来提取Proxy。
	'''

	#
	# Static
	# 
	__instance = None
	__parent_return_conn = None
	__processsafe_queue = None

	#@return (instance, parent_conn, child_conn)
	@staticmethod
	def getInstance():
		if ProxyMgr.__instance is None:
			print "ProxyMgr.getInstance()"
			ProxyMgr.__parent_return_conn, child_return_conn = Pipe()
			mgr = Manager()
			ProxyMgr.__processsafe_queue = mgr.Queue(6) # used to get proxies from.

			ProxyMgr.__instance = ProxyMgr(child_return_conn, ProxyMgr.__processsafe_queue)
			ProxyMgr.__instance.start()
		return (ProxyMgr.__instance, ProxyMgr.__parent_return_conn, ProxyMgr.__processsafe_queue)

	#
	# Instance
	#
	def __init__(self, child_return_conn, processsafe_queue):
		super(ProxyMgr, self).__init__()

		self.settings = Settings.getInstance()

		# pipe conns
#		self.conn = child_get_conn
		self.return_conn = child_return_conn

		# stores
		self.proxies = {} 					# DICT: ip -> ProxyModel
		self.proxyQueue = PriorityQueue()	# ProxyKey, pk.value is priority
		self.sleepProxies = {}				# ip -> ProxyKey, waited queue
		self.processsafe_queue = processsafe_queue# used to get proxies from.

		# threads
		self.t_mgr = None
		self.t_provider = None
		self.t_receiver = None

		# control flags
		self.daemon_running = True
		self.loader = None
		self.mgr_interval = 20
		self.print_report = True

	def run(self):
		# start
		self.loader = ProxyLoader(self) # load proxies and start autosave thread.
		self.t_provider = Thread(target=self.tbody_proxy_provider, args=(), name='proxy-provider-thread')
		self.t_receiver = Thread(target=self.tbody_proxy_receiver, args=(), name='proxy-receiver-thread')
		self.t_provider.start()
		self.t_receiver.start()
		print "proxy thread started..."

		proxy_report_count = 0
		# this is manager thread interval code
		while self.daemon_running:
			proxy_report_count += 1
			if self.print_report:
				print ">> proxy thread interval(%s): (%s proxies, %s avaliable, %s waiting, %s in interface queue) -----" % \
					(proxy_report_count, len(self.proxies), len(self.proxies) - len(self.sleepProxies), len(self.sleepProxies), self.processsafe_queue.qsize())

#			# 什么时候重启 provider.
#			reload_all_thread = False
#			if self.num_report % 10000 == 0:
#				reload_all_thread = True
#				message = "Kill & Restart All Thread."

			try:
				pkeys = []
				try:
					for pkey in self.sleepProxies.itervalues():
						pkeys.append(pkey)
				except:
					print "raise modification error"

				# process sleep queue
				while len(pkeys) >= 1:
					proxyKey = pkeys.pop(0)
					proxy = self.proxies.get(proxyKey.ip)
					#print "release? - %s\t%s\t%s\t%s" % (proxy, datetime.now(), proxy.invalid_time, proxy.isInRest())

					if not proxy.isInRest():
						#print "rel--- - %s\t%s\t%s\t%s" % (proxy, datetime.now(), proxy.invalid_time, proxy.isInRest())
						self.proxyQueue.put(proxyKey)
						del self.sleepProxies[proxyKey.ip]

				# recover all proxies.
				if len(self.proxies) - len(self.sleepProxies) < 80:
					self.reload_proxy(False)

#				# process sleep queue
#				while len(self.sleepProxies) >= 1:
#					proxyKey = self.sleepProxies.pop(0)
#					proxy = self.proxies.get(proxyKey.ip)
#					if not proxy.isInRest():
#						self.proxyQueue.put(proxyKey)
#						del self.sleepProxies[proxyKey.ip]

				# sleep
			except Exception, e:
				ExceptionHelper.print_exec(e)
				print "Error %s, %s]" % (sys.exc_info(), "")
				raise e

			time.sleep(self.mgr_interval)
		# ~ interval code ~

		# terminate
		self.t_provider.join()
		self.t_receiver.join()
		print "proxy process terminated."

	def reload_proxy(self, from_web=False):
		''' Reset all proxies, reload from source. '''
		print "\n\n========== reload proxies ===============\n\n"
		# reinit all data store.
		self.proxies = {} 					# DICT: ip -> ProxyModel
		self.proxyQueue = PriorityQueue()	# ProxyKey, pk.value is priority
		self.sleepProxies = {}				# ip -> ProxyKey, waited queue
		# important! load from web may cause the proxy server block us.
		self.loader = ProxyLoader(self, from_web) # reload all proxies ** From local file.

	#
	# Threads
	#
	def tbody_proxy_provider(self):
		while self.daemon_running:
			try:
				proxy = self.getProxy()
				if proxy is not None:
					self.processsafe_queue.put(proxy) # will block
				else:
					print "********* proxy got is None, wait for 1 second and retry."
					time.sleep(1)
			except Exception, e:
				ExceptionHelper.print_exec(e)
				raise

	def tbody_proxy_receiver(self):
		while self.daemon_running:
			try:
				if self.return_conn.poll(5):
					ip, port, action = self.return_conn.recv()
					# perform
					proxy = self.proxies.get(ip)
					if proxy is not None:
						if action == "good":
							proxy.value -= 1
							proxy.take_a_rest(seconds=3)
							#print "-- goodconnection --"
						elif action == "bad":
							proxy.value += 8
							proxy.take_a_rest(minutes=10)
						elif action == "banned":
							proxy.value += 5
							proxy.take_a_rest(minutes=30)
					self.proxies[ip] = proxy
					#print "receve:: %s\t%s\t%s\t%s" % (proxy, datetime.now(), proxy.invalid_time, proxy.isInRest())
			except:
				raise

	def stop(self):
		self.daemon_running = False

	#
	# Get & Manager
	# 
	def getProxy(self):
		while self.daemon_running:
			try:
				proxy_key = self.proxyQueue.get(False)
				proxy = self.proxies[proxy_key.ip]
				if proxy is not None:
					proxy_key.value = proxy.value 		# update proxyKey
					if proxy.isInRest(): 				# add to waiting queue.
						if proxy_key.ip not in self.sleepProxies:
							self.sleepProxies[proxy_key.ip] = proxy_key
					else:
						proxy.take_a_rest(3)
						self.sleepProxies[proxy.ip] = proxy_key
						return proxy
			except:# nothing in proxyQueue.
				print 'current proxy is none.'
				return None


if __name__ == '__main__':
	ProxyMgr.getInstance()
	pass


