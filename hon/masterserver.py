from utils.phpserialize import *
from urllib2 import *
from hashlib import md5

MASTERSERVER_URL = 'http://masterserver.hon.s2games.com/'

def auth(login,password=None,pass_hash=None):
    if password is None and pass_hash is None:
        return None
    if pass_hash is None:
        pass_hash = md5(password).hexdigest()
    req = Request(MASTERSERVER_URL + 'client_requester.php?f=auth&login=%s&password=%s'%(login, pass_hash))
    masterserver_response = urlopen(req).read()
    masterserver_dict = loads(masterserver_response)
    return masterserver_dict

