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
    bot.config.set_add('ignore',input.group(2))
ignore.commands = ['ignore']

def unignore(bot, input): 
    """makes bot stop ignoring user, admins only""" 
    if not input.admin: return
    bot.config.set_del('ignore',input.group(2))
unignore.commands = ['unignore']
