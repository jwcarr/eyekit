'''
.. include:: ../.GUIDE.md
   :start-line: 4
'''

from .fixation import FixationSequence
from .image import Image, Figure
from .text import TextBlock
from . import analysis
from . import io
from . import tools

del fixation, image, text

try:
	from ._version import __version__
except ImportError:
	__version__ = '???'
