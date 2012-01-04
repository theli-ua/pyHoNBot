from utils.phpserialize import *
from hashlib import md5
try:
    #3.x
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.parse import urlencode
except:
    #2.7
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib import urlencode

USER_AGENT = "S2 Games/Heroes of Newerth/2.3.5.1/lac/x86-biarch"
MASTERSERVER = 'masterserver.hon.s2games.com'

def auth(login,password=None,pass_hash=None):
    if password is None and pass_hash is None:
        return None
    if pass_hash is None:
        pass_hash = md5(password).hexdigest()
    query = { 'f' : 'auth' , 'login' : login, 'password' : pass_hash}
    return request(query)

def request(query,path = None,decode = True):
    if path is None:
        path = 'client_requester.php'
    details = urlencode(query,True).encode('utf8')
    url = Request('http://{0}/{1}'.format(MASTERSERVER, path),details)
    url.add_header("User-Agent",USER_AGENT)
    data = urlopen(url).read().decode("utf8", 'ignore')
    if decode:
        return loads(data)
    else:
        return data

