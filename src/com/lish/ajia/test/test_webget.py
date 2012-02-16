'''
Created on Nov 2, 2011

@author: bogao
'''
from com.lish.ajia.util.web import HtmlRetriever
class TestWebGet:
	pass

if __name__ == '__main__':
	url = 'http://scholar.google.com/scholar?hl=en&num=100&q=%22A%20fast%20algorithm%20for%20computing%20distance%20spectrum%20of%20convolutional%20codes.%22OR%22A%20new%20upper%20bound%20on%20the%20first-event%20error%20probability%20for%20maximum-likelihood%20decoding%20of%20fixed%20binary%20convolutional%20codes.%22'
	htmlRetriever = HtmlRetriever.getInstance(False)
	html = htmlRetriever.getHtmlRetry(url)
	print html[0:300], "..."
	
	
