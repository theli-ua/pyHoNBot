#!/usr/bin/env python
"""
"""

from subprocess import check_output

def gitCheck(bot, input):
	"""Am I up-to-date?"""
	if not input.admin: return
	if not os.path.exists('.git'):
		bot.reply('Not a git repository??')
		return
	args = ['git', 'pull']
	noUpStr = 'Already up-to-date.'
	if check_output(args) != noUpStr:
		bot.reply('Icbot updated. Restarting...')
		bot.close()
		return True
	bot.reply('Already up-to-date.')
	return False

gitCheck.commands = ['check', 'update']