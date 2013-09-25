## GoogleScholar Citation Number Crawller


### GoogleScholar Citation Crawller    crawler

抓取scholar.google.com的 `CitedBy` 数据，填充至AMiner数据库对应的paper中。使 用Python编写。

#### Technique
##### 代理服务器

由于google有放抓取机制，所以我们找了2000多个代理服务器（proxycn.com），使用代理服务器抓取数据。
按一定策略使用代理服务器，最好时最开始时可以做到每天20W次Requesst。一周更新一次全库数据。

##### 抓取策略

为了减少对google的访问次数，使用了一些技巧。

1. 先按 Author:"jie tang" 这样的方式抓取，每页显示最多100条结果，抓取 前15页内容。然后进行匹配，这样可以一次匹配这个作者的多篇Paper，大量 减少Request次数。
	>对需要抓取的paper数量>5的人使用这种策略。

2. 对于没有匹配上的paper， 再按照 "paper1 title" AND "paper2 title" AND … 这样的方式抓取，url最长可以拼255字符，也可减少Request次数。
	> BUG: 很短的title如果用这种方式取，会导致这次Request中所有title都取不到数据。
	> 
	> BUG: 有些诡异的情况，这样取不到，但是单独取还能取到。
对于剩下的paper，再去用 "paper title" 的方式去搜索。
对Author按照paper count 排序，从paper最多的开始抓取。

##### 匹配策略

按照三个标准进行松匹配，具体策略参见代码：

* cleaned title
* authors
* year

#### resources
> see evernote

#### Example
跑一下环境系项目的新库，步骤

##### Requirements

1. Required python libraries
	> DBUtils1.0, MySQL-python-1.2.4, py-editdistance-0.3, simplejson

2. Database table requirements (needs arnetminer db)
	* core-tables
		> e.g.: publication, na_person, …
	* constants
		> empty table is ok.
	* person_update_ext
		> need empty table.

##### Run

> TODO: Latest code --> ask Wei Chen

1. Download Crawller code.
2. Update proxy files
	```
	rm Runner/resources/proxies.txt
	cd Runner/src/
	python reload_proxy.py   # TODO proxycn.com访问不能，如何更新代理文件呢?
	mv /tmp/proxies.txt Runner/resources/
	```
3. Modify Settings, file: Runner/src/com/lish/ajia/googlescholar/settings.py
```
# db
self.db_host = "10.1.1.110"
self.db_user = "root"
self.db_passwd = "keg2012"
self.db_database = "evm"
```
4. Run
```
cd Runner/src
python start_google_citation.
```