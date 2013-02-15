from utils.phpserialize import *
from hashlib import md5,sha256
import json
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
from urllib import quote_plus
USER_AGENT = "S2 Games/Heroes of Newerth/2.6.32.2/lac/x86-biarch"
NA_MASTERSERVER = 'masterserver.hon.s2games.com'
SEA_GARENA_MASTERSERVER = 'masterserver.garena.s2games.com'
CIS_GARENA_MASTERSERVER = 'masterserver.cis.s2games.com'
LA_MASTERSERVER = 'masterserver.lat.s2games.com'
MASTERSERVER = None
REGION = 'na'

API_URL = "api.heroesofnewerth.com"

s2_n = 'DA950C6C97918CAE89E4F5ECB32461032A217D740064BC12FC0723CD204BD02A7AE29B53F3310C13BA998B7910F8B6A14112CBC67BDD2427EDF494CB8BCA68510C0AAEE5346BD320845981546873069B337C073B9A9369D500873D647D261CCED571826E54C6089E7D5085DC2AF01FD861AE44C8E64BCA3EA4DCE942C5F5B89E5496C2741A9E7E9F509C261D104D11DD4494577038B33016E28D118AE4FD2E85D9C3557A2346FAECED3EDBE0F4D694411686BA6E65FEE43A772DC84D394ADAE5A14AF33817351D29DE074740AA263187AB18E3A25665EACAA8267C16CDE064B1D5AF0588893C89C1556D6AEF644A3BA6BA3F7DEC2F3D6FDC30AE43FBD6D144BB'
s2_g = '2'

def srp_auth(login,password):
    import srp
    query = { 'f' : 'pre_auth' , 'login' : login}
    usr = srp.User( login, None, hash_alg=srp.SHA256, ng_type=srp.NG_CUSTOM, n_hex = s2_n , g_hex = s2_g )
    _, A = usr.start_authentication()
    query['A'] = A.encode('hex')
    res = request(query)
    if 'B' not in res: return res
    s = res['salt'].decode('hex')
    B = res['B'].decode('hex')
    salt2 = res['salt2']
    usr.password = sha256(md5(md5(password).hexdigest() + salt2 + '[!~esTo0}').hexdigest() + 'taquzaph_?98phab&junaj=z=kuChusu').hexdigest()
    usr.p = usr.password
    M = usr.process_challenge( s, B )
    del(query['A'])
    query['f'] = 'srpAuth'
    query['proof'] = M.encode('hex')
    res = request(query)
    return res

def auth(login,password=None,pass_hash=None):
    if REGION == 'na' :
       return srp_auth(login,password)
    if password is None and pass_hash is None:
        return None
    if pass_hash is None:
        pass_hash = md5(password).hexdigest()
    if REGION == 'na' or REGION == 'la':
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
    try:
        data = urlopen(url).read().decode("utf8", 'ignore')
    except:
        print("Error querying masterservers")
        return None
    if decode:
        return loads(data)
    else:
        return data

def api_request(apikey, path):
    url = 'http://{0}/{1}?token={2}'.format(API_URL, quote_plus(path, '/'), apikey)
    try:
        data = urlopen(url, None, 3).read()
        return json.loads(data)
    except Exception as e:
        print "Error querying HoNAPI:", e
        return None

def set_region(region):
    global REGION,MASTERSERVER
    if region == 'na':
        MASTERSERVER = NA_MASTERSERVER
    elif region == 'cis':
        MASTERSERVER = CIS_GARENA_MASTERSERVER
    elif region == 'sea':
        MASTERSERVER = SEA_GARENA_MASTERSERVER
    elif region == 'la':
        MASTERSERVER = LA_MASTERSERVER
    REGION = region