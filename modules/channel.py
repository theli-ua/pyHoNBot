# -*- coding: utf8 -*-
from hon.packets import ID
from time import sleep
from datetime import datetime

channel_channels = {}

def setup(bot):
    bot.config.module_config('channel_limit',[0,'Will try to keep channel at this limit kicking afk non-clanmates'])

def channel_joined_channel(bot,origin,data):
    channel_channels[data[1]] = dict([[m[1],[m[1],m[0],datetime.now()]] for m in data[-1]])
channel_joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]

def channel_user_joined_channel(bot,origin,data):
    channel_channels[data[2]][data[1]] = [data[1],data[0],datetime.now()]
    l = len(channel_channels[data[2]])
    CHANNEL_MAX = bot.config.channel_limit
    if CHANNEL_MAX == 0:
        return
    if l > CHANNEL_MAX:
        l -= CHANNEL_MAX
        for i in sorted(channel_channels[data[2]].values(), key=lambda x:x[2]):
            if l <= 0:break
            if i[0] not in bot.clan_roster and i[1].split(']')[0] not in ['[GM','[S2']:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,data[2],i[0])
                sleep(0.5)
                bot.write_packet(ID.HON_CS_WHISPER,i[1],'Sorry, too many people in channel, we need some place for clan members')
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
    channel_channels[origin[2]][origin[1]][2] = datetime.now()
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
