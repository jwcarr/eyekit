'''
.. include:: ../.GUIDE.md
   :start-line: 4
'''

from .fixation import FixationSequence
from .image import Image
from .text import TextBlock, set_default_alphabet, ALPHABETS
from . import analysis
from . import io
from . import tools

try:
	from ._version import __version__
except ImportError:
	__version__ = '???'
