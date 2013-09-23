#!/usr/bin/env python
from com.lish.ajia.googlescholar.start import GoogleScholarExtractor

#######################################################
# Self Test
#######################################################
if __name__ == '__main__':
	print "====== Start Extract Citation ======"
	inst = GoogleScholarExtractor()
	inst.start()
	print "====== DONE ======"
