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

def member_changestatus(bot,origin,data):
    id = data[0]
    if id in bot.clan_roster:
        if data[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
            bot.clan_online[id] = {"status": data[1]}
        else:
            bot.clan_online[id] = False
member_changestatus.event = [ID.HON_SC_UPDATE_STATUS]

def member_initstatus(bot,origin,data):
    info = data[1]
    id = info[0]
    if id in bot.clan_roster:
        if info[1] in [ ID.HON_STATUS_INLOBBY , ID.HON_STATUS_INGAME ]:
            bot.clan_online[id] = {"status": info[1]}
        else:
            bot.clan_online[id] = False
member_initstatus.event = [ID.HON_SC_INITIAL_STATUS]

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
        query = { 'f' : 'set_rank', 'target_id' : id, 'member_ck': bot.cookie, 'rank' : 'Remove', 'clan_id' : bot.clan_info['clan_id'] }
        bot.masterserver_request(query)
        bot.reply(nick + " was removed from the clan")
remove.commands = ['remove']

def info(bot,input):
    """Get clan member info"""
    nick = input.group(2).lower()
    if nick not in bot.nick2id:
        bot.reply("Unknown Player")
    else:
        id = bot.nick2id[nick]
        if id in bot.clan_roster:
            player = bot.clan_roster[id]
            query = {'nickname' : nick}
            query['f'] = 'show_stats'
            query['table'] = 'player'
            data = bot.masterserver_request(query,cookie=True)
            bot.reply("{0} - Rank: {1}, Last Online: {2}".format(nick, player['rank'], data['last_activity']))
        else:
            bot.reply("Not in clan")
info.commands = ['info']

def officers(bot, input):
    """Find available officers"""
    avail_officers = {}
    for ply in bot.clan_online:
        if bot.clan_online[ply]['status'] in [ID.HON_STATUS_INLOBBY]:
            avail_officers[ply] = bot.id2nick[ply]
    outstr = ", ".join(avail_officers) if len(avail_officers) > 0 else "None"
    bot.reply( "Available officers: {0}".format( outstr ) )
officers.commands = ['officers']