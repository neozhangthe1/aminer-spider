#!/usr/bin/env python
# -*- coding: utf-8 -*-
from com.lish.namedisambiguation.checker import checker
import SocketServer
import re
import socket
import threading
import time
from xml.dom import minidom, Node

class MultithreadSocketServer():
	'''Multithread NA google method.
	'''
	def __init__(self):
		pass
	
	class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
		def handle(self):
			self.re_title = re.compile("<title1>([^\\x00]+?)</title1>\\s*<title2>([^\\x00]+?)</title2>", re.I)
			self.googlechecker = checker();		

			# receive data																				  
			print "From:", self.client_address
			datapieces = []
			datapiece = self.request.recv(10240)
			datapieces.append(datapiece)
			print 'first get ', len(datapiece)

			piece_last = ''
			
			self.request.setblocking(0)
			while(len(datapiece) > 0):
				try:
					#print 'second get ', len(datapiece)
					datapiece = self.request.recv(10240)
					datapieces.append(datapiece)
				except Exception, e:
					print e
					time.sleep(0.5)
					#break
				last2pieces = ''.join((piece_last, datapiece))
				if  last2pieces.endswith('</root>'):
					break
				piece_last = datapiece
				
			self.request.setblocking(1)

			data = "".join(datapieces)

			print '- XML -----------------------------------------'
			print data
			print '- XML -----------------------------------------'
			matchs = re.findall(self.re_title, data)

			# print titles
			paircount = 0;
			print '- Receive title pair --------------------------'
			for title1, title2 in matchs:
				print "%s: %s\n\t%s" % (paircount, title1, title2)
				paircount += 1
			print '< Receive title pair --------------------------'
			
			# process and send result back
			debug = False
			if debug:
				#r = '''{0: True, 1: True, 2: True, 3: False, 4: False, 5: True, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False, 13: False, 14: False, 15: False, 16: False}'''
				r = '''
				<root>
					<pair>
						<result>true</result>
						<matched>link1</matched>
					</pair>
					<pair>
						<result>false</result>
					</pair>
				</root>
				'''
			else:
				na_results = self.googlechecker.isInSamePageMulti(matchs)
				r = self.pinXML(na_results, len(matchs))
			print 'Result is:', str(r)
			
			self.request.sendall(str(r))
			self.request.close()
		
		def pinXML(self, na_results, length):
			if na_results is None or len(na_results) == 0:
				return '<root></root>';
			else:
				doc = minidom.Document()
				root_elm = doc.createElement("root");
				doc.appendChild(root_elm);
				
				for i in range(0, length):
					na_result = na_results[i]
#				for na_result in na_results:
					pair_elm = doc.createElement("pair");
					# result
					result_elm = doc.createElement("result")
					result_text = doc.createTextNode((str)(na_result.result))
					result_elm.appendChild(result_text);
					pair_elm.appendChild(result_elm);
					# links
					for link in na_result.links:
						link_elm = doc.createElement("matched")
						link_elm.appendChild(doc.createTextNode(link))
						pair_elm.appendChild(link_elm)
					root_elm.appendChild(pair_elm)
				return doc.toxml("utf-8");
			
			
	class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
		pass
	
	def client(self, ip, port, message):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((ip, port))
		sock.send(message)
		response = sock.recv(1024)
		print "Received: %s" % response
		sock.close()
	
	
	def start_server(self, HOST, PORT):
		try:
			# Port 0 means to select an arbitrary unused port
			# HOST, PORT = "localhost", 55555
		
			server = self.ThreadedTCPServer((HOST, PORT), self.ThreadedTCPRequestHandler)
			# ip, port = server.server_address
		
			# Start a thread with the server -- that thread will then start one
			# more thread for each request
			server_thread = threading.Thread(target=server.serve_forever)
			# Exit the server thread when the main thread terminates
			server_thread.setDaemon(True)
			server_thread.start()
			print "Server loop running in thread:", server_thread.getName()
			
			while(1):
				time.sleep(1)
				
		except KeyboardInterrupt:
			server.shutdown()
			raise
	
if __name__ == "__main__":
	server = MultithreadSocketServer()
	server.start_server("localhost", 55555)
	
	
	
	
