from datetime import timedelta

MATCH_FORMAT_STRING = '{nick} {hero}[{lvl}] {outcome} ^g{K}^*/^r{D}^*/^y{A}^* {name}{mode} {len} ^:|^; CK:{ck} CD:{cd} ^:|^; XPM:{xpm:g} GPM:{gpm:g} ^:|^; WARDS:{wards} ^:|^; {mdt}'
PLAYER_STATS_FORMAT = '{nick} ^g{rating}^* WIN^g{win_percent:.2%}^*({matches} played) ^:|^; Average stats ^r^:=>^*^; len: {len} ^:|^; CK:{ck} CD:{cd} ^:|^; XPM:{xpm:g} GPM:{gpm:g} APM:{apm} ^:|^; K/D/A {kda} ^:|^; WARDS {wards}'
def match(bot,input):
    """Show last match info for player (or command sender if unspecified)"""
    player = input.group(2)
    if player is None:
        player = input.nick
    query = { 'f' : 'grab_last_matches_from_nick', 'nickname' : player }
    matches = bot.masterserver_request(query)
    if not matches[0]:
        bot.reply("Couldn't grab last matches for {0}".format(player))
    else:
        matches = sorted(matches['last_stats'].keys())
        if len(matches) < 1 or matches[0] == 'error':
            bot.reply("No matches played")
        else:
            matchid = matches[-1]
            match = bot.masterserver_request({'f':'get_match_stats','match_id[]':[matchid]},cookie = True)
            summary = match['match_summ']
            if matchid not in summary:
                bot.reply('Couldn''t grab info on latest match for {0}'.format(player))
            else:
                summary = summary[matchid]
                match_stats = {}
                #game settings
                mode = []
                for i in ["nm","sd","rd","dm","bd","bp","cd","cm","league"]:
                    try:
                        if summary[i] == "1":
                            mode.append(i)
                    except:pass
                match_stats['mode'] = '[' + ','.join(mode) + ']'
                match_stats['name'] = summary['mname']
                match_stats['mdt'] = summary['mdt']
                match_stats['len'] = str(timedelta(seconds = int(summary['time_played'])))
                match_stats['date'] = summary['mdt']
                match_type = summary['class']

                #player stats
                player_stats = match['match_player_stats'].values()[0]
                if player in bot.nick2id:
                    player_stats = player_stats[bot.nick2id[player]]
                else:
                    for id in player_stats.keys():
                        if player_stats[id]['nickname'].lower() == player.lower():
                            player_stats = player_stats[id]
                            break
                if match_type == "1":
                    match_stats['rating'] = player_stats['pub_skill']
                else:
                    match_stats['rating'] = player_stats['amm_team_rating']
                match_stats['D'] = player_stats['deaths']
                match_stats['K'] = player_stats['herokills']
                match_stats['A'] = player_stats['heroassists']
                match_stats['hero'] = player_stats['cli_name']
                match_stats['ck'] = player_stats['teamcreepkills']
                match_stats['cd'] = player_stats['denies']
                match_stats['lvl'] = player_stats['level']

                if player_stats['wins'] == '1':
                    match_stats['outcome'] = 'WIN'
                else:
                    match_stats['outcome'] = 'LOSS'
                
                match_stats['wards'] = player_stats['wards']
                time = float(summary['time_played']) / 60.0
                match_stats['xpm'] = float(player_stats['exp'])/time
                match_stats['gpm'] = float(player_stats['gold'])/time
                match_stats['nick'] = player_stats['nickname']

                if match_stats['hero'] + '_name' in bot.stringtables:
                    match_stats['hero'] = bot.stringtables[match_stats['hero'] + '_name']
                elif match_stats['hero'].startswith('Hero_'):
                    match_stats['hero'] = match_stats['hero'][5:]

                bot.say(MATCH_FORMAT_STRING.format(**match_stats))
match.commands = ['match']

def rstats(bot,input):
    """Get ranked (mm) stats for [player] .. nick is optional"""
    get_stats(bot,input,'ranked')
rstats.commands = ['rstats']
def cstats(bot,input):
    """Get casual (mm) stats for [player] .. nick is optional"""
    get_stats(bot,input,'casual')
cstats.commands = ['cstats']
def player_stats(bot,input):
    """Get public stats for [player] .. nick is optional"""
    get_stats(bot,input,'player')
player_stats.commands = ['stats']


def get_stats(bot,input,table):
    player = input.group(2)
    if player is None:
        player = input.nick
    query = { 'f' : 'show_stats', 'nickname' : player, 'table' : table }
    stats_data = bot.masterserver_request(query)
    
    stats = {'nick' : player}
    common = { 
            'len' : 'avgGameLength',
            'xpm' : 'avgXP_min',
            'ck' : 'avgCreepKills',
            'cd' : 'avgDenies',
            'wards' : 'avgWardsUsed',
            'apm' : 'avgActions_min',
            'kda' : 'k_d_a',
            }
    mapping = { 
            'ranked' :
            { 
                'rating' : 'rnk_amm_team_rating',
                'matches' : 'rnk_games_played',
                'wins' : 'rnk_wins',
                'gold' : 'rnk_gold',
                'exp_time' : 'rnk_time_earning_exp',
            },
            'casual' :
            { 
                'rating' : 'cs_amm_team_rating',
                'matches' : 'cs_games_played',
                'wins' : 'cs_wins',
                'gold' : 'cs_gold',
                'exp_time' : 'cs_time_earning_exp',
            },
            'player' :
            { 
                'rating' : 'acc_pub_skill',
                'matches' : 'acc_games_played',
                'wins' : 'acc_wins',
                'gold' : 'acc_gold',
                'exp_time' : 'acc_time_earning_exp',
            }
            }
    for d in [common,mapping[table]]:
        for k,v in d.iteritems():
            stats[k] = stats_data[v]
    total = float(stats['matches'])
    wins = float(stats['wins'])
    if total == 0.0 or wins == 0.0:
        stats['win_percent'] = 0.0
    else:
        stats['win_percent'] = wins/total
    stats['gpm'] = float(stats['gold']) / (float(stats['exp_time']) / 60.0)
    stats['len'] = str(timedelta(seconds=int(stats['len'])))
    bot.say(PLAYER_STATS_FORMAT.format(**stats))
