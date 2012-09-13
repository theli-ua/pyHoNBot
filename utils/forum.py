#!/usr/bin/env python
# (c) 2012 Ninja101
# Epoch Forum Check
#
"""
"""

import hashlib
import urllib
import json

class VB:
	def __init__(self, url, apikey):
		self.url = url
		self.apikey = apikey

		self.allowed = ['redirect_inline_moved', 'redirect_login', 'redirect_postthanks']

		if not self.InitAPI():
			print("Error connecting to vB API")

	def IsInit(self):
		try:
			test = self.init
			return True
		except:
			return False

	def IsError(self, ret):
		try:
			test = ret['response']['errormessage']
			if test in self.allowed:
				return False
			print("Error:" + test)
			return True
		except:
			return False

	def Sign(self, args):
		args = sorted(args.items())
		fullstr = ''.join([urllib.urlencode(args), self.init["apiaccesstoken"], self.init["apiclientid"], self.init["secret"], self.apikey])
		return hashlib.md5(fullstr).hexdigest()

	def InitAPI(self):
		params = urllib.urlencode({"api_m": "api_init", "clientname": "icbot", "clientversion": "1.0", "platformname": "Python", "platformversion": "1.0", "uniqueid": "icbot"})
		try:
			self.init = json.load(urllib.urlopen(self.url + "?%s" % params))
			return True
		except Exception as inst:
			return False

	def Login(self, username, password):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "login_login"})
		get = urllib.urlencode({'api_m': 'login_login', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urllib.urlencode({"vb_login_username": username, "vb_login_md5password": password})
		try:
			retval = json.load(urllib.urlopen(self.url + "?%s" % get, post))
			print("Forum: Logged in")
			return not self.IsError(retval)
		except:
			return False

	def GetPost(self, postid):
		if not self.IsInit(): return False
		# todo

	def GetThread(self, threadid):
		if not self.IsInit(): return False
		# todo

	def GetThreads(self, forumid, limit):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "forumdisplay", 'forumid': forumid, 'perpage': limit})
		get = urllib.urlencode({'api_m': 'forumdisplay', 'forumid': forumid, 'perpage': limit, 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		try:
			retval = json.load(urllib.urlopen(self.url + "?%s" % get))
			if not self.IsError(retval):
				print("Forum: Fetching Threads from " + str(forumid))
				return retval['response']['threadbits']
			else:
				return False
		except Exception as inst:
			print(inst)
			return False

	def NewThread(self, forumid, title, body):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "newthread_postthread"})
		get = urllib.urlencode({'api_m': 'newthread_postthread', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urllib.urlencode({"subject": title, "message": body, "forumid": forumid})
		try:
			retval = json.load(urllib.urlopen(self.url + "?%s" % get, post))
			return not self.IsError(retval)
		except:
			return False

	def NewPost(self, threadid, title, body):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "newreply_postreply"})
		get = urllib.urlencode({'api_m': 'newreply_postreply', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urllib.urlencode({"threadid": threadid, "subject": title, "message": body})
		try:
			retval = json.load(urllib.urlopen(self.url + "?%s" % get, post))
			return not self.IsError(retval)
		except:
			return False

	def MoveThread(self, threadid, forumid_to):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "inlinemod_domovethreads"})
		get = urllib.urlencode({'api_m': 'inlinemod_domovethreads', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urllib.urlencode({"threadids": threadid, "destforumid": forumid_to})
		try:
			retval = json.load(urllib.urlopen(self.url + "?%s" % get, post))
			return not self.IsError(retval)
		except:
			return False