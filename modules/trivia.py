#!/usr/bin/env python
"""
"""

from hon.packets import ID
import time
import os
import pickle
import threading
import sys
from random import randint

class Trivia:
	def __init__(self, bot):
		self.bot = bot
		self.thread = None
		self.current = {}
		self.high_score = 5
		self.scores = {}
		self.questions = []
		self.used_questions = []
		self.running = False
		self.channel = bot.config.trivia_channel
		self.lastaction = 0
		self.lastquestion = 0
		self.load()
	def timeout(self):
		while True:
			if not self.running:
				break
			if ( self.lastaction > 0 and ( self.lastaction + self.bot.config.trivia_endtimeout ) <= time.time() ):
				self.stop(True)
				break
			elif ( self.lastquestion > 0 and ( self.lastquestion + self.bot.config.trivia_timeout ) <= time.time() ):
				self.nextQuestion(True)
			time.sleep(1)
	def recvMsg(self, bot, origin, data):
		if data.lower() == self.current['answer'].lower():
			self.lastaction = time.time()
			score = int( self.high_score - ( self.lastaction - self.lastquestion ) )
			if score < 1: score = 1

			nick = bot.id2nick[origin[1]]
			aid = origin[1]

			self.sendMsg( "{0} got it right and scored {1}!".format( nick, score ) )
			time.sleep(4)
			self.nextQuestion()
	def sendMsg(self, message):
		chan = self.bot.chan2id[self.channel]
		self.bot.write_packet( ID.HON_SC_CHANNEL_EMOTE, "Trivia: " + message, chan )
	def setPoints(self, accountid, points):
		if accountid in self.scores:
			self.scores[accountid] += points
		else:
			self.scores[accountid] = points
	def nextQuestion(self, failed=False):
		if len(self.used_questions) == len(self.questions):
			self.sendMsg("Questions exhausted! We need to write more!")
			self.stop()
			return
		rand = randint(0, len(self.questions) - 1)
		while rand in self.used_questions:
			rand = randint(0, len(self.questions) - 1)
		self.used_questions.append(rand)
		if failed:
			self.sendMsg("Times up! Next question")
			time.sleep(1)
		self.lastquestion = time.time()
		self.current = self.questions[rand]
		self.sendMsg(self.current['question'])
		return
	def start(self):
		if self.running: return
		self.running = True
		self.reset()
		self.sendMsg("Started")
		time.sleep(4)
		self.thread = threading.Thread(target=self.timeout)
		self.thread.start()
		self.nextQuestion()
	def stop(self, activity=False):
		if not self.running: return
		self.running = False
		self.reset()
		if activity:
			self.sendMsg("Stopped due to inactivity")
		else:
			self.sendMsg("Stopped")
	def reset(self):
		self.used_questions = []
		self.lastquestion = 0
		self.lastaction = 0
	def load(self):
		if os.path.exists( self.bot.config.trivia_file ):
			self.questions = pickle.load( open( self.bot.config.trivia_file, 'r' ) )
		else:
			self.questions = []
	def save(self):
		pickle.dump( self.questions, open( self.bot.config.trivia_file, 'w' ) )


def receivemessage(bot, origin, data):
	if bot.trivia.channel in bot.chan2id:
		if origin[2] == bot.chan2id[bot.trivia.channel]:
			if not bot.trivia.running: return
			bot.trivia.recvMsg(bot,origin,data)
	else:
		# bot.write_packet( ID.HON_CS_JOIN_CHANNEL, bot.trivia.channel )
		print("Channel not in chan2id")
receivemessage.event = [ID.HON_SC_CHANNEL_MSG]
receivemessage.priority = 'high'
receivemessage.thread = True

def trivia(bot, input):
	if input.origin[2] != bot.chan2id[bot.trivia.channel]:
		bot.reply("This only works in the HoNTrivia channel.")
		return
	if not input.group(2):
		bot.reply("Accepted arguments: start, stop")
	else:
		if input.group(2) == "start":
			bot.trivia.start()
		elif input.group(2) == "stop":
			if input.admin:
				bot.trivia.stop()
			else:
				bot.reply("Only an admin can use stop. It will stop automatically after inactivity.")
trivia.commands = ['trivia']

def setup(bot):
	bot.config.module_config( 'trivia_channel', ['hontrivia', 'Set the channel the trivia bot will work in'] )
	bot.config.module_config( 'trivia_file', ['triviadb', 'Set the channel the trivia bot will work in'] )
	bot.config.module_config( 'trivia_timeout', [15, 'Set the timeout for a question'] )
	bot.config.module_config( 'trivia_endtimeout', [30, 'Set the timeout for trivia'] )

	bot.trivia = Trivia(bot)

if __name__ == '__main__': 
    print __doc__.strip()