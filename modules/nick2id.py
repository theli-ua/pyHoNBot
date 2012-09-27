# captures nicks and ids and builds dicts for both nick2id and id2nick
#
from hon.packets import ID
from hon.honutils import normalize_nick

def joined_channel(bot,origin,data):
    print("Joined " + data[0])
    bot.chan2id[data[0].lower()] = data[1]
    bot.id2chan[data[1]] = data[0]
    for m in data[-1]:
        m[0] = normalize_nick(m[0])
        bot.nick2id[m[0]] = m[1]
        bot.id2nick[m[1]] = m[0]
        bot.user_status[m[1]] = m[2]
joined_channel.event = [ID.HON_SC_CHANGED_CHANNEL]
joined_channel.priority = 'high'
joined_channel.thread = False

def user_joined_channel(bot,origin,data):
    nick = normalize_nick(data[0]).lower()
    bot.nick2id[nick] = data[1]
    bot.id2nick[data[1]] = nick
    bot.user_status[data[1]] = data[3]
user_joined_channel.event = [ID.HON_SC_JOINED_CHANNEL]
user_joined_channel.priority = 'high'
user_joined_channel.thread = False

def name_change(bot,origin,data):
    nick = normalize_nick(data[1]).lower()
    bot.nick2id[nick] = data[0]
    bot.id2nick[data[0]] = nick
name_change.event = [ID.HON_SC_NAME_CHANGE]
name_change.priority = 'high'
name_change.thread = False

def update_status(bot, origin, data):
    bot.user_status[data[0]] = data[1]
update_status.event = [ID.HON_SC_UPDATE_STATUS]