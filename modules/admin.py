from hon.packets import ID


def join(bot, input): 
    """Joins a channel, admins only""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_JOIN_CHANNEL,input.group(2))
    bot.config.set_add('channels',input.group(2))
join.commands = ['join']

def part(bot, input): 
    """parts a channel, admins only""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_LEAVE_CHANNEL,input.group(2))
    bot.config.set_del('channels',input.group(2))
part.commands = ['part']

def ignore(bot, input): 
    """makes bot ignore user, admins only""" 
    if not input.admin: return
    bot.config.set_add('ignore',input.group(2).lower())
ignore.commands = ['ignore']

def unignore(bot, input): 
    """makes bot stop ignoring user, admins only""" 
    if not input.admin: return
    bot.config.set_del('ignore',input.group(2).lower())
unignore.commands = ['unignore']

def ban(bot, input): 
    """makes bot ban user, bot will try to reban user on each occasion""" 
    if not input.admin: return
    bot.config.set_add('banlist',input.group(2).lower())
    if input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.write_packet(ID.HON_CS_CHANNEL_BAN,input.origin[2],input.group(2))
ban.commands = ['ban']

def unban(bot, input): 
    """makes bot stop banning user, admins only""" 
    if not input.admin: return
    bot.config.set_del('banlist',input.group(2).lower())
    if input.origin[0] == ID.HON_SC_CHANNEL_MSG:
        bot.write_packet(ID.HON_CS_CHANNEL_UNBAN,input.origin[2],input.group(2))
unban.commands = ['unban']
