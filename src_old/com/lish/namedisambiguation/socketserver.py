#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.namedisambiguation.checker import checker
import re
import socket
import traceback
''' Single Thread Server
'''
class SocketServer:
	def start(self):
		host = ''
		port = 55555

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((host, port))
		s.listen(1)
		googlechecker = checker();

		re_title = re.compile("<title>([^\\x00]+?)</title>", re.I)
		while 1:
			try:
				clientsock, clientaddr = s.accept()
				print "Got connection from", clientsock.getpeername()
				while 1:
					try:
						data = clientsock.recv(4096)
			#			if not len(data):
			#				break
						matchs = re.findall(re_title, data)
						if len(matchs) < 2:
							print "ERROR NOTENOUGH TITLE:", data
							continue

						r = googlechecker.isInSamePage(matchs[0], matchs[1])
						print 'Result is:', r

					except Exception, e:
						print e
					finally:
						clientsock.sendall(str(r))
						clientsock.close()
				clientsock.close()
			except KeyboardInterrupt:
				raise
			except:
				traceback.print_exc()
				continue

if __name__ == "__main__":
	SocketServer().start()
