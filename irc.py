##############################################################
##############################################################
##			   IMBot			    ##
##							    ##
##							    ##
##							    ##
##			by Trixar_za			    ##
##		 	 and Squirm			    ##
##	       - I know noone will see this :D -	    ##
##############################################################
##############################################################

########################
#    Imports Needed    #
########################
import socket
import time
from time import strftime
from threading import Thread
import pickle
import re

########################
#     Read Config      #
########################
def readconf():
## Made it a global function to make it easier to use for functions like reloading or rehashing ##
	file = open("imbot.conf")
	## It should read by default, so no need to set it :P ##
	info = file.readlines()
	for item in info:
		try:
			item = item[:-1]
			## Checks if the thing is comments/spaces or a configuration option: ##
			if item != "" and "=" in item:
				item = item.split(" = ")
				key = item[0]
				try:		
					value = item[1:]
					## The value has to be changed from a list to a string ##
					value = ' '.join(value)

					## Globalise ##
					global clientnick
					global clientname

					global serverhost
					global serverport
					global serverpass
					global serverid
					global servername

					## We might have to rewrite how it does this  ##
					## to allow for dynamic reloading & rehashing ##
					## Read: Do direct setting of example:        ##
					## bot.nick = value or serv.nick = value      ##

					## Client Options ##
					if key == "CLIENTNICK":
						clientnick = value
					if key == "CLIENTNAME":
						clientname = value

					## Server Options ##
					if key == "SERVERHOST":
						serverhost = value
					if key == "SERVERPORT":
						serverport = value
					if key == "SERVERNAME":
						servername = value
					if key == "SERVERPASS":
						serverpass = value
					if key == "SERVERID":
						serverid = value

				except IndexError, err:
					print "Please set a value for %s" % key
		except IndexError, err:
			print "%s - File not configured correctly" % err
	file.close()

	file = open("general.settings", "r")
	global general
	general = pickle.load(file)
	file.close()

	file = open("user.settings", "r")
	global usersets
	usersets = pickle.load(file)
	file.close()

########################
#   IRC Global Class   #
########################
class glo(Thread):
	## A few self. startup variables ##
	def __init__ (self):
		Thread.__init__(self)

	def irc_global(self, msg, nick, txt, channel):
		## Sends the message to all IM users other than the user who sent it ##
		clregex = re.compile('\003([0-9][0-9]?(,[0-9][0-9]?)?)?|[^\x20-\x7E]')
		msg = clregex.sub('', msg)
		for user in func.general["users"]:
			if user != nick:
				if user in func.chanusers[channel]:
					keys = func.pvt.keys()
					if user in keys:
						if txt:
							bot.send_message("PRIVMSG %s :**Chan - %s: %s" % (user, nick, msg))
						else:
							bot.send_message("PRIVMSG %s :**Chan - *** %s %s" % (user, nick, msg))
					else:
						if txt:
							bot.send_message("PRIVMSG %s :%s: %s" % (user, nick, msg))
						else:
							bot.send_message("PRIVMSG %s :*** %s %s" % (user, nick, msg))

