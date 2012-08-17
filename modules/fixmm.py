from hon.packets import ID
from time import sleep

def startgroup(bot,origin,data):
    VERSION = '.'.join(bot.stringtable_version.split('.')[:3])
    bot.write_packet(ID.HON_CS_START_MM_GROUP,VERSION,0x0102,'caldavar','sd|','EU|',0x0001)
startgroup.event = [ID.HON_SC_INITIAL_STATUS]

def startgroup2(bot,input):
    if not input.owner:return
    VERSION = '.'.join(bot.stringtable_version.split('.')[:3])
    bot.write_packet(ID.HON_CS_START_MM_GROUP,VERSION,0x0102,'caldavar','sd|','EU|',0x0001)
startgroup2.commands = ['refixmm']

def fixmm(bot,input):
    bot.write_packet(ID.HON_CS_INVITE_TO_MM,input.nick)
fixmm.commands = ['fixmm']

def mmkick(bot,origin,data):
    bot.write_packet(ID.HON_CS_KICK_FROM_MM,0)
mmkick.event = [ID.HON_SC_TMM_GROUP_CHANGE]
