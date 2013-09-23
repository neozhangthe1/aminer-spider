# -*- coding: utf-8 -*-
from com.lish.ajia.googlescholar.daos import PublicationDao
from com.lish.ajia.googlescholar.settings import Settings

class TestCase():

	def __init__(self):
		self.settings = Settings()

	def test_getpublications(self):
		'''Test get all publications from database.'''
		print '-TEST-:', TestCase.test_getpublications.__doc__
		pubdao = PublicationDao()
		pubs = pubdao.getPublicationByPerson(13423, self.settings.generation)  # id for jie tang, current generation
		for pub in pubs:
			print pub
		print '-END TEST-'

if __name__ == '__main__':
	test = TestCase()
	test.test_getpublications()



