'''
.. include:: ../.GUIDE.md
   :start-line: 4
'''

from .fixation import FixationSequence
from .text import TextBlock
from . import analysis
from . import io
from . import tools
from . import vis

del fixation, text

try:
	from ._version import __version__
except ImportError:
	__version__ = '???'
