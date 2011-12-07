
def normalize_nick(nick):
    if nick[0] == '[':
        return nick[nick.index(']') + 1 :]
    else:
        return nick
