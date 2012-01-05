from hon.packets import ID


def join(bot, input): 
    """Joins a channel, admins only""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_JOIN_CHANNEL,input.group(2))
join.commands = ['join']

def part(bot, input): 
    """parts a channel, admins only""" 
    if not input.admin: return
    bot.write_packet(ID.HON_CS_LEAVE_CHANNEL,input.group(2))
part.commands = ['part']
