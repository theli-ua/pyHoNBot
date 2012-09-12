from datetime import timedelta

depend = ['honstringtables']
GAME_MODES = [("nm","ap"),"sd","rd","dm","bd","bp","cd","cm","ar","league",("cas","casual")]
#'smackdown'
#'bloodlust'
#'annihilation'
#'doublekill'
#'quadkill'
#'ks3'
#'ks4'
#'ks5'
#'ks6'
#'ks7'
#'ks8'
#'ks9'
#'ks10'
#'ks15'
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
                for i in GAME_MODES:
                    if isinstance(i,tuple):
                        key = i[0]
                        val = i[1]
                    else:
                        key = val = i
                    try:
                        if summary[key] == "1":
                            mode.append(val)
                    except:pass
                match_stats['mode'] = '[' + ','.join(mode) + ']'
                match_stats['name'] = summary['mname']
                match_stats['mdt'] = summary['mdt']
                match_stats['len'] = str(timedelta(seconds = int(summary['time_played'])))
                match_stats['date'] = summary['mdt']
                match_type = summary['class']

                #player stats
                player_stats = match['match_player_stats'].values()[0]
                if player.lower() in bot.nick2id:
                    player_stats = player_stats[bot.nick2id[player.lower()]]
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
                match_stats['ckn'] = player_stats['neutralcreepkills']

                if player_stats['wins'] == '1':
                    match_stats['outcome'] = 'WIN'
                else:
                    match_stats['outcome'] = 'LOSS'

                if match_stats['name'].startswith('TMM'):
                    match_stats['rating_type'] = 'MMR'
                else:
                    match_stats['rating_type'] = 'PSR'

                match_stats['wards'] = player_stats['wards']
                time = float(summary['time_played']) / 60.0
                match_stats['xpm'] = float(player_stats['exp'])/time
                match_stats['gpm'] = float(player_stats['gold'])/time
                match_stats['apm'] = float(player_stats['actions'])/time
                match_stats['nick'] = player_stats['nickname']

                if match_stats['hero'] + '_name' in bot.stringtables:
                    match_stats['hero'] = bot.stringtables[match_stats['hero'] + '_name']
                elif match_stats['hero'].startswith('Hero_'):
                    match_stats['hero'] = match_stats['hero'][5:]

                bot.say(bot.config.honstats_match.format(**match_stats))
match.commands = ['match']

def rstats(bot,input):
    """Get ranked (mm) stats for [player] .. nick is optional"""
    get_stats(bot,input,'ranked')
rstats.commands = ['rstats','stats']
def cstats(bot,input):
    """Get casual (mm) stats for [player] .. nick is optional"""
    get_stats(bot,input,'casual')
cstats.commands = ['cstats']
def player_stats(bot,input):
    """Get public stats for [player] .. nick is optional"""
    get_stats(bot,input,'player')
player_stats.commands = ['pstats']


