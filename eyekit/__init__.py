"""
.. include:: ../.GUIDE.md
   :start-line: 2
"""

from .fixation import FixationSequence
from .text import TextBlock
from . import measure
from . import io
from . import tools
from . import vis

del fixation, text

__version__ = vis.__version__
