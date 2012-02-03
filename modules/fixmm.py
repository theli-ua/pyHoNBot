from hon.packets import ID

VERSION = '2.5.9'

def startgroup(bot,packet_id,data):
    bot.write_packet(ID.HON_CS_START_MM_GROUP,VERSION,0x0102,'caldavar','sd|bd|bp|','EU|',0x0001)
startgroup.event = [ID.HON_SC_INITIAL_STATUS]


def fixmm(bot,input):
    bot.write_packet(ID.HON_CS_INVITE_TO_MM,input.nick)
fixmm.commands = ['fixmm']