def get_stats(bot,input,table,hero=None):
    if hero is None:
        player = input.group(2)
    else:
        player = input.group(3)
    if player is None:
        player = input.nick
    query = {'nickname' : player}
    if hero is None:
        query['table'] = table
        query['f'] = 'show_stats'
    else:
        query['f'] = 'get_hero_stats'
        query['hero'] = hero
    stats_data = bot.masterserver_request(query,cookie=True)
    
    stats = {'nick' : player}
    mapping = { 
            'ranked' :
            { 
                'rating' : 'rnk_amm_team_rating',
                'matches' : 'rnk_games_played',
                'wins' : 'rnk_wins',
                'gold' : 'rnk_gold',
                'exp_time' : 'rnk_time_earning_exp',
                'secs' : 'rnk_secs',
                'xp'    : 'rnk_exp',
                'ck'    : 'rnk_teamcreepkills',
                'cd'    : 'rnk_denies',
                'actions':'rnk_actions',
                'K'     : 'rnk_herokills',
                'D'     : 'rnk_deaths',
                'A'     : 'rnk_heroassists',
                'wards' : 'rnk_wards',
                'neuts' : 'rnk_neutralcreepkills',
                },
            'casual' :
            { 
                'rating' : 'cs_amm_team_rating',
                'matches' : 'cs_games_played',
                'wins' : 'cs_wins',
                'gold' : 'cs_gold',
                'exp_time' : 'cs_time_earning_exp',
                'secs' : 'cs_secs',
                'xp'    : 'cs_exp',
                'ck'    : 'cs_teamcreepkills',
                'cd'    : 'cs_denies',
                'actions':'cs_actions',
                'K'     : 'cs_herokills',
                'D'     : 'cs_deaths',
                'A'     : 'cs_heroassists',
                'wards' : 'cs_wards',
                'neuts' : 'cs_neutralcreepkills',
                },
            'player' :
            { 
                'rating' : 'acc_pub_skill',
                'matches' : 'acc_games_played',
                'wins' : 'acc_wins',
                'gold' : 'acc_gold',
                'exp_time' : 'acc_time_earning_exp',
                'secs' : 'acc_secs',
                'xp'    : 'acc_exp',
                'ck'    : 'acc_teamcreepkills',
                'cd'    : 'acc_denies',
                'actions':'acc_actions',
                'K'     : 'acc_herokills',
                'D'     : 'acc_deaths',
                'A'     : 'acc_heroassists',
                'wards' : 'acc_wards',
                'neuts' : 'acc_neutralcreepkills',
                },
            'hero_ranked':
                {
                'rating' : 'rnk_ph_amm_team_rating',
                'matches' : 'rnk_ph_used',
                'wins' : 'rnk_ph_wins',
                'gold' : 'rnk_ph_gold',
                'exp_time' : 'rnk_ph_time_earning_exp',
                'secs' : 'rnk_ph_secs',
                'xp'    : 'rnk_ph_exp',
                'ck'    : 'rnk_ph_teamcreepkills',
                'cd'    : 'rnk_ph_denies',
                'actions':'rnk_ph_actions',
                'K'     : 'rnk_ph_herokills',
                'D'     : 'rnk_ph_deaths',
                'A'     : 'rnk_ph_heroassists',
                'wards' : 'rnk_ph_wards',
                'neuts' : 'rnk_ph_neutralcreepkills',
                },
            'hero_pub' :
                {
                'rating' : 'ph_pub_skill',
                'matches' : 'ph_used',
                'wins' : 'ph_wins',
                'gold' : 'ph_gold',
                'exp_time' : 'ph_time_earning_exp',
                'secs' : 'ph_secs',
                'xp'    : 'ph_exp',
                'ck'    : 'ph_teamcreepkills',
                'cd'    : 'ph_denies',
                'actions':'ph_actions',
                'K'     : 'ph_herokills',
                'D'     : 'ph_deaths',
                'A'     : 'ph_heroassists',
                'wards' : 'ph_wards',
                'neuts' : 'ph_neutralcreepkills',
                },
            'hero_casual':
                {
                'rating' : 'cs_ph_amm_team_rating',
                'matches' : 'cs_ph_used',
                'wins' : 'cs_ph_wins',
                'gold' : 'cs_ph_gold',
                'exp_time' : 'cs_ph_time_earning_exp',
                'secs' : 'cs_ph_secs',
                'xp'    : 'cs_ph_exp',
                'ck'    : 'cs_ph_teamcreepkills',
                'cd'    : 'cs_ph_denies',
                'actions':'cs_ph_actions',
                'K'     : 'cs_ph_herokills',
                'D'     : 'cs_ph_deaths',
                'A'     : 'cs_ph_heroassists',
                'wards' : 'cs_ph_wards',
                'neuts' : 'cs_ph_neutralcreepkills',
                },
        }
    for k,v in mapping[table].iteritems():
        stats[k] = stats_data[v]
    total = float(stats['matches'])
    wins = float(stats['wins'])
    if total == 0.0 or wins == 0.0:
        stats['win_percent'] = 0.0
    else:
        stats['win_percent'] = wins/total
    #averages per game
    for stat in [('K','avg_K'), ('D','avg_D'), ('A','avg_A'), ('ck','avg_ck'),
            ('cd','avg_cd'), ('wards','avg_wards'),('neuts','avg_ckn'),
            ('exp_time','avg_len')]:
        if int(stats['matches']) > 0:
            stats[stat[1]] = float(stats[stat[0]])/float(stats['matches'])
        else:
            stats[stat[1]] = 0.0
    #averages per minute
    for stat in [('gold','gpm'), ('xp','xpm'), ('actions','apm')]:
        if stats['exp_time'] > 0:
            stats[stat[1]] = float(stats[stat[0]]) / (float(stats['exp_time']) / 60.0)
        else:
            stats[stat[1]] = 0

    stats['avg_len'] = str(timedelta(seconds=int(stats['avg_len'])))
    if hero is None:
        stats['hero'] = ''
    else:
        stats['hero'] = bot.stringtables[hero + '_name']

    if table == 'player' or table == 'hero_pub':
        stats['rating_type'] = 'PSR'
    else:
        stats['rating_type'] = 'MMR'
    print( "Debug: exp_time: %f, matches: %f" % (float(stats['exp_time']), float(stats['matches'])) )
    stats['TSR'] = ((float(stats['K'])/float(stats['D'])/1.15)*0.65)+\
            ((float(stats['A'])/float(stats['D'])/1.55)*1.20)+\
            (((float(stats['wins'])/(float(stats['matches'])))/0.55)*0.9)+\
            (((float(stats['gold'])/float(stats['exp_time'])*60)/230)*(1-((230/195)*((0.0/float(stats['matches'])))))*0.35)+\
            ((((float(stats['xp'])/float(stats['exp_time'])*60)/380)*(1-((380/565)*(0.0/float(stats['matches'])))))*0.40)+\
            ((((((float(stats['cd'])/float(stats['matches']))/12)*(1-((4.5/8.5)*(0.0/float(stats['matches'])))))*0.70)+\
            ((((float(stats['ck'])/float(stats['matches']))/93)*(1-((63/81)*(0.0/float(stats['matches'])))))*0.50)+\
            ((float(stats['wards'])/float(stats['matches']))/1.45*0.30))*(37.5/(float(stats['exp_time'])/float(stats['matches'])/60)))

    bot.say(bot.config.honstats_player.format(**stats))

