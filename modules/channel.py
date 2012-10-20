# -*- coding: utf8 -*-
from hon.packets import ID
from time import sleep
from datetime import datetime
from hon.honutils import normalize_nick
from hon.honutils import user_upgrades
import re

def setup(bot):
    bot.channel_channels = {}
    bot.not_smurfs = []
    bot.config.module_config('channel_limit',[0,'Will try to keep channel at this limit kicking afk non-clanmates'])
    bot.config.module_config('silence_smurfs',[-1,'Will silence anyone with normal mode tmm wins equal or lower than this'])
    bot.config.module_config('spam_threshold',[0,'number of seconds, if user repeats his message in channel with delay lower than this he will be considered spamming and banned'])
    bot.config.module_config('whitelist',[[],'whitelist for antispam etc'])
    bot.config.module_config('clanwhitelist', [[], 'Clan whitelist'])
    bot.config.module_config('default_topic', [[], 'Default Topics'])

silenced = {}

def getTopic(bot, cname):
    if isinstance(bot.config.default_topic, dict):
        bot.config.set('default_topic', [])
    for topic in bot.config.default_topic:
        if not isinstance(topic, dict): break
        if topic['name'] == cname:
            return topic['topic']
    return False
def setTopic(bot, cname, topic):
    curr = bot.config.default_topic
    found = False
    for key,item in enumerate(curr):
        if not isinstance(item, dict): break
        if item['name'] == cname:
            found = True
            curr[key]['topic'] = topic
    if not found:
        curr.append({"name": cname, "topic": topic})
    bot.config.set('default_topic', curr)

def silence_smurfs(bot,chanid,nick):
    if bot.config.silence_smurfs < 0:
        return
    if (nick,chanid) in silenced:
        return
    if nick in bot.nick2id and bot.nick2id[nick] in bot.clan_roster:
        return
    if nick in bot.not_smurfs or nick in bot.config.whitelist:
        return
    if bot.nick2clan[nick].lower() in bot.config.clanwhitelist:
        return
    query = {'nickname' : nick,'f': 'show_stats','table': 'ranked'}
    stats_data = bot.masterserver_request(query,cookie=True)
    if 'rnk_wins' not in stats_data:
        bot.err("Received malformed data from masterserver")
        return
    if int(stats_data['rnk_wins']) <= bot.config.silence_smurfs:
        bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER, chanid, nick, 0x7fffffff)
        silenced[(nick,chanid)] = True
    else:
        bot.not_smurfs.append(nick)

def channel_joined_channel(bot,origin,data):
    bot.channel_channels[data[1]] = dict([[m[1],[m[1],m[0],datetime.now(),None]] for m in data[-1]])
    for m in data[-1]:
        if m[1] in bot.clan_roster:
            if not 'upgrades' in bot.clan_roster[m[1]]:
                bot.clan_roster[m[1]]['upgrades'] = user_upgrades(m)
    # Default topic setting
    topic = data[3]
    if ( len(topic) == 0 ) or ( topic == "Welcome to the {0} clan channel!".format( bot.clan_info['name'] ) ):
        cname = bot.id2chan[data[1]]
        if getTopic(bot, cname):
            bot.write_packet( ID.HON_CS_UPDATE_TOPIC, data[1], getTopic(bot, cname) )

channel_joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]

def channel_user_joined_channel_smurfs(bot,origin,data):
    nick = normalize_nick(data[0]).lower()
    silence_smurfs(bot,data[2],nick)
channel_user_joined_channel_smurfs.event = [ID.HON_SC_JOINED_CHANNEL]
channel_user_joined_channel_smurfs.thread = True

def channel_user_joined_channel(bot,origin,data):
    if data[2] not in bot.channel_channels:
        bot.channel_channels[data[2]] = {}
    bot.channel_channels[data[2]][data[1]] = [data[1],data[0],datetime.now(),None]
    l = len(bot.channel_channels[data[2]])
    CHANNEL_MAX = bot.config.channel_limit
    #banlist management
    nick = normalize_nick(data[0]).lower()
    if data[1] in bot.clan_roster:
        if not 'upgrades' in bot.clan_roster[data[1]]:
            bot.clan_roster[data[1]]['upgrades'] = user_upgrades(data, 1)
    if CHANNEL_MAX == 0:
        return
    if l > CHANNEL_MAX:
        l -= CHANNEL_MAX
        for i in sorted(bot.channel_channels[data[2]].values(), key=lambda x:x[2]):
            if l <= 0:break
            nick = normalize_nick(i[1])
            if i[0] not in bot.clan_roster and nick not in bot.config.whitelist and i[1].split(']')[0] not in ['[GM','[S2']:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,data[2],i[0])
                sleep(0.5)
                bot.write_packet(ID.HON_CS_WHISPER,i[1],'Sorry, too many people in channel, we need some place for active members')
                l -= 1
                sleep(0.5)
channel_user_joined_channel.event = [ID.HON_SC_JOINED_CHANNEL]
channel_user_joined_channel.thread = False

def channel_user_left_channel(bot,origin,data):
    try:
        del(bot.channel_channels[data[1]][data[0]])
    except:
        pass
channel_user_left_channel.event = [ID.HON_SC_LEFT_CHANNEL]

def update_stats(bot,origin,data):
    time = datetime.now()
    if (time - bot.channel_channels[origin[2]][origin[1]][2]).seconds < bot.config.spam_threshold and data == bot.channel_channels[origin[2]][origin[1]][3]:
        nick = bot.id2nick[origin[1]].lower()
        bot.write_packet(ID.HON_CS_CHANNEL_BAN,origin[2],nick)
        # bot.config.set_add('banlist',nick)
        bot.banlist.Add(nick)
    bot.channel_channels[origin[2]][origin[1]][2] = time
    bot.channel_channels[origin[2]][origin[1]][3] = data