########################
# IRC Functions Class #
########################
## IRCFunctions class stores functions in its own thread ##
class ircfunctions(Thread):
	## A few self. startup variables ##
	def __init__ (self):
		Thread.__init__(self)
		self.server_buffer = ""
		self.identhost = ''
		self.nick = ''
		self.msg = ''
		self.userinfo = {}
		self.chanusers = {}
		self.pvt = {}
		self.general = general
		self.usersettings = usersets
		self.accounts = { "check": False }
		self.userid = {}
		self.illegalchars = ["/", "+", "$", "&", "#", "@", "!", "=", "%", "*", "{", "}", "~", ":", ";", "'", ".", "?", "|"]

	## Encryption Functions ##
	def encode(self, encode):
		original = encode
		finished = ""
		length = len(original)-1
		x = 0
		while x <= length:
			tmp = ord(original[x])
			if finished == "":
				if tmp <= 63:
					finished = chr(134) + chr(tmp)
				else:
					strftime("%Y-%m-%d %H:%M:%S")
					finished = chr(2*tmp -126)
			else:
				if tmp <= 63:
					finished = finished + chr(134) + chr(tmp)
				else:
					finished = finished + chr(2*tmp -126)
			x = x+1
		return finished

	def decode(self, decode):
		q = False
		x = 0
		length = len(decode)
		finished = ""
		while x <= length-1:
			if q:
				if finished == "":
					finished = decode[x]
				else:
					finished = finished + decode[x]
				x = x+1
				q = False
			else:
				tmp = ord(decode[x])
				tmp1 = tmp
				tmp = tmp-126
				tmp = tmp/(-2)
				if tmp1 == 134:
					q = True
				else:
					if finished == "":
						finished = chr(tmp+tmp1)
					else:
						finished = finished + chr(tmp+tmp1)
				x = x+1
		return finished

	##############
	## File I/O ##
	##############
	## Pickle(For Dicts) ##
	def pickle_write(self, filename, obj):
		file = open(filename, "w+")
		pickle.dump(obj, file)
		file.close()

	def pickle_read(self, filename):
		file = open(filename, "r")
		obj = pickle.load(file)
		return obj
		file.close()

	## List ##
	def file_write(self, filename, obj, code):
		file = open(filename, "w+")
		for item in obj:
			if code:
				item = self.encode(item)
			file.write(item + "\n")
		file.close()

	def file_read(self, filename, code):
		file = open(filename, "r")
		obj = file.readlines()
		obj2 = []
		for item in obj:
			item = item[:-1]
			if code:
				item = self.decode(item)
			obj2.append(item)
		return obj2
		file.close()

	## Wrappers for IMBot ###
	def log(self, msg, server):
		time = strftime("%H:%M:%S")
		if server:
			print "- %s - Server: %s" %(time, " ".join(msg))
		else:
			print "- %s - Client: %s" %(time, " ".join(msg))
		

	def irc_send(self, msg):
		bot.send_message("%s\r\n" % msg)

	def irc_msg(self, msg, nick):
		self.irc_send("PRIVMSG %s :%s" % (nick, msg))

	def user_query(self, nick, target, msg):
		serv.send_message(":%s PRIVMSG %s :%s" % (nick, target, msg))

	def irc_say(self, msg, nick):
		serv.send_message(":%s PRIVMSG %s :%s" % (nick, self.chanusers[nick], msg))
		gl.irc_global(msg, nick, True, self.chanusers[nick])

	def irc_act(self, nick, msg, target):
		if target.lower() in self.general["chans"]:
			try:
				if self.pvt[nick]:
					serv.send_message(":%s PRIVMSG %s :\001ACTION %s\001" % (nick, self.pvt[nick], msg))
			except KeyError, err:
				serv.send_message(":%s PRIVMSG %s :\001ACTION %s\001" % (nick, self.chanusers[nick], msg))
				gl.irc_global(msg, nick, False, target)
				self.log(err, False)
		else:
			serv.send_message(":%s PRIVMSG %s :\001ACTION %s\001" % (nick, target, msg))

	def irc_service(self, msg, target, nick):
		serv.send_message(":%s PRIVMSG %s :%s" % (nick, target, msg))

	def irc_ns_identify(self, msg, nick):
		serv.send_message(":%s PRIVMSG NickServ :identify %s" % (nick, msg))

	def irc_help(self, nick, hnum):
		try:
			hnum = int(hnum)
			if hnum == 101:
				self.irc_msg("Type .in to start, .out to stop or .h for help", nick)
				self.irc_msg("News: %s" % (self.general["news"]), nick)
			if hnum == 0:
				self.irc_msg("Common Commands:", nick)
				self.irc_msg(".n new_nick - Changes your nick", nick)
				self.irc_msg(".nl - Shows who's in the channel", nick)
				self.irc_msg(".me - Performs an action", nick)
				self.irc_msg("For more help see:", nick)
				self.irc_msg(".h 1 - General Commands", nick)
				self.irc_msg(".h 2 - Nickname Commands", nick)
				self.irc_msg(".h 3 - Private Commands", nick)
				self.irc_msg(".h 4 - User Settings", nick)
				if nick in self.general["botmasters"]: self.irc_msg(".h 5 - Admin Commands", nick)
			if hnum == 1:
				self.irc_msg("General Commands:", nick)
				self.irc_msg(".in - Connects you", nick)
				self.irc_msg(".out - Disconnects you", nick)
				self.irc_msg(".quit - Disconnects you", nick)
				self.irc_msg(".nl - Shows who's in the channel", nick)
				self.irc_msg(".me - Performs an action", nick)
				self.irc_msg(".listmasters - Lists Botmasters", nick)
				self.irc_msg(".chans - Lists the channels you can join", nick)
				self.irc_msg(".list - Lists the channels you can join", nick)
				self.irc_msg(".j <chan> - Joins <chan>", nick)
				self.irc_msg(".join <chan> - Joins <chan>", nick)
				self.irc_msg(".news - Current news", nick)
				self.irc_msg(".bug <bug> - <bug> is the bug description", nick)
				self.irc_msg(".idea <idea> - <idea> is your brilliant idea!", nick)
	
			if hnum == 2:
				self.irc_msg("Nickname Commands:", nick)
				self.irc_msg(".n new_nick - Changes your nick", nick)
				self.irc_msg(".nick new_nick - Changes your nick", nick)
				self.irc_msg(".n? - Shows your current nick", nick)
	
			if hnum == 3:
				self.irc_msg("Private Commands:", nick)
				self.irc_msg(".p <nick> <msg> - Sends private msg <msg> to <nick>", nick)
				self.irc_msg(".msg <nick> <msg> - Sends private msg <msg> to <nick>", nick)
				self.irc_msg(".pl <nick> - Locks you in private with <nick>", nick)
				self.irc_msg(".pu - Unlocks your private", nick)
				self.irc_msg(".cm - Sends message to chan while private locked", nick)
				self.irc_msg(".cme - Sends action to chan while private locked", nick)
				self.irc_msg(".mep <nick> <msg> - Sends <msg> to <nick> as an action", nick)
	
			if hnum == 4:
				self.irc_msg("User Settings:", nick)
				self.irc_msg(".set <setting> <value> - eg. .set notify off:", nick)
				self.irc_msg("notify on/off - Changes your whether you get a message on connect", nick)
				self.irc_msg("nicklist on/off - Shows who is on the channel when you join", nick)
				self.irc_msg("chan <channel> - Joins <channel> by default", nick)
				self.irc_msg("-", nick)
				self.irc_msg(".set - Shows Current Settings", nick)

			if hnum == 5 and nick in self.general["botmasters"]:
				self.irc_msg("Admin Commands:", nick)
				self.irc_msg(".die - Shutsdown IMBot", nick)
				self.irc_msg(".raw <message> - Client side raw <message>", nick)
				self.irc_msg(".res <num> - Resets the IM account <num>(<num> may be 'all')", nick)
				self.irc_msg(".conn - Shows connected IM users", nick)
				self.irc_msg(".imconn - Shows logged in IM users with there account details", nick)
				self.irc_msg(".ban <nick> - Bans <nick>", nick)
				self.irc_msg(".unban <nick> - Unbans <nick>", nick)
				self.irc_msg(".banlist - List of Banned Users", nick)
				self.irc_msg(".online - Activates the bot if disactivated", nick)
				self.irc_msg(".offline - Disactivates the bot(Botmaster Use Only)", nick)
				self.irc_msg(".dc <nick> - Disconnects <nick>", nick)
				self.irc_msg(".addmaster <nick> - Adds <nick>", nick)
				self.irc_msg(".delmaster <nick> - Adds <nick>", nick)
				self.irc_msg(".raw <command> - Client Side Raw Command(Must know raw irc commands)", nick)
				self.irc_msg(".sraw <command> - Serve Side Raw Command(Must know raw irc server commands)", nick)
				self.irc_msg(".acclist - Lists accounts", nick)
				self.irc_msg(".addaccount <type> <username> <password> - Adds an IM account", nick)
				self.irc_msg(".delaccount <number> - Deletes account <number>", nick)
				self.irc_msg(".addchan <chan> - Adds <chan> to the bot join list", nick)
				self.irc_msg(".delchan <chan> - Removes <chan> from the bot join list", nick)
				self.irc_msg(".gl <msg> - Sends <msg as an IM global message", nick)
				self.irc_msg(".usercount - The number of users who have accessed the bot", nick)

		except ValueError, err:
			self.irc_msg("Please supply a valid number.", nick)

	def pvtcheck(self, msg, nick):
		try:
			if self.pvt[nick]:
				self.user_query(nick, self.pvt[nick], msg)
		except KeyError, err:
			self.irc_say(msg, self.nick)
			self.log(err, False)

	## Creates the unique timestamp ##
	def get_time(self):
		tstamp = time.time()
		tstamp = str(tstamp)
		tstamp = tstamp[:-3]
		return int(tstamp)

	def create_settings(self, ident):
		# Notify, nicklist on join, topic on join, default chan, nickserv
		self.usersettings[ident] = [True, False, False, "#Chatz", "", "", "", "", ""]
		self.pickle_write("user.settings", self.usersettings)

	def create_user(self, nick, silent):
		ident = self.userinfo[nick]
		try:
			check = []
			check = self.usersettings[ident]
		except KeyError, err:
			self.create_settings(ident)
		
		settings = self.usersettings[ident]
		serv.send_message("NICK %s 1 %d %s %s.user.imbot %s %s :IMBot" % (nick, self.get_time(), nick, self.userid[self.identhost], serv.NAME, serv.SNUMBER))
		self.join_channel(settings[3], nick, silent)
		self.general["users"].append(nick)		## Added to the self.general["users"] list ##
		settings = self.usersettings[self.userinfo[nick]]
		if not settings[4] == "":
			self.irc_ns_identify(self.decode(settings[4]), nick)

	def user_check(self, nick):
		if nick[:3] == "_27":
			self.irc_msg("Your nickname is your cellphone number.", nick)
			self.irc_msg("Type .n new_nick_here to change it.", nick)
		else:
			try:
				if self.identhost in self.general["banlist"]:
					self.irc_msg("You are currently banned. Please contact an administrator for more information.", nick)
				else:
					if self.nick in self.general["users"]:
						self.irc_msg("You are already connected.", nick)
					else:
						self.create_user(nick, False)
			except KeyError, err:
				self.general["banlist"] = []
				if self.nick in self.general["users"]:
					self.irc_msg("You are already connected.", nick)
				else:
					self.create_user(nick, False)

	def ban_user(self, nick):
		try:
			if nick in self.general["users"]:
				if self.userinfo[nick] in self.general["banlist"]:
					return "User is already banned."
				else:
					self.general["banlist"].append(self.userinfo[nick])
					self.quit_user(nick, 1)
					return "User has been banned."
			else:
				return "User is not an IM user"
		except AttributeError, err:
			return "User needs to be logged on to use this action"
		self.pickle_write("general.settings", self.general)

	def unban_user(self, nick):
		try:
			if self.userinfo[nick] in self.general["banlist"]:
				self.general["banlist"].remove(self.userinfo[nick])
				return "User has been unbanned."
			else:
				return "User is not banned."
		except AttributeError, err:
			return "User needs to be logged on to use this action"
		self.pickle_write("general.settings", self.general)

	def change_nick(self, old_nick, new_nick, connected):
		if connected:
			if len(new_nick) < 31:
				notillegal = True
				for x in self.illegalchars:
					if notillegal:
						if x in new_nick:
							self.irc_msg("Nickname has not been changed. Please keep it below 31 characters", old_nick)
							notillegal = False
				if notillegal:
					self.general["users"].append(new_nick)
					self.general["users"].remove(old_nick)
					self.chanusers[self.chanusers[old_nick]].remove(old_nick)
					self.chanusers[self.chanusers[old_nick]].append(new_nick)
					self.chanusers[new_nick] = self.chanusers[old_nick]
					del self.chanusers[old_nick]
					gl.irc_global("is now known as %s" % new_nick, old_nick, False, self.chanusers[new_nick])
					serv.send_message(":%s NICK %s" % (old_nick, new_nick))
					self.irc_send("PRIVMSG &bitlbee :rename %s %s" % (old_nick, new_nick))
					self.irc_msg("You are now known as %s" % new_nick, new_nick)
					try:
						if self.pvt[old_nick]:
							self.pvt[new_nick] = self.pvt[old_nick]
							del self.pvt[old_nick]
					except KeyError, err:
						self.log(err, False)

			else:
				self.irc_msg("Nickname has not been changed. Please keep it below 31 characters", old_nick)

		else:
			self.irc_send("PRIVMSG &bitlbee :rename %s %s" % (old_nick, new_nick))
			self.irc_msg("You are now known as %s" % new_nick, new_nick)
			self.nick = new_nick

		self.userinfo[new_nick] = self.userinfo[old_nick]
		del self.userinfo[old_nick]

	def add_chan(self, chan):
		chan = chan.lower()
		try:
			self.general["chans"].append(chan)
		except AttributeError, err:
			self.general["chans"] = [chan]
		self.chanusers[chan] = []
		sfunc.bot_do("JOIN %s" % chan)
		self.pickle_write("general.settings", self.general)

	def del_chan(self, chan, part):
		chan = chan.lower()
		if chan in self.general["chans"]:
			self.general["chans"].remove(chan)
		if part == 1:
			sfunc.bot_do("PART %s :PyIMBot by Trixar_za and Squirm" % chan)
		self.pickle_write("general.settings", self.general)

	def list_chan(self):
		try:
			return self.general["chans"]
		except KeyError, err:
			return "None"

	def quit_user(self, nick, tnum):
		if nick in self.general["users"]:
			serv.send_message(":%s QUIT :PyIMBot by Trixar_za and Squirm" % (nick))
			serv.send_message(":%s QUIT :PyIMBot by Trixar_za and Squirm" % (nick))
		gl.irc_global("has quit", nick, False, self.chanusers[nick])
		if tnum != 0:
			self.irc_msg("Disconnected", nick)
		self.remove_user(nick)

	def remove_user(self, nick):
		self.general["users"].remove(nick)
		chan = self.chanusers[nick]
		try:
			self.chanusers[chan].remove(nick)
		except ValueError, err:
			pass
		del self.chanusers[nick]

	def irc_quit(self):
		self.irc_send("QUIT :IMBot by Trixar_za and Squirm")
		serv.send_message(":Analogue QUIT :IMBot by Trixar_za and Squirm")
		self.irc_send(":imbot.gigirc.com SQUIT :IMBot by Trixar_za and Squirm")
		for nick in self.general["users"]:
			serv.send_message(":%s QUIT :IMBot by Trixar_za and Squirm" % nick)
			self.irc_msg("Disconnected Due to Shutdown", nick)
		bot.running = False
		serv.running = False
		thread.interrupt_main()

	def irc_reset(self, num):
		sfunc.bot_say("Resetting IM Accounts...", "all")
		if num == "all":
			self.irc_send("PRIVMSG &bitlbee :account off")
			time.sleep(3)
			self.irc_send("PRIVMSG &bitlbee :account on")
			time.sleep(3)
			self.irc_send("PRIVMSG &bitlbee :yes")
		else:
			self.irc_send("PRIVMSG &bitlbee :account %s off" % num)
			time.sleep(3)
			self.irc_send("PRIVMSG &bitlbee :account %s on" % num)
		sfunc.bot_say("IM Accounts Reset Complete", "all")

	def active(self, act):
		self.general["active"] = act
		self.pickle_write("general.settings", self.general)

	def isactive(self):
		act = self.general["active"]
		return act

	def report_bug(self, args, nick):
		bug = ' '.join(args)
		bug = "%s: %s" % (nick, bug)
		file = open("bugs.txt", "w")
		file.write(bug + "\n")
		file.close()
		return "Bug accepted, thanks for your help in making IMBot better."

	def report_idea(self, args, nick):
		idea = ' '.join(args)
		idea = "%s: %s" % (nick, idea)
		file = open("ideas.txt", "w")
		file.write(idea + "\n")
		file.close()
		return "Idea accepted, thanks for your help in making IMBot better."

	def im_global(self, args, nick):
		for channel in self.general["chans"]:
			gl.irc_global("**Global msg - %s **" % ' '.join(args), nick, True, channel)
		return "Global sent"

	def join_channel(self, channel, nick, silent):
		channel = channel.lower()
		if channel in self.general["chans"]:
			try:
				try:
					serv.send_message(":%s PART %s :PyIMBot by Trixar_za and Squirm" % (nick, self.chanusers[nick]))
					self.chanusers[self.chanusers[nick]].remove(nick)
					gl.irc_global("has parted the channel", nick, False, self.chanusers[nick])
				except ValueError, err:
					pass
			except KeyError, err:
				pass
			serv.send_message(":%s JOIN %s" % (nick, channel))
			gl.irc_global("has joined the channel", nick, False, channel)
			if not silent:
				self.irc_msg("Joined %s" % channel, nick)
			try:
				try:
					self.chanusers[channel].append(nick)
				except AttributeError, err:
					self.chanusers[channel] = [nick]
					
			except KeyError, err:
				self.chanusers[channel] = [nick]
			self.chanusers[nick] = channel
			settings = self.usersettings[self.userinfo[nick]]
			if settings[1]:
				num = str(len(self.chanusers[self.chanusers[nick]]))
				us = ', '.join(self.chanusers[self.chanusers[nick]])
				send = "(%s) %s" % (num, us)
				self.irc_msg(send, nick)

	def catch_accounts(self, cmd, msg2, args):
		if cmd == " ":
			try:
				number = int(msg2[1:2])
				self.accounts[number] = args[2]
				self.accounts["total"] = number
			except ValueError, err:
				rand = err
		else:
			try:
				number = int(msg2[0:2])
				self.accounts[number] = args[2]
				self.accounts["total"] = number
			except ValueError, err:
				rand = err
	
	def account_list(self, nick, frm):
		x = 0
		if frm == "c":
			self.irc_msg("Accounts List:", nick)
		else:
			sfunc.bot_notice("Accounts List:", nick)
		while x <= self.accounts["total"]:
			string = "%s - %s" % (str(x), self.accounts[x])
			if frm == "c":
				self.irc_msg(string, nick)
			else:
				sfunc.bot_notice(string, nick)
			
			x = x+1

	def account(self, frm, nick, action, args):
		if action == "add":
			try:
				imlist = ["msn",  "jabber", "oscar", "yahoo"]
				if args[0].lower() in imlist:
					self.irc_send("PRIVMSG &bitlbee :account add %s %s %s" % (args[0], args[1], args[2]))
					self.accounts["check"] = True
					self.irc_send("PRIVMSG &bitlbee :account list")
					if frm == "c":
						self.irc_msg("Added %s as an account. Username: %s and Password: %s" % (args[0], args[1], args[2]), nick)
					else:
						sfunc.bot_notice("Added %s as an account. Username: %s and Password: %s" % (args[0], args[1], args[2]), nick)
				else:
					if frm == "c":
						self.irc_msg("%s is an invalid account type" % (args[0]), nick)
					else:
						sfunc.bot_notice("%s is an invalid account type" % (args[0]), nick)
			except ValueError, err:
				rand = err
		if action == "del":
			try:
				num = int(args[0])
				if num <= self.accounts["total"]:
					self.irc_send("PRIVMSG &bitlbee :account off %s" % (str(num)))
					self.irc_send("PRIVMSG &bitlbee :account del %s" % (str(num)))
					self.irc_send("PRIVMSG &bitlbee :account list")
					if frm == "c":
						self.irc_msg("Deleted account %s" % (args[0]), nick)
					else:
						sfunc.bot_notice("Deleted account %s" % (args[0]), nick)
				else:
					if frm == "c":
						self.irc_msg("Invalid accound number: %s" % (args[0]), nick)
					else:
						sfunc.bot_notice("Invalid accound number: %s" % (args[0]), nick)
			except ValueError, err:
				rand = err	

	## Grabs the nickname out of the IRC Raw messages ##
	def irc_getnick(self, rnick):
		rnick = rnick.split("!")
		if rnick != '':
			return rnick

	## Cleans out the inital : in raw messages & removes the other possible junk the user might send... ##
	def irc_clean(self, msg):
		msg = msg.rstrip()
		if msg[:1] == ":":
			msg = msg[1:]
                clregex = re.compile('\003([0-9][0-9]?(,[0-9][0-9]?)?)?|[^\x20-\x7E]')
		msg = clregex.sub('', msg)
	        msg = msg.split()
		return msg


	#########################
	## IRC Commands parser ##
	#########################
	def irc_parser(self, msg):
		self.msg = self.irc_clean(msg)

		## Do not Log these
		if self.msg[1] != "301":
			self.log(self.msg, False)
		try:
			tempnick = self.irc_getnick(self.msg[0])
			self.identhost = tempnick[1]
		
			self.nick = tempnick[0]
		except IndexError, err:
			self.log(err, False)

		## This keeps us connected to the IRC server ##
	       	if self.msg[0] == "PING":
	       	    	self.irc_send("PONG %s" % msg[1])

	       	if self.msg[0] != "server":
			## This controls what happens once the bot is connected ##
			try:
				msg2 = ' '.join(self.msg[3:])
				msg2 = msg2[1:]			## Just joins all text after self.msg[2] ##
				msg3 = ' '.join(self.msg[4:])	## Just joins all text after self.msg[3] ##

				## Identifies to Bitlbee and starts the accounts ##
				if self.msg[1] == "353":
					self.irc_send("PRIVMSG &bitlbee :identify TheIMBot")
					time.sleep(1)
					self.irc_send("PRIVMSG &bitlbee :account list")
					self.accounts["check"] = True

				## Message Events ##
				if self.msg[1] == "PRIVMSG":
					chan = self.msg[2]		## The Channel the Command was issued from ##
					cmd = self.msg[3].lower()	## The Command that was used ##
					cmd = cmd[1:]
					args = self.msg[4:]		## What came after the command and starts at args[0] ##

					## Channel Commands ##
					## This is to show what the bot can do ##
					if chan[:1] == "&":
						if "accept/reject" in self.msg:
							self.irc_send("PRIVMSG &bitlbee :yes")
							self.irc_send("PRIVMSG &bitlbee :yes")
						if msg2 == "End of account list":
							self.accounts["check"] = False
						if self.accounts["check"] == True:
							self.catch_accounts(cmd, msg2, args)

					## Private Messages & Commands ##
					else:
						status = self.isactive()
						if self.nick in self.general["botmasters"]:
							status = True
						if status == True:
							usedcmd = False
							if cmd == ".in":
								if not usedcmd:
									usedcmd = True
									self.user_check(self.nick)
	
							if cmd == ".h":
								if not usedcmd:
									usedcmd = True
									try:
										self.irc_help(self.nick, args[0])
									except IndexError, err:
										self.irc_help(self.nick, 0)

							if cmd == ".help":
								if not usedcmd:
									usedcmd = True
									try:
										self.irc_help(self.nick, args[0])
									except IndexError, err:
										self.irc_help(self.nick, 0)
	
							if cmd == ".n":
								if not usedcmd:
									usedcmd = True
									if self.nick in self.general["users"]:
										self.change_nick(self.nick, args[0], True)
									else:
										self.change_nick(self.nick, args[0], False)

							if cmd == ".nick":
								if not usedcmd:
									usedcmd = True
									if self.nick in self.general["users"]:
										self.change_nick(self.nick, args[0], True)
									else:
										self.change_nick(self.nick, args[0], False)

							if cmd == ".n?":
								if not usedcmd:
									usedcmd = True
									self.irc_msg("Your nickname is: %s" % self.nick, self.nick)
	
							if cmd == ".news":
								if not usedcmd:
									usedcmd = True
									self.irc_msg("News: %s" % (self.general["news"]), self.nick)
	
							if cmd == ".listmasters":
								if not usedcmd:
									usedcmd = True
									sfunc.listmaster(self.nick, 1)

							if cmd == ".bug":
								if not usedcmd:
									usedcmd = True
									self.irc_msg(self.report_bug(args, self.nick), self.nick)

							if cmd == ".idea":
								if not usedcmd:
									usedcmd = True
									self.irc_msg(self.report_idea(args, self.nick), self.nick)

							if cmd == ".set":
								# Notify(0), nicklist on join(1), topic on join(2), default chan(3), nickserv(4)
								if not usedcmd:

									try:
										settings = self.usersettings[self.identhost]
									except KeyError, err:
										self.create_settings(self.identhost)
										settings = self.usersettings[self.identhost]

									try:	
										if self.nick in self.general["botmasters"]:
											if args[0] == "news":
												usedcmd = True
												self.general["news"] = ' '.join(args[1:])
												self.irc_msg("News Set", self.nick)
												self.irc_msg("News: %s" %(self.general["news"]), self.nick)
												self.pickle_write("general.settings", self.general)
										if args[0] == "notify":
											if args[1] == "off":
												settings[0] = False
												self.irc_msg("Notify Off", self.nick)
											else:
												settings[0] = True
												self.irc_msg("Notify On", self.nick)
										if args[0] == "nicklist":
											if args[1] == "off":
												settings[1] = False
												self.irc_msg("Nicklist on join: off", self.nick)
											else:
												settings[1] = True
												self.irc_msg("Nicklist on join: on", self.nick)
										if args[0] == "topic":
											if args[1] == "off":
												settings[2] = False
												self.irc_msg("Topic on join: off", self.nick)
											else:
												settings[2] = True
												self.irc_msg("Topic on join: on", self.nick)
										if args[0] == "chan":
											try:
												if args[1] in self.list_chan():
													settings[3] = args[1]
													self.irc_msg("Default Channel: %s" %(settings[3]), self.nick)
												else:
													self.irc_msg("To get a list of channels, type: .chans", self.nick)
											except IndexError, err:
												settings[3] = "#Chatz"
												self.irc_msg("Default Channel: %s" %(settings[3]), self.nick)
										if args[0] == "pass":
											try:
												settings[4] = self.encode(args[1])
												self.irc_msg("Nickserv Password: %s" %(args[1]), self.nick)
											except IndexError, err:
												settings[4] = ""
												self.irc_msg("Nickserv Password Removed", self.nick)
										self.usersettings[self.identhost] = settings
										self.pickle_write("user.settings", self.usersettings)
									except IndexError, err:
										self.irc_msg("Notify on connect: %s" %(str(settings[0])), self.nick)
										self.irc_msg("Nicklist on join: %s" %(str(settings[1])), self.nick)
										self.irc_msg("Topic on join: %s" %(str(settings[2])), self.nick)
										self.irc_msg("Default Channel: %s" %(settings[3]), self.nick)
										self.irc_msg("Nickname Password: %s" %(self.decode(settings[4])), self.nick)
										print settings[4]
									usedcmd = True

			
	
							if self.nick in self.general["botmasters"]:
								if cmd == ".die":
									if not usedcmd:
										usedcmd = True
										self.irc_quit()

								if cmd == ".restart":
									if not usedcmd:
										usedcmd = True
										self.irc_quit()
	
								if cmd == ".offline":
									if not usedcmd:
										usedcmd = True
										self.active(False)
										self.irc_msg("Bot activity: %s" % str(self.isactive), self.nick)
	
								if cmd == ".online":
									if not usedcmd:
										usedcmd = True
										self.active(True)
										self.irc_msg("Bot activity: %s" % str(self.isactive), self.nick)
	
								if cmd == ".res":
									if not usedcmd:
										usedcmd = True
										try:
											self.irc_reset(args[0])
										except IndexError, err:
											self.irc_msg("Invalid Account Number", self.nick)

								if cmd == ".reset":
									if not usedcmd:
										usedcmd = True
										try:
											self.irc_reset(args[0])
										except IndexError, err:
											self.irc_msg("Invalid Account Number", self.nick)
	
								if cmd == ".usercount":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("Total users: %s" % self.userid["total"], self.nick)
	
								if cmd == ".banlist":
									if not usedcmd:
										usedcmd = True
										self.irc_msg(self.general["banlist"], self.nick)

								if cmd == ".banned":
									if not usedcmd:
										usedcmd = True
										self.irc_msg(self.general["banlist"], self.nick)
	
								if cmd == ".ban":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("%s" % self.ban_user(args[0]), self.nick)
	
								if cmd == ".unban":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("%s" % self.unban_user(args[0]), self.nick)
	
								if cmd == ".addchan":
									if not usedcmd:
										usedcmd = True
										self.add_chan(args[0])

								if cmd == ".delchan":
									if not usedcmd:
										usedcmd = True
										self.del_chan(args[0], 1)

								if cmd == ".conn":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("IM Users:", self.nick)
										self.irc_msg(self.general["users"], self.nick)

								if cmd == ".connected":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("IM Users:", self.nick)
										self.irc_msg(self.general["users"], self.nick)
	
								if cmd == ".imconn":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("User Info for Connected Users:", self.nick)
										self.irc_msg("%s" % self.userinfo, self.nick)

								if cmd == ".imconnected":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("User Info for Connected Users:", self.nick)
										self.irc_msg("%s" % self.userinfo, self.nick)

								if cmd == ".dc":
									if not usedcmd:
										usedcmd = True
										try:
											if args[0] in self.general["users"]:
												self.quit_user(args[0], 1)
										except IndexError, err:
											self.irc_msg("Please provide a nickname", self.nick)

								if cmd == ".kill":
									if not usedcmd:
										usedcmd = True
										try:
											if args[0] in self.general["users"]:
												self.quit_user(args[0], 1)
										except IndexError, err:
											self.irc_msg("Please provide a nickname", self.nick)
	
								if cmd == ".acclist":
									if not usedcmd:
										usedcmd = True
										self.account_list(self.nick, "c")

								if cmd == ".accountlist":
									if not usedcmd:
										usedcmd = True
										self.account_list(self.nick, "c")

								if cmd == ".addmaster":
									if not usedcmd:
										usedcmd = True
										try:
											sfunc.addmaster(self.nick, args[0], 1)
										except IndexError, err:
											self.irc_msg("Please provide a nickname", self.nick)
	
								if cmd == ".delmaster":
									if not usedcmd:
										usedcmd = True
										try:
											sfunc.delmaster(self.nick, args[0], 1)
										except IndexError, err:
											self.irc_msg("Please provide a nickname", self.nick)
	
								if cmd == ".addaccount":
									if not usedcmd:
										usedcmd = True
										self.account("c", self.nick, "add", args)
	
								if cmd == ".delaccount":
									if not usedcmd:
										usedcmd = True
										self.account("c", self.nick, "del", args)
	
								if cmd == ".raw":
									if not usedcmd:
										usedcmd = True
										self.irc_send(' '.join(args))
	
								if cmd == ".sraw":
									if not usedcmd:
										usedcmd = True
										serv.send_message("%s" % (' '.join(args)))

								if cmd == ".gl":
									if not usedcmd:
										usedcmd = True
										self.irc_msg(self.im_global(args, self.nick), self.nick)

								if cmd == ".global":
									if not usedcmd:
										usedcmd = True
										self.irc_msg(self.im_global(args, self.nick), self.nick)
	
							if self.nick in self.general["users"]:
								if cmd == ".out":
									if not usedcmd:
										usedcmd = True
										self.quit_user(self.nick, 1)

								if cmd == ".quit":
									if not usedcmd:
										usedcmd = True
										self.quit_user(self.nick, 1)
	
								if cmd == ".j":
									if not usedcmd:
										usedcmd = True
										self.join_channel(args[0], self.nick, False)

								if cmd == ".join":
									if not usedcmd:
										usedcmd = True
										self.join_channel(args[0], self.nick, False)

								if cmd == ".chans":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("Channels:", self.nick)
										self.irc_msg("%s" % ', '.join(self.list_chan()), self.nick)

								if cmd == ".list":
									if not usedcmd:
										usedcmd = True
										self.irc_msg("Channels:", self.nick)
										self.irc_msg("%s" % ', '.join(self.list_chan()), self.nick)

								if cmd == ".nl":
									if not usedcmd:
										usedcmd = True
										num = str(len(self.chanusers[self.chanusers[self.nick]]))
										us = ', '.join(self.chanusers[self.chanusers[self.nick]])
										send = "(%s) %s" % (num, us)
										self.irc_msg(send, self.nick)

								if cmd == ".names":
									if not usedcmd:
										usedcmd = True
										num = str(len(self.chanusers[self.chanusers[self.nick]]))
										us = ', '.join(self.chanusers[self.chanusers[self.nick]])
										send = "(%s) %s" % (num, us)
										self.irc_msg(send, self.nick)
	
								if cmd == ".me":
									if not usedcmd:
										usedcmd = True
										self.irc_act(self.nick, msg3, self.chanusers[self.nick])

								if cmd == ".mep":
									if not usedcmd:
										usedcmd = True
										self.irc_act(self.nick, ' '.join(self.msg[5:]), args[0])
	
								if cmd == ".p":
									if not usedcmd:
										usedcmd = True
										self.user_query(self.nick, args[0], ' '.join(self.msg[5:]))

								if cmd == ".msg":
									if not usedcmd:
										usedcmd = True
										self.user_query(self.nick, args[0], ' '.join(self.msg[5:]))

								if cmd == ".pl":
									if not usedcmd:
										usedcmd = True
										self.pvt[self.nick] = args[0]
										self.irc_msg("Private lock with %s" % args[0], self.nick)
	
								if cmd == ".pu":
									if not usedcmd:
										usedcmd = True
										try:
											self.irc_msg("Private unlocked", self.nick)
											del self.pvt[self.nick]
										except KeyError, err:
											self.irc_msg("Not in private lock", self.nick)
	
								if cmd == ".cmsg":
									if not usedcmd:
										usedcmd = True
										if self.nick in self.pvt.keys():
											msg = ' '.join(args)
											# a new function :P
											sfunc.user_say(msg, self.nick)
											gl.irc_global(msg, self.nick, True, self.chanusers[self.nick])
										else:
											self.irc_msg("Not in private lock", self.nick)
	
								if cmd == ".cme":
									if not usedcmd:
										usedcmd = True
										if self.nick in self.pvt.keys():
											msg = ' '.join(args)
											# another new function ;)
											sfunc.user_act(msg, self.nick)
											gl.irc_global(msg, self.nick, False, self.chanusers[self.nick])
										else:
											self.irc_msg("Not in private lock", self.nick)

								if cmd == ".cs":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "ChanServ", self.nick)

								if cmd == ".chanserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "ChanServ", self.nick)


								if cmd == ".ns":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "NickServ", self.nick)

								if cmd == ".nickserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "NickServ", self.nick)


								if cmd == ".bs":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "BotServ", self.nick)

								if cmd == ".botserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "BotServ", self.nick)

								if cmd == ".hs":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "HostServ", self.nick)

								if cmd == ".hostserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "HostServ", self.nick)

								if cmd == ".ls":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "LoveServ", self.nick)

								if cmd == ".loveserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "LoveServ", self.nick)

								if cmd == ".gs":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "GameServ", self.nick)

								if cmd == ".gameserv":
									if not usedcmd:
										usedcmd = True
										msg = ' '.join(args)
										self.irc_service(msg, "GameServ", self.nick)

								if cmd == ".id":
									if not usedcmd:
										usedcmd = True
										passwd = ' '.join(args)
										self.irc_ns_identify(passwd, self.nick)

								if cmd == ".identify":
									if not usedcmd:
										usedcmd = True
										passwd = ' '.join(args)
										self.irc_ns_identify(passwd, self.nick)

								if not usedcmd:
									self.pvtcheck(msg2, self.nick)
									usedcmd = True

