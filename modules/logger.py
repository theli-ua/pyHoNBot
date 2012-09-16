#!/usr/bin/env python
"""
logger.py - Esteban Feldman
based on logger.py - Phenny Room Logging Module
Author: Peter Higgins (dante@dojotoolkit.org)
About: http://higginsforpresident.net
License: AFL | New BSD

Modified and ported to HoNBot by Anton Romanov
"""
# -*- coding: utf8 -*-
from hon.packets import ID
from hon.honutils import normalize_nick
from datetime import datetime
import logging
import logging.handlers

import os

CM_PSEUDO_CHANNEL = 'clan messages'
CLAN_EVENTS_PSEUDO_CHANNEL = 'clan events'
WHISP_PSEUDO_CHANNEL = 'whispers'
ONLINE_PSEUDO_CHANNEL = 'online count'

def get_logger(bot,filename):
    my_logger = logging.getLogger(filename)
    if len(my_logger.handlers) == 0:
        my_logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        #Add the log message handler to the logger
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=filename,
            when='Midnight',
            backupCount = 14,
            utc = True,
        )
        handler.setFormatter(formatter)
        my_logger.addHandler(handler)
    return my_logger


def get_file(phenny, chan):
    return chan + ".log"


def setup(bot):

    bot.config.module_config('logchannels',[[CM_PSEUDO_CHANNEL,CLAN_EVENTS_PSEUDO_CHANNEL,WHISP_PSEUDO_CHANNEL],'list of channels to log, use log/unlog commands to add/del to this list'])
    bot.config.module_config('logdir',['/tmp/','path to store channel logs in'])

    bot.reportRunning = False

    # make the logdir path if not there
    logdir = bot.config.logdir
    if not os.path.exists(logdir):
        os.mkdir(logdir)

def log_message(phenny, teller, chan, msg):
    # only log the channels we care about
    if chan.lower() in phenny.config.logchannels or chan.decode('utf-8').lower() in phenny.config.logchannels:
        #line = "\t".join((chan, teller, msg))
        line = u"<{0}>\t{1}".format(teller,msg).encode('utf-8')
        logger = get_logger(phenny, os.path.join(phenny.config.logdir, get_file(phenny, chan)))
        logger.info(line)

def log(bot, input): 
    """Adds channel to log list, owner only""" 
    if not input.owner: return
    bot.config.set_add('logchannels',input.group(2).lower())
log.commands = ['log']

def unlog(bot, input): 
    """Removes channel from log list, owner only""" 
    if not input.admin: return
    bot.config.set_del('logchannels',input.group(2).lower())
unlog.commands = ['unlog']

def activityreport(bot, input):
    if not input.owner: return
    if bot.reportRunning:
        bot.reply("Report is already running.")
        return
    bot.reply("Running report")
    bot.reportRunning = True
    toOut = []
    out = "Project Epoch Activity Report\n\n\n"
    for id in bot.clan_roster:
        nick = bot.id2nick[id]
        print("Processing " + nick)
        query = {'nickname' : nick}
        query['f'] = 'show_stats'
        query['table'] = 'player'
        data = bot.masterserver_request(query,cookie=True)
        toOut.append({"nick": nick, "date": data['last_activity']})
        # out += "{0}: {1}\n".format(nick, data['last_activity'])
    for each in toOut.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%m/%d/%Y')):
        out += "{0}: {1}\n".format( each['nick'], each['date'] )
    f = open(bot.config.logdir + 'activity.log', 'w')
    f.write(out)
    bot.reply("Log written to log directory. URL in officer forum")
    bot.reportRunning = False
activityreport.commands = ['activityreport']
activityreport.thread = True

def loggit(bot, origin,data):
    if origin[0] in [ID.HON_SC_CHANNEL_MSG,ID.HON_SC_CHANNEL_EMOTE,ID.HON_SC_CHANNEL_ROLL]:
        if origin[0] == ID.HON_SC_CHANNEL_EMOTE:
            data = '[EMOTE]\t'+ data
        elif origin[0] == ID.HON_SC_CHANNEL_ROLL:
            data = '[ROLL]\t'+ data
        log_message(bot, bot.id2nick[origin[1]], bot.id2chan[origin[2]], data)
    elif origin[0] == ID.HON_SC_CLAN_MESSAGE:
        log_message(bot, bot.id2nick[data[0]], CM_PSEUDO_CHANNEL, data[1])

loggit.event = [ID.HON_SC_CHANNEL_MSG,ID.HON_SC_CHANNEL_EMOTE,ID.HON_SC_CHANNEL_ROLL,ID.HON_SC_CLAN_MESSAGE]
loggit.priority = 'high'
loggit.thread = False

def logwhisper(bot, origin, data):
    nick = normalize_nick(origin[1])
    log_message(bot, nick, WHISP_PSEUDO_CHANNEL, data)
logwhisper.event = [ID.HON_SC_WHISPER,ID.HON_CS_PM]
logwhisper.priority = 'high'
logwhisper.thread = False

def logonline(bot,origin,data):
    log_message(bot,ONLINE_PSEUDO_CHANNEL,ONLINE_PSEUDO_CHANNEL,data[1])
logonline.event = [ID.HON_SC_TOTAL_ONLINE]

def log_change_member(bot,origin,data):
    who,status,whodid = data[0],data[1],data[2]
    if who in bot.id2nick:
        nick = bot.id2nick[who]
    else:
        nick = 'User ' + str(who)
    if status == 0:
        msg = 'Removed from clan by'
    else:
        msg = 'Promoted/demoted to ' + ['Member','Officer','Leader'][stats - 1] + ' by'

    if whodid in bot.id2nick:
        msg += ' ' + bot.id2nick[whodid]
    else:
        msg += ' user ' + str(whodid)
    log_message(bot, nick, CLAN_EVENTS_PSEUDO_CHANNEL, msg)
log_change_member.event = [ID.HON_SC_CLAN_MEMBER_CHANGE]
log_change_member.thread = False

def log_add_member(bot,origin,data):
    id = data[0]
    if data[0] in bot.id2nick:
        nick = bot.id2nick[data[0]]
    else:
        nick = 'User ' + str(data[0])
    log_message(bot, nick, CLAN_EVENTS_PSEUDO_CHANNEL, 'joined the clan')
log_add_member.event = [ID.HON_SC_CLAN_MEMBER_ADDED]
log_add_member.thread = False

if __name__ == '__main__':
    print __doc__.strip()
