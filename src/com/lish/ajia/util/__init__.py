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
	('Cookie', 'GSP=ID=95ba63df0d00168b:S=FFHb1eJV9OelrHwB; PREF=ID=95ba63df0d00168b:NW=1:TM=1369309949:LM=1369309949:S=mdYppCBNNzxpsV'),
#    ('Cookie', 'PREF=ID=ec3c076862e0b02b:U=cac317b6394968ad:LD=en:NR=10:NW=1:CR=2:TM=1330664473:LM=1335417048:GM=1:S=50GQeoV9xkTgrLrN; SS=DQAAAL0AAABvypgyHPqwSw0-rjn-XTDSRpzskVndpZ-rItaXJ7nFuYurPB1psFe9FyVm68eetmO04GnSt_yZ_bx3OZ_cEUcDpt8By3257clGanp-2YNVSvZHYZ5wyBmlh-Y1l8XWV3rLJaqyoXZ5gCZD_sZvrc6WRbGQedkXnMfKGak6rxPKeHp9E9otyK_d4zdLc-y5w2zf2dEQvOUwwxx-tsEkjs2Kd_I09h4qAUB81hORPnx78vFJZ917KoDAdOSzBc8TGWE; HSID=A0_nqPOdpqC042XTn; APISID=Ff1hrOKL1Z7wYBcf/AosfTiZgxii-N7NFo; GSP=ID=ec3c076862e0b02b:IN=e5ffd187aee42e82+8b9a455bd1c58d67:CF=4:UI=1:S=v2gHmeovcUDrBDUT; NID=60=AqhxHbvNGgXuytsC3ZH-hf5Egwye_6UoWoJRrHBSn0hlmb9Zpj5jc7Rf4i7U7gtdKaEk-G4wf_JpZFp6lPwSIhKHcp-MwPLYT1b5HRhBLUJoanR1paNxec6goOGAwPoMYvykytG22FZ4H7lImLG-V9EKGCE6qG8vTmN0NzCBDmCN4D77_B_6qUOi7QI; GDSESS=ID=74c0ae72a299270f:TM=1338800889:C=c:IP=166.111.134.53-:S=ADSvE-cUtJiPIgpC4XwuimeW8fipwOtgEA; SID=DQAAAC4BAAB31ZEj49yN182_gq2_DX6OqtCe9AGhXaD4FwRWtvNZmxBB-d4zctSWtsK_KNQIvH9vJ26dFG1usmUtt8_a1SOP8qFUCnkPnGuDSl8-jkHjBfEOAEKSQBZSOU3qKOsSB05JVTcGvyL3GYUrozeHpDs8GaAafpJdlxNln85ZGS_WPHgNbvSl5fbisovVV1xNPRhilfxFU5tTluitFWh_0L5dtPgFKmbiV4wKEAV2xTef5VDVAro3JjLgQRVJciNqLFJxvgYCJet6AaxQRKYGl97P_KCb3CRWzLE5c918YBEsgIHyxp-93tZS9xPryjkXSCsG1N95h2DzkaxeQaa13X-hwSohxk2feW8jkAlGLv2IL3J1RNzIg8c0EsMIdUXYE8nMgi-mCr5dJDEZXwWXa3nE'),
	('Accept-Language', 'en')
]
