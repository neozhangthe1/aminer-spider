#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.namedisambiguation.checker import checker
#from xml.dom import minidom

import re
import socket
import traceback

class SocketServer:
	'''Multithread, use proxy.
	'''
	def __init__(self):
		self.host = ''
		self.port = 55555
		self.use_proxy = True

	def start(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self.host, self.port))
		s.listen(1)
		googlechecker = checker();

		re_title = re.compile("<title1>([^\\x00]+?)</title1>\\s*<title2>([^\\x00]+?)</title2>", re.I)
		while 1:
			try:
				clientsock, clientaddr = s.accept()
				print "Got connection from", clientsock.getpeername()
				while 1:
					try:
						data = clientsock.recv(409600000)
						if not len(data):
							break

						matchs = re.findall(re_title, data)

						print '- XML -----------------------------------------'
						print data
						print '- XML -----------------------------------------'
						paircount = 0;
						print '- Receive title pair --------------------------'
						for title1, title2 in matchs:
							print "%s: %s\n\t%s" % (paircount, title1, title2)
							paircount += 1
						print '< Receive title pair --------------------------'
						
#						if len(matchs) < 2:
#							print "ERROR NOTENOUGH TITLE:", data
#							continue

						# [('t1', 't2'), ('b1', 'b2')]
						r = googlechecker.isInSamePageMulti(matchs)
						print 'Result is:', str(r)

					except Exception, e:
						print e
					finally:
						clientsock.send(str(r))
						clientsock.send("\n")
						clientsock.close()
				clientsock.close()
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc()
				continue

if __name__ == "__main__":
	SocketServer().start()