#						if not usedcmd:
#							self.irc_msg("You need to be connected, type .in or .h", self.nick)
						else:
							self.irc_msg("This service is offline, please try again later.", self.nick)

				## Other Events ##
				if self.msg[1] == "QUIT":
					if self.nick in self.general["users"]:
						self.quit_user(self.nick, 0)
						del self.userinfo[self.nick]

				if self.msg[1] == "PART":
					if self.nick in self.general["users"]:
						self.quit_user(self.nick, 0)
						del self.userinfo[self.nick]

				if self.msg[1] == "JOIN":
						if self.nick == sfunc.botnick:
							self.irc_send("PRIVMSG &bitlbee :yes")
							self.irc_send("PRIVMSG &bitlbee :yes")
						self.userinfo[self.nick] = self.identhost

						try:
							userid = self.userid[self.identhost]
						except KeyError, err:
							try:
								total = self.userid["total"]
							except KeyError, err:
								total = str(0)
								self.userid["total"] = str(0)
							userid = str(int(total)+1)
							self.userid["total"] = userid
						self.userid[self.identhost] = userid
						self.pickle_write("userid.imbot", self.userid)
						try:
							val = self.usersettings[self.identhost]
							val = val[0]
						except KeyError, err:
							val = True
						if val:
							if self.isactive() == True:
								self.irc_help(self.nick, 101)
							else:
								if self.nick in self.general["botmasters"]:
									self.irc_help(self.nick, 101)

			except IndexError, err:
				self.log(err, False)


