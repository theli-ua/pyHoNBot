# -*- coding: utf8 -*-
from hon.packets import ID
from time import sleep
from datetime import datetime
from hon.honutils import normalize_nick

def setup(bot):
    bot.channel_channels = {}
    bot.not_smurfs = []
    bot.config.module_config('channel_limit',[0,'Will try to keep channel at this limit kicking afk non-clanmates'])
    bot.config.module_config('silence_smurfs',[-1,'Will silence anyone with normal mode tmm wins equal or lower than this'])
    bot.config.module_config('spam_threshold',[0,'number of seconds, if user repeats his message in channel with delay lower than this he will be considered spamming and banned'])
    bot.config.module_config('whitelist',[[],'whitelist for antispam etc'])

def silence_smurfs(bot,chanid,nick):
    if bot.config.silence_smurfs < 0:
        return
    if nick in bot.nick2id and bot.nick2id[nick] in bot.clan_roster:
        return
    if nick in bot.not_smurfs or nick in bot.config.whitelist:
        return
    query = {'nickname' : nick,'f': 'show_stats','table': 'ranked'}
    stats_data = bot.masterserver_request(query,cookie=True)
    if int(stats_data['rnk_wins']) <= bot.config.silence_smurfs:
        bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER,chanid,nick,0x7fffffff)
    else:
        bot.not_smurfs.append(nick)

    

def channel_joined_channel(bot,origin,data):
    bot.channel_channels[data[1]] = dict([[m[1],[m[1],m[0],datetime.now(),None]] for m in data[-1]])

    #banlist management
    for m in data[-1]:
        nick = normalize_nick(m[0]).lower()
        if bot.store.banlist_re.match(nick):
            bot.write_packet(ID.HON_CS_CHANNEL_BAN,data[1],nick)
        #else:
            #silence_smurfs(bot,data[1],nick)

channel_joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]

def channel_user_joined_channel_smurfs(bot,origin,data):
    nick = normalize_nick(data[0]).lower()
    silence_smurfs(bot,data[2],nick)
channel_user_joined_channel_smurfs.event = [ID.HON_SC_JOINED_CHANNEL]
channel_user_joined_channel_smurfs.thread = True

def channel_user_joined_channel(bot,origin,data):
    bot.channel_channels[data[2]][data[1]] = [data[1],data[0],datetime.now(),None]
    l = len(bot.channel_channels[data[2]])
    CHANNEL_MAX = bot.config.channel_limit
    #banlist management
    nick = normalize_nick(data[0]).lower()
    if bot.store.banlist_re.match(nick):
        bot.write_packet(ID.HON_CS_CHANNEL_BAN,data[2],data[0])
    else:
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
        bot.config.set_add('banlist',nick)
    bot.channel_channels[origin[2]][origin[1]][2] = time
    bot.channel_channels[origin[2]][origin[1]][3] = data
update_stats.event = [ID.HON_SC_CHANNEL_MSG]

def kickall(bot,input):
    if not input.admin:
        return
    if input.origin[2] in bot.channel_channels:
        for i in bot.channel_channels[input.origin[2]]:
            if i[0] not in bot.clan_roster and i[1].split(']')[0] not in ['[GM','[S2','[TECH']:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,input.origin[2],i[0])
                sleep(0.5)
kickall.commands = ['kickall']
kickall.event = [ID.HON_SC_CHANNEL_MSG]
kickall.thread = False

def unwhitelist(bot,input):
    if not input.admin:
        return
    bot.config.set_del('whitelist',input.group(2).lower())
unwhitelist.commands = ['unwhitelist']
def whitelist(bot,input):
    if not input.admin:
        return
    bot.config.set_add('whitelist',input.group(2).lower())
whitelist.commands = ['whitelist']

def kick(bot, input): 
    """makes bot kick user""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_CHANNEL_KICK,input.origin[2],bot.nick2id[input.group(2).lower()])
kick.commands = ['kick']
kick.event = [ID.HON_SC_CHANNEL_MSG]

def promote(bot, input): 
    """makes bot promote user""" 
    if not input.admin: return
    if not input.group(2):
        bot.write_packet(ID.HON_CS_CHANNEL_PROMOTE,input.origin[2],input.account_id)
    else:
        bot.write_packet(ID.HON_CS_CHANNEL_PROMOTE,input.origin[2],bot.nick2id[input.group(2).lower()])
promote.commands = ['promote']
promote.event = [ID.HON_SC_CHANNEL_MSG]

def demote(bot, input): 
    """makes bot demote user""" 
    if not input.admin: return
    if not input.group(2):
        bot.write_packet(ID.HON_CS_CHANNEL_DEMOTE,input.origin[2],input.account_id)
    else:
        bot.write_packet(ID.HON_CS_CHANNEL_DEMOTE,input.origin[2],bot.nick2id[input.group(2).lower()])
demote.commands = ['demote']
demote.event = [ID.HON_SC_CHANNEL_MSG]

def topic(bot,input):
    """Sets topic on channel issued"""
    if not input.admin:
        return
    bot.write_packet(ID.HON_CS_UPDATE_TOPIC,input.origin[2],input.group(2))
topic.commands = ['topic']
topic.event = [ID.HON_SC_CHANNEL_MSG]

def silence(bot, input): 
    """makes bot silence user""" 
    if not input.admin: return
    nick,time = input.group(2).split(' ') 
    bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER,input.origin[2],nick,int(time))
silence.commands = ['silence']
silence.event = [ID.HON_SC_CHANNEL_MSG]
