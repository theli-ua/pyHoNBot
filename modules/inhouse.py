"""
should announce inhouses
and track games people play together
"""

from hon.packets import ID
import re
from hon.honutils import normalize_nick


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
_re_split_color = re.compile(r'\^([0-9]{3}|[a-zA-Z\*\;\:])')
_re_split = re.compile(r'\w+')
def _check_ih(game_name,_ih_keywords,_ih_threshold):
    _ih_keywords = set(_ih_keywords)
    game_name = _re_split_color.sub('',game_name)
    keywords = set([w.lower() for w in _re_split.findall(game_name)])
    if len(keywords & _ih_keywords) >= _ih_threshold:
        return True
    return False

def _add_game(account_id,game_name,matchid,server,bot):
    key = (matchid,game_name)
    if key not in _games:
        _games[key] = Game(game_name,matchid,server)
        if _check_ih(game_name,bot.config.ih_keywords,bot.config.ih_threshold):
            bot.write_packet(ID.HON_CS_CLAN_MESSAGE,'{0}^* was started by ^r{1}^*, join up!'.format(game_name,bot.id2nick[account_id]))  
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

def status_update(bot,origin,data):
    #id,status,flags,clan_id,clan_name,chatsymbol,shield,icon
    #if ingame -> server,game name, matchid
    if data[0] in bot.clan_roster:
        if data[1] == ID.HON_STATUS_INGAME:
            _add_game(data[0],data[9],data[10],data[8],bot)
        else:
            _del_game(data[0])
status_update.event = [ID.HON_SC_UPDATE_STATUS]

def initiall_statuses(bot,origin,data):
    #id,status,flags
    #server, gamename
    for u in data[1]:
        if u[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
            _add_game(u[0],u[4],0,u[3],bot)
initiall_statuses.event = [ID.HON_SC_INITIAL_STATUS]

def ih(bot,input):
    """List inhouses"""
    inhouses = {}
    for game in _games.values():
        if len(game.players) >= bot.config.ih_min_players or _check_ih(game.name,bot.config.ih_keywords,bot.config.ih_threshold):
            players = [bot.id2nick[id] for id in game.players]
            inhouses[game.name] = '{0}^* [{1}]'.format(game.name,','.join(players))
    real_inhouses = []
    tmm = []
    for name in inhouses:
        if name.startswith('TMM'):
            tmm.append(name)
        else:
            real_inhouses.append(name)
    for s in [real_inhouses,tmm]:
        for name in s:
            bot.say(inhouses[name])

ih.commands = ['ih']

def ihadd(bot,input):
    """Add a keyword on match inhouse name"""
    if not input.admin:
        return
    bot.config.set_add('ih_keywords',input.group(2))
ihadd.commands = ['ihadd']

def ihdel(bot,input):
    """Add a keyword on match inhouse name"""
    if not input.admin:
        return
    bot.config.set_del('ih_keywords',input.group(2))
ihdel.commands = ['ihdel']

def setup(bot):
    bot.config.module_config('ih_min_players',[3,'Minimum players number to consider game an "inhouse"'])
    bot.config.module_config('ih_threshold',[1,'Minimum number of keywords found in game''s name to announce it'])
    bot.config.module_config('ih_keywords',[['ih','inhouse'],'Key words to be found in game name to consider game an "inhouse"'])
