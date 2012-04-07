# -*- coding: utf8 -*-
from hon.packets import ID
from time import sleep
from datetime import datetime
from hon.honutils import normalize_nick

channel_channels = {}

def setup(bot):
    bot.config.module_config('channel_limit',[0,'Will try to keep channel at this limit kicking afk non-clanmates'])
    bot.config.module_config('spam_threshold',[0,'number of seconds, if user repeats his message in channel with delay lower than this he will be considered spamming and banned'])

def channel_joined_channel(bot,origin,data):
    channel_channels[data[1]] = dict([[m[1],[m[1],m[0],datetime.now(),None]] for m in data[-1]])

    #banlist management
    for m in data[-1]:
        nick = normalize_nick(m[0]).lower()
        if nick in bot.config.banlist:
            bot.write_packet(ID.HON_CS_CHANNEL_BAN,data[1],nick)

channel_joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]

def channel_user_joined_channel(bot,origin,data):
    channel_channels[data[2]][data[1]] = [data[1],data[0],datetime.now(),None]
    l = len(channel_channels[data[2]])
    CHANNEL_MAX = bot.config.channel_limit

    #banlist management
    nick = normalize_nick(data[0]).lower()
    if nick in bot.config.banlist:
        bot.write_packet(ID.HON_CS_CHANNEL_BAN,data[2],data[0])

    if CHANNEL_MAX == 0:
        return
    if l > CHANNEL_MAX:
        l -= CHANNEL_MAX
        for i in sorted(channel_channels[data[2]].values(), key=lambda x:x[2]):
            if l <= 0:break
            if i[0] not in bot.clan_roster and i[1].split(']')[0] not in ['[GM','[S2']:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,data[2],i[0])
                sleep(0.5)
                bot.write_packet(ID.HON_CS_WHISPER,i[1],'Sorry, too many people in channel, we need some place for active members')
                l -= 1
                sleep(0.5)

channel_user_joined_channel.event = [ID.HON_SC_JOINED_CHANNEL]
#channel_user_joined_channel.thread = False

def channel_user_left_channel(bot,origin,data):
    try:
        del(channel_channels[data[1]][data[0]])
    except:
        pass
channel_user_left_channel.event = [ID.HON_SC_LEFT_CHANNEL]

def update_stats(bot,origin,data):
    time = datetime.now()
    if (time - channel_channels[origin[2]][origin[1]][2]).seconds < bot.config.spam_threshold and data[2] == channel_channels[origin[2]][origin[1]][3]:
        nick = bot.id2nick[origin[1]].lower()
        #bot.write_packet(ID.HON_CS_CHANNEL_BAN,origin[2],nick)
        #bot.config.set_add('banlist',nick)
        print('spammer')
        print(nick)
    channel_channels[origin[2]][origin[1]][2] = time
    channel_channels[origin[2]][origin[1]][3] = data[2]
update_stats.event = [ID.HON_SC_CHANNEL_MSG]

def kickall(bot,input):
    if not input.admin:
        return
    if input.origin[2] in channel_channels:
        for i in channel_channels[input.origin[2]]:
            if i[0] not in bot.clan_roster and i[1].split(']')[0] not in ['[GM','[S2','[TECH']:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,input.origin[2],i[0])
                sleep(0.5)
kickall.commands = ['kickall']
kickall.event = [ID.HON_SC_CHANNEL_MSG]
kickall.thread = False
