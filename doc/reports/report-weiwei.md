## Google Scholar 系统分析报告

### 系统的说明

##### 对网页的抓取方式
- 从proxyPool中取出一个proxy，用这个proxy进行发起网页请求，如果在20s内获得了请求的网页则返回，并向将此proxy的优先值-1，并让他休息3s（采用低优先的优先队列管理proxy）;
- 如果20s无法获得网页，将此proxy优先值+8，并让他休息10min，如果重复次数小于5则重复a), 否则返回None.

##### paper匹配流程（在pubmatcher.py）
- 首先对网页抓取的title和数据库中的paper title进行clean，去掉各种标点符号，并且全部转为小写字母，变为key_title.
	- 比较两个key_title，如果完全一致则该对象成为candidate匹配项。（精确匹配）
	- 如果不完全一致，则两者的最小编辑距离dist（即任一title经过增删改变为另一个title的最小操作数），如果dist<10 且dist<数据库中title的长度，那么对象成为candidate匹配项。（模糊匹配）
- 如果candidates的作者也匹配则选出其中的citations数最大的作为匹配的结果。
- 返回对于数据库中的paper，抓取的网页中匹配的个数和为匹配的个数（都是针对数据库中的paper而言，不管网页中有但没有匹配的paper。）
	
##### 系统准确性
经查证，原有系统一旦能够正确的抓取网页，之后进行匹配工作所得的结果不会有错，也就是说在系统打印信息“{+P}[1/0] [found/notfound] pub”时，显示找到就肯定没有错误，所以只要保证可以进行正常的网页抓取，就可以基本维持原有系统的性能。

### 存在的问题

##### 无法正常从网页上抽取信息
究其原因有两个：
	
- 系统利用同一个cookie不停的向谷歌学术的网站发送访问请求，而谷歌对于cookie的过多过快访问有反作弊机制，超过一定限度就会封掉cookie，如此，系统便无法正常得到访问响应了。
- 系统中原先的代理很多已经不再工作了，这样通过一个不存在的或者响应时间过长的代理向目标网站发送请求，定然不会在规定时间内（系统设定timeout=20s）收到响应，那么访问不成功就导致抓取网页失败，更不用说从网页中抽取信息了。

##### paper匹配存在问题
从(V. N. Vapnik), (W. Bruce Croft), (Jiawei Han), (Michael Bendersky), (Pat Langley)五个人的paper 进行单独抽取分析得到了下面的结果：
      
一共进行了publication的匹配次数为2467，匹配中匹配失败的次数为151个。如此计算系统大约有6%的错误率。但是，通过对这151个错误进行分析整合，一共有80个无重复的，发现错误原因大致分为以下四类：

- a) 最终是匹配成功了,只是由于网页中paper还没有被引用而无法获得citations，或者由于网络故障网页没有抓取成功而匹配失败。30个

- b) 在谷歌学术中不存在这样的文章or文章作者名字不匹配  31个
	- 谷歌学术中不存在的文章如：
		- Thirteenth International Work Shop on Research Issues in Data Engineering: Multi-lingual Information Management, RIDE-MLIM 2003, Hyderabad, India, March 10-11, 2003——会议记录等
		- Experience with Large Document Collections (Panel)——确实不存在
	- 作者名字是错误的如：
		- Guiding Revision of Regulatory Models with Expression Data
		- Hypertext and Information Retrieval: What are the Fundamental Concepts? (Panel)


- c) 数据库中文章的title有错误（缺词，多词or只有部分）18个
		- Maintenance of Discovered Knowledge: A Strategy for Updating Association Rules (Abstract)——名字错误，本应该为Maintenance of discovered association rules in large databases: An incremental updating technique
		- Editorial——名字太短而且名字不全
		- Research Paper: Ad Hoc Classification of Radiology Reports 数据库中比Google scholar上多了“Research Paper:”
		- ：trajectory classification using hierarchical region-based and trajectory-based clustering，数据库中比Google scholar上少了” TraClass”


- d) 作者顺次太低（比如第五作者）没有显示出来，如： 1个
	- HyLiEn: a hybrid approach to general list extraction on the web中Jiawei Han是第五作者，在谷歌上没有列出来，所以匹配错误。


由以上看来，a 类错误最终匹配成功了，不为错误，b类错误是无法避免的错误，c类错误是由于数据库里存储的title有误引起的也不能算作系统的问题， d类错误系统能够自我完善这个错误，因为按author没有匹配的paper成功会再按照publication的名字进行搜索提取，经查证这样的作品最后被抽取出了正确的citations. 所以经过分析，事实上，系统在匹配方面基本没有什么错误，而且对于c类错误，系统还可以进行有限度的识别（系统说明中所说的模糊匹配）。而就系统改进方面来说，也只有C类错误可以进行一定程度的避免，通过对系统匹配算法的调整，我们还可以有一定的改进空间。

### 系统改进

