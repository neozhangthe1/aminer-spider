# -*- coding: utf-8 -*-
import simplejson
import urllib2

# This example request includes an optional API key which you will need to
# remove or replace with your own key.
# Read more about why it's useful to have an API key.
# The request also includes the userip parameter which provides the end
# user's IP address. Doing so will help distinguish this legitimate
# server-side traffic from traffic which doesn't come from an end-user.
#url = ('http://ajax.googleapis.com/ajax/services/search/web'
#       '?v=1.0&q=Paris%20Hilton')
url = '''http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%22Asymptotic%20inference%20for%20spatial%20CDFs%20over%20time%22%20AND%20%22Comparison%20of%20spatial%20variables%20over%20subregions%20using%20a%20block%20bootstrap.%20Journal%20of%20Agricultural,%20Biological,%20and%20Environmental%20Statistics%22'''
request = urllib2.Request(
    url, None, {'Referer': 'a.org' })
response = urllib2.urlopen(request)

# Process the JSON string.
results = simplejson.load(response)
# now have some fun with the results...

print results
