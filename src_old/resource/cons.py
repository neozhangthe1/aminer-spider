import os

class cons:

	@staticmethod
	def respath(file_name=None):
		path = os.path.abspath(os.curdir)
		idx = path.index("Runner")
		if not file_name:
			return "%s/Runner/src/%s" % (path[0:idx - 1], "resource")
		else:
			return "%s/Runner/src/%s/%s" % (path[0:idx - 1], "resource", file_name)

	@staticmethod
	def proxy_file_for_read():
		return file(cons.proxy_file, "r")

	@staticmethod
	def proxy_file_for_write():
		return file(cons.proxy_file, "w")

if __name__ == '__main__':
	print "====== Start Extract Citation ======"
	print cons.respath()
	print cons.respath("aaaaaaaaaaa")
