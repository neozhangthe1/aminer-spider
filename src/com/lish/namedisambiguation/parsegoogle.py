# -*- coding: utf-8 -*-

#from runner.proxy import proxy
from com.lish.ajia.util.web import HtmlRetriever
from settings import Settings
import re

class GoogleResultParser:
	'''Extract google search result information.
	'''
	__instance = None

	@staticmethod
	def getInstance():
		if GoogleResultParser.__instance is None:
			GoogleResultParser.__instance = GoogleResultParser()
		return GoogleResultParser.__instance


	def __init__(self):
		self.settings = Settings.getInstance()
		self.debug = self.settings.debug
		self.htmlRetriever = HtmlRetriever.getInstance(self.settings.use_proxy)

	def extract_from_source(self, page_html):
		'''Extract information from html, return ExtractedModel
		@return: models - [models.ExtractedCitationModel]
		@param: 
			page_html - str:html source of google scholar search result.
		'''
		blocks_html = self.__split_into_blocks(page_html)
#		i = 0
#		for block in blocks_html:
#			print i, '>>', block[1]
#			i += 1
#		print 'exit'
		if blocks_html is None:
			print '-' * 100
			print page_html
			print '-' * 100
		models = []
		for block in blocks_html:
			model = self.__extract_googlescholar_result(block[1])
			if model is not None:
				models.append(model)
		return models


	def __split_into_blocks(self, html):
		'''Split google scholar result page html into blocks of each search result.'''
		if html is not None and len(html) > 0:
			blocks_html = re.findall(self.settings.re_extract_blocks, html)
			return blocks_html

	def __extract_googlescholar_result(self, block_html):
		'''parse html_block into google scholar result model.'''
		if block_html is None or block_html == '': 
			return None
		
		matchs_link = re.findall(self.settings.re_title_link, block_html)
		matchs = re.findall(self.settings.re_cite, block_html)
		result = []
		if matchs_link is not None and len(matchs_link)>0:
			result.append(matchs_link[0])
		else:
			result.append("")

		if matchs is not None and len(matchs)>0:
			result.append(matchs[0])
		else:
			result.append("")

#		for match in matchs:
#			print match
		return result
		# match title
#		matchs = re.findall(self.settings.re_gs_title, block_html)
#		if len(matchs) == 0:
#			return None
#		type = matchs[0][1]
#		url = matchs[0][3]
#		title = matchs[0][4]
#
#		print '--', type, url, title
#
#		(readable_title, title_cleaned, has_dot) = GoogleResultParser.cleanTitle(title)
#
#		if self.debug and False:
#			print '>get:\t', (type, title, url)
#			print '>3titles: %s <to> %s <to> %s' % (title, readable_title, title_cleaned)
#
#		gs_result = models.ExtractedGoogleScholarResult()
#		gs_result.title = title
#		gs_result.readable_title = readable_title
#		gs_result.shunked_title = title_cleaned
#		gs_result.title_has_dot = has_dot
#
#		# match #citation
#		citation_match = re.findall(self.settings.re_citedby, block_html)
#		if len(citation_match) == 0:
#			gs_result.ncitation = 0;
#		else:
#			gs_result.ncitation = int(citation_match[0][1])
#		# author
#		authors = re.findall(self.settings.re_author, block_html)
#		if authors is not None and len(authors) > 0:
#			gs_result.authors = authors[0]
#
#		# pdf link
#		if self.settings.save_pdflink:
#			link = re.findall(self.settings.re_pdflink, block_html)
#			if link is not None and len(link) > 0:
#				gs_result.pdflink = link
#				self.pdfcache.add(gs_result.readable_title, link)
#
#		return gs_result


	def __merge_into_extractedmap(self, out_all_models, models):
		'''Add all in list models into out_all_models'''
		if out_all_models is None : out_all_models = {}
		for model in models:
			keytitle = model.shunked_title
			if keytitle not in out_all_models:
				out_all_models[keytitle] = [model]
			else:
				models = out_all_models[keytitle]
				models.append(model)
		return out_all_models


	@staticmethod
	def cleanTitle(title):
		has_dot = False
		titleCleaned = title
		# clean step 1
		titleCleaned = re.sub("(\[(.*?)\]|<(.*?)>)", "", titleCleaned)
		# if has dot
		re_hasdot = re.compile("(\.\.\.|&hellip;)", re.I)
		match = re_hasdot.search(title)
		if match is not None:
			has_dot = True
		# clean step 2, here title is readable
		titleCleaned = re.sub("(&nbsp;|&#x25ba;|&hellip;)", "", titleCleaned)
		titleCleaned = re.sub("(&#.+?;|&.+?;)", "", titleCleaned)

		titleCleaned = titleCleaned.strip()
		readableTitle = titleCleaned

		# Shrink, only letters left
		titleCleaned = re.sub("\W", "", titleCleaned)
		titleCleaned = titleCleaned.lower()
		return (readableTitle, titleCleaned, has_dot)

