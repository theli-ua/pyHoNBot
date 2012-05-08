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
from datetime import datetime
import logging
import logging.handlers

import os

CM_PSEUDO_CHANNEL = 'clan messages'
CLAN_EVENTS_PSEUDO_CHANNEL = 'clan events'

def get_logger(bot,filename):
    if filename in bot.loggers:
        return bot.loggers[filename]
    my_logger = logging.getLogger(filename)
    my_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    #Add the log message handler to the logger
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=filename,
        #when='W5', # caturday
        when='Midnight',
        backupCount = 14,
        utc = True,
    )
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    bot.loggers[filename] = my_logger
    return my_logger


def get_file(phenny, chan):
    return chan + ".log"


def setup(bot):

    bot.config.module_config('logchannels',[[CM_PSEUDO_CHANNEL,CLAN_EVENTS_PSEUDO_CHANNEL],'list of channels to log, use log/unlog commands to add/del to this list'])
    bot.config.module_config('logdir',['/tmp/','path to store channel logs in'])

    # make the logdir path if not there
    logdir = bot.config.logdir
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    bot.loggers = {}


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

def log_add_member(bot,origin,data):
    id = data[0]
    if data[0] in bot.id2nick:
        nick = bot.id2nick[data[0]]
    else:
        nick = 'User ' + str(data[0])
    log_message(bot, nick, 'clan^events', 'joined the clan')
log_add_member.event = [ID.HON_SC_CLAN_MEMBER_ADDED]

if __name__ == '__main__':
    print __doc__.strip()
