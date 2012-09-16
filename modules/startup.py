#!/usr/bin/env python
"""
"""
from hon.packets import ID
from time import sleep

def startup(bot, *args): 
    print ('authenticated to chatserver')
    for channel in bot.config.channels: 
        bot.write_packet(ID.HON_CS_JOIN_CHANNEL,channel)
        sleep(0.5)

startup.event = [ID.HON_SC_AUTH_ACCEPTED]
startup.priority = 'low'
startup.thread = True

if __name__ == '__main__': 
    print __doc__.strip()
