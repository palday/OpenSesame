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

from libopensesame.py3compat import *
from PyQt4 import QtGui
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from libqtopensesame.console._base_console import base_console
from libqtopensesame.misc.config import cfg

def _style(cs, token):

	"""
	desc:
		Extracts the color from a QProgEdit style spec.

	arguments:
		cs:
			desc:	A QProgEdit colorscheme.
			type:	dict
		token:
			desc:	The style name.
			type:	[str, unicode]

	returns:
		desc:	A color string.
		type:	unicode
	"""

	color = cs.get(token, u'#000000')
	if isinstance(color, tuple):
		return color[0]
	return color

def pygments_style_factory(cs):

	"""
	arguments:
		cs:
			desc:	A QProgEdit colorscheme.
			type:	dict

	returns:
		desc:	A Pygments Style class that emulates the QProgEdit colorscheme.
		type:	Style
	"""

	from pygments.style import Style
	from pygments import token
	class my_style(Style):
		default_style = u''
		styles = {
			token.Comment 	: _style(cs, 'Comment'),
			token.Keyword	: _style(cs, 'Keyword'),
			token.Name		: _style(cs, 'Identifier'),
			token.String	: _style(cs, 'Double-quoted string'),
			token.Error		: _style(cs, 'Invalid'),
			token.Number	: _style(cs, 'Number'),
			token.Operator	: _style(cs, 'Operator'),
			token.Generic	: _style(cs, 'Default'),
		}
	return my_style

class ipython_console(base_console, QtGui.QWidget):

	"""
	desc:
		An IPython-based debug window.
	"""

	def __init__(self, main_window):

		"""
		desc:
			Constructor.

		arguments:
			main_window:	The main window object.
		"""

		super(ipython_console, self).__init__(main_window)
		kernel_manager = QtInProcessKernelManager()
		kernel_manager.start_kernel()
		self.kernel = kernel_manager.kernel
		self.kernel.gui = 'qt4'
		kernel_client = kernel_manager.client()
		kernel_client.start_channels()
		self.control = RichIPythonWidget()
		self.control.banner = self.banner()
		self.control.kernel_manager = kernel_manager
		self.control.kernel_client = kernel_client
		self.verticalLayout = QtGui.QVBoxLayout(self)
		self.verticalLayout.setContentsMargins(0,0,0,0)
		self.setLayout(self.verticalLayout)
		self.verticalLayout.addWidget(self.control)

	def clear(self):

		"""See base_console."""

		self.control.reset(clear=True)

	def focus(self):

		"""See base_console."""

		self.control._control.setFocus()

	def show_prompt(self):

		"""See base_console."""

		self.control._show_interpreter_prompt()

	def write(self, s):

		"""See base_console."""

		self.control._append_plain_text(str(s))

	def set_workspace_globals(self, _globals={}):

		"""See base_console."""

		self.kernel.shell.push(_globals)

	def setTheme(self):

		"""
		desc:
			Sets the theme, based on the QProgEdit settings.
		"""

		pass
		from QProgEdit import QColorScheme
		if not hasattr(QColorScheme, cfg.qProgEditColorScheme):
			debug.msg(u'Failed to set debug-output colorscheme')
			return u''
		cs = getattr(QColorScheme, cfg.qProgEditColorScheme)
		self.control._highlighter.set_style(pygments_style_factory(cs))
		qss = u'''QPlainTextEdit, QTextEdit {
				background-color: %(Background)s;
				color: %(Default)s;
			}
			.in-prompt { color: %(Prompt in)s; }
			.in-prompt-number { font-weight: bold; }
			.out-prompt { color: %(Prompt out)s; }
			.out-prompt-number { font-weight: bold; }
			''' % cs
		self.control.style_sheet = qss
		self.control._control.setFont(QtGui.QFont(cfg.qProgEditFontFamily,
			cfg.qProgEditFontSize))

	def setup(self, main_window):

		"""See base_subcomponent."""

		super(ipython_console, self).setup(main_window)
		self.kernel.shell.push(self.default_globals())
