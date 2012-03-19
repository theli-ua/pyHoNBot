# -*- coding: utf8 -*-
from hon.packets import ID

def add_member(bot,origin,data):
    id = data[0]
    bot.clan_roster[id] = {"rank":"Member"}
    if id in bot.id2nick:
        nick = bot.id2nick[id]
        bot.write_packet(ID.HON_CS_CLAN_MESSAGE,'Welcome, {0}!'.format(nick))
add_member.event = [ID.HON_SC_CLAN_MEMBER_ADDED]
        
def del_member(bot,origin,data):
    del(bot.clan_roster[data[0]])
del_member.event = [ID.HON_SC_CLAN_MEMBER_LEFT]

