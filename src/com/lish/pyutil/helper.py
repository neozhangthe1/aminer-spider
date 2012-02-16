# -*- coding: utf-8 -*-
import traceback

class ExceptionHelper():
	@staticmethod
	def print_exec(e):
		print '-------------------------'
		print "Error [%s]" % (e)
		traceback.print_exc()
		print '-------------------------'
