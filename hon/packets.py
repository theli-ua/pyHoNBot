import struct

class ID:
    #generic constants
    HON_CHAT_PORT = 11031
    HON_PROTOCOL_VERSION = 36

    HON_STATUS_OFFLINE    =  0
    HON_STATUS_ONLINE     =  3
    HON_STATUS_INLOBBY    =  4
    HON_STATUS_INGAME     =  5

    HON_FLAGS_PREPURCHASED =0x40
    HON_FLAGS_CHAT_NONE =0x00
    HON_FLAGS_CHAT_OFFICER =0x01
    HON_FLAGS_CHAT_LEADER =0x02
    HON_FLAGS_CHAT_ADMINISTRATOR =0x03
    HON_FLAGS_CHAT_STAFF =0x04
        
    

    #- Client -> Server
    HON_CS_PONG = 0x2A01
    HON_CS_CHANNEL_MSG = 0x03
    HON_CS_WHISPER = 0x08
    HON_CS_AUTH_INFO = 0x0C00
    HON_CS_BUDDY_ADD_NOTIFY = 0x0D
    HON_CS_JOIN_GAME = 0x10
    HON_CS_CLAN_MESSAGE = 0x13
    HON_CS_PM = 0x1C
    HON_CS_JOIN_CHANNEL = 0x1E
    HON_CS_WHISPER_BUDDIES = 0x20
    HON_CS_LEAVE_CHANNEL = 0x22
    HON_CS_USER_INFO = 0x2A
    HON_CS_UPDATE_TOPIC = 0x30
    HON_CS_CHANNEL_KICK = 0x31
    HON_CS_CHANNEL_BAN = 0x32
    HON_CS_CHANNEL_UNBAN = 0x33
    HON_CS_CHANNEL_SILENCE_USER = 0x38
    HON_CS_CHANNEL_PROMOTE = 0x3A
    HON_CS_CHANNEL_DEMOTE = 0x3B
    HON_CS_CHANNEL_AUTH_ENABLE = 0x3E
    HON_CS_CHANNEL_AUTH_DISABLE = 0x3F
    HON_CS_CHANNEL_AUTH_ADD = 0x40
    HON_CS_CHANNEL_AUTH_DELETE = 0x41
    HON_CS_CHANNEL_AUTH_LIST = 0x42
    HON_CS_CHANNEL_SET_PASSWORD = 0x43
    HON_CS_JOIN_CHANNEL_PASSWORD = 0x46
    HON_CS_CLAN_ADD_MEMBER = 0x47
    HON_CS_CLAN_REMOVE_MEMBER = 0x17
    HON_CS_CHANNEL_EMOTE = 0x65
    HON_CS_BUDDY_ACCEPT = 0xB3
    HON_CS_START_MM_GROUP = 0x0C0A
    HON_CS_INVITE_TO_MM = 0x0C0D
    HON_CS_KICK_FROM_MM = 0x0D00
    HON_CS_GLOBAL_MESSAGE = 0x39

    #- Server -> Client
    HON_SC_AUTH_ACCEPTED = 0x1c00
    HON_SC_PING = 0x2A00
    HON_SC_CHANNEL_MSG = 0x03
    HON_SC_CHANGED_CHANNEL = 0x04
    HON_SC_JOINED_CHANNEL = 0x05
    HON_SC_LEFT_CHANNEL = 0x06
    HON_SC_WHISPER = 0x08
    HON_SC_WHISPER_FAILED = 0x09
    HON_SC_INITIAL_STATUS = 0x0B
    HON_SC_UPDATE_STATUS = 0xC
    HON_SC_CLAN_MESSAGE = 0x13
    HON_SC_LOOKING_FOR_CLAN = 0x18
    HON_SC_PM = 0x1C
    HON_SC_PM_FAILED = 0x1D
    HON_SC_WHISPER_BUDDIES = 0x20
    HON_SC_MAX_CHANNELS = 0x21
    HON_SC_USER_INFO_NO_EXIST = 0x2B
    HON_SC_USER_INFO_OFFLINE = 0x2C
    HON_SC_USER_INFO_ONLINE = 0x2D
    HON_SC_USER_INFO_IN_GAME = 0x2E
    HON_SC_CHANNEL_UPDATE = 0x2F
    HON_SC_UPDATE_TOPIC = 0x30
    HON_SC_CHANNEL_KICK = 0x31
    HON_SC_CHANNEL_BAN = 0x32
    HON_SC_CHANNEL_UNBAN = 0x33
    HON_SC_CHANNEL_BANNED = 0x34
    HON_SC_CHANNEL_SILENCED = 0x35
    HON_SC_CHANNEL_SILENCE_LIFTED = 0x36
    HON_SC_CHANNEL_SILENCE_PLACED = 0x37
    HON_SC_GLOBAL_MESSAGE = 0x39
    HON_SC_CHANNEL_PROMOTE = 0x3A
    HON_SC_CHANNEL_DEMOTE = 0x3B
    HON_SC_CHANNEL_AUTH_ENABLE = 0x3E
    HON_SC_CHANNEL_AUTH_DISABLE = 0x3F
    HON_SC_CHANNEL_AUTH_ADD  =  0x40
    HON_SC_CHANNEL_AUTH_DELETE = 0x41 
    HON_SC_CHANNEL_AUTH_LIST = 0x42
    HON_SC_CHANNEL_PASSWORD_CHANGED = 0x43
    HON_SC_CHANNEL_ADD_AUTH_FAIL = 0x44
    HON_SC_CHANNEL_DEL_AUTH_FAIL = 0x45
    HON_SC_JOIN_CHANNEL_PASSWORD = 0x46
    HON_SC_CLAN_MEMBER_ADDED = 0x4E #not sure about that
    HON_SC_CLAN_MEMBER_CHANGE = 0x50
    HON_SC_NAME_CHANGE = 0x5A
    HON_SC_CHANNEL_EMOTE = 0x65
    HON_SC_CHANNEL_ROLL = 0x64
    HON_SC_TOTAL_ONLINE = 0x68
    HON_SC_REQUEST_NOTIFICATION = 0xB2
    HON_SC_NOTIFICATION = 0xB4
    HON_SC_TMM_GROUP_JOIN = 0xC0E
    HON_SC_TMM_GROUP_CHANGE = 0xD03


FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump(src, length=8):
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
    return result

def parse_channel_join(packet_id,data):
    origin = [packet_id,None,None]
    res,data = parse_part(data, 'sIBsI') #name,id,unk,topic,op_count
    ops = []
    for _ in xrange(res[-1]):
        tmp,data = parse_part(data,'IB') #id,flags
        ops.append(tmp)
    res.append(ops)
    tmp,data = parse_part(data,'I') # member count
    res.append(tmp)
    members = []
    for _ in xrange(tmp[0]):
        tmp,data = parse_part(data,'sIBBsss') #nick,id,status,flags,chatsymbol,shield,icon?
        members.append(tmp)
    res.append(members)
    return origin,res

def parse_initiall_statuses(packet_id,data):
    origin = [packet_id,None,None]
    res,data = parse_part(data,'I') #count
    buddies = []
    for _ in xrange(res[-1]):
        m,data = parse_part(data,'IBB') #id,status,flags
        if m[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
            tmp,data = parse_part(data,'ss') # server, gamename
            m.extend(tmp)
        else:
            m.extend([None,None])
        buddies.append(m)
    res.append(buddies)
    return origin,res

def parse_user_status(packet_id,data):
    origin = [packet_id,None,None]
    res,data = parse_part(data,'IBBIssss') #id,status,flags,clan_id,clan_name,chatsymbol,shield,icon
    if res[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
        tmp,data = parse_part(data,'s') #server
        res.append(tmp[0])
        if res[1] == ID.HON_STATUS_INGAME:
            tmp,data = parse_part(data,'sI') #game name, matchid
            res.extend(tmp)
    return origin,res


chat_packets = [ID.HON_SC_PM,ID.HON_SC_WHISPER,ID.HON_SC_CHANNEL_MSG,ID.HON_SC_CHANNEL_ROLL,ID.HON_SC_CHANNEL_EMOTE]
cs_structs = {
        ID.HON_CS_AUTH_INFO : 'IsssIIBIIsI',
        ID.HON_CS_PONG      : '',
        ID.HON_CS_JOIN_CHANNEL : 's',
        ID.HON_CS_PM : 'ss',
        ID.HON_CS_WHISPER : 'ss',
        ID.HON_CS_CHANNEL_MSG : 'sI',
        ID.HON_CS_CHANNEL_EMOTE : 'sI',
        ID.HON_CS_JOIN_CHANNEL : 's',
        ID.HON_CS_LEAVE_CHANNEL : 's',
        ID.HON_CS_USER_INFO : 's',
        ID.HON_CS_START_MM_GROUP : 'sHsssH',
        ID.HON_CS_INVITE_TO_MM : 's',
        ID.HON_CS_CHANNEL_KICK : 'II',
        ID.HON_CS_CHANNEL_BAN : 'Is',
        ID.HON_CS_CHANNEL_UNBAN : 'Is',
        ID.HON_CS_CHANNEL_SILENCE_USER : 'IsI',
        ID.HON_CS_UPDATE_TOPIC : 'Is',
        ID.HON_CS_CHANNEL_AUTH_ENABLE : 'I',
        ID.HON_CS_CHANNEL_AUTH_DISABLE : 'I',
        ID.HON_CS_CHANNEL_AUTH_ADD : 'Is',
        ID.HON_CS_CHANNEL_AUTH_DELETE : 'Is',
        ID.HON_CS_CHANNEL_PROMOTE : 'II',
        ID.HON_CS_CHANNEL_DEMOTE : 'II',
        ID.HON_CS_CLAN_ADD_MEMBER : 's',
        ID.HON_CS_CLAN_MESSAGE : 's',
        ID.HON_CS_GLOBAL_MESSAGE : 's',
        ID.HON_CS_CLAN_REMOVE_MEMBER : 'I',
        ID.HON_CS_KICK_FROM_MM : 'B',
        }
sc_structs = {
        ID.HON_SC_PING : '',
        ID.HON_SC_PM    : 'ss',
        ID.HON_SC_WHISPER : 'ss',
        ID.HON_SC_CHANNEL_MSG : 'IIs',
        ID.HON_SC_CHANNEL_EMOTE : 'IIs',
        ID.HON_SC_CHANNEL_ROLL : 'IIs',
        ID.HON_SC_CHANGED_CHANNEL : parse_channel_join,
        ID.HON_SC_INITIAL_STATUS  : parse_initiall_statuses,
        ID.HON_SC_UPDATE_STATUS : parse_user_status,
        ID.HON_SC_JOINED_CHANNEL : 'sIIBBsss', #nick,id,chat_id,status,flags,chatsymbol,shield,icon
        ID.HON_SC_CLAN_MEMBER_ADDED : 'I',
        ID.HON_SC_CLAN_MEMBER_CHANGE : 'IBI', #whom,wat,who (theli, promoted to officer, by visions)
        ID.HON_SC_NAME_CHANGE : 'Is',
        ID.HON_SC_CLAN_MESSAGE : 'Is',
        ID.HON_SC_LEFT_CHANNEL : 'II',
        ID.HON_SC_TOTAL_ONLINE : 'Is',
        ID.HON_SC_USER_INFO_NO_EXIST : 's',
        ID.HON_SC_USER_INFO_OFFLINE : 'ss',
        ID.HON_SC_USER_INFO_IN_GAME : 'sss',
        }
def pack(packet_id, *args):
    args = list(args)
    fmt = list(cs_structs[packet_id])
    for i,f in enumerate(fmt):
        if f == 's':
            #print (args[i].__class__.__name__)
            if isinstance(args[i],unicode):
                args[i] = args[i].encode('utf-8')
            fmt[i] = '{0}s'.format(1 + len(args[i]))
    fmt = ''.join(fmt)
    packet = struct.pack('<H' + fmt,packet_id,*args)
    #print(dump(packet))
    return packet
def parse_part(data,fmt):
    res = []
    for f in fmt:
        if f == 's':
            i = data.index('\0')
            res.append(data[:i].decode("utf-8"))
            #print res
            data = data[i+1:]
        else:
            f = '<' + f
            i = struct.calcsize(f)
            res.append(struct.unpack(f,data[:i])[0])
            data = data[i:]
    return res,data


def parse_packet(data):
    packet_id,data = parse_part(data,'H')
    packet_id = packet_id[0]
    origin = [packet_id,None,None]

    if packet_id in sc_structs:
        if hasattr(sc_structs[packet_id],'__call__'):
            return sc_structs[packet_id](packet_id,data)
        fmt = list(sc_structs[packet_id])
        res,data = parse_part(data,fmt)
        data = res
        if packet_id in chat_packets:
            origin[1] = data[0]
            if packet_id in [ID.HON_SC_CHANNEL_MSG,ID.HON_SC_CHANNEL_EMOTE,ID.HON_SC_CHANNEL_ROLL]:
                origin[2] = data[1]
                data = data[2]
            else:
                data = data[1]
    #else:
        #print 'unknown packet'
        #print(origin)
        #print(dump(data))
    #except:pass
    return origin,data
