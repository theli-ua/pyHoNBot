# -*- coding: utf8 -*-
from hon.packets import ID
from time import sleep

channel_channels = {}

def channel_joined_channel(bot,packet_id,data):
    channel_channels[data[1]] = set([m[1] for m in data[-1]])
channel_joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]

def channel_user_joined_channel(bot,packet_id,data):
    channel_channels[data[2]] = channel_channels[data[2]] | set([data[1]])
channel_user_joined_channel.event = [ID.HON_SC_JOINED_CHANNEL]

def kickall(bot,input):
    if not input.admin and \
        (input.account_id not in bot.clan_roster or bot.clan_roster[input.account_id] == 'Member'):
        return
    if input.origin[2] in channel_channels:
        for i in channel_channels[input.origin[2]]:
            if i not in bot.clan_roster:
                bot.write_packet(ID.HON_CS_CHANNEL_KICK,input.origin[2],i)
                sleep(0.5)
kickall.commands = ['kickall']
kickall.event = [ID.HON_SC_CHANNEL_MSG]
