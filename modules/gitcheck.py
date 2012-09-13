#!/usr/bin/env python
"""
"""

from subprocess import check_output
from os import path
import sys

def update(bot, input):
	"""Am I up-to-date?"""
	if not input.admin: return
	if not path.exists('.git'):
		bot.reply('Not a git repository??')
		return
	args = ['git', 'pull']
	noUpStr = 'Already up-to-date.'
	retStr = check_output(args)
	if retStr.strip() !=  noUpStr:
		bot.reply('{0} updated. Restarting...'.format(bot.config.nick))
		raise SystemExit
	bot.reply('Already up-to-date.')

update.commands = ['update']

def frestart(bot, inpu):
	"""Full restart of the bot"""
	if not input.owner: return
	raise SystemExit
frestart.commands = ['frestart']