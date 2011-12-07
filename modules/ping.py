#!/usr/bin/env python
"""
"""
from hon.packets import ID


def pong(bot,*args): 
    #print('got ping,sending pong!')
    bot.write_packet(ID.HON_CS_PONG)
pong.event = [ID.HON_SC_PING]
pong.priority = 'high'


if __name__ == '__main__': 
   print __doc__.strip()