###################
#####IRC Bot#######
###################
class ircbot(Thread):
	def __init__ (self):
		Thread.__init__(self)
		self.server_buffer = ""
		self.HOST = 'rock.gigirc.com'
		self.PORT = 6668
		self.NICK = clientnick
		self.NAME = clientname
		self.running = True

	def send_message(self, msg):
		if "\n" not in msg or "\r" not in msg:
			self.server.send("%s\r\n" % msg)
		else:
			self.server.send(msg)

	def run(self):
		self.server=socket.socket()
		self.server.connect((self.HOST, self.PORT))
		self.send_message("NICK %s" % (self.NICK))
		self.send_message("USER %s %s bla :%s" % (self.NAME, self.NAME, self.NAME))

		while self.running:
			self.server_buffer = self.server_buffer + self.server.recv(1024)
			self.server_temp = self.server_buffer.split("\r\n")
			self.server_buffer = self.server_temp.pop()

			for self.server_line in self.server_temp:
				func.irc_parser(self.server_line)

		else:
			self.server.close()


###############################
###############################
######The IRC Server Part######
###############################
###############################

##########################
# Server Functions Class #
##########################
## Serverfunctions class stores functions in its own thread ##
class serverfunctions(Thread):
	## A few self. startup variables ##
	def __init__ (self):
		Thread.__init__(self)
		self.server_buffer = ""
		self.nick = ''
		self.msg = ''
		self.botnick = clientnick

	## Wrappers for the Server and Server side controller bot ##
	def bot_notice(self, msg, nick):
		serv.send_message(":%s NOTICE %s :%s" % (self.botnick, nick, msg))

	def bot_say(self, msg, chan):
		if chan == "all":
			for x in func.general["chans"]:
				serv.send_message(":%s PRIVMSG %s :%s" % (self.botnick, x, msg))
		else:
			serv.send_message(":%s PRIVMSG %s :%s" % (self.botnick, chan, msg))

	def bot_do(self, todo):
		serv.send_message(":%s %s" % (self.botnick, todo))

	def user_say(self, msg, nick):
		serv.send_message(":%s PRIVMSG %s :%s" % (nick, func.chanusers[nick], msg))

	def user_act(self, msg, nick):
		serv.send_message(":%s PRIVMSG %s :\001ACTION %s\001" % (nick, func.chanusers[nick], msg))

	def on_start(self):
		func.general["botmasters"] = func.file_read("masters.imbot", True)
		func.general["users"] = []
		func.userid = func.pickle_read("userid.imbot")
		serv.send_message("NICK %s 1 %d %s admin.%s %s %s :IMBot" % (self.botnick, (func.get_time()+1), self.botnick, serv.NAME, serv.NAME, serv.SNUMBER))
		try:
			for x in func.general["chans"]:
				self.bot_do("JOIN %s" % x)
				serv.serv_do("MODE %s +ao %s %s" % (x, self.botnick, self.botnick))
		except KeyError, err:
			func.general["chans"] = ""
			func.pickle_write("general.settings", func.general)

	def on_join(self, nick, msg):
		msg2 = msg[2]
		msg2 = msg2.lower()
		msg2 = msg2.split(",")
		for x in msg2:
			try:
				if x in func.general["chans"]:
					try:
						gl.irc_global("has joined the channel", nick, False, x)
						func.chanusers[x].append(nick)
					except KeyError, err:
						func.chanusers[x] = [nick]

			except KeyError, err:
				func.general["chans"] = ""
				func.pickle_write("general.settings", func.general)
	

	def on_leave(self, nick, channel):
		if channel in func.general["chans"]:
			if nick in func.chanusers[channel]:
				func.chanusers[channel].remove(nick)
				gl.irc_global("has parted the channel", nick, False, channel)

	def on_quit(self, nick):
		for channel in func.general["chans"]:
			if nick in func.chanusers[channel]:
				gl.irc_global("has quit", nick, False, channel)
				func.chanusers[channel].remove(nick)

	def on_kick(self, nick, channel):
		if nick == self.botnick:
			serv.send_message(":%s JOIN %s" % (nick, channel))
			serv.serv_do("MODE %s +ao %s %s" % (channel, nick, nick))
			serv.send_message(":%s KICK %s %s :Unauthorised Kick" % (nick, channel, self.nick))

		if channel in func.general["chans"]:
			if nick in func.chanusers[channel]:
				func.chanusers[channel].remove(nick)
				gl.irc_global("has been kicked by %s" % self.nick, nick, False, channel)
				if nick in func.general["users"]:
					func.irc_msg("You have been kicked by %s. Type .in to reconnect" % self.nick, nick)
					func.remove_user(nick)
					

	def on_nick(self, old_nick, new_nick):
		for channel in func.general["chans"]:
			if old_nick in func.chanusers[channel]:
				func.chanusers[channel].remove(old_nick)
				func.chanusers[channel].append(new_nick)
				gl.irc_global("is now known as %s" % new_nick, old_nick, False, channel)

	def on_whois(self, nick, rest):
		## No Fucking clue what rest is or does - lol ##
		## ^^ I suggest http://www.mirc.net/raws/ ##
		if rest == self.botnick:
			serv.serv_do("311 %s %s Analogue admin.imbot * :PyIMBot Admin" % (nick, rest))
			serv.serv_do("319 %s %s :%s" % (nick, rest, ' '.join(func.general["chans"])))
			serv.serv_do("378 %s %s :is connecting from %s %s" % (nick, rest, "*@admin.imbot", "127.0.0.1"))
			serv.serv_do("312 %s %s imbot.gigirc.com :PyIMBot Server" % (nick, rest))
			serv.serv_do("320 %s %s :Using PyIMBot by Squirm and Trixar_za" % (nick, rest))
			serv.serv_do("318 %s %s :End of /WHOIS list" % (nick, rest))

		if rest in func.general["users"]:
			serv.serv_do("311 %s %s %s %s.user.imbot * :PyIMBot User" % (nick, rest, rest, func.userid[func.userinfo[rest]]))
			serv.serv_do("319 %s %s :%s" % (nick, rest, func.chanusers[rest]))
			serv.serv_do("378 %s %s :is connecting from %s %s" % (nick, rest, "*@user.imbot", "127.0.0.1"))
			serv.serv_do("312 %s %s imbot.gigirc.com :PyIMBot Server" % (nick, rest))
			serv.serv_do("320 %s %s :Using PyIMBot by Squirm and Trixar_za" % (nick, rest))
			serv.serv_do("318 %s %s :End of /WHOIS list" % (nick, rest))
			print "here1"
			if nick in func.general["botmasters"]:
				print "here2"
				try:
					print "yes"
					self.bot_notice("IM Address: %s" % (func.userinfo[rest]), nick)
				except IndexError, err:
					print "no"
					self.bot_notice("Could not retrieve address", nick)

	def on_acc_cmd(self, nick):
		self.bot_notice("Accounts Available:", nick)
		self.bot_notice("MSN: analogueirc@hotmail.com", nick)
		self.bot_notice("Jabber: analogue@jabber.org", nick)
		self.bot_notice("GTalk/Mxit: analogueirc@gmail.com", nick)
		self.bot_notice("GTalk/Mxit: chatznetirc@gmail.com", nick)
		self.bot_notice("Yahoo: analogueirc@yahoo.com", nick)
		self.bot_notice("Yahoo: ircanalogue@yahoo.com", nick)
		self.bot_notice("Facebook: http://www.facebook.com/analogueirc", nick)

	def on_ban_cmd(self, nick, nick2ban):
		if nick in func.general["botmasters"]:
			try:
				func.irc_send("WHOIS %s" % nick2ban)
			except IndexError, err:
				self.bot_notice("Please supply a nickname to ban", nick)
		else:
			self.bot_notice("You may not use this command", nick)

	def on_kill(self, msg):	
		nick = msg[2]
		p = True
		if nick in func.general["users"]:
			reason = ' '.join(msg[4:])
			func.remove_user(nick)
			print reason

			if msg[4] == "(Nick" and msg[5] == "Collision)":
				reason = ":Nickname is use. Please change your nickname, then type .in"

			if msg[5] == "<-":
				func.create_user(nick, True)
				p = False

			temp = msg[4]
			temp = temp[0]
			print temp
			if temp == "(":
				if p:
					func.irc_msg("You have been killed by %s" % msg[0], nick)
					func.irc_msg("Reason %s" % reason, nick)
		else:
			for channel in func.general["chans"]:
				if nick in func.chanusers[channel]:
					func.chanusers[channel].remove(nick)	

		for channel in func.general["chans"]:
			if nick in func.chanusers[channel]:
				gl.irc_global("has parted the channel", nick, False, channel)

	def on_svskill(self, msg):		
		nick = msg[2]
		if nick in func.general["users"]:
			func.irc_msg("You have been killed by %s" % msg[0], nick)
			func.irc_msg("Reason %s" % ' '.join(msg[3:]), nick)
			func.remove_user(nick)
		for channel in func.general["chans"]:
			if nick in func.chanusers[channel]:
				gl.irc_global("has parted the channel", nick, False, channel)
				func.chanusers[channel].remove(nick)

	def addmaster(self, me, nick, tp):
		if tp == 0:
			self.bot_notice("Added %s as a master" % nick, me)
		else:
			func.irc_msg("Added %s as a master" % nick, me)
		func.general["botmasters"].append(nick)
		func.file_write("masters.imbot", func.general["botmasters"], True)

	def delmaster(self, me, nick, tp):
		if tp == 0:
			self.bot_notice("Deleted %s as being a master" % nick, me)
		else:
			func.irc_msg("Deleted %s as being a master" % nick, me)
		func.general["botmasters"].remove(nick)
		func.file_write("masters.imbot", func.general["botmasters"], True)

	def listmaster(self, me, tp):
		if tp == 0:
			self.bot_notice("Masters of this bot in list form:", me)
			self.bot_notice(func.general["botmasters"], me)
		else:
			func.irc_msg("Masters of this bot in list form:", me)
			func.irc_msg(func.general["botmasters"], me)

	def dc_user(self, nick):
			if nick in func.general["users"]:
				func.quit_user(nick, 1)

	def chan_help(self, nick):
		self.bot_notice("User Commands:", nick)
		self.bot_notice(".acc - Shows IM accounts", nick)
		self.bot_notice(".chans - Shows Channels Analogue Joins", nick)
		self.bot_notice(".bug <bug> - <bug> is the bug description", nick)
		self.bot_notice(".idea <idea> - <idea> is Your brilliant idea!", nick)
		if self.nick in func.general["botmasters"]:
			self.bot_notice("-", nick)
			self.bot_notice("Admin Commands:", nick)
			self.bot_notice(".die - Shutsdown IMBot", nick)
			self.bot_notice(".res <num> - Resets the IM account <num>(<num> may be 'all')", nick)
			self.bot_notice(".conn - Shows connected IM users", nick)
			self.bot_notice(".imconn - Shows logged in IM users with there account details", nick)
			self.bot_notice(".ban <nick> - Bans <nick>", nick)
			self.bot_notice(".unban <nick> - Unbans <nick>", nick)
			self.bot_notice(".banlist - List of Banned Users", nick)
			self.bot_notice(".online - Activates the bot if disactivated", nick)
			self.bot_notice(".offline - Disactivates the bot(Botmaster Use Only)", nick)
			self.bot_notice(".dc <nick> - Disconnects <nick>", nick)
			self.bot_notice(".listmasters - Shows the list of botmasters", nick)
			self.bot_notice(".addmaster <nick> - Adds <nick>", nick)
			self.bot_notice(".delmaster <nick> - Adds <nick>", nick)
			self.bot_notice(".addchan <chan> - Adds Channel <chan>", nick)
			self.bot_notice(".delchan <chan> - Deletes Channel <chan>", nick)
			self.bot_notice(".chans - Lists Channels", nick)
			self.bot_notice(".acclist - Lists accounts", nick)
			self.bot_notice(".addaccount <type> <username> <password> - Adds an IM account", nick)
			self.bot_notice(".delaccount <number> - Deletes account <number>", nick)
			self.bot_notice(".gl <msg> - Sends <msg as an IM global message", nick)
			self.bot_notice(".usercount - The number of users who have accessed the bot", nick)

	def on_version(self, target, nick):
		serv.send_message(":%s NOTICE %s :\x01VERSION PyIMBot Server by Trixar_za and Squirm\x01" % (target, nick))

	def on_chat(self, target, nick):
		serv.send_message(":%s NOTICE %s :I do not yet support CHAT" % (target, nick))

	def on_ping(self, target, nick, tmp):
		serv.send_message(":%s NOTICE %s :\x01PING %s\x01" % (target, nick, tmp))

	def on_numeric(self, msg):
		if msg[1] == "432":
			new_nick = func.get_time()
			func.irc_msg("You have Illegal Characers in your nickname.", msg[3])
			func.irc_msg("Your nickname is now: %s - Please use .n new_nick to change it" % new_nick, msg[3])
			func.irc_send("PRIVMSG &bitlbee :rename %s %s" % (msg[3], new_nick))
			func.remove_user(msg[3])
			serv.send_message(":%s QUIT :PyIMBot by Trixar_za and Squirm" % (msg[3]))

	def on_chan(self, msg, channel):
		if msg[0] == "\x01":
			if msg[1:7] == "ACTION":
				tmp = " ".join(self.msg[4:])
				tmp = tmp[0:len(tmp)-1]
				gl.irc_global(tmp, self.nick, False, channel)
		else:
			usedcmd = False
			tmp = self.msg[3].lower()
			cmd = tmp[1:]

			if cmd == ".h":
				usedcmd = True
				self.chan_help(self.nick)

			if cmd == ".help":
				usedcmd = True
				self.chan_help(self.nick)

			if cmd == ".acc":
				usedcmd = True
				self.on_acc_cmd(self.nick)

			if cmd == ".accounts":
				usedcmd = True
				self.on_acc_cmd(self.nick)

			if cmd == ".die":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.irc_quit()

			if cmd == ".restart":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.irc_quit()

			if cmd == ".res":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					try:
						func.irc_reset(self.msg[4])
					except IndexError, err:
						self.bot_notice("Invalid Account Number.", self.nick)

			if cmd == ".reset":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					try:
						func.irc_reset(self.msg[4])
					except IndexError, err:
						self.bot_notice("Invalid Account Number.", self.nick)

			if cmd == ".addmaster":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.addmaster(self.nick, self.msg[4], 0)

			if cmd == ".delmaster":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.delmaster(self.nick, self.msg[4], 0)

			if cmd == ".dc":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.dc_user(self.msg[4])

			if cmd == ".kill":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.dc_user(self.msg[4])

			if cmd == ".conn":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice("IM Users:", self.nick)
					self.bot_notice(func.general["users"], self.nick)

			if cmd == ".connected":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice("IM Users:", self.nick)
					self.bot_notice(func.general["users"], self.nick)

			if cmd == ".imconnected":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice("Logged on IM Users:", self.nick)
					self.bot_notice(func.userinfo, self.nick)

			if cmd == ".imconn":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice("Logged on IM Users:", self.nick)
					self.bot_notice(func.userinfo, self.nick)

			if cmd == ".banlist":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.general["banlist"], self.nick)

			if cmd == ".banned":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.general["banlist"], self.nick)

			if cmd == ".ban":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.ban_user(self.msg[4]), self.nick)	

			if cmd == ".unban":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.unban_user(self.msg[4]), self.nick)					

			if cmd == ".addchan":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.add_chan(self.msg[4])

			if cmd == ".delchan":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.del_chan(self.msg[4], 1)

			if cmd == ".chans":
				self.bot_notice("Channels:", self.nick)
				self.bot_notice(', '.join(func.list_chan()), self.nick)
				usedcmd = True

			if cmd == ".list":
				self.bot_notice("Channels:", self.nick)
				self.bot_notice(', '.join(func.list_chan()), self.nick)
				usedcmd = True

			if cmd == ".bug":
				self.bot_notice(func.report_bug(self.msg[4:], self.nick), self.nick)
				usedcmd = True

			if cmd == ".idea":
				self.bot_notice(func.report_idea(self.msg[4:], self.nick), self.nick)
				usedcmd = True

			if cmd == ".acclist":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.account_list(self.nick, "s")

			if cmd == ".accountlist":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.account_list(self.nick, "s")

			if cmd == ".addaccount":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.account("s", self.nick, "add", self.msg[4:])

			if cmd == ".delaccount":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.account("s", self.nick, "del", self.msg[4:])

			if cmd == ".offline":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.active(False)
					self.bot_notice("Bot activity: %s" % str(func.isactive), self.nick)

			if cmd == ".online":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					func.active(True)
					self.bot_notice("Bot activity: %s" % str(func.isactive), self.nick)

			if cmd == ".usercount":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice("Total users: %s" % func.userid["total"], self.nick)

			if cmd == ".listmasters":
				usedcmd = True
				self.listmaster(self.nick, 0)

			if cmd == ".gl":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.im_global(self.msg[4:], self.nick), self.nick)

			if cmd == ".global":
				if self.nick in func.general["botmasters"]:
					usedcmd = True
					self.bot_notice(func.im_global(self.msg[4:], self.nick), self.nick)

			else:
				gl.irc_global(msg, self.nick, True, channel)

	def on_query(self, msg, target):
		if target in func.general["users"]:
			if msg[0] == "\x01":
				try:
					if msg[1:8] == "VERSION":
						self.on_version(target, self.nick)

					if msg[1:5] == "CHAT":
						self.on_chat(target, self.nick)

					if msg[1:5] == "PING":
						tmp = " ".join(self.msg[4:])
						tmp = tmp[0:len(tmp)-2]
						self.on_ping(target, self.nick, tmp)

					if msg[1:7] == "ACTION":
						tmp = " ".join(self.msg[4:])
						tmp = tmp[0:len(tmp)-2]
						func.irc_send("PRIVMSG %s :*** %s %s" % (target, self.nick, tmp))

				except IndexError, err:
					self.log(err, True)

			else:
				syncheck = self.msg[3]
				if syncheck[:1] != "\x01":
					func.irc_msg("*Pvt - %s: %s" % (self.nick, msg), target)

	def on_notice(self, msg, target):
		if target in func.general["users"]:
			clregex = re.compile('\003([0-9][0-9]?(,[0-9][0-9]?)?)?|[^\x20-\x7E]')
			msg = clregex.sub('', msg)
			syncheck = self.msg[3]
			if syncheck[:1] != "\x01":
				func.irc_msg("*Pvt - %s: %s" % (self.nick, msg), target)


	############################
	## Server Commands parser ##
	############################
	def server_parser(self, msg):
		self.msg = msg
		func.log(self.msg, True)

		nick = self.msg[0]
		self.nick = nick[1:]

		if self.msg[0] == "PING":
			serv.server.send("PONG %s" % self.msg[1])

		try:
			if self.msg[1] == "SMO":
				qregx = re.compile('imbot.gigirc.com\[.+\]')
				self.msg[7] = qregx.sub('imbot.gigirc.com', self.msg[7])
				if self.msg[7] == "imbot.gigirc.com":
					self.on_start()

			if self.msg[1] == "JOIN":
				self.on_join(self.nick, self.msg)

			if self.msg[1] == "PART":
				self.on_leave(self.nick, self.msg[2])

			if self.msg[1] == "QUIT":
				self.on_quit(self.nick)

			if self.msg[1] == "KICK":
				self.on_kick(self.msg[3], self.msg[2])

			if self.msg[1] == "KILL":
				self.on_kill(self.msg)

			if self.msg[1] == "SVSKILL":
				self.on_svskill(self.msg)

			if self.msg[1] == "NICK":
				self.on_nick(self.nick, self.msg[2])

			if self.msg[1] == "WHOIS":
				self.on_whois(self.nick, self.msg[2])

			if self.msg[1] == "432":
				self.on_numeric(self.msg)

			if self.msg[1] == "PRIVMSG":
				target = self.msg[2]

				msg2 = ' '.join(self.msg[3:])
				msg2 = msg2[1:]

				if target.lower() in func.general["chans"]:
					self.on_chan(msg2, target.lower())
				else:
					self.on_query(msg2, target)

			if self.msg[1] == "NOTICE":
				target = self.msg[2]

				msg2 = ' '.join(self.msg[3:])
				msg2 = msg2[1:]

				if target.lower() in func.general["chans"]:
					self.on_notice(msg2, target.lower())
				else:
					self.on_notice(msg2, target)

		except IndexError, err:
			func.log(err, True)


