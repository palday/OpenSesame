#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import os.path
import sys

version = "0.26-pre1"
codename = "Earnest Einstein"

def change_working_dir():

	"""A horrifyingly ugly hack to change the working directory under Windows"""

	import libqtopensesame

	if os.name == "nt":
		try:
			# Extract the part of the description containing the path
			s = str(libqtopensesame.qtopensesame)
			i = s.find("from '") + 6
			j = s.find("'>'") - 1
			s = s[i:j]
			# Go up the tree until the path of the current script
			while not os.path.exists(os.path.join(s, "opensesame")) and \
				not os.path.exists(os.path.join(s, "opensesame.exe")):
				s = os.path.dirname(s)
			os.chdir(s)
			if s not in sys.path:
				sys.path.append(s)
			print "misc.change_working_dir(): Changing working directory to '%s'" % s
		except Exception as e:
			print "misc.change_working_dir(): Failed to change working directory:", e

def opensesamerun_options():

	"""Parse the command line options for opensesamerun"""

	import optparse
	global version, codename

	parser = optparse.OptionParser("usage: opensesamerun [experiment] [options]", \
		version = "%s '%s'" % (version, codename))

	parser.set_defaults(subject = 0)
	parser.set_defaults(logfile = None)
	parser.set_defaults(debug = False)
	parser.set_defaults(fullscreen = False)
	parser.set_defaults(pylink = False)
	parser.set_defaults(width = 1024)
	parser.set_defaults(height = 768)
	parser.set_defaults(custom_resolution = False)
	group = optparse.OptionGroup(parser, "Subject and log file options")
	group.add_option("-s", "--subject", action = "store", dest = "subject", help = "Subject number")
	group.add_option("-l", "--logfile", action = "store", dest = "logfile", help = "Logfile")
	parser.add_option_group(group)
	group = optparse.OptionGroup(parser, "Display options")
	group.add_option("-f", "--fullscreen", action = "store_true", dest = "fullscreen", help = "Run fullscreen")
	group.add_option("-c", "--custom_resolution", action = "store_true", dest = "custom_resolution", help = "Do not use the display resolution specified in the experiment file")
	group.add_option("-w", "--width", action = "store", dest = "width", help = "Display width")
	group.add_option("-e", "--height", action = "store", dest = "height", help = "Display height")
	parser.add_option_group(group)
	group = optparse.OptionGroup(parser, "Miscellaneous options")
	group.add_option("-d", "--debug", action = "store_true", dest = "debug", help = "Print lots of debugging messages to the standard output")
	parser.add_option_group(group)
	group = optparse.OptionGroup(parser, "Miscellaneous options")
	group.add_option("--pylink", action = "store_true", dest = "pylink", help = "Load PyLink before PyGame (necessary for using the Eyelink plug-ins in non-dummy mode)")
	parser.add_option_group(group)
	options, args = parser.parse_args(sys.argv)

	# Set the default logfile based on the subject nr
	if options.logfile == None:
		options.logfile = "subject%s.csv" % options.subject

	if len(sys.argv) > 1 and os.path.exists:
		options.experiment = sys.argv[1]
	else:
		options.experiment = ""

	try:
		options.subject = int(options.subject)
	except:
		parser.error("Subject (-s / --subject) should be numeric")

	try:
		options.width = int(options.width)
	except:
		parser.error("Width (-w / --width) should be numeric")

	try:
		options.height = int(options.height)
	except:
		parser.error("Height (-e / --height) should be numeric")

	return options

def opensesamerun_ready(options):

	"""
	Check if the opensesamerun options are sufficiently complete to run the experiment

	Arguments:
	options -- a dictionary containing the options

	Returns:
	True or False, depending on whether the options are sufficient
	"""

	# Check if the experiment exists
	if not os.path.exists(options.experiment):
		return False

	# Check if the logfile is writable
	try:
		open(options.logfile, "w")
	except:
		return False

	# Ready to run!
	return True

def messagebox(title, msg):

	"""
	Presents a simple tk messagebox

	Arguments:
	title -- the title of the messagebox
	msg -- the message
	"""

	import Tkinter
	root = Tkinter.Tk()
	root.title(title)
	l = Tkinter.Label(root, text=msg, justify=Tkinter.LEFT, padx=8, pady=8, \
		wraplength=300)
	l.pack()
	b = Tkinter.Button(root, text="Ok", command=root.quit)
	b.pack(side=Tkinter.RIGHT)
	root.mainloop()

def strip_tags(s):

	"""
	Strip html tags from a string and convert breaks to newlines.

	Arguments:
	s -- the string to be stripped

	Returns:
	The stripped string
	"""

	import re
	return re.compile(r'<.*?>').sub('', str(s).replace("<br />", "\n").replace("<br>", "\n"))

def resource(name):

	"""
	A hacky way to get a resource using the functionality from openexp

	Arguments:
	name -- the name of the requested resource

	Returns:
	The full path to the resource
	"""

	path = os.path.join("resources", name)
	if os.path.exists(path):
		return os.path.join("resources", name)
	if os.name == "posix":
		path = "/usr/share/opensesame/resources/%s" % name
		if os.path.exists(path):
			return path
	return None

def home_folder():

	"""
	Determines the home folder

	Returns:
	A path to the home folder
	"""

	import platform

	# Determine the home folder
	if platform.system() == "Windows":
		return os.environ["USERPROFILE"]
	if platform.system() == "Darwin":
		return os.environ["HOME"]
	if platform.system() == "Linux":
		return os.environ["HOME"]
	home_folder = os.environ["HOME"]
	print "qtopensesame.__init__(): unknown platform '%s', using '%s' as home folder" \
		% (platform.system(), home_folder)
	return home_folder

def module_versions():

	"""
	Get version info

	Returns:
	A string with version numbers
	"""

	from PyQt4 import QtCore

	s = "OpenSesame %s" % version
	s += "\nPython %d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
	s += "\nPyQt %s" % QtCore.PYQT_VERSION_STR
	try:
		import pygame
		s += "\nPyGame %s" % pygame.ver
	except:
		s += "\nPyGame not available"
	try:
		import OpenGL
		s += "\nPyOpenGL %s" % OpenGL.__version__
	except:
		s += "\nPyOpenGL not available"
	try:
		import psychopy
		s += "\nPsychoPy %s" % psychopy.__version__
	except:
		s += "\nPsychoPy not available"
	try:
		import pyglet
		s += "\nPyglet %s" % pyglet.version
	except:
		s += "\nPyglet not available"
	return s