update_stats.event = [ID.HON_SC_CHANNEL_MSG]

def kickall(bot,input):
    if not input.admin:
        return False
    if input.origin[2] in bot.channel_channels:
        for i in bot.channel_channels[input.origin[2]]:
            if i not in bot.clan_roster and (i in bot.id2nick and bot.id2nick[i] not in bot.config.admins and bot.id2nick[i] not in bot.config.officers):
                bot.write_packet(ID.HON_CS_CHANNEL_KICK, input.origin[2], i)
                sleep(0.5)
kickall.commands = ['kickall']
kickall.event = [ID.HON_SC_CHANNEL_MSG]
kickall.thread = False

def unwhitelist(bot,input):
    """Unwhitelist player"""
    if not input.admin:
        return False
    bot.config.set_del('whitelist',input.group(2).lower())
    bot.reply("Unwhitelisted {0}".format(input.group(2)))
unwhitelist.commands = ['unwhitelist']
def whitelist(bot,input):
    """Whitelist player"""
    if not input.admin:
        return False
    bot.config.set_add('whitelist',input.group(2).lower())
    bot.reply("Whitelisted {0}".format(input.group(2)))
whitelist.commands = ['whitelist']

def cw(bot,input):
    """Whitelist Clan"""
    if not input.admin:
        return False
    bot.config.set_add('clanwhitelist', input.group(2).lower())
    bot.reply("Whitelisted clan {0}".format(input.group(2)))
cw.commands = ['cw']

def ucw(bot,input):
    """Unwhitelist Clan"""
    if not input.admin:
        return False
    bot.config.set_del('clanwhitelist', input.group(2).lower())
    bot.reply("Unwhitelisted clan {0}".format(input.group(2)))
ucw.commands = ['ucw']

def kick(bot, input): 
    """makes bot kick user""" 
    if not input.admin: return False
    if not input.group(2): return
    if not input.group(3) and input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.write_packet(ID.HON_CS_CHANNEL_KICK,input.origin[2],bot.nick2id[input.group(2).lower()])
    else:
        nick = input.group(2)
        chan = input.group(3)
        if chan is not None:
            chan = bot.chan2id[chan.lower()]
        elif input.origin[0] == ID.HON_SC_CHANNEL_MSG:
            chan = input.origin[2]
        if chan is not None:
            bot.write_packet(ID.HON_CS_CHANNEL_KICK,chan,bot.nick2id[nick.lower()])
kick.rule = (['kick'],'([^\ ]+)(?:\ +(.+))?')

def promote(bot, input): 
    """makes bot promote user""" 
    if not input.admin: return False
    if not input.group(2) and input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.write_packet(ID.HON_CS_CHANNEL_PROMOTE,input.origin[2],input.account_id)
    else:
        nick = input.group(2)
        chan = input.group(3)
        if chan is not None:
            chan = bot.chan2id[chan.lower()]
        elif input.origin[0] == ID.HON_SC_CHANNEL_MSG:
            chan = input.origin[2]
        if chan is not None:
            bot.write_packet(ID.HON_CS_CHANNEL_PROMOTE,chan,bot.nick2id[nick.lower()])
promote.rule = (['promote'],'([^\ ]+)?(?:\ +(.+))?')

def demote(bot, input): 
    """makes bot demote user""" 
    if not input.admin: return False
    if not input.group(2) and input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.write_packet(ID.HON_CS_CHANNEL_DEMOTE,input.origin[2],input.account_id)
    else:
        nick = input.group(2)
        chan = input.group(3)
        if chan is not None:
            chan = bot.chan2id[chan.lower()]
        elif input.origin[0] == ID.HON_SC_CHANNEL_MSG:
            chan = input.origin[2]
        if chan is not None:
            bot.write_packet(ID.HON_CS_CHANNEL_DEMOTE,chan,bot.nick2id[nick.lower()])
demote.rule = (['demote'],'([^\ ]+)?(?:\ +(.+))?')

def dtopic(bot, input):
    """Set default channel topic, run this from intended channel"""
    if not input.admin:
        return False
    if not input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.reply("Run me from channel intended for the default topic!")
    else:
        cname = bot.id2chan[input.origin[2]]
        if input.group(2):
            print( "Inserting dtopic for {0}: {1}".format( cname, input.group(2) ) )
            setTopic(bot, cname, input.group(2))
        else:
            if getTopic(bot, cname):
                bot.reply( "Current: {0}".format( getTopic(bot, cname) ) )
            else:
                bot.reply( "Default topic for the current channel is not set." )
dtopic.commands = ['dtopic']

def topic(bot,input):
    """Sets topic on channel issued"""
    if not input.admin:
        return False
    bot.write_packet(ID.HON_CS_UPDATE_TOPIC,input.origin[2],input.group(2))
topic.commands = ['topic']
topic.event = [ID.HON_SC_CHANNEL_MSG]

def silence(bot, input): 
    """makes bot silence user, seconds""" 
    if not input.admin: return False
    nick = input.group(2)
    time = input.group(3)
    chan = input.group(4)
    if chan is not None:
        chan = bot.chan2id[chan.lower()]
    elif input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        chan = input.origin[2]
    if chan is not None and time is not None and nick is not None:
        bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER,chan,nick,1000*int(time))
silence.rule = (['silence'],'([^\ ]+) ([0-9]+)(?:\ +(.+))?')