- 网页抓取的改进
	- 从网上找到一些代理，对代理进行测试。   
		利用和系统中同样的配置（访问头REQUEST_HEADERS）, 对找到的每个代理进行测试，如果能在5次访问中至少获取到正常网页一次，便把这个代理保存下来。测试完成之后，把好的代理按照系统的格式存到一个文件里放入系统的相应位置，这样系统启动可以获取到good proxy for running.[代码见testProxy.myproxyjudge.testProxyFinal.py]
	- 在访问网站的时候，不再使用静态的cookie头，而是每访问100次更换一次cookie头，防止cookie被封的情况。[更改在com.lish.ajia.util.web.py中]
	- 由于测试好的代理只有427个，如果用原来的20个线程去跑的话，会出现代理不够用经常会reload代理文件，程序的效率不高，所以修改配置为16个线程（8 for person, 8 for publication）.
	- 对于每个代理进行访问后所获得的不同判决（判断为“good proxy” or ”bad proxy”）,休息时间调整为“good proxy”休息 3s，”bad proxy”休息 3min(由于现在所选的proxy已经是优质的代理了，所以休息时间可以相应缩短)

进行上述修改之后，经统计系统进行的3427次访问中， 有28次访问失败，有1171次返回结果，1143次抓取成功，抓取成功率为97.60%。平均每次访问所需的代理数为3427/1171=2.92个。

- paper 匹配的改进
	- 将原有的模糊匹配的衡量两个title相似度的标准由最短编辑距离改变为最长公共子序列的长度和最短编辑距离共同决定。
	- 将相似度阈值变为 最长公共子序列长度>目标title的长度90% 且 最短编辑距离<目标title长度的10%。

改进之后：我专门将进入这一分支的paper抽取出来发现，效果很好，没有一个进入这个分支的paper是与db中的titleb不匹配的，原来无法识别的“：trajectory classification using hierarchical region-based and trajectory-based clustering”等也都可以识别了。

### 改动的理论依据
	
- 为什么在测试代理的时候retry次数为5？   
		因为在系统中，抓取一个网页尝试的最大次数为5，5次没有抓取成功则这个网页就被跳过，放入publication Queue中继续抓取了。因此，应该尽可能的让网页在5次内能够取回，理论上讲测试时应该选择代理的retry=1, 1次不成功抽取就认为是bad,但是由于这样测试出来的代理只有200多个不满足系统的需求，无法提高抓取的效率。因此折中之计，选择retry=5, 才能获得足够多的代理，而这些代理都有可能在第一次访问的时候就返回正确的网页，实践证明还是比较可行的。如果retry=5,仍不能获得足够多的代理的话可以适当考虑增加retry的次数。[在testProxyFinal.py中修改]
	
- 怎样设定系统允许的最大线程数？
	首先假设一些变量，设拥有proxy数量为y, bad proxy休息时间为T,  proxy平均访问访问网页所需的时间为∆t, 对每次网页访问之后系统处理数据的开销为s（设定为1秒）, 则每次网页访问的平均最终用时为t=s+∆t, 最大线程数为x,  proxy的平均访问成功率为w, 则(1-w)为进行一次访问后proxy被勒令休息3min的概率，以t划分时间T所得的间隔个数为k=ceil(T/t),
	
	如果想让系统正常运行，不出现block或者reload proxy的情况，即在T时间内有足够的proxy可供利用，则需要满足下面的不等式：
      $k*x(1-w)+x<=y*0.9$

	上式的意义在于在K个时间间隔内，每个时间间隔利用的proxy数为x, 这些proxy 有(1-w)的概率坏掉，那么在第k+1个时间点, 必须要有x个proxy可用，才能保证系统不被block，而y*0.8则代表系统的proxy利用率在80%以下的时候会有比较好的性能。

	由上式可以计算出最大的容许的线程数.(用testProxy.calPara.getStatis.py可以自动计算出)
	
- 模糊匹配的分析
	经过数据的分析，发现模糊匹配的限制太强了，只有极少数误差在10个字母以内的title可以满足这样的条件。

	比如：系统中有这样一个title“：trajectory classification using hierarchical region-based and trajectory-based clustering”，而这个title是有缺损的，正确的title应该是“TraClass: trajectory classification using hierarchical region-based and trajectory-based clustering”，然而这样的只差几个字母的title无法通过原有系统的模糊匹配限制。

	而且经过分析，最短编辑距离其实并不能确切的反应抓取到的title和目标title的相似程度，比如‘abc’和‘bcd’编辑距离为2，按原有标准理解为不相似度为2/3*100%=66.7%，相似度为33.3%，然而这两个字符串的公共子序列式是bc，应该相似度为66.7%才对。由此可见这个情况下，最短编辑距离并不可用，应该用两个字符串的最长公共子序列作为度量标准。然而，当一个长串和短串进行比较的时候，很有可能，他们的公共子序列是较短的那个字符串，如‘kambermdataminin-gconceptsandtechniques’和‘meanshift’两串的公共子序列为标准的相似度就接近了90%，然而，这两个字符串并不符合要求，所以应该将两种衡量标准结合起来才能更好的发挥出模糊匹配的效果。所以有了上面的修改。

	经过实验，样本（1082个publication）的最佳衡量标准是 最长公共子序列长度>目标title的长度85% 且 最短编辑距离<目标title长度的12%。但是样本可能包含不了整个系统的情况，出于稳定性的考虑，最后将衡量标准定义为 最长公共子序列长度>目标title的长度90% 且 最短编辑距离<目标title长度的10%.

