#!/usr/bin/env python
# -*- coding: utf-8 -*-

# binary search.


class BinarySearch():
	def __init__(self):
		pass
	
	def bsearch(self, list, value):
		if list is None or len(list) == 0:
			return - 1;
		cs = 0
		ce = len(list) - 1
		if list[cs] == value:
			return cs
		if list[ce] == value:
			return ce
		while ce != cs:
			cm = (ce - cs + 1) / 2
#			print 's:%s,m:%s,e:%s.' % (cs, cm, ce)
			if list[cm] == value:
				return cm
			elif list[cm] > value:
				ce = cm
			else:
				cs = cm
	
if __name__ == '__main__':
	# search 3
	l1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	l2 = [2, 2.5, 3, 200, 9234]
	l3 = [3]
	l4 = [3, 5]
	l5 = [1, 3]
	bs = BinarySearch()
	print bs.bsearch(l1, 3);
	print bs.bsearch(l2, 3);
	print bs.bsearch(l3, 3);
	print bs.bsearch(l4, 3);
	print bs.bsearch(l5, 3);
