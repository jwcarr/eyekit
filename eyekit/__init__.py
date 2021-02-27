"""
.. include:: ../.GUIDE.md
   :start-line: 4
"""

from .fixation import FixationSequence
from .text import TextBlock
from . import analysis
from . import io
from . import tools
from . import vis

del fixation, text

__version__ = vis.__version__