### 系统目前状况

##### 以唐总的文章为例说明

title	Original_ncitation	Update_ncitation
ArnetMiner: extraction and mining of academic social networks.	228	238
Social influence analysis in large-scale networks.	174	184
RiMOM: A Dynamic Multistrategy Ontology Alignment Framework.	157	168
Using Bayesian decision for ontology mapping.	153	156
Expert Finding in a Social Network.	85	91
Social Network Extraction of Academic Researchers.	64	67
Result of Ontology Alignment with RiMOM at OAEI'06.	66	66
Result of Ontology Alignment with RiMOM at OAEI'07.	58	58
A Topic Modeling Approach and Its Integration into the Random Walk Framework for Academic Search.	53	55
Mining advisor-advisee relationships from research publication networks.	-1	52
Email data cleaning.	50	50
Tree-Structured Conditional Random Fields for Semantic Annotation.	49	49
Keyword Extraction Using Support Vector Machine.	48	48
Mining topic-level influence in heterogeneous networks.	48	48
User-level sentiment analysis incorporating social networks	44	44
User-level sentiment analysis incorporating social networks.	44	44
RiMOM Results for OAEI 2008.	38	42
Understanding retweeting behaviors in social networks.	36	40
RiMOM Results for OAEI 2009.	38	38
RiMOM results for OAEI 2010.	38	38
Fuzzy-PI-Based Direct-Output-Voltage Control Strategy for the STATCOM Used in Utility Distribution Systems.	35	37
Who will follow you back?: reciprocal relationship prediction.	19	36
Multi-topic Based Query-Oriented Summarization.	33	35
Towards Ontology Learning from Folksonomies.	34	34
A Combination Approach to Web User Profiling.	25	31
EOS: expertise oriented search using social networks.	29	29
Inferring social ties across heterogenous networks.	23	29

如上是更新前和更新后从数据库中抽取出来的信息，完全与网络上的一致。有一些文章以前没有搜到，现在也查到了如Mining advisor-advisee relationships from research publication networks.。当然也存在一些citations为-1的文章（共16篇），这类文章有的是没有citations，如“A Voltage Control Scheme of Distribution Static Synchronous Compensator Based on Current Sensorless”，有的文章是网络上没有找到的，有的应该是可以找到的，可能由于网络故障，没有查到如，Association search in semantic web: search + inference.

title	Original_ncitation	Update_ncitation
Using DAML+OIL to Enhance Search Semantic.	-1	-1
Association search in semantic web: search + inference.	-1	-1
WWW 2008 workshop on social web search and mining: SWSM2008.	-1	-1
Proceedings of the 2nd ACM Workshop on Social Web Search and Mining, CIKM-SWSM 2009, Hong Kong, China, November 2, 2009	-1	-1
Interective Point Clouds Fairing on Many-Core System.	-1	-1
Recommending interesting activity-related local entities.	0	-1
A Voltage Control Scheme of Distribution Static Synchronous Compensator Based on Current Sensorless.	-1	-1
Improving Performance of the Irregular Data Intensive Application with Small Computation Workload for CMPs.	-1	-1
Advanced Data Mining and Applications - 7th International Conference, ADMA 2011, Beijing, China, December 17-19, 2011, Proceedings, Part I	-1	-1
Advanced Data Mining and Applications - 7th International Conference, ADMA 2011, Beijing, China, December 17-19, 2011, Proceedings, Part II	0	-1
Preface.	-1	-1
Instant Social Graph Search.	0	-1
To better stand on the shoulder of giants.	-1	-1
Reducing Cache Pollution of Threaded Prefetching by Controlling Prefetch Distance.	0	-1
Social Informatics - 4th International Conference, SocInfo 2012, Lausanne, Switzerland, December 5-7, 2012. Proceedings	-1	-1
Social Informatics - 4th International Conference, SocInfo 2012, Lausanne, Switzerland, December 5-7, 2012. Proceedings	0	-1

### 仍存在的问题

在匹配成功paper之后，目前系统的策略是citations取max( db, web),也就是说，如果db中的citations比较大，则不会进行更改，这个有点不符合实际。如果只要citation不比实际的小就可以接受，那么这一点可以不用更改。[pubmatcher.py中涉及]

在web与db中的数据匹配成功后，现有系统title不会改变，而事实上，往往web上的title更准确。[pubmatcher.py中涉及]

###有风险的建议
	
如果能接受一定的错误（千分之三），可以将模糊匹配的系数调整为 最长公共子序列长度>目标title的长度80% 且 最短编辑距离<目标title长度的15%，如此会增加千分之三的paper被正确匹配。

