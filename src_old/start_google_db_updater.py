#!/usr/bin/env python
from com.lish.namedisambiguation.update_na_result_in_db import \
	GoogleResultDBUpdater
from com.lish.pyutil.db import DB

#DB.initpool("localhost", "arnet_local", "root", "root")
DB.initpool("10.1.1.209", "arnet_int2", "root", "root")
GoogleResultDBUpdater().update()



