#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.namedisambiguation.checker import checker
import SocketServer
import re
#from xml.dom import minidom


class MyRequestHandler(SocketServer.BaseRequestHandler):
	def __init__(self):
		self.re_title = re.compile("<title1>([^\\x00]+?)</title1>\\s*<title2>([^\\x00]+?)</title2>", re.I)
		self.googlechecker = checker();
		
	def handle(self):
		print "From:", self.client_address
		data = self.request.recv(10240)
		print '- XML -----------------------------------------'
		print data
		print '- XML -----------------------------------------'
		matchs = re.findall(self.re_title, data)
						
		paircount = 0;
		print '- Receive title pair --------------------------'
		for title1, title2 in matchs:
			print "%s: %s\n\t%s" % (paircount, title1, title2)
			paircount += 1
		print '< Receive title pair --------------------------'
		r = self.googlechecker.isInSamePageMulti(matchs)
		print 'Result is:', str(r)
		
#		self.request.send("HTTP/1.1 200 OK\r\n")
#		self.request.send("Content-Type: text/html\n\n")
#		self.request.send("<HTML><BODY><H2>Hello!</H2></BODY></HTML>")
		self.request.send(str(r))
		self.request.close()

class SocketServer:
	'''Multithread, use proxy.
	'''
	def __init__(self):
		self.host = ''
		self.port = 55555
		self.use_proxy = True

	def start(self):
		myServer = SocketServer.TCPServer((self.host, self.port), MyRequestHandler)
		myServer.handle_request()

if __name__ == "__main__":
	SocketServer().start()
