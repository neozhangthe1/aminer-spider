#!/usr/bin/env python
from com.lish.namedisambiguation.socket_server import MultithreadSocketServer
server = MultithreadSocketServer()
#server.start_server("10.1.1.248",55555)
server.start_server("10.1.1.209",55559)
