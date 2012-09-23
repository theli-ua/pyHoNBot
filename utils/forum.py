#!/usr/bin/env python
# (c) 2012 Ninja101
# Epoch Forum Check
#
"""
"""

import hashlib
try: # Py32
	from urllib.parse import urlencode
	from urllib.request import urlopen
except: # Py27
	from urllib import urlopen
	from urllib import urlencode
import json
from time import time

class VB:
	def __init__(self, url, apikey, autoInit=True):
		self.url = url
		self.apikey = apikey
		self.loggedIn = False

		self.allowed = ['redirect_inline_moved', 'redirect_login', 'redirect_postthanks', 'search']

		if autoInit and not self.InitAPI():
				print("Error connecting to vB API")

	def IsInit(self):
		try:
			test = self.init
			return True
		except:
			return False

	def IsError(self, ret, allowed=[None]):
		try:
			test = ret['response']['errormessage']
			if isinstance(test, list):
				if test[0] == 'invalid_accesstoken':
					self.ReInit()
					return True
				return test[0] in allowed
			return not test in allowed
		except:
			return None

	def ReInit(self):
		if not self.username: return
		self.InitAPI()
		self.Login(self.username, self.password)

	def Sign(self, args):
		args = sorted(args.items())
		fullstr = ''.join([urlencode(args), self.init["apiaccesstoken"], self.init["apiclientid"], self.init["secret"], self.apikey])
		return hashlib.md5(fullstr).hexdigest()

	def InitAPI(self):
		params = urlencode({"api_m": "api_init", "clientname": "icbot", "clientversion": "1.0", "platformname": "Python", "platformversion": "1.0", "uniqueid": "icbot"})
		try:
			self.init = json.load(urlopen(self.url + "?%s" % params))
			return True
		except Exception as inst:
			return False

	def Login(self, username, password):
		if not self.IsInit(): return False
		if self.loggedIn is not False and (self.loggedIn+900) > time(): return True
		self.username = username
		self.password = password
		signed = self.Sign({"api_m": "login_login"})
		get = urlencode({'api_m': 'login_login', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"vb_login_username": username, "vb_login_md5password": password})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			self.loggedIn = time()
			return not self.IsError(retval)
		except Exception as inst:
			print("Login Error: " + inst)
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
		get = urlencode({'api_m': 'forumdisplay', 'forumid': forumid, 'perpage': limit, 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get))
			if self.IsError(retval) is None:
				return retval['response']['threadbits']
			else:
				return False
		except Exception as inst:
			print(inst)
			return False

	def NewThread(self, forumid, title, body):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "newthread_postthread"})
		get = urlencode({'api_m': 'newthread_postthread', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"subject": title, "message": body, "forumid": forumid})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			return self.IsError(retval) is None
		except:
			return False

	def NewPost(self, threadid, title, body):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "newreply_postreply"})
		get = urlencode({'api_m': 'newreply_postreply', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"threadid": threadid, "subject": title, "message": body})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			return not self.IsError(retval)
		except:
			return False

	def MoveThread(self, threadid, forumid_to):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "inlinemod_domovethreads"})
		get = urlencode({'api_m': 'inlinemod_domovethreads', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"threadids": threadid, "destforumid": forumid_to})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			return not self.IsError(retval)
		except:
			return False
	def Search(self, contenttypeid, query, forumchoice='', prefixchoice='', titleonly=False, showposts=False):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "search_process"})
		get = urlencode({'api_m': 'search_process', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"type": contenttypeid, "query": query, "titleonly": titleonly and 1 or 0, "forumchoice": forumchoice, "prefixchoice": prefixchoice, "showposts": showposts and 1 or 0})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			if not self.IsError(retval, ['search']):
				return retval['show']['searchid']
			else:
				print(retval)
				return False
		except:
			return False
	def ProcessSearch(self, searchid):
		if not self.IsInit(): return False
		signed = self.Sign({"api_m": "search_showresults"})
		get = urlencode({'api_m': 'search_showresults', 'api_c': self.init["apiclientid"], 'api_s': self.init["apiaccesstoken"], 'api_sig': signed})
		post = urlencode({"searchid": searchid})
		try:
			retval = json.load(urlopen(self.url + "?%s" % get, post))
			if not self.IsError(retval):
				if isinstance(retval['response']['searchbits'], dict):
					out = []
					out.append(retval['response']['searchbits'])
					return out
				return retval['response']['searchbits']
			else:
				return []
		except:
			return []