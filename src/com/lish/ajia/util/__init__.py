# -*- coding: utf-8 -*-

# HTTP Errors found.
HTTPErrors = {
    #100: ('Continue', 'Request received, please continue'),
    #101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),

    #200: ('OK', 'Request fulfilled, document follows'),
    #201: ('Created', 'Document created, URL follows'),
    #202: ('Accepted', 'Request accepted, processing continues off-line'),
    #203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    #204: ('No Content', 'Request fulfilled, nothing follows'),
    #205: ('Reset Content', 'Clear input form for further input.'),
    #206: ('Partial Content', 'Partial content follows.'),

    #300: ('Multiple Choices', 'Object has several resources -- see URI list'),
    #301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    #302: ('Found', 'Object moved temporarily -- see URI list'),
    #303: ('See Other', 'Object moved -- see Method and URL list'),
    #304: ('Not Modified', 'Document has not changed since given time'),
    #305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
    #307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),

    400: ('Bad Request', 'Bad request syntax or unsupported method'),
    401: ('Unauthorized', 'No permission -- see authorization schemes'),
    402: ('Payment Required', 'No payment -- see charging schemes'),
    403: ('Forbidden', 'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed', 'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone', 'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
    417: ('Expectation Failed', 'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented', 'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable', 'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}



# download parameters
REQUEST_HEADER = [
	('User-agent', 'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; iCafeMedia; .NET CLR 2.0.50727; CIBA)'),
	('Accept', '*/*'),
	('Accept-Charset', 'gzip, deflate'),
	('Cookie', 'Tango_UserReference=38D8FF1624305B16496E9808; MTCCK=1; _csuid=48feeef505683659; cookmcnt=999; CID=1459382; cookMemberName=YunFan; cookMemberID=61448; savedEmail=liyunfan@genscriptcorp.com; DLDExec=OK; __utma=232384002.1655516880.1231991960.1231994793.1232000250.3; __utmb=232384002; __utmc=232384002; __utmz=232384002.1231991960.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none)'),
	('Accept-Language', 'en')
]

