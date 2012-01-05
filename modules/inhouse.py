"""
should announce inhouses
and track games people play together
"""

from hon.packets import ID

class Game:
    def __init__(self,gamename,matchid,server):
        self.name = gamename
        self.matchid = matchid
        self.server = server
        self.announced = False
        self.time = None
        self.players = set()
_games = {}
_id2game = {}
_min_players = 2
_ih_keywords = set(['inhouse','ih','funhouse'])
_ih_threshold = 1
def _check_ih(game_name):
    keywords = set([w.strip('^;;"').lower() for w in game_name.split(' ')])
    if len(keywords & _ih_keywords) >= _ih_threshold:
        return True
    return False

def _add_game(account_id,game_name,matchid,server,bot):
    key = (matchid,game_name)
    if key not in _games:
        _games[key] = Game(game_name,matchid,server)
        if _check_ih(game_name):
            bot.write_packet(ID.HON_CS_CLAN_MESSAGE,'^:{0} ^;was started,join up!'.format(game_name))  
            if hasattr(bot,'mumbleannounce'):
                bot.mumbleannounce('"{0}" was started,join up!'.format(game_name))
            _games[key].announced = True
    _games[key].players |= set([account_id])
    _id2game[account_id] = key

def _del_game(account_id):
    if account_id in _id2game:
        key = _id2game[account_id]
        _games[key].players -= set([account_id])
        if len(_games[key].players) == 0:
            del _games[key]
        del _id2game[account_id]

def status_update(bot,packet_id,data):
    #id,status,flags,clan_id,clan_name,chatsymbol,shield,icon
    #if ingame -> server,game name, matchid
    if data[1] == ID.HON_STATUS_INGAME:
        _add_game(data[0],data[9],data[10],data[8],bot)
    else:
        _del_game(data[0])
status_update.event = [ID.HON_SC_UPDATE_STATUS]

def initiall_statuses(bot,packet_id,data):
    #id,status,flags
    #server, gamename
    for u in data[1]:
        if u[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
            _add_game(u[0],u[4],0,u[3],bot)
initiall_statuses.event = [ID.HON_SC_INITIAL_STATUS]

def ih(bot,input):
    """List inhouses"""
    for game in _games.values():
        if len(game.players) >= _min_players or _check_ih(game.name):
            players = [bot.id2nick[id] for id in game.players]
            bot.say('{0} [{1}]'.format(game.name,','.join(players)))
ih.commands = ['ih']
