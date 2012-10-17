colors = {
	"mentorwings": "#FF6600",
	"s2logo": "#FF0000",
	"sgm": "#DD0040",
	"gmshield": "#DD0040",
	"banhammer": "#DD0040",
	"tech": "#DD0040",
	"sbteye": "#0059FF",
	"emerald": "#1CFC2F",
	"tanzanite": "#863EF0",
	"pink": "#FC65A5",
	"diamond": "#2ACC1FA",
	"goldshield": "#DBBF4A",
	"silvershield": "#7C8DA7"
}

def normalize_nick(nick):
	nick = nick.lower()
	if nick[0] == '[':
		return nick[nick.index(']') + 1 :]
	else:
		return nick
def user_upgrades(bot, nick):
	upgrades = {}
	query = {'nickname': nick, 'f': 'show_stats', 'table': 'player'}
	info = bot.masterserver_request( query, cookie=True )
	for i in info['selected_upgrades']:
		upgrade = info['selected_upgrades'][i]
		up_type = upgrade[:upgrade.find('.')]
		up_name = upgrade[upgrade.find('.')+1:]
		if up_type == "cc":
			upgrades['cc'] = up_name in colors and colors[up_name] or up_name
		else:
			upgrades[up_type] = up_name
	return upgrades