class server(Thread):
	def __init__ (self):
		Thread.__init__(self)
		self.server_buffer = ""
		self.HOST = serverhost
		self.PORT = int(serverport)
		self.PASS = serverpass
		self.NAME = servername
		self.HOPCOUNT = 1
		self.SNUMBER = int(serverid)
		self.running = True
		self.channel = "#chatz"

	def send_message(self, msg):
		if "\n" not in msg or "\r" not in msg:
			self.server.send("%s\r\n" % msg)
		else:
			self.server.send(msg)

	def serv_do(self, msg):
		self.send_message(":%s %s" % (self.NAME, msg))

	def run(self):
		self.server=socket.socket()
		self.server.connect((self.HOST, self.PORT))
		self.send_message("PASS %s\n" % self.PASS)
		self.send_message("SERVER %s %s %s :IMBot Server\n" % (self.NAME, self.HOPCOUNT, self.SNUMBER))

		while self.running:
			self.server_buffer = self.server_buffer + self.server.recv(1024)
			self.server_temp = self.server_buffer.split("\r\n")
			self.server_buffer = self.server_temp.pop()

			for self.server_line in self.server_temp:
				self.server_line = self.server_line.split(" ")
				sfunc.server_parser(self.server_line)

		else:
			self.server.close()


###########################
# This starts the threads #
###########################
## Let's read the conf first... ##
readconf()

gl = glo()
gl.start()

func = ircfunctions()
func.start()

sfunc = serverfunctions()
sfunc.start()

bot = ircbot()
bot.start()

serv = server()
serv.start()
