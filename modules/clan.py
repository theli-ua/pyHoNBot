# -*- coding: utf8 -*-
from hon.packets import ID

def setup(bot):
    bot.config.module_config('welcome_members',[1,'Will welcome members in /c m if set to non-zero value'])

def change_member(bot,origin,data):
    who,status,whodid = data[0],data[1],data[2]
    if status == 0:
        del(bot.clan_roster[who])
    elif status == 1:
        if who in bot.clan_roster:
            bot.clan_roster[who]['rank'] = 'Member'
        else:
            bot.clan_roster[who] = {"rank":"Member"}
    elif status == 2:
        bot.clan_roster[who]['rank'] = 'Officer'
    elif status == 3:#not sure about this one
        bot.clan_roster[who]['rank'] = 'Leader'

change_member.event = [ID.HON_SC_CLAN_MEMBER_CHANGE]

def add_member(bot,origin,data):
    id = data[0]
    bot.clan_roster[id] = {"rank":"Member"}
    if bot.config.welcome_members > 0 and id in bot.id2nick:
        nick = bot.id2nick[id]
        bot.write_packet(ID.HON_CS_CLAN_MESSAGE,'Welcome, {0}!'.format(nick))
add_member.event = [ID.HON_SC_CLAN_MEMBER_ADDED]

def invite(bot,input):
    """invites to clan, admins only""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_CLAN_ADD_MEMBER,input.group(2))
invite.commands = ['invite']

def remove(bot,input):
    """remove from clan, admins only""" 
    if not input.admin: return
    nick = input.group(2).lower()
    if nick not in bot.nick2id:
        bot.reply('Sorry, I don''t know ' + nick)
    else:
        id = bot.nick2id[nick]
        bot.write_packet(ID.HON_CS_CLAN_REMOVE_MEMBER,id)
        query = { 'f' : 'set_rank', 'target_id' : id, 'member_ck': bot.cookie, 'rank' : 'Remove', 'clan_id' : self.clan_info['clan_id'] }
        bot.masterserver_request(query)
remove.commands = ['remove']
