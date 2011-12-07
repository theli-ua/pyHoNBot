# captures nicks and ids and builds dicts for both nick2id and id2nick
#
from hon.packets import ID

def setup(bot):
    bot.nick2id = {}
    bot.id2nick = {}

def joined_channel(bot,packet_id,data):
    for m in data[-1]:
        bot.nick2id[m[0]] = m[1]
        bot.id2nick[m[1]] = m[0]
    #print bot.nick2id
    #print bot.id2nick
joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]