if __name__ == "__main__":
	html = '''
	<!doctype html><head><meta http-equiv=content-type content="text/html; charset=UTF-8"><title>&quot;New event detection based on indexing-tree and named entity&quot; AND &quot;Term Committee Based Event Identification within News Topics&quot; - Google Search</title><script>window.google={kEI:"8w7TS6ubJIr46QOJn-y8Dw",kEXPI:"24587,24591,24605",kCSI:{e:"24587,24591,24605",ei:"8w7TS6ubJIr46QOJn-y8Dw",expi:"24587,24591,24605"},ml:function(){},kHL:"en",time:function(){return(new Date).getTime()},log:function(b,d,c){var a=new Image,e=google,g=e.lc,f=e.li;a.onerror=(a.onload=(a.onabort=function(){delete g[f]}));g[f]=a;c=c||"/gen_204?atyp=i&ct="+b+"&cad="+d+"&zx="+google.time();a.src=c;e.li=f+1},lc:[],li:0,Toolbelt:{}};
window.google.sn="web";window.google.timers={load:{t:{start:(new Date).getTime()}}};try{window.google.pt=window.external&&window.external.pageT;}catch(u){}window.google.jsrt_kill=1;
</script><style>body{background:#fff;color:#000;margin:3px 8px}#gbar,#guser{font-size:13px;padding-top:1px !important}#gbar{float:left;height:22px}#guser{padding-bottom:7px !important;text-align:right}.gbh,.gbd{border-top:1px solid #c9d7f1;font-size:1px}.gbh{height:0;position:absolute;top:24px;width:100%}#gbs,.gbm{background:#fff;left:0;position:absolute;text-align:left;visibility:hidden;z-index:1000}.gbm{border:1px solid;border-color:#c9d7f1 #36c #36c #a2bae7;z-index:1001}.gb1{margin-right:.5em}.gb1,.gb3{zoom:1}.gb2{display:block;padding:.2em .5em;}.gb2,.gb3{text-decoration:none;border-bottom:none}a.gb1,a.gb2,a.gb3,a.gb4{color:#00c !important}a.gb2:hover{background:#36c;color:#fff !important}a.gb1,a.gb2,a.gb3,.link{color:#20c!important}.ts{border-collapse:collapse}.ts td{padding:0}.ti,.bl,form,#res h3{display:inline}.ti{display:inline-table}.fl:link,.gl,.gl a:link{color:#77c}a:link,.w,#prs a:visited,#prs a:active,.q:active,.q:visited{color:#20c}.mblink:visited,a:visited{color:#551a8b}a:active{color:red}.vst:link{color:#551a8b}.cur{color:#a90a08;font-weight:bold}.b{font-weight:bold}.j{width:42em;font-size:82%}.s{max-width:42em}.sl{font-size:82%}#gb{text-align:right;padding:1px 0 7px;margin:0}.hd{position:absolute;width:1px;height:1px;top:-1000em;overflow:hidden}.f,.m,.c h2,#mbEnd h2{color:#676767}.a,cite,.cite,.cite:link{color:green;font-style:normal}#mbEnd{float:right}h1,ol{margin:0;padding:0}li.g,body,html,.std,.c h2,#mbEnd h2,h1{font-size:small;font-family:arial,sans-serif}.c h2,#mbEnd h2,h1{font-weight:normal}#ssb,.clr{clear:both;margin:0 8px}#nav a,#nav a:visited,.blk a{color:#000}#nav a{display:block}#nav .b a,#nav .b a:visited{color:#20c}#nav .i{color:#a90a08;font-weight:bold}.csb,.ss,#logo span,#rptglbl{background:url(/images/nav_logo8.png) no-repeat;overflow:hidden}.csb,.ss{background-position:0 0;height:26px;display:block}.ss{background-position:0 -88px;position:absolute;left:0;top:0}.cps{height:18px;overflow:hidden;width:114px}.mbi{font-size:0;width:13px;height:13px;background-position:-91px -74px;position:relative;top:2px;margin-right:3px}#nav td{padding:0;text-align:center}#logo{display:block;overflow:hidden;position:relative;width:103px;height:37px;margin:11px 0 7px}#logo img{border:none;position:absolute;left:-0px;top:-26px}#logo span,.ch{cursor:pointer}.lst{font-family:arial,sans-serif;font-size:17px;vertical-align:middle}.lsb{font-family:arial,sans-serif;font-size:15px;height:1.85em;vertical-align:middle}h3,.med{font-size:medium;font-weight:normal;padding:0;margin:0}.e{margin:.75em 0}.bc a{color:green;text-decoration:none}.bc a:hover{text-decoration:underline}.bc a:visited,.bc a:active{color:green}.slk td{padding-left:40px;padding-top:5px;vertical-align:top}.slk div{padding-left:10px;text-indent:-10px}.fc{margin-top:.5em;padding-left:3em}#mbEnd cite{display:block;text-align:left}#mbEnd p{margin:-.5em 0 0 .5em;text-align:center}#bsf,#ssb,.blk{border-top:1px solid #6b90da;background:#f0f7f9}#bsf{border-bottom:1px solid #6b90da}#flp{margin:7px 0}#ssb div{float:left;padding:4px 0 0;padding-left:7px;padding-right:.5em}#prs a,#prs b{margin-right:.6em}#ssb p{text-align:right;white-space:nowrap;margin:.1em 0;padding:.2em;zoom:1}#ssb{margin:0 8px 11px;padding:.1em}#cnt{max-width:80em;clear:both}#mbEnd{background:#fff;padding:0;border-left:11px solid #fff;border-spacing:0;white-space:nowrap}#res{padding-right:1em;margin:0 16px}.c{background:#fff8dd;margin:0 8px}.c li{padding:0 3px 0 8px;margin:0}.c .tam,.c .tal{padding-top:12px}#mbEnd li{margin:1em 0;padding:0;zoom:1}.xsm{font-size:x-small}.sm{margin:0 0 0 40px;padding:0}ol li{list-style:none}.sm li{margin:0}.gl,#bsf a,.nobr{white-space:nowrap}#mbEnd .med{white-space:normal}.sl,.r{display:inline;font-weight:normal;margin:0}.r{font-size:medium}h4.r{font-size:small}.mr{margin-top:-.5em}h3.tbpr{margin-top:.3em;margin-bottom:1em}img.tbpr {border:0px;width:15px;height:15px;margin-right:3px}.jsb{display:block}.nojsb{display:none}.rt1{background:transparent url(/images/bubble1b.png) no-repeat}.rt2{background:transparent url(/images/bubble2.png) repeat 0 0 scroll}.sb{background:url(/images/scrollbar.png) repeat scroll 0 0;cursor:pointer;width:14px}.rtdm:hover{text-decoration:underline}.ri_cb{left:0;margin:2px;position:absolute;top:0;z-index:1}.ri_sp{display:-moz-inline-box;display:inline-block;text-align:center;vertical-align:top;margin-bottom:6px}.g{margin:1em 0}.mbl{margin:1em 0 0}em{font-weight:bold;font-style:normal}.tbi div, #tbp{background:url(/images/nav_logo8.png) no-repeat;overflow:hidden;width:13px;height:13px;cursor:pointer}#ssb #tbp{background-position:-91px -74px;padding:0;margin-top:1px;margin-left:0.75em;}.tbpo,.tbpc{margin-left:3px;margin-right:1em;text-decoration:underline;white-space:nowrap;cursor:pointer}.tbpc,.tbo .tbpo {display:inline}.tbo .tbpc,.tbpo{display:none}#prs *{float:left}#prs a, #prs b{position:relative;bottom:.08em;margin-right:.3em}.std dfn{padding-left:.2em;padding-right:.5em}dfn{font-style:normal;font-weight:bold;padding-left:1px;_line-height:100%;position:relative;top:-.12em}#tbd{display:none;margin-left:-9.6em;z-index:1}.tbo #tads,.tbo #pp,.tbo #tadsb{margin-left:12.7em}.tbo #res{margin-left:11.05em;}.tbo #tbd{width:9.6em;padding:0;left:11px;background:#fff;border-right:1px solid #c9d7f1;position:absolute;display:block;margin-left:0}.tbo #mbEnd{width:26%}</style><noscript><style>.jsb{display:none}.nojsb{display:block}</style></noscript><script>google.y={};google.x=function(e,g){google.y[e.id]=[e,g];return false};if(!window.google)window.google={};window.google.crm={};window.google.cri=0;window.clk=function(e,f,g,k,l,b,m){if(document.images){var a=encodeURIComponent||escape,c=new Image,h=window.google.cri++;window.google.crm[h]=c;c.onerror=(c.onload=(c.onabort=function(){delete window.google.crm[h]}));if(b&&b.substring(0,6)!="&sig2=")b="&sig2="+b;c.src=["/url?sa=T","\x26source\x3dweb",f?"&oi="+a(f):"",g?"&cad="+a(g):"","&ct=",a(k||"res"),"&cd=",a(l),"&ved=",a(m),e?"&url="+a(e.replace(/#.*/,"")).replace(/\+/g,"%2B"):"","&ei=","8w7TS6ubJIr46QOJn-y8Dw",b].join("")}return true};
window.gbar={qs:function(){},tg:function(e){var o={id:'gbar'};for(i in e)o[i]=e[i];google.x(o,function(){gbar.tg(o)})}};</script></head><body id=gsr topmargin=3 marginheight=3><div id=xjsc></div><textarea id=csi style=display:none></textarea><div id=gbar><nobr><b class=gb1>Web</b> <a href="http://images.google.com.hk/images?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&source=og&sa=N&tab=wi" onclick=gbar.qs(this) class=gb1>Images</a> <a href="http://www.google.com.hk/search?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&tbo=u&tbs=vid:1&source=og&sa=N&tab=wv" onclick=gbar.qs(this) class=gb1>Videos</a> <a href="http://maps.google.com.hk/maps?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=wl" onclick=gbar.qs(this) class=gb1>Maps</a> <a href="http://www.google.com.hk/finance?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=we" onclick=gbar.qs(this) class=gb1>Finance</a> <a href="http://translate.google.com.hk/translate_t?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=wT" onclick=gbar.qs(this) class=gb1>Translate</a> <a href="http://mail.google.com/mail/?hl=en&tab=wm" class=gb1>Gmail</a> <a href="http://www.google.com.hk/intl/en/options/" onclick="this.blur();gbar.tg(event);return !1" aria-haspopup=true class=gb3><u>more</u> <small>&#9660;</small></a><div class=gbm id=gbi><a href="http://scholar.google.com.hk/scholar?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=ws" onclick=gbar.qs(this) class=gb2>Scholar</a> <a href="http://www.google.com.hk/search?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&tbo=u&tbs=blg:1&source=og&sa=N&tab=wb" onclick=gbar.qs(this) class=gb2>Blogs</a> <div class=gb2><div class=gbd></div></div><a href="http://www.youtube.com/results?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=w1&gl=HK" onclick=gbar.qs(this) class=gb2>YouTube</a> <a href="http://www.google.com/calendar/render?hl=en&tab=wc" class=gb2>Calendar</a> <a href="http://picasaweb.google.com.hk/lh/view?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=wq" onclick=gbar.qs(this) class=gb2>Photos</a> <a href="http://docs.google.com/?hl=en&tab=wo" class=gb2>Documents</a> <a href="http://www.google.com.hk/reader/view/?hl=en&tab=wy" class=gb2>Reader</a> <a href="http://sites.google.com/?hl=en&tab=w3" class=gb2>Sites</a> <a href="http://groups.google.com.hk/groups?hl=en&safe=strict&q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&um=1&ie=UTF-8&sa=N&tab=wg" onclick=gbar.qs(this) class=gb2>Groups</a> <div class=gb2><div class=gbd></div></div><a href="http://www.google.com.hk/intl/en/options/" class=gb2>even more &raquo;</a> </div></nobr></div><div id=guser width=100%><nobr><span id=gbn class=gbi></span><span id=gbf class=gbf></span><span id=gbe></span><a href="/preferences?hl=en" class=gb4>Search settings</a> | <a href="https://www.google.com/accounts/Login?hl=en&continue=http://www.google.com.hk/search%3Fhl%3Den%26safe%3Dstrict%26q%3D%2522New%2Bevent%2Bdetection%2Bbased%2Bon%2Bindexing-tree%2Band%2Bnamed%2Bentity%2522%2BAND%2B%2522Term%2BCommittee%2BBased%2BEvent%2BIdentification%2Bwithin%2BNews%2BTopics%2522%26aq%3Df%26aqi%3Dg1%26aql%3D%26oq%3D%26gs_rfai%3D" class=gb4>Sign in</a></nobr></div><div class=gbh style=left:0></div><div class=gbh style=right:0></div><div id=cnt><form id=tsf name=gs method=GET action="/search"><table id=sft class=ts style="clear:both;margin:19px 3px 20px 3px"><tr valign=top><td style="padding-right:8px"><h1><a id=logo href="http://www.google.com.hk/webhp?hl=en" title="Go to Google Home">Google<img width=164 height=106 src="/images/nav_logo8.png" alt=""></a></h1><td id=sff style="padding:1px 3px 7px;padding-left:9px;width:100%"><table class=ts style="margin:12px 0 3px"><tr><td nowrap><input type=hidden name=hl value="en"><input type=hidden name=newwindow value="1"><input type=hidden name=safe value="strict"><input autocomplete="off" class=lst type=text name=q size=70 maxlength=2048 value="&quot;New event detection based on indexing-tree and named entity&quot; AND &quot;Term Committee Based Event Identification within News Topics&quot;" title="Search"> <input type=submit name="btnG" class=lsb value="Search"></td><td style="padding:0 6px" class="nobr xsm"><a href="/advanced_search?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict">Advanced Search</a><br></table>  <div id=issferb>Search: <input id=all type=radio name=meta value="" checked><label for=all> the web </label> <input id=cty type=radio name=meta value="cr=countryHK"><label for=cty> pages from Hong Kong </label> </div></table></form><noscript><style>.bl{display:none !important}</style></noscript><div id=ssb><div id=prs><span class=std><b>Web</b></span><a href="/search?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict&amp;tbo=1" id=tbpi class=q onclick="return google.x(this,function(){return google.Toolbelt.toggle(this, event)})"><div id=tbp></div><span class=tbpo>Hide options</span><span class=tbpc>Show options...</span></a></div><p id=resultStats>&nbsp;Results <b>1</b> - <b>4</b> of <b>4</b> for <b>&quot;New event detection based on indexing-tree and named entity&quot; AND &quot;Term Committee Based Event Identification within News Topics&quot;</b> with <b>Safesearch on</b>.  (<b>0.10</b> seconds)&nbsp;</div><div id=tbd class=med><h2 class=hd></h2></div><div id=res class=med><script>var a=document.styleSheets[0],b=a.rules,c=document.getElementById("mbEnd"),d=document.getElementById("tbd"),e=0;a.addRule(".s","width:auto");var f=b[b.length-1].style;a.addRule("#cnt","width:auto");var h=b[b.length-1].style;function i(){f.width=document.body.clientWidth-
(c?c.offsetWidth:0)-(d?d.offsetWidth:0)<=588?"auto":"544px";h.width=document.body.clientWidth<=1050?"auto":"1050px";}window.attachEvent("onresize",function(){var g=new Date;if(g-e>100){i();e=g}});i();
</script><h2 class=hd>Search Results</h2><div><ol><li class=g><h3 class=r><a href="http://www.informatik.uni-trier.de/~ley/db/indices/a-tree/z/Zhang:Kuo.html" target=_blank class=l onmousedown="return clk(0,'','','res','1','','0CAYQFjAA')">DBLP: Kuo Zhang</a></h3><div class="s"><b>...</b> Kehong Wang: <em>Term Committee Based Event Identification within News Topics</em>. <b>...</b> Li Gang Wu: <em>New event detection based on indexing-tree and named entity</em>. <b>...</b><br><cite>www.informatik.uni-trier.de/~ley/db/indices/a.../Zhang:Kuo.html - </cite><span class=gl><a href="http://74.125.153.132/search?q=cache:WQuvN7krWEwJ:www.informatik.uni-trier.de/~ley/db/indices/a-tree/z/Zhang:Kuo.html+%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;cd=1&amp;hl=en&amp;ct=clnk&amp;gl=hk" target=_blank onmousedown="return clk(0,'','','clnk','1','')">Cached</a></span></div><li class=g><h3 class=r><a href="http://keg.cs.tsinghua.edu.cn/persons/gangwu/publications.jsp" target=_blank class=l onmousedown="return clk(0,'','','res','2','','0CAgQFjAB')">Gang Wu&#39;s Homepage - Publications</a></h3><div class="s"><b>...</b> <em>Term committee based event identification within news topics</em>, PAKDD 2008 <b>...</b> <em>New Event Detection Based on Indexing-tree and Named Entity</em>, SIGIR 2007 <b>...</b><br><cite>keg.cs.tsinghua.edu.cn/persons/gangwu/publications.jsp - </cite><span class=gl><a href="http://74.125.153.132/search?q=cache:wZh6Y9ygMD4J:keg.cs.tsinghua.edu.cn/persons/gangwu/publications.jsp+%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;cd=2&amp;hl=en&amp;ct=clnk&amp;gl=hk" target=_blank onmousedown="return clk(0,'','','clnk','2','')">Cached</a></span></div><li class=g><h3 class=r><a href="http://search.ustc.edu.cn/notold/search.php?q=Gang" target=_blank class=l onmousedown="return clk(0,'','','res','3','','0CAoQFjAC')">Gang - Not Old学术搜索</a></h3><div class="s">390, <em>Term Committee Based Event Identification within News Topics</em>. null <b>......</b> 835, <em>New event detection based on indexing-tree and named entity</em>. null <b>...</b><br><cite>search.ustc.edu.cn/notold/search.php?q=Gang - </cite><span class=gl><a href="http://74.125.153.132/search?q=cache:k8fOGKhrZaYJ:search.ustc.edu.cn/notold/search.php%3Fq%3DGang+%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;cd=3&amp;hl=en&amp;ct=clnk&amp;gl=hk" target=_blank onmousedown="return clk(0,'','','clnk','3','')">Cached</a></span></div><li class=g style="margin-left:3em"><h3 class=r><a href="http://search.ustc.edu.cn/notold/search.php?q=Zi" target=_blank class=l onmousedown="return clk(0,'','','res','4','','0CAwQFjAD')">Zi - Not Old学术搜索</a></h3><div class="s hc" valign=top id=mbb4>114, <em>Term Committee Based Event Identification within News Topics</em>. null <b>......</b> 765, <em>New event detection based on indexing-tree and named entity</em>. null <b>...</b><br><cite>search.ustc.edu.cn/notold/search.php?q=Zi - </cite><span class=gl><a href="http://74.125.153.132/search?q=cache:5SSN1QUqHJwJ:search.ustc.edu.cn/notold/search.php%3Fq%3DZi+%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;cd=4&amp;hl=en&amp;ct=clnk&amp;gl=hk" target=_blank onmousedown="return clk(0,'','','clnk','4','')">Cached</a></span><div class=mbl><div class=bl><span class=ch id=mbl4 onclick="google.x(this)"><table class="ts ti"><tr><td><div class="csb mbi"></div></table><a href=# onclick="return false" class=mblink>Show more results from search.ustc.edu.cn</a></span></div></div><div id=mbf4><span/></div></div></ol></div><p id=ofr><i>In order to show you the most relevant results, we have omitted some entries very similar to the 4 already displayed.<br>If you like, you can <a href="/search?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict&amp;filter=0">repeat the search with the omitted results included</a>.</i></p></div><div id=navcnt></div><div style="height:1px;line-height:0"></div><div style="text-align:center;margin-top:1.4em" class=clr><div id=bsf style="padding:1.8em 0;margin-top:0"><form method=get action="/search"><div><input class=lst type=text name=q size=70 maxlength=2048 value="&quot;New event detection based on indexing-tree and named entity&quot; AND &quot;Term Committee Based Event Identification within News Topics&quot;" title="Search"> <input type=submit name="btnG" class=lsb value="Search"><input type=hidden name=hl value="en"><input type=hidden name=newwindow value="1"><input type=hidden name=safe value="strict"><input type=hidden name=sa value="2"></div></form><p style="margin:1.2em 0 0"><a href="/swr?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict&amp;swrnum=4">Search&nbsp;within&nbsp;results</a> - <a href="/language_tools?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict">Language Tools</a> - <a href="/support/websearch/bin/answer.py?answer=134479&amp;hl=en">Search Help</a> - <a href="/quality_form?q=%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22&amp;hl=en&amp;newwindow=1&amp;safe=strict" target=_blank>Dissatisfied? Help us improve</a></div><p><a href="/">Google&nbsp;Home</a> - <a href="/intl/en/ads/">Advertising&nbsp;Programs</a> - <a href="/intl/en/privacy.html">Privacy</a> - <a href="/intl/en/about.html">About Google</a></p></div><textarea style="display:none" id=hcache></textarea><div id=xjsd></div><div id=xjsi><script>if(google.y)google.y.first=[];if(google.y)google.y.first=[];google.dstr=[];google.rein=[];window.setTimeout(function(){var a=document.createElement("script");a.src="/extern_js/f/CgJlbhICaGsrMAo4Y0ACLCswDjgNLCswFjgXLCswFzgGLCswGDgFLCswGTgcLCswJTjKiAEsKzAmOAosKzAnOAQsKzA8OAIsKzBAOA8sKzBFOAEsKzBOOAQsKzBROAAsgAIN/5SMGwp-9BoI.js";(document.getElementById("xjsd")||document.body).appendChild(a);if(google.timers&&google.timers.load.t)google.timers.load.t.xjsls=(new Date).getTime();},0);
;window.mbtb1={tbs:"",docid:"2087627624594372094",usg:"efe7",obd:false};google.base_href='/search?q\x3d%22New+event+detection+based+on+indexing-tree+and+named+entity%22+AND+%22Term+Committee+Based+Event+Identification+within+News+Topics%22\x26hl\x3den\x26newwindow\x3d1\x26safe\x3dstrict';google.sn='web';google.y.first.push(function(){google.Toolbelt.resetListeners();;window.mb4=ManyBox.register('4','5SSN1QUqHJwJ','ce7a',32,'Hide more results from search.ustc.edu.cn');mb4.append(['mres=5SSN1QUqHJwJ:k8fOGKhrZaYJ:']);mb4.append(['q=/search%3Fhl%3Den%26newwindow%3D1%26safe%3Dstrict%26q%3D%2Bsite%3Asearch.ustc.edu.cn%2B%2522New%2Bevent%2Bdetection%2Bbased%2Bon%2Bindexing-tree%2Band%2Bnamed%2Bentity%2522%2BAND%2B%2522Term%2BCommittee%2BBased%2BEvent%2BIdentification%2Bwithin%2BNews%2BTopics%2522']);google.ac.b=true;google.ac.i(document.gs,document.gs.q,'','\x22New event detection based on indexing-tree and named entity\x22 AND \x22Term Committee Based Event Identification within News Topics\x22','',{a:0,o:0});(function(){
function b(a){document.cookie=a}function c(){if(!document.cookie.match(/GZ=Z=[0,1]/)){b("GZ=Z=0");var a=document.createElement("iframe");a.src="/compressiontest/gzip.html";a.style.display="none";(document.getElementById("xjsd")||document.body).appendChild(a)}}c();
})()
;google.riu={render:function(){window.setTimeout(function(){var a=document.createElement("script");a.src="/extern_js/f/CgJlbhICaGsrMD84AiyAAg0/KB1t0AeW2FM.js";(document.getElementById("xjsd")||document.body).appendChild(a);},0);
}};;ManyBox.init();google.History&&google.History.initialize('/search?hl\x3den\x26amp;safe\x3dstrict\x26amp;q\x3d%22New%20event%20detection%20based%20on%20indexing-tree%20and%20named%20entity%22%20AND%20%22Term%20Committee%20Based%20Event%20Identification%20within%20News%20Topics%22\x26amp;meta\x3d\x26amp;aq\x3df\x26amp;aqi\x3dg1\x26amp;aql\x3d\x26amp;oq\x3d\x26amp;gs_rfai\x3d')});if(google.j&&google.j.en&&google.j.xi){window.setTimeout(google.j.xi,0);google.fade=null;}</script></div><script>(function(){
var b,d,e,f;function g(a,c){if(a.removeEventListener){a.removeEventListener("load",c,false);a.removeEventListener("error",c,false)}else{a.detachEvent("onload",c);a.detachEvent("onerror",c)}}function h(a){f=(new Date).getTime();++d;a=a||window.event;var c=a.target||a.srcElement;g(c,h)}var i=document.getElementsByTagName("img");b=i.length;d=0;for(var j=0,k;j<b;++j){k=i[j];if(k.complete||typeof k.src!="string"||!k.src)++d;else if(k.addEventListener){k.addEventListener("load",h,false);k.addEventListener("error",
h,false)}else{k.attachEvent("onload",h);k.attachEvent("onerror",h)}}e=b-d;function l(){google.timers.load.t.ol=(new Date).getTime();google.timers.load.t.iml=f;google.kCSI.imc=d;google.kCSI.imn=b;google.kCSI.imp=e;google.report&&google.report(google.timers.load,google.kCSI)}if(window.addEventListener)window.addEventListener("load",l,false);else if(window.attachEvent)window.attachEvent("onload",l);google.timers.load.t.prt=(f=(new Date).getTime());
})();
</script></div>     
'''
	data = GoogleResultParser().extract_from_source(html)
	print '---'
	for d in data:
		print d
	print '---'

