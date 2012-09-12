#!/usr/bin/env python
"""
"""

from subprocess import check_output
from os import path

def gitcheck(bot, input):
	"""Am I up-to-date?"""
	if not input.admin: return
	if not path.exists('.git'):
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

gitcheck.commands = ['update']