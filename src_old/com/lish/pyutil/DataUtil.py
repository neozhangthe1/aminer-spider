# -*- coding: utf-8 -*-
'''
Runner Platform Module: DB
KEG | elivoa | gmail.com
Time-stamp: "root 2010/09/24 13:04:13"
'''
import re
import urllib2

class GoogleDataCleaner():
    def __init__(self):
        pass
    
    @staticmethod
    def cleanGoogleTitle(title):
        has_dot = False
        titleCleaned = title
        # clean step 1
        
        # BUGFIX: don't remove [xxx]. eg: "OQL[C++]: Ext..."
        # titleCleaned = re.sub("(\[(.*?)\]|<(.*?)>)", "", titleCleaned)
        titleCleaned = re.sub("(<(.*?)>)", "", titleCleaned)
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


class URLCleaner():
    @staticmethod
    def encodeUrlForDownload(url):
        return urllib2.quote(url, safe=":/[]")
        # return url.replace(" ", "%20").replace("\"", "%22").replace("+", "%2B")



if __name__ == "__main__":
    a = "OQL[C++]: Extending C++ with an Object Query Capability."
    print a
    print GoogleDataCleaner.cleanGoogleTitle(a)
    print urllib2.quote(a, safe=":/[]")




