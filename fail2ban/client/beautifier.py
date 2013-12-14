# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet :

# This file is part of Fail2Ban.
#
# Fail2Ban is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fail2Ban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fail2Ban; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

__author__ = "Cyril Jaquier, Yaroslav Halchenko"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier, 2013- Yaroslav Halchenko"
__license__ = "GPL"

import logging

from fail2ban.exceptions import UnknownJailException, DuplicateJailException

# Gets the instance of the logger.
logSys = logging.getLogger(__name__)

##
# Beautify the output of the client.
#
# Fail2ban server only return unformatted return codes which need to be
# converted into user readable messages.

class Beautifier:
	
	def __init__(self, cmd = None):
		self.__inputCmd = cmd

	def setInputCmd(self, cmd):
		self.__inputCmd = cmd
		
	def getInputCmd(self):
		return self.__inputCmd
		
	def beautify(self, response):
		logSys.debug("Beautify " + `response` + " with " + `self.__inputCmd`)
		inC = self.__inputCmd
		msg = response
		try:
			if inC[0] == "ping":
				msg = "Server replied: " + response
			elif inC[0] == "start":
				msg = "Jail started"
			elif inC[0] == "stop":
				if len(inC) == 1:
					if response is None:
						msg = "Shutdown successful"
				else:
					if response is None:
						msg = "Jail stopped"
			elif inC[0] == "add":
				msg = "Added jail " + response
			elif inC[0:1] == ['status']:
				if len(inC) > 1:
					# Create IP list
					ipList = ""
					for ip in response[1][1][2][1]:
						ipList += ip + " "
					# Creates file list.
					fileList = ""
					for f in response[0][1][2][1]:
						fileList += f + " "
					# Display information
					msg = "Status for the jail: " + inC[1] + "\n"
					msg = msg + "|- " + response[0][0] + "\n"
					msg = msg + "|  |- " + response[0][1][2][0] + ":\t" + fileList + "\n"
					msg = msg + "|  |- " + response[0][1][0][0] + ":\t" + `response[0][1][0][1]` + "\n"
					msg = msg + "|  `- " + response[0][1][1][0] + ":\t" + `response[0][1][1][1]` + "\n"
					msg = msg + "`- " + response[1][0] + "\n"
					msg = msg + "   |- " + response[1][1][0][0] + ":\t" + `response[1][1][0][1]` + "\n"
					msg = msg + "   |  `- " + response[1][1][2][0] + ":\t" + ipList + "\n"
					msg = msg + "   `- " + response[1][1][1][0] + ":\t" + `response[1][1][1][1]`
				else:
					msg = "Status\n"
					msg = msg + "|- " + response[0][0] + ":\t" + `response[0][1]` + "\n"
					msg = msg + "`- " + response[1][0] + ":\t\t" + response[1][1]
			elif inC[1] == "logtarget":
				msg = "Current logging target is:\n"
				msg = msg + "`- " + response
			elif inC[1:2] == ['loglevel']:
				msg = "Current logging level is "
				if response == 1:
					msg = msg + "ERROR"
				elif response == 2:
					msg = msg + "WARN"
				elif response == 3:
					msg = msg + "INFO"
				elif response == 4:
					msg = msg + "DEBUG"
				else:
					msg = msg + `response`
			elif inC[1] == "dbfile":
				if response is None:
					msg = "Database currently disabled"
				else:
					msg = "Current database file is:\n"
					msg = msg + "`- " + response
			elif inC[1] == "dbpurgeage":
				if response is None:
					msg = "Database currently disabled"
				else:
					msg = "Current database purge age is:\n"
					msg = msg + "`- %iseconds" % response
			elif inC[2] in ("logpath", "addlogpath", "dellogpath"):
				if len(response) == 0:
					msg = "No file is currently monitored"
				else:
					msg = "Current monitored log file(s):\n"
					for path in response[:-1]:
						msg = msg + "|- " + path + "\n"
					msg = msg + "`- " + response[len(response)-1]
			elif inC[2] == "logencoding":
				msg = "Current log encoding is set to:\n"
				msg = msg + response
			elif inC[2] in ("journalmatch", "addjournalmatch", "deljournalmatch"):
				if len(response) == 0:
					msg = "No journal match filter set"
				else:
					msg = "Current match filter:\n"
					msg += ' + '.join(" ".join(res) for res in response)
			elif inC[2] == "datepattern":
				msg = "Current date pattern set to: "
				if response is None:
					msg = msg + "Default Detectors"
				elif response[0] is None:
					msg = msg + "%s" % response[1]
				else:
					msg = msg + "%s (%s)" % response
			elif inC[2] in ("ignoreip", "addignoreip", "delignoreip"):
				if len(response) == 0:
					msg = "No IP address/network is ignored"
				else:
					msg = "These IP addresses/networks are ignored:\n"
					for ip in response[:-1]:
						msg = msg + "|- " + ip + "\n"
					msg = msg + "`- " + response[len(response)-1]
			elif inC[2] in ("failregex", "addfailregex", "delfailregex",
							"ignoreregex", "addignoreregex", "delignoreregex"):
				if len(response) == 0:
					msg = "No regular expression is defined"
				else:
					msg = "The following regular expression are defined:\n"
					c = 0
					for ip in response[:-1]:
						msg = msg + "|- [" + str(c) + "]: " + ip + "\n"
						c += 1
					msg = msg + "`- [" + str(c) + "]: " + response[len(response)-1]
			elif inC[2] == "actions":
				if len(response) == 0:
					msg = "No actions for jail %s" % inC[1]
				else:
					msg = "The jail %s has the following actions:\n" % inC[1]
					msg += ", ".join(action.getName() for action in response)
		except Exception:
			logSys.warning("Beautifier error. Please report the error")
			logSys.error("Beautify " + `response` + " with " + `self.__inputCmd` +
						 " failed")
			msg = msg + `response`
		return msg

	def beautifyError(self, response):
		logSys.debug("Beautify (error) " + `response` + " with " + `self.__inputCmd`)
		msg = response
		if isinstance(response, UnknownJailException):
			msg = "Sorry but the jail '" + response[0] + "' does not exist"
		elif isinstance(response, IndexError):
			msg = "Sorry but the command is invalid"
		elif isinstance(response, DuplicateJailException):
			msg = "The jail '" + response[0] + "' already exists"
		return msg