# -*- coding: utf-8 -*-
from com.lish.ajia.util.db import ConstantsDAO, DB
from com.lish.ajia.util.web import HtmlRetriever

class Try():

	def __init__(self):
		pass

	def try_passbyvalue(self):
		out = [1, 2, 3]
		self.__add(out, 4)
		print out
		print 'done'

	def __add(self, out, list):
		out.append(list)

if __name__ == '__main__':
	a = [1, 2]
	print a
	b = []
	for item in a:
		print item
		b.append(str(item))
	print "-".join(b)
#	test = Try()
#	test.try_passbyvalue()