def hero_stats(bot,input):
    table = 'hero_ranked'
    if input.group(2) == 'p':
        table = 'hero_pub'
    elif input.group(2) == 'c':
        table = 'hero_casual'
    get_stats(bot,input,table=table,hero=bot.heroshorts[input.group(1).lower()])

def setup(bot):
    bot.config.module_config('honstats_match',['{nick} {hero}[{lvl}] {rating}{rating_type} {outcome} ^g{K}^*/^r{D}^*/^b{A}^* {name}{mode} {len}^:|^;CK:{ck}+{ckn} CD:{cd}^:|^;X:{xpm:.2f} G:{gpm:.2f} A:{apm:.2f}^:|^;W:{wards}^:|^;{mdt}','Python format string for match stats output'])
    bot.config.module_config('honstats_player',['{nick} {hero} ^g{rating}^*{rating_type} ^g{win_percent:.2%}^*({wins}/{matches})^:|^;^g{avg_K:.2f}^*/^r{avg_D:.2f}^*/^b{avg_A:.2f}^*^:|^;X:{xpm:.2f} G:{gpm:.2f} A:{apm:.2f}^:|^;CK:{avg_ck:.2f}+{avg_ckn:.2f} CD:{avg_cd:.2f}^:|^;{avg_len}^:|^;W {avg_wards:.2f}','Python format string for player stats output'])
    if hasattr(bot,'heroshorts'):
        hero_stats.rule = '(?i)' + bot.config.prefix + r'({0})(?:[^\ ]*\ +(?:(p|c)\ +)?(.+))?'.format('|'.join(bot.heroshorts.keys()))
