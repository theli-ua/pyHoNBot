from hon.packets import ID

VERSION = '2.5.8'

def initiall_statuses(bot,packet_id,data):
    bot.write_packet(ID.HON_CS_START_MM_GROUP,VERSION,0x0102,'caldavar','sd|bd|bp|','EU|',0x0001)
initiall_statuses.event = [ID.HON_SC_INITIAL_STATUS]


def fixmm(bot,input):
    print(input.nick)
    bot.write_packet(ID.HON_CS_INVITE_TO_MM,input.nick)
fixmm.commands = ['fixmm']
