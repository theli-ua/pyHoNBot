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
NA_MASTERSERVER = 'masterserver.hon.s2games.com'
SEA_GARENA_MASTERSERVER = 'masterserver.garena.s2games.com'
CIS_GARENA_MASTERSERVER = 'masterserver.cis.s2games.com'
MASTERSERVER = None
REGION = 'na'

def auth(login,password=None,pass_hash=None):
    if password is None and pass_hash is None:
        return None
    if pass_hash is None:
        pass_hash = md5(password).hexdigest()
    if REGION == 'na':
        query = { 'f' : 'auth' , 'login' : login, 'password' : pass_hash}
    else:
        from garena import get_garena_token
        garena_token = get_garena_token(login,pass_hash,REGION)
        query = {'f':'token_auth','token' : garena_token }
    return request(query)

def request(query,path = None,decode = True):
    if path is None:
        path = 'client_requester.php'
    details = urlencode(query,True).encode('utf8')
    url = Request('http://{0}/{1}'.format(MASTERSERVER, path),details, headers = {'X-Forwarded-For': 'unknown'})
    url.add_header("User-Agent",USER_AGENT)
    data = urlopen(url).read().decode("utf8", 'ignore')
    if decode:
        return loads(data)
    else:
        return data

def set_region(region):
    global REGION,MASTERSERVER
    if region == 'na':
        MASTERSERVER = NA_MASTERSERVER
    elif region == 'cis':
        MASTERSERVER = CIS_GARENA_MASTERSERVER
    elif region == 'sea':
        MASTERSERVER = SEA_GARENA_MASTERSERVER
    REGION = region

