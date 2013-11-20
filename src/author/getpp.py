import urllib2
import urllib
import re
import time
class buildPP():
    import socket
    def __init__(self):
        self.socket.setdefaulttimeout(3.0)
        self.urls=['http://www.youdaili.cn/Daili/guowai/1211.html',
                  'http://www.youdaili.cn/Daili/guowai/1211_2.html',
                  #'http://www.youdaili.cn/Daili/guowai/1211_3.html',
                 #'http://www.youdaili.cn/Daili/guonei/1211_4.html',
                  #'http://www.youdaili.cn/Daili/guonei/1211_5.html',
                  #'http://www.youdaili.cn/Daili/guonei/1115_6.html'
                  ]

    def getprobyurl(self,url):
        pattern = re.compile(r"""\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,}""")
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()
        proxies = pattern.findall(data)
        return proxies
    def getpp(self,c):
        pp = []
        if c == 1:
          for url in self.urls:
            print url
            proxies = self.getprobyurl(url)
            pp.extend(proxies)
          print pp
        elif c==2:
          f = open(r'C:\Python27\author\author\pp.txt','r',)
          for ps in f.readlines():
            pp.append(ps)
          f.close()
        elif c == 3:
          f = open (r'C:\Python27\author\author\validpp.txt','r')
          for ps in f.readlines():
            pp.append(ps)
          f.close()
        elif c ==4:
          f = open(r'C:\Python27\author\author\extraproxies.txt','r')
          for ps in f.readlines():
            pp.append(ps)
          f.close()
        return pp




